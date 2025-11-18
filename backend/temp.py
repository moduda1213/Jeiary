import asyncio
from app.db.session import get_db
from app.schemas.user import UserCreate
from app.repositories.user_repo import UserRepository

#  임시 사용자 생성 스크립트 실행
async def main():
    print("Attempting to create a test user...")
    db_generator = get_db()
    db = await anext(db_generator)
    try:
        user_repo = UserRepository(db)

        user_data = UserCreate(email="test@example.com", password="password123@")

        # Check if user already exists
        existing_user = await user_repo.get_by_email(email=user_data.email)
        if existing_user:
            print(f"User with email '{user_data.email}' already exists.")
            return

        # Create user using the repository's create method
        new_user = await user_repo.create(user_data)
        await db.commit() # Commit the transaction
        print(f"User created successfully: {new_user.email}")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Properly close the session by exhausting the generator
        try:
            await anext(db_generator)
        except StopAsyncIteration:
            pass

if __name__ == "__main__":
    asyncio.run(main())
    
    
# docker-compose exec backend python create_user_temp.py
# docker 내부 컨테이너 backend에서 실행