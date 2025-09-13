import os
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", f"sqlite:///{os.path.join(BASE_DIR, 'panda.db')}")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "changeme")  # simple admin protection token
