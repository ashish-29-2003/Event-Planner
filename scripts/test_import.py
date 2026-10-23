import sys
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")

try:
    import fastapi
    print(f"FastAPI: {fastapi.__version__}")
except Exception as e:
    print(f"FastAPI import error: {e}")

try:
    import pydantic
    print(f"Pydantic: {pydantic.__version__}")
except Exception as e:
    print(f"Pydantic import error: {e}")

try:
    import httpx
    print(f"HTTPX: {httpx.__version__}")
except Exception as e:
    print(f"HTTPX import error: {e}")

try:
    from google import genai
    print("Google GenAI SDK (google.genai) imported successfully!")
except Exception as e:
    print(f"Google GenAI import error: {e}")

try:
    import pytest
    print(f"Pytest: {pytest.__version__}")
except Exception as e:
    print(f"Pytest import error: {e}")
