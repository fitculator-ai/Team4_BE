# Fitculator 4팀 백엔드 API 명세서입니다.

### 회원가입 요청 


# POST /api/signup
# 설명: 새로운 사용자를 등록합니다.(소셜 로그인)

        {
            "user_name" : "string",
            "user_nickname" : "string",
            "user_email" : "string",
            "user_phone_num" : "string",
            "user_age" : int,
            "creat_at" : date,
            "photo_url" : []
        }

# 회원가입 응답

{
    “message” : “회원가입 성공”,
    “user”: { 
    “id” : int,
    “name” : “string”,
    “nickname” : “string”,
    “age” : int,
    “gender” : “string”,
    “email” : “string”,
    “phone” : “string”,
    “create_at” : date,
    “photo_url” : []
    }
}