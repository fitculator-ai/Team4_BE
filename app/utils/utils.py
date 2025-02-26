from app.schemas import ExerciseLogView, WeekExerciseLogView
from app.models import ExerciseLog, Exercise, User_detail, User
from fastapi import HTTPException, status, UploadFile
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from boto3 import client
from decouple import config
from app.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME, AWS_REGION
from botocore.exceptions import NoCredentialsError
import io
import uuid
import magic
from PIL import Image

# 선택한 datetime의 월요일 일요일의 날짜를 반환하는 함수
def get_week_start_end(target_date: datetime):
    monday = target_date - timedelta(days=target_date.weekday())  # 해당 주의 월요일
    sunday = monday + timedelta(days=6)  # 해당 주의 일요일
    return monday.date(), sunday.date()

# 요청을 보낸 유저의 주간 운동 기록을 반환하는 함수
def get_exercise_logs(db: Session, user_id: int, date: datetime):
    monday, sunday = get_week_start_end(date)
    raw_data = (
    db.query(ExerciseLog, Exercise.exercise_name)
    .join(Exercise, ExerciseLog.exercise_id == Exercise.id)
    .filter(
        ExerciseLog.user_id == user_id,
        ExerciseLog.end_at.between(monday, sunday)
    )
    .group_by(
        ExerciseLog.id,
        ExerciseLog.user_id,
        ExerciseLog.exercise_id,
        ExerciseLog.avg_bpm,
        ExerciseLog.max_bpm,
        ExerciseLog.duration,
        ExerciseLog.end_at,
        ExerciseLog.exercise_intensity,
        ExerciseLog.earned_point,
        ExerciseLog.exercise_note,
        Exercise.exercise_name
    )
    .order_by(ExerciseLog.end_at.desc())
    .all()
)
    return [
    {
        "id": log.id,
        "user_id": log.user_id,
        "exercise_name": exercise_name,
        "avg_bpm": log.avg_bpm,
        "max_bpm": log.max_bpm,
        "duration": log.duration,
        "end_at": log.end_at.isoformat(),
        "exercise_intensity": log.exercise_intensity,
        "earned_point": log.earned_point,
        "exercise_note": log.exercise_note or None
    }
    for log, exercise_name in raw_data 
]

# 운동 강도 측정 로직
def exercise_intensity(avg_bpm, age):
    hr_max = 220 - age
    avg_intensity = (avg_bpm / hr_max) * 100

    if avg_intensity < 40:
        return "매우 낮음"
    elif avg_intensity < 50:
        return "낮음"
    elif avg_intensity < 65:
        return "보통"
    elif avg_intensity < 80:
        return "높음"
    else:
        return "매우 높음"
    
# 유저의 유, 무를 판단하는 로직
def get_user_info(db: Session, user_id: int):
    user = db.query(User_detail).filter(User_detail.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="해당 유저를 찾을 수 없습니다.")
    return user

# 로그인 - 토큰 생성
def create_access_token(data: dict, expires_delta: timedelta = None):
    """JWT 토큰 생성"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=int(config("ACCESS_TOKEN_EXPIRE_MINUTES", default = 30))))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config("SECRET_KEY"), algorithm=config("ALGORITHM"))
    return encoded_jwt

# 토큰 검증
def get_sub_from_token(token: str):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 없습니다."
        )
    try:
        # verify_exp=False로 만료 여부를 확인하지 않음
        decoded_token = jwt.decode(token, config("SECRET_KEY"), algorithms=[config("ALGORITHM")], options={"verify_exp": False})
        return decoded_token.get("sub")  # sub 값 반환    
    except JWTError:
        # 토큰이 유효하지 않은 경우 (예: 위조된 토큰)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 유호하지 않습니다."
        )
    
# 최근 4주간 운동 기록 조회 
def get_last_4_weeks_exercise_logs(db: Session, user_id: int, date: datetime, target: int):
    all_weeks_logs = []

    for week_offset in range(target): # 총 4주
        target_date = date - timedelta(weeks=week_offset)
        monday, sunday = get_week_start_end(target_date)

        raw_data = (
            db.query(ExerciseLog, Exercise.exercise_name)
            .join(Exercise, ExerciseLog.exercise_id == Exercise.id)
            .filter(
                ExerciseLog.user_id == user_id,
                ExerciseLog.end_at.between(monday, sunday)
            )
            .all()
        )

        week_data = WeekExerciseLogView(
            week_start=monday.isoformat(),
            week_end=sunday.isoformat(),
            logs=[
                ExerciseLogView(
                    user_id=log.user_id,
                    exercise_name=exercise_name,
                    avg_bpm=log.avg_bpm,
                    max_bpm=log.max_bpm,
                    duration=log.duration,
                    end_at=log.end_at,
                    exercise_intensity=log.exercise_intensity,
                    earned_point=log.earned_point,
                    exercise_note=log.exercise_note if log.exercise_note else None
                )
                for log, exercise_name in raw_data
            ]
        )

        all_weeks_logs.append(week_data)

    return all_weeks_logs

def existing_user(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="없는 유저입니다.")
    else:
        return user

# S3 클라이언트 초기화
s3_client = client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

def upload_to_s3(file: io.BytesIO, file_name: str) -> None:
    """S3에 파일 업로드 후 URL 반환"""
    try:
        s3_client.upload_fileobj(
            file,
            S3_BUCKET_NAME,
            file_name,
            ExtraArgs={"ContentType": "image/jpeg"},
        )
        file_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{file_name}"
        return file_url
    except NoCredentialsError:
        raise ValueError("AWS 인증 정보가 잘못되었습니다.")
    
# s3 중복이름 방지 uuid 고유 이미지이름 
def generate_unique_filename(user_id: int, filename: str) -> str:
    unique_id = str(uuid.uuid4())  # 고유한 UUID 생성
    unique_filename = f"user_{user_id}_profile_{unique_id}_{filename}"
    return unique_filename

# 이미지 파일인지 확인하는 함수
def is_image(file_content):
    # BytesIO 객체의 길이를 명시적으로 확인
    if isinstance(file_content, io.BytesIO):
        file_content.seek(0, io.SEEK_END)
        file_size = file_content.tell()
        file_content.seek(0)
    else:
        raise HTTPException(status_code=400, detail="잘못된 파일 형식입니다.")
    
    mime = magic.Magic(mime=True)
    file_type = mime.from_buffer(file_content.read(file_size))

    # MIME 타입이 이미지가 아닐 경우 예외 처리
    if "image" not in file_type:
        raise HTTPException(status_code=400, detail="이미지만 업로드 가능합니다.")
    
    try:
        # PIL로 파일을 실제로 열어 이미지 파일인지 확인
        file_content.seek(0)  # 파일을 처음부터 다시 읽을 수 있도록 시퀀스를 초기화
        Image.open(file_content)
        return True
    except IOError:
        # PIL에서 이미지로 열 수 없는 경우 (비 이미지 파일)
        raise HTTPException(status_code=400, detail="이미지만 업로드 가능합니다.")