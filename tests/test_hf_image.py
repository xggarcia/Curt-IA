"""
Test Hugging Face image generation
"""
from dotenv import load_dotenv
load_dotenv()

from cine_genesis.utils.imagen_client import ImagenClient
import os

print(f"✓ API Key loaded: {bool(os.getenv('HUGGINGFACE_API_KEY'))}")

client = ImagenClient(api_key='dummy')
print("\n🎨 Generating test image...")
print("Prompt: A happy golden retriever dog in a cozy living room")

img = client.generate_cinematic_scene(
    scene_description="A happy golden retriever dog sitting in a cozy living room",
    lighting="Warm, soft lighting",
    color_palette="Warm ambers and browns",
    style="cinematic"
)

output_file = 'test_huggingface.png'
img.save(output_file)
print(f"\n✅ Success! Image saved: {output_file}")
print(f"   Size: {img.size[0]}x{img.size[1]} pixels")
