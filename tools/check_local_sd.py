"""
Test local Stable Diffusion image generation
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

from cine_genesis.utils.imagen_client import ImagenClient
import torch

print("=" * 60)
print("  Testing Local Stable Diffusion")
print("=" * 60)
print()

# Check GPU availability
print(f"✓ PyTorch version: {torch.__version__}")
print(f"✓ CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"✓ GPU: {torch.cuda.get_device_name(0)}")
    print(f"✓ CUDA version: {torch.version.cuda}")
print()

print("📥 Initializing Stable Diffusion pipeline...")
print("   (First run will download ~4GB model - please wait)")
print()

client = ImagenClient()

print("\n🎨 Generating test image...")
print("   Prompt: A happy golden retriever in a cozy living room")
print()

img = client.generate_cinematic_scene(
    scene_description="A happy golden retriever dog sitting in a cozy living room",
    lighting="Warm, soft lighting from a floor lamp",
    color_palette="Warm ambers and browns",
    style="cinematic"
)

output_file = 'test_local_sd.png'
img.save(output_file)

print()
print("=" * 60)
print(f"✅ SUCCESS! Image saved: {output_file}")
print(f"   Size: {img.size[0]}x{img.size[1]} pixels")
print("=" * 60)
