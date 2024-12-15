from repository.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from setting.settings import Settings

engine = create_engine(Settings().DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    # drop_all은 데이터가 전부 날아가니 주의
    # Base.metadata.drop_all(bind=engine)
    # Base.metadata.create_all(bind=engine)
    print('⚡️ DB connection established.')

__all__ = ['SessionLocal']
