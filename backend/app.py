from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from PIL import Image
from transformers import Blip2Processor, Blip2ForConditionalGeneration
import torch
import requests
import json

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Device setup
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load BLIP-2 FLAN-T5
blip_processor = Blip2Processor.from_pretrained("Salesforce/blip2-flan-t5-xl")
blip_model = Blip2ForConditionalGeneration.from_pretrained(
    "Salesforce/blip2-flan-t5-xl",
    device_map="auto",
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
)

# Labels
OBJECT_LABELS = ["Shoe", "Watch", "Wallet", "Bag", "Purse", "Glasses", "Hat", "Phone", "Jacket", "Belt"]
MATERIAL_LABELS = ["Leather", "Canvas", "Suede", "Synthetic", "Rubber", "Metal", "Plastic", "Glass", "Wood", "Fabric"]

# Product-specific condition tags
PRODUCT_TAGS = {
    "Shoe": ["creased toe box", "worn sole", "heel wear", "misaligned heel", "sole intact", "upper intact", "visible scuff marks", "clean surface", "smooth finish", "like new"],
    "Watch": ["shiny bezel", "scratched glass", "buckle rusted", "strap discolored", "dial clean", "metal polished", "clean surface", "dial dirty", "well maintained"],
    "Wallet": ["soft leather", "strap cracked", "zipper broken", "corners frayed", "lining clean", "logo faded"],
    "Bag": ["strap cracked", "zipper broken", "lining clean", "corners frayed", "logo faded", "torn material"],
    "Purse": ["zipper broken", "soft leather", "strap wrinkled", "pristine condition"],
    "Glasses": ["frame intact", "lens scratched", "hinge loose", "nose pad clean", "lens spotless"],
    "Hat": ["brim firm", "fabric stretched", "collar worn", "fabric smooth"],
    "Phone": ["screen pristine", "cracked screen", "back cover intact", "body dented", "buttons responsive", "frame scuffed"],
    "Jacket": ["buttons intact", "fabric smooth", "collar worn", "lining damaged"],
    "Belt": ["buckle polished", "buckle rusted", "holes stretched", "strap wrinkled", "leather supple", "strap smooth"]
}

class ReportResponse(BaseModel):
    success: bool
    product_type: str
    material: str
    condition_score: int
    condition_report: str
    tags: List[str]

def analyze_with_blip(image: Image.Image, label_list: List[str], label_type: str = "object") -> str:
    best_label = "Unknown"
    best_confidence = 0
    for label in label_list:
        prompt = f"What is shown in the image? Is the {label_type} a {label}?"
        inputs = blip_processor(images=image, text=prompt, return_tensors="pt").to(blip_model.device)
        with torch.no_grad():
            output = blip_model.generate(**inputs, max_new_tokens=15)
            answer = blip_processor.decode(output[0], skip_special_tokens=True).lower()
        if any(word in answer for word in ["yes", "definitely", "clearly"]):
            return label  # confident match
        elif any(word in answer for word in ["probably", "maybe", "likely"]):
            best_label = label
    return best_label

def extract_top_tags_with_blip(image: Image.Image, product_type: str) -> List[str]:
    tags = PRODUCT_TAGS.get(product_type, [])
    selected_tags = []
    for tag in tags:
        prompt = f"What visible signs of {tag} can you observe in this {product_type.lower()}?"
        inputs = blip_processor(images=image, text=prompt, return_tensors="pt").to(blip_model.device)
        with torch.no_grad():
            output = blip_model.generate(**inputs, max_new_tokens=20)
            response = blip_processor.decode(output[0], skip_special_tokens=True).lower()

        trigger_words = ["yes", "shows", "visible", "worn", "damaged", "scratched", "minor", "marks", "slight", "some", "faint", "present"]
        if any(word in response for word in trigger_words) or tag.split()[0] in response:
            selected_tags.append(tag)

    return selected_tags

def map_condition_to_score(tags: List[str]) -> int:
    damage_tags = {
        "creased toe box", "worn sole", "heel wear", "misaligned heel", "visible scuff marks",
        "scratched glass", "buckle rusted", "strap discolored", "strap cracked", "zipper broken", "dial dirty",
        "corners frayed", "logo faded", "torn material", "strap wrinkled", "lens scratched",
        "hinge loose", "fabric stretched", "collar worn", "lining damaged", "cracked screen",
        "body dented", "frame scuffed", "holes stretched"
    }
    damage_detected = [tag for tag in tags if tag in damage_tags]
    if not damage_detected:
        return 10
    elif len(damage_detected) == 1:
        return 8
    elif len(damage_detected) == 2:
        return 6
    else:
        return 4

def call_phi4(product_type: str, material: str, tags: list[str]) -> str:
    tag_string = ", ".join(tags)
    if not tag_string:
        tag_string = "no visible flaws"
    prompt = (
        f"Write a 50-word condition summary for a {material} {product_type} based on these observations: {tag_string}. "
        f"If the item appears flawless, describe it positively, but avoid excessive praise and poetic exaggeration. If any imperfections exist, describe them naturally. "
        f"Use a warm, human tone. Avoid technical jargon, judgments, or repair suggestions."
    )
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "phi4:14b-q4_K_M", "prompt": prompt},
        stream=True
    )
    if response.status_code == 200:
        chunks = []
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode("utf-8"))
                    chunks.append(data.get("response", ""))
                except Exception:
                    continue
        return "".join(chunks).strip()
    else:
        raise RuntimeError(f"Ollama error: {response.text}")

@app.post("/analyze-images/", response_model=ReportResponse)
async def analyze_images(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No images uploaded.")

    all_tags = []
    image_objects = []

    for file in files:
        img = Image.open(file.file).convert("RGB")
        image_objects.append(img)

    product_type = analyze_with_blip(image_objects[0], OBJECT_LABELS, label_type="object")
    material = analyze_with_blip(image_objects[0], MATERIAL_LABELS, label_type="material")

    condition_tags = PRODUCT_TAGS.get(product_type, [])
    if not condition_tags:
        raise HTTPException(status_code=500, detail=f"No condition tags defined for product type: {product_type}")

    for img in image_objects:
        tags = extract_top_tags_with_blip(img, product_type)
        all_tags.extend(tags)

    unique_tags = list(set(all_tags))
    condition_score = map_condition_to_score(unique_tags)

    try:
        report = call_phi4(product_type, material, unique_tags)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

    return ReportResponse(
        success=True,
        product_type=product_type,
        material=material,
        condition_score=condition_score,
        condition_report=report,
        tags=unique_tags
    )
