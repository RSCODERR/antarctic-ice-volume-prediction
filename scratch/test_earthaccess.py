"""
Test script for earthaccess token authentication.
"""
import os
from dotenv import load_dotenv
import earthaccess

load_dotenv()
token = os.getenv("EARTHDATA_TOKEN")
print(f"Token present: {bool(token)}, length: {len(token) if token else 0}")

try:
    auth = earthaccess.login(strategy="environment")
    print(f"earthaccess authenticated: {auth.authenticated}")
except Exception as e:
    print(f"earthaccess login error: {e}")

