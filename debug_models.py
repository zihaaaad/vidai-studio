
import google.generativeai as genai
import json
import os

try:
    with open('config.json') as f:
        api_key = json.load(f)['api_key']
    genai.configure(api_key=api_key)
    print("Listing models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name} ({m.display_name})")
except Exception as e:
    print(f"Error: {e}")
