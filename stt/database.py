import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Завантажуємо змінні з .env файлів
# (Переконайтеся, що шлях правильний відносно розташування цього файлу)
load_dotenv("config.env")
load_dotenv("secret.env")

# Отримуємо налаштування з оточення (з дефолтними значеннями для Docker)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "semantic_analysis_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "Test1234")

# Формуємо рядок підключення для PostgreSQL
# Формат: postgresql://user:password@host:port/dbname
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
SQLALCHEMY_DATABASE_URL = os.getenv("DB_CONNECTION_STRING", SQLALCHEMY_DATABASE_URL)

# Створюємо Engine. 
# pool_size та max_overflow допомагають контролювати кількість одночасних з'єднань.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=5,
    max_overflow=10
)

# SessionLocal — це клас, кожна інстанція якого буде окремою сесією з БД
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовий клас, від якого будуть наслідуватися всі моделі в models.py
Base = declarative_base()