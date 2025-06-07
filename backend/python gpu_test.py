# Check for TensorFlow GPU
print("Checking TensorFlow...")
try:
    import tensorflow as tf
    print("TensorFlow version:", tf.__version__)
    print("Num GPUs Available:", len(tf.config.list_physical_devices('GPU')))
    print("TensorFlow is using GPU:", tf.test.is_gpu_available(cuda_only=False, min_cuda_compute_capability=None))
except ImportError:
    print("TensorFlow not installed.")

# Check for PyTorch GPU
print("\nChecking PyTorch...")
try:
    import torch
    print("PyTorch version:", torch.__version__)
    print("CUDA available:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("GPU Name:", torch.cuda.get_device_name(0))
except ImportError:
    print("PyTorch not installed.")

# NumPy doesn't use GPU by default
print("\nChecking NumPy...")
try:
    import numpy as np
    print("NumPy version:", np.__version__)
    print("NumPy runs on CPU (unless used with special GPU-accelerated libraries like CuPy or JAX).")
except ImportError:
    print("NumPy not installed.")
