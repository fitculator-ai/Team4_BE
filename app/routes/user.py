from fastapi import APIRouter
from fastapi import Depends, HTTPException, status
from datetime import timedelta, datetime
from app.config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM
from app.schemas import UserCreate, UserDetailCreate
from app.database import get_db
from app.models import User,  User_detail
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.utils.utils import create_access_token

router = APIRouter()

# 유저 추가
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

# 유저 상세정보 추가
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


# 유저 로그인 - 이메일 있으면 토큰 저장
@router.post("/login")
def login(email: str, db: Session = Depends(get_db)):
    """이메일로 로그인 → access_token 발급"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="이메일이 존재하지 않습니다.",
            )
    access_token = create_access_token({"sub": user.email})
    user.token = access_token  # 발급한 토큰 저장
    db.commit()
    return {"access_token": access_token, "token_type": "bearer"}


# @router.get("/")
# def get_user(db: Session = Depends(get_db)):
#     # 예시로 이메일을 'ex@ex.com'으로 설정
#     user = db.query(User).filter(User.email == 'ex@ex.com').first()
    
#     if user:
#         return {"id": user.id, "name": user.name, "email": user.email}
#     return {"message": "User not found"}

# # token=user.token # 재로그인 방지 - refresh token
