import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

with open('available_models.txt', 'w') as f:
    f.write("Finding available Gemini models...\n\n")
    
    models = list(genai.list_models())
    generate_models = [m for m in models if 'generateContent' in m.supported_generation_methods]
    
    f.write(f"Found {len(generate_models)} models that support generateContent:\n\n")
    
    for m in generate_models:
        f.write(f"Model: {m.name}\n")
        f.write(f"  Display Name: {m.display_name}\n")
        f.write(f"  Supported: {m.supported_generation_methods}\n\n")
    
    if generate_models:
        first_model = generate_models[0].name
        # Remove 'models/' prefix if present
        if first_model.startswith('models/'):
            first_model = first_model[7:]
        
        f.write(f"\n✅ RECOMMENDED MODEL TO USE: {first_model}\n")
    else:
        f.write("❌ No models found! Check your API key.\n")

print("Model list saved to available_models.txt")
