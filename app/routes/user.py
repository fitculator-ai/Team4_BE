from fastapi import APIRouter

# get 유저조회
# get 피로도
# get 운동량 기록 
# put 프로필 수정

router = APIRouter()

@router.get("/")
def create_user():
    return {"message": "회원가입"}

# 로그인
@router.post("/login")
def create_user():
    return {"message": "로그인"}
