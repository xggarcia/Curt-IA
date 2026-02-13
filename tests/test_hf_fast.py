"""
Test Hugging Face with a faster, smaller model
"""
from dotenv import load_dotenv
load_dotenv()

import os
import requests
from PIL import Image
import io

# Check API key
hf_key = os.getenv('HUGGINGFACE_API_KEY')
print(f"✓ API Key: {hf_key[:15]}..." if hf_key else "❌ No API key")

# Try a faster model
API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
headers = {"Authorization": f"Bearer {hf_key}"}

prompt = "cinematic photo of a golden retriever dog in a living room, warm lighting, 8k, professional"

print(f"\n🎨 Generating image...")
print(f"   Model: runwayml/stable-diffusion-v1-5 (faster)")

try:
    response = requests.post(
        API_URL,
        headers=headers,
        json={"inputs": prompt, "options": {"wait_for_model": True}},
        timeout=120
    )
    
    print(f"\n✓ Response: {response.status_code}")
    
    if response.status_code == 200:
        img = Image.open(io.BytesIO(response.content))
        output_file = 'test_hf_success.png'
        img.save(output_file)
        print(f"✅ SUCCESS! Image saved: {output_file}")
        print(f"   Size: {img.size}")
    else:
        print(f"❌ Error {response.status_code}")
        try:
            error_data = response.json()
            print(f"   Message: {error_data.get('error', 'Unknown error')}")
        except:
            print(f"   Response: {response.text[:200]}")
            
except Exception as e:
    print(f"❌ Exception: {type(e).__name__}")
    print(f"   {str(e)[:200]}")
