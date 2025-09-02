#!/usr/bin/env python3
"""
간단한 A.X 4.0 API 연결 테스트
"""

from openai import OpenAI

# A.X 4.0 API 설정
AX4_API_BASE_URL = "https://guest-api.sktax.chat/v1"
AX4_API_KEY = "sktax-XyeKFrq67ZjS4EpsDlrHHXV8it"
AX4_MODEL = "ax4"

def test_connection():
    """API 연결 테스트"""
    print("🔗 A.X 4.0 API 연결 테스트")
    
    try:
        client = OpenAI(
            base_url=AX4_API_BASE_URL,
            api_key=AX4_API_KEY
        )
        
        response = client.chat.completions.create(
            model=AX4_MODEL,
            messages=[
                {"role": "user", "content": "안녕하세요"}
            ],
            max_tokens=50
        )
        
        answer = response.choices[0].message.content
        print(f"✅ API 연결 성공!")
        print(f"응답: {answer}")
        return True
        
    except Exception as e:
        print(f"❌ API 연결 실패: {e}")
        return False

if __name__ == "__main__":
    test_connection()