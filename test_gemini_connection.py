import os
import sys

# Check if google.generativeai is installed
try:
    import google.generativeai as genai
    print("✓ google.generativeai library is installed")
except ImportError:
    print("✗ google.generativeai library NOT installed")
    print("\nTo install, run:")
    print("pip install google-generativeai")
    sys.exit(1)

# Check if API key is set
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("✗ GEMINI_API_KEY environment variable is not set")
    print("\nTo set it:")
    print("Windows: set GEMINI_API_KEY=your_api_key_here")
    print("Linux/Mac: export GEMINI_API_KEY=your_api_key_here")
    sys.exit(1)
else:
    print(f"✓ GEMINI_API_KEY is set (length: {len(api_key)} characters)")

# Try to configure and make a test call
try:
    genai.configure(api_key=api_key)
    print("✓ API key configured successfully")
    
    # Test with a simple prompt
    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    print("✓ Model initialized: gemini-2.0-flash-exp")
    
    print("\nTesting API call with a simple prompt...")
    response = model.generate_content("Say 'Hello, API is working!'")
    
    if hasattr(response, 'text') and response.text:
        print(f"✓ API Response: {response.text}")
        print("\n✅ CONNECTION TEST SUCCESSFUL!")
    else:
        print("✗ Response received but no text content")
        print(f"Response object: {response}")
        
except Exception as e:
    print(f"✗ Error during API call: {e}")
    print(f"Error type: {type(e).__name__}")
    sys.exit(1)