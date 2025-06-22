# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager

DATABASE_URL = "sqlite:///./test.db"

Base = declarative_base()

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db():
    """
    Контекстный менеджер для работы с сессиями БД.
    Гарантирует правильное закрытие сессии даже при возникновении ошибок.
    
    Пример использования:
    with get_db() as db:
        result = db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Создает все таблицы в базе данных на основе зарегистрированных моделей"""
    # Импорт моделей необходим для их регистрации в декларативной базе Base
    import models  # Импортируем модели для регистрации
    Base.metadata.create_all(bind=engine)