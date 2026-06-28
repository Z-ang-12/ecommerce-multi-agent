from functools import lru_cache
from langchain_community.embeddings import HuggingFaceEmbeddings

@lru_cache()
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="C:\\Users\\asus\\.cache\\huggingface\\hub\\models--sentence-transformers--all-MiniLM-L6-v2\\snapshots\\1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
    )

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth import verify_token

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        username = verify_token(token)
        return username
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 无效或已过期",
        )