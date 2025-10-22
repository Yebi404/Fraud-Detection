import os
import google.generativeai as genai

# Configure API key
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Pick a model from the list above
model_name = "models/gemini-2.5-pro"

try:
    response = genai.generate_text(
        model=model_name,
        prompt="Explain how a transaction verification system works in simple terms.",
        temperature=0.7,
        max_output_tokens=200
    )
    
    print("💡 Model output:\n")
    print(response.text)

except Exception as e:
    print("❌ Error generating text:", e)
