# 환경 변수, 설정 관리
from decouple import config

 
# 데이터베이스 설정
DB_USER = config("DB_USER")
DB_PASSWORD = config("DB_PASSWORD")
DB_HOST = config("DB_HOST")
DB_PORT = config("DB_PORT")
DB_NAME = config("DB_NAME")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

SECRET_KEY = config("SECRET_KEY")
ALGORITHM = config("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES")

AWS_ACCESS_KEY_ID=config("AWS_ACCESS_KEY_ID") # 본인 소유의 키를 입력
AWS_SECRET_ACCESS_KEY=config("AWS_SECRET_ACCESS_KEY") # 본인 소유의 키를 입력
S3_BUCKET_NAME = config("S3_BUCKET_NAME")
AWS_REGION = "ap-northeast-2"

DISCORD_WEBHOOK_URL =config("DISCORD_WEBHOOK_URL")