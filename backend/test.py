import asyncio
from tiktoken import get_encoding, encoding_for_model
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.config import settings

async def test_connection():
    try:
        engine = create_async_engine(settings.DATABASE_URL, echo=True)
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            value = result.scalar()
            print(f"시도한 URL: {settings.DATABASE_URL}")
            print(f"✅ 데이터베이스 연결 성공! 결과: {value}")
        await engine.dispose()
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        print(f"시도한 URL: {settings.DATABASE_URL}")

def get_text_token():
    text = """<여기에 위 코드 그대로 붙여넣기>"""
    enc = get_encoding("cl100k_base")
    len(enc.encode(text))
    
    # 사용할 모델 지정 (예: gpt-3.5-turbo)
    model = "gpt-3.5-turbo"

    # 텍스트 예제
    text = "안녕하세요, 저는 ChatGPT입니다."

    # 모델에 맞는 인코딩 가져오기
    encoding = encoding_for_model(model)

    # 텍스트를 토큰화
    tokens = encoding.encode(text)
    print(f"Tokens: {tokens}")

    # 토큰 수 계산
    num_tokens = len(tokens)
    print(f"Number of tokens: {num_tokens}")

    # 토큰을 다시 텍스트로 디코딩
    decoded_text = encoding.decode(tokens)
    print(f"Decoded text: {decoded_text}")

if __name__ == "__main__":
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text
    
    asyncio.run(test_connection())