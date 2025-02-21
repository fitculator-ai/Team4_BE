from fastapi import APIRouter, Depends, HTTPException, status


from app.database import get_db
from sqlalchemy.orm import Session
from app.models import User
from app.utils.utils import get_sub_from_token

# get 유저조회
# get 피로도
# get 운동량 기록 
# put 프로필 수정

router = APIRouter()

@router.get("/get-user")
def get_user(email: str, db: Session = Depends(get_db)):
    # 유저 존재 여부 확인
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일이 존재하지 않습니다.",
        )
    # 토큰을 이용해 sub 값을 확인
    try:
        sub = get_sub_from_token(user.token)
    except HTTPException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 유효하지 않습니다.",
        )  

    # 토큰이 잘못되었거나 누락된 경우 처리
    if not user.token or sub != user.email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 잘못되었거나 누락되었습니다.",
        )

    return user

@router.put("/edit-user")
def edit_user(email: str, db: Session = Depends(get_db)):
    pass