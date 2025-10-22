import os
import google.generativeai as genai

# Configure API key
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

try:
    models = genai.list_models()
    print("✅ Accessible models:\n")
    
    for m in models:
        # Print all attributes of the model object
        print(vars(m))  # or use dir(m) to see methods too

except Exception as e:
    print("❌ Error listing models:", e)
