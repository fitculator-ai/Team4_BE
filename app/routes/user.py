from app.config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM
from fastapi import FastAPI, Depends, HTTPException
from datetime import timedelta, datetime
from fastapi import APIRouter
from jose import jwt


router = APIRouter()

@router.get("/")
def get_user():
    return {"message": "유저조회"}

