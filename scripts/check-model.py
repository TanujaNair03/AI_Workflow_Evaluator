import os
import sys
from google import genai

def list_active_models():
    # Explicitly fetch your custom environment variable
    api_key = os.environ.get("GENAI_API_KEY")
    
    if not api_key:
        print("Error: GENAI_API_KEY is not set in your environment.")
        print("Run: export GENAI_API_KEY='your_key_here'")
        sys.exit(1)

    # Initialize client with the explicit key
    client = genai.Client(api_key=api_key)

    print(f"{'Model Name':<50} | {'Supported Actions'}")
    print("-" * 85)

    try:
        # client.models.list() returns an iterable of Model objects
        for model in client.models.list():
            # In the 2026 SDK, supported_actions contains the capabilities 
            # like 'generateContent', 'embedContent', etc.
            actions = ", ".join(model.supported_actions)
            print(f"{model.name:<50} | {actions}")
            
    except Exception as e:
        print(f"Critial Failure during model enumeration: {e}")

if __name__ == "__main__":
    list_active_models()