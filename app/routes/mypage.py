from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db
from sqlalchemy.orm import Session
from app.schemas import UserDetailUpdate, UserDetailView, WeekExerciseLogView
from app.models import User, User_detail, ExerciseLog
from app.utils.utils import get_sub_from_token, get_exercise_logs, get_last_4_weeks_exercise_logs
from typing import List
from datetime import datetime
from dateutil import tz


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

# 유저 상제정보 조회
@router.get("/get-user-details", response_model=UserDetailView)
def get_user_details(user_id: int, db: Session = Depends(get_db)):
    # 유저 상세정보 존재 여부 확인
    existing_user_details = db.query(User_detail).filter(User_detail.user_id == user_id).first()
    if not existing_user_details:
        raise HTTPException(status_code=404, detail="유저 상세정보가 존재하지 않습니다.")
    return existing_user_details


# 유저 프로필 수정
@router.put("/edit-user/{user_id}", response_model=UserDetailUpdate, summary="유저의 프로필 정보를 수정함")
def edit_user(user_id: int, user_details: UserDetailUpdate, db: Session = Depends(get_db)):
    """ 유저 상세정보 수정 필요한 값 요청가능
    """
    # 유저 상세정보 존재 여부 확인
    existing_user = db.query(User_detail).filter(User_detail.user_id == user_id).first()

    if not existing_user:
        raise HTTPException(status_code=404, detail="유저 상세정보가 존재하지 않습니다.")

    # 입력된 필드만 업데이트
    update_data = user_details.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing_user, key, value)

    db.add(existing_user)
    db.commit()
    db.refresh(existing_user)

    return existing_user

#유저 안정심박수 조회
@router.get("/resting-heart-rate", summary="유저의 안정 심박수를 조회함")
def get_resting_heart_rate(user_id: int, db: Session = Depends(get_db)):

    # 유저 상세정보  존재 여부 확인
    existing_user = db.query(User_detail).filter(User_detail.user_id == user_id).first()

    if not existing_user:
        raise HTTPException(status_code=404, detail="유저 안정심박수가 존재하지 않습니다.")

    result = {"resting_bpm" : existing_user.resting_bpm}
    return result
    
# 미설정 
# 안정심박수 설정
@router.put("/put-resting-heart-rate", response_model=None, summary="유저의 안정 심박수를 수정함")
def put_resting_heart_rate(user_id: int, resting_bpm: int, db: Session = Depends(get_db)):
    if 40 >= resting_bpm or resting_bpm >= 120:
        raise HTTPException(status_code=404, detail="40 ~ 120 사이를 입력해주세요")
    # 유저 상세정보  존재 여부 확인
    existing_user = db.query(User_detail).filter(User_detail.user_id == user_id).first()

    if not existing_user:
        raise HTTPException(status_code=404, detail="유저 안정심박수가 존재하지 않습니다.")

    existing_user.resting_bpm= resting_bpm
    db.commit()
    db.refresh(existing_user)

    return {"msg": "resting_bpm이 성공적으로 업데이트되었습니다.", "resting_bpm": existing_user.resting_bpm}

# 운동량 기록 조회
@router.get("/get-exercise-log", response_model=List[WeekExerciseLogView], summary="지난 4주간 운동량을 조회함")
def get_exercise_log(user_id: int, db: Session = Depends(get_db)):
     # 유저 상세정보  존재 여부 확인
    existing_user = db.query(ExerciseLog).filter(ExerciseLog.user_id == user_id).first()

    if not existing_user:
        raise HTTPException(status_code=404, detail="유저 운동기록이 존재하지 않습니다.")
    request_time = datetime.now(tz.tzlocal())
    result = get_last_4_weeks_exercise_logs(user_id=user_id, db=db, date=request_time)
    return result

# get 피로도 
