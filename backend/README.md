# Item-Inspector AI Pipeline (BLIP-2 + FastAPI + Ollama-Phi4)

This project provides a complete image-based condition analysis backend using Salesforce's BLIP-2 model for visual understanding and Phi-4 via Ollama for natural language report generation.

---

## 🚀 Features
- Detects **product type** (e.g., Watch, Shoe, Belt, etc.)
- Identifies **material** (e.g., Leather, Metal, Suede, etc.)
- Extracts **product-specific visual condition tags** (e.g., "scratched glass", "worn sole", etc.)
- Generates **50-word condition reports** using the **Phi-4 LLM**
- Outputs structured `JSON` response with product metadata and condition score

---

## 🛠 Setup Instructions

### ✅ Requirements
- Python 3.10+
- Ollama installed and running
- Git (optional)

### 📁 Folder Structure
```
Item-Inspector AI/
├── backend/
│   ├── app.py               # This FastAPI file
│   ├── requirements.txt
│   └── README.md            # (this file)
├── frontend/
│   └── index.html           # Web UI for uploading images
├── sample_images/
│   └── example_watch.jpg    # Example test image
```

### 📦 Create and Activate Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 📥 Install Python Dependencies
```bash
pip install -r requirements.txt
```

### ⚙️ Start Ollama (Phi-4)
Open another terminal:
```bash
ollama run phi4
```

### ▶️ Start FastAPI Server
```bash
uvicorn app:app --reload
```

You’ll see: `Uvicorn running on http://127.0.0.1:8000`

### 🌐 Test in Browser
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Upload an image to `/analyze-images/`
- You will receive:
```json
{
  "success": true,
  "product_type": "Watch",
  "material": "Metal",
  "condition_score": 8,
  "condition_report": "This metal watch...",
  "tags": ["scratched glass"]
}
```

### 🖼 Optional: Use HTML Upload UI
Open `frontend/index.html` in your browser and drag-drop images.

---

## 🧠 How it Works
- BLIP-2 is queried with prompt templates to match object, material, and visual tags.
- Tags are filtered and used to compute a `condition_score` (4–10)
- Tags are passed to Phi-4 to generate a 50-word natural language condition report.

---

## 📄 License
MIT License — Open use for development, research, and internal testing.

---

For feedback or contributions, contact [rooshikeshbhatt@gmail.com](mailto:rooshikeshbhatt@gmail.com).
