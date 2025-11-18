from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    모든 ORM 모델이 상속할 기본 클래스
    SQLAlchemy 2.0의 권장 방식, 타입 힌팅을 완벽하게 지원
    """
    pass

# from sqlalchemy.orm import declarative_base

# # 모든 ORM 모델에게 상속할 기본 클래스
# # 상속받는 모든 클래스는 SQLAlchemy에 의해 테이블로 관리
# Base = declarative_base()