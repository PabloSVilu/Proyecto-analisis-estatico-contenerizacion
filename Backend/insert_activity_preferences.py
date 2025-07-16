from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Actividad, ActivityType, Modality, ActivityPreference

# Conexión
DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Asegurar creación de tablas
Base.metadata.create_all(bind=engine)

# Mapear nombres a IDs 
tipos = {t.name.lower().strip(): t.id for t in db.query(ActivityType).all()}
modalidades = {m.name.lower().strip(): m.id for m in db.query(Modality).all()}

# Lista preferencias: (nombre actividad, tipo, modalidad)
preferencias = [
    # Clear
    ("Caminata en el parque", "Deportiva", "Individual y Grupal"),
    ("Ciclismo de montaña", "Deportiva", "Individual"),
    ("Nadar en la piscina", "Deportiva", "Individual y Grupal"),
    ("Día de picnic", "Recreativa", "Grupal"),
    ("Senderismo", "Deportiva", "Individual y Grupal"),
    ("Correr en el parque", "Deportiva", "Individual"),
    ("Fotografía en el campo", "Recreativa", "Individual"),
    ("Golf", "Recreativa", "Grupal"),
    ("Paseo en bote", "Recreativa", "Grupal"),
    ("Escalada en roca", "Deportiva", "Individual"),

    # Rain
    ("Leer un libro bajo techo", "Educativo", "Individual"),
    ("Ver una película en casa", "Entretenimiento", "Grupal"),
    ("Cocinar recetas nuevas", "Cocina", "Grupal"),
    ("Hacer yoga en casa", "Deportiva", "Individual"),
    ("Pintura o manualidades", "Recreativa", "Individual"),
    ("Escuchar música y relajarse", "Entretenimiento", "Individual"),
    ("Jugar a juegos de mesa", "Entretenimiento", "Grupal"),
    ("Meditar", "Recreativa", "Individual"),
    ("Planificar tus próximas vacaciones", "Educativo", "Individual"),
    ("Hacer tareas de limpieza en casa", "Casa", "Individual"),

    # Snow
    ("Esquí o snowboard", "Deportiva", "Grupal"),
    ("Construir un muñeco de nieve", "Recreativa", "Grupal"),
    ("Patinaje sobre hielo", "Deportiva", "Grupal"),
    ("Senderismo en la nieve", "Deportiva", "Individual"),
    ("Tomar chocolate caliente", "Casa", "Individual"),
    ("Leer junto a la chimenea", "Educativo", "Individual"),
    ("Fotografía de paisajes nevados", "Recreativa", "Individual"),
    ("Sledging (andar en trineo)", "Recreativa", "Grupal"),
    ("Hacer un ángel en la nieve", "Recreativa", "Grupal"),
    ("Ver películas navideñas", "Entretenimiento", "Grupal"),

    # Mist
    ("Caminata en el bosque", "Recreativa", "Individual"),
    ("Paseo en barco en el río", "Recreativa", "Grupal"),
    ("Visita a un mirador", "Recreativa", "Individual"),
    ("Sesión de fotografía en la niebla", "Recreativa", "Individual"),
    ("Ciclismo en la niebla", "Deportiva", "Individual"),
    ("Trekking en la montaña", "Deportiva", "Individual"),
    ("Observación de aves", "Recreativa", "Individual"),
    ("Escalada en roca", "Deportiva", "Individual"),
    ("Paseo por el jardín botánico", "Recreativa", "Individual y Grupal"),
    ("Café en la terraza con niebla", "Recreativa", "Individual"),

    # Clouds
    ("Café en una terraza", "Recreativa", "Individual"),
    ("Visitar un museo", "Educativo", "Grupal"),
    ("Leer en un café", "Educativo", "Individual"),
    ("Películas en casa", "Entretenimiento", "Grupal"),
    ("Día de spa", "Recreativa", "Individual"),
    ("Cultura en un centro de arte", "Educativo", "Grupal"),
    ("Tarde de juegos de mesa", "Entretenimiento", "Grupal"),
    ("Cocina en casa", "Cocina", "Individual"),
    ("Té en una librería", "Recreativa", "Individual"),
    ("Visitar un centro comercial", "Entretenimiento", "Grupal"),

   
    ("Observa las aves", "Recreativa", "Individual"),
    ("Observa la lluvia caer", "Recreativa", "Individual"),
    ("Paseo por la ciudad", "Recreativa", "Individual y Grupal"),
    ("Cocina en la casa", "Cocina", "Individual"),
    ("Comer galletas y bebida caliente", "Casa", "Individual"),
]

# Insertar preferencias (manejo de duplicados y actividades duplicadas)
for nombre_actividad, tipo_nombre, modalidad_nombre in preferencias:
    tipo_id = tipos.get(tipo_nombre.lower().strip())
    modalidad_id = modalidades.get(modalidad_nombre.lower().strip())

    if tipo_id is None:
        print(f"Tipo no encontrado: {tipo_nombre}")
        continue
    if modalidad_id is None:
        print(f" Modalidad no encontrada: {modalidad_nombre}")
        continue

    actividades = db.query(Actividad).filter_by(nombre=nombre_actividad).all()

    if not actividades:
        print(f"Actividad no encontrada: {nombre_actividad}")
        continue

    for actividad in actividades:
        existente = db.query(ActivityPreference).filter_by(
            actividad_id=actividad.id,
            activity_type_id=tipo_id,
            modality_id=modalidad_id
        ).first()

        if existente:
            print(f"Ya existe para ID {actividad.id}: {nombre_actividad} ({tipo_nombre}, {modalidad_nombre})")
        else:
            nueva = ActivityPreference(
                actividad_id=actividad.id,
                activity_type_id=tipo_id,
                modality_id=modalidad_id
            )
            db.add(nueva)
            print(f"Insertada para ID {actividad.id}: {nombre_actividad} ({tipo_nombre}, {modalidad_nombre})")

# Guardar cambios
db.commit()
db.close()
print("\nTodas las preferencias fueron procesadas correctamente.")
