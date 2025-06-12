import os
from dotenv import load_dotenv

load_dotenv()

ACOUSTID_API_KEY = os.getenv("ACOUSTID_API_KEY")
if not ACOUSTID_API_KEY:
    raise ValueError("ACOUSTID_API_KEY environment variable not set.")

VERBOSE = os.getenv("VERBOSE")
