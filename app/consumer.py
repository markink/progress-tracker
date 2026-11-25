import asyncio
import json
from aiokafka import AIOKafkaConsumer
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Настройки БД
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модель для сохранения кликов
class ClickAnalytics(Base):
    __tablename__ = "click_analytics"
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Создаем таблицу при запуске
Base.metadata.create_all(bind=engine)

async def consume():
    # Подключаемся к Redpanda
    consumer = AIOKafkaConsumer(
        'click-events',
        bootstrap_servers='redpanda:9092',
        group_id="analytics-group", # Группа консьюмеров
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )
    await consumer.start()
    print("✅ Консьюмер запущен и слушает топик click-events...")
    
    try:
        async for msg in consumer:
            event = msg.value
            print(f" Получено событие: {event}")
            
            # Сохраняем в PostgreSQL
            db = SessionLocal()
            try:
                new_click = ClickAnalytics(
                    action=event.get("action"),
                    timestamp=datetime.fromisoformat(event.get("timestamp"))
                )
                db.add(new_click)
                db.commit()
                print(f" Сохранено в БД: {new_click.action}")
            except Exception as e:
                print(f" Ошибка сохранения в БД: {e}")
            finally:
                db.close()
                
    finally:
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(consume())
