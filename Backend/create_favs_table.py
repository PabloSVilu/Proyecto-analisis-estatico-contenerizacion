from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Base, Actividad

# Establece la conexión con la base de datos
DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Crea una sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE favorite_activities (
            user_id INTEGER NOT NULL,
            activity_id INTEGER NOT NULL,
            PRIMARY KEY (user_id, activity_id)
        );
    """))
    conn.commit()