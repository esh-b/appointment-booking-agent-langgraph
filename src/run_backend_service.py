import uvicorn
from dotenv import load_dotenv

load_dotenv()


if __name__ == "__main__":
    uvicorn.run("backend_service:app", host='0.0.0.0', port=8000)
