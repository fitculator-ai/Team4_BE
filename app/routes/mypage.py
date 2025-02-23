from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db
from sqlalchemy.orm import Session
from app.schemas import UserDetailUpdate
from app.models import User, User_detail
from app.utils.utils import get_sub_from_token


router = APIRouter()

# 유저조회
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

# 유저 프로필 수정
@router.put("/edit-user/{user_id}", response_model=UserDetailUpdate)
def edit_user(user_id: int, user_details: UserDetailUpdate, db: Session = Depends(get_db)):
    # 유저 존재 여부 확인
    existing_user = db.query(User_detail).filter(User_detail.user_id == user_id).first()

    if not existing_user:
        raise HTTPException(status_code=404, detail="유저가 존재하지 않습니다")

    # 입력된 필드만 업데이트
    update_data = user_details.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing_user, key, value)

    db.add(existing_user)
    db.commit()
    db.refresh(existing_user)

    return existing_user

# 운동량 기록 조회
# @router.get("/get-exercise-log")



# get 피로도 
