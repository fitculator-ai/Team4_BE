from fastapi import APIRouter
from fastapi import Depends, HTTPException
from datetime import timedelta, datetime
from app.config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM
from app.schemas import UserCreate, UserDetailCreate
from app.database import get_db
from app.models import User,  User_detail
from sqlalchemy.orm import Session
from sqlalchemy import text
from jose import jwt

router = APIRouter()

@router.post("/create-user")
def create_users(user: UserCreate, db: Session = Depends(get_db)): 
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")

    newbie = User(
        email=user.email,
        name=user.name
    )

    db.add(newbie)
    db.commit()
    db.refresh(newbie)
    
    return newbie

@router.post("/create-user-details")
def create_user_details(user_details: UserDetailCreate, db: Session = Depends(get_db)): 
    new_details = User_detail(
        user_id = user_details.user_id,
        user_nickname = user_details.user_nickname,
        exercise_issue = user_details.exercise_issue,
        exercise_goal = user_details.exercise_goal,
        resting_bpm = user_details.resting_bpm,
        height = user_details.height,
        birth = user_details.birth,
        device = user_details.device,
        profile_image = user_details.profile_image
    )

    db.add(new_details)
    db.commit()
    db.refresh(new_details)
    
    return new_details


# # token=user.token # 재로그인 방지 - refresh token

# def create_access_token(data: dict, expires_delta: timedelta = None):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# @router.post("/login")
# def login():
#     """임시 로그인 API - access_token 발급"""
#     access_token = create_access_token({"sub": "test@example.com"})
#     return {"access_token": access_token, "token_type": "bearer"}

# @router.get("/")
# def get_user(db: Session = Depends(get_db)):
#     # 예시로 이메일을 'ex@ex.com'으로 설정
#     user = db.query(User).filter(User.email == 'ex@ex.com').first()
    
#     if user:
#         return {"id": user.id, "name": user.name, "email": user.email}
#     return {"message": "User not found"}