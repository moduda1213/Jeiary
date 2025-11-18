import asyncio
from logging.config import fileConfig

# from sqlalchemy import engine_from_config # 기존
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool

from alembic import context

# import os
# import sys

# # 현재 env.py 파일의 경로를 기준으로 프로젝트 루트(backend)를 sys.path에 추가
# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # 절대 경로 사용
# if project_root not in sys.path:
#     sys.path.insert(0, project_root) # insert(0, ...) 사용으로 우선순위 보장

from app.db.base import Base
from app.config import settings

# __init__.py를 통해 모든 모델을 Base.metadata에 등록
import app.models

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

######### 비동기 전환 ##################################
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    
    오프라인 모드에서는 데이터베이스 연결 없이 SQL 스크립트만 생성합니다.
    """
    url = settings.DATABASE_URL
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # 컬럼 타입 변경 감지
        compare_server_default=True,  # server_default 변경 감지
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    """
    Alembic 컨텍스트를 설정하고 마이그레이션을 실행하는 동기 헬퍼 함수
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    
    온라인 모드에서는 실제 데이터베이스에 연결하여 마이그레이션을 실행합니다.
    비동기 방식으로 구현되어 asyncpg 드라이버와 호환됩니다.
    """
    # 비동기 엔진 생성
    connectable = create_async_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,  # 마이그레이션 중에는 풀 사용 안 함
        echo=False,  # SQL 로깅 (필요시 True)
    )

    print(settings.DATABASE_URL)
    
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    # 엔진 정리
    await connectable.dispose()
    
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
    
####################################################################
# 기존 동기 방식
# def run_migrations_offline() -> None:
#     """Run migrations in 'offline' mode.

#     This configures the context with just a URL
#     and not an Engine, though an Engine is acceptable
#     here as well.  By skipping the Engine creation
#     we don't even need a DBAPI to be available.

#     Calls to context.execute() here emit the given string to the
#     script output.

#     """
#     url = config.get_main_option("sqlalchemy.url")
#     context.configure(
#         url=url,
#         target_metadata=target_metadata,
#         literal_binds=True,
#         dialect_opts={"paramstyle": "named"},
#     )

#     with context.begin_transaction():
#         context.run_migrations()


# def run_migrations_online() -> None:
#     """Run migrations in 'online' mode.

#     In this scenario we need to create an Engine
#     and associate a connection with the context.

#     """
#     connectable = engine_from_config(
#         config.get_section(config.config_ini_section, {}),
#         prefix="sqlalchemy.",
#         poolclass=pool.NullPool,
#     )

#     with connectable.connect() as connection:
#         context.configure(
#             connection=connection, target_metadata=target_metadata
#         )

#         with context.begin_transaction():
#             context.run_migrations()

# if context.is_offline_mode():
#     run_migrations_offline()
# else:
#     run_migrations_online()
######################################################################################################
