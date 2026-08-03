"""
scripts/generate_sample_model.py
==================================
Generates a sample MobileNetV2 model with random weights for development
and testing purposes.

This script should be run once before starting the API for the first time,
OR whenever you need to replace the model with a fresh untrained baseline.

Usage:
    python scripts/generate_sample_model.py

Output:
    models/mobilenetv2_padi.pth

WARNING:
    This generates RANDOM weights. The model will NOT produce meaningful
    predictions. Replace with the trained .pth file from Google Colab for
    production use.
"""
import json
import sys
from pathlib import Path

# Allow importing from the project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def generate_sample_model() -> None:
    """Build and save a MobileNetV2 model with random (untrained) weights."""
    try:
        import torch
        import torch.nn as nn
        from torchvision import models
    except ImportError as exc:
        print(f"[ERROR] Missing dependency: {exc}")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)

    # Load class labels from labels.json
    labels_path = Path("models/labels.json")
    if not labels_path.exists():
        print(f"[ERROR] {labels_path} not found. Run from the project root.")
        sys.exit(1)

    with open(labels_path, "r", encoding="utf-8") as f:
        labels = json.load(f)
    num_classes = len(labels)

    print(f"[INFO] Building MobileNetV2 with {num_classes} classes: {labels}")

    # Build architecture matching what loader.py expects
    model = models.mobilenet_v2(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, num_classes)

    # Save state dict (no random seed — weights are arbitrary for testing)
    output_path = Path("models/mobilenetv2_padi.pth")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), output_path)

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"[SUCCESS] Saved sample model to: {output_path} ({size_mb:.1f} MB)")
    print("[WARNING] This model uses RANDOM weights and is for testing only.")
    print("          Replace with your trained .pth file from Google Colab.")


if __name__ == "__main__":
    generate_sample_model()
