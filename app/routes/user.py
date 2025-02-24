from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import UserCreate, UserDetailCreate
from app.utils.utils import create_access_token
from app.utils.utils import get_sub_from_token
from app.models import User,  User_detail
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter()

# 유저 추가
@router.post("/create-user", summary="유저 생성")
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
@router.post("/create-user-details", summary="유저 상세 정보 생성")
def create_user_details(user_details: UserDetailCreate, db: Session = Depends(get_db)): 
    user = db.query(User_detail).filter(User_detail.user_id == user_details.user_id).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유저 상세정보가 존재합니다. Edit-profile을 이용하여 상세정보를 수정하십시오.",
        )

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
@router.post("/login", summary="유저 로그인(토큰 저장)")
def login(email: str, db: Session = Depends(get_db)):
    """이메일로 로그인 → access_token 발급"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="이메일이 존재하지 않습니다.",
            )
    # 기존 토큰이 만료된 상태라면 새로 발급
    if user.token:
        sub = get_sub_from_token(user.token)
        if sub is None:
            # 기존 만료된 토큰을 삭제하고 새로 발급
            user.token = None

    access_token = create_access_token({"sub": user.email})
    user.token = access_token  # 발급한 토큰 저장
    db.commit()
    return {"access_token": access_token, "token_type": "bearer"}

# 로그아웃
@router.post("/logout", summary="로그아웃(토큰 삭제)")
def logout(email: str, db: Session = Depends(get_db)):
    """로그인 토큰이 있는 유저만 로그아웃 가능"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일이 존재하지 않습니다.",
        )

    # 토큰이 없으면 로그아웃할 수 없음
    if not user.token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인된 상태가 아닙니다.",
        )
    
    # 토큰 검증
    sub = get_sub_from_token(user.token)

    if sub is None:
        # 만료된 토큰인 경우 그냥 처리
        user.token = None  # 만료된 토큰이므로 삭제
        db.commit()
        return {"message": "만료된 토큰입니다, 다시 로그인 해주세요."}
    
    # 토큰을 null로 업데이트하여 로그아웃 처리
    user.token = None
    db.commit()

    return {"message": "로그아웃 되었습니다."}