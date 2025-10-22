import os
import google.generativeai as genai

# Make sure your GEMINI_API_KEY is set as an environment variable
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set!")

# Configure the API key
genai.configure(api_key=api_key)

try:
    # Generate text using the 'text-bison-001' model
    response = genai.generate_text(
        model="text-bison-001",
        prompt="Hello! Explain Variational Autoencoders (VAE) in simple terms.",
        max_output_tokens=200
    )
    
    # Print the generated text
    print("Generated Text:\n")
    print(response.result)

except Exception as e:
    print(f"❌ Error generating text: {e}")
