from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, ActivityType, Modality

# Establece la conexión con la base de datos
DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Crea una sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Crea las tablas si no existen
Base.metadata.create_all(bind=engine)


activity_types = [
    ActivityType(name="Deportiva"),
    ActivityType(name="Casa"),
    ActivityType(name="Entretenimiento"),
    ActivityType(name="Educativo"),
    ActivityType(name="Recreativa"),
    ActivityType(name = "Cocina")
]

modality = [
    Modality(name="Individual"),
    Modality(name = "Grupal"),
    Modality(name= "Individual y Grupal"),
    Modality(name = "Virtual")


]

for tipo in activity_types:
    db.add(tipo)

for tipo in modality:
    db.add(tipo)


# Confirma la transacción
db.commit()

# Cierra la sesión
db.close()

print("Actividades insertadas exitosamente.")
