import os
import google.generativeai as genai

# Get API key from environment
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ GEMINI_API_KEY environment variable not set!")
    exit(1)

print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
print(f"✅ google-generativeai version: {genai.__version__}")

try:
    # Configure the API
    genai.configure(api_key=api_key)
    print("✅ API configured successfully")
    
    # Test listing models
    print("\n📋 Available models:")
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"  - {model.name}")
    
    # Simple test generation with latest model
    print("\n🧪 Testing content generation...")
    model = genai.GenerativeModel('gemini-2.5-flash')  # Using latest fast model
    response = model.generate_content("Say 'Hello, I am working!' in one sentence.")
    
    print("\n✅ CONNECTION SUCCESSFUL!")
    print(f"📝 Response: {response.text}")
    
except Exception as e:
    print(f"\n❌ CONNECTION FAILED!")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()