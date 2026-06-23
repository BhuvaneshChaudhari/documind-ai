import subprocess
import sys

subprocess.run([
    sys.executable, "-m", "uvicorn", "app:app",
    "--reload",
    "--reload-exclude", "chroma_db/*",
    "--reload-exclude", "uploads/*",
    "--port", "8000",
    "--timeout-keep-alive", "300",
])
