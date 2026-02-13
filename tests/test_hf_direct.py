"""
Test Hugging Face image generation with better error handling
"""
from dotenv import load_dotenv
load_dotenv()

import os
import requests

# Check API key
hf_key = os.getenv('HUGGINGFACE_API_KEY')
print(f"✓ API Key loaded: {bool(hf_key)}")
print(f"  Key prefix: {hf_key[:10]}..." if hf_key else "  No key found")

# Test API directly
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {hf_key}"}

prompt = "A happy golden retriever dog in a cozy living room, cinematic lighting, professional photography"

print(f"\n🎨 Testing Hugging Face API...")
print(f"   Model: stabilityai/stable-diffusion-xl-base-1.0")
print(f"   Prompt: {prompt[:60]}...")

response = requests.post(
    API_URL,
    headers=headers,
    json={"inputs": prompt},
    timeout=60
)

print(f"\n Response status: {response.status_code}")

if response.status_code == 200:
    print("✅ Success! Image data received")
    from PIL import Image
    import io
    img = Image.open(io.BytesIO(response.content))
    img.save('test_hf_direct.png')
    print(f"   Saved to: test_hf_direct.png")
    print(f"   Size: {img.size}")
else:
    print(f"❌ Error: {response.status_code}")
    print(f"   Response: {response.text[:500]}")
