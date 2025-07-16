from sqlalchemy.orm import Session
import models, schemas
from models import Actividad, User, UserPreference, ActivityType
from schemas import ActividadCreate, UserCreate, Preferencias
from passlib.context import CryptContext
from typing import List
import re


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def is_password_strong(password: str):
    """
    Valida la fortaleza de la contraseña.
    Requisitos:
    - Al menos 6 caracteres.
    - Al menos una letra mayúscula.
    - Al menos un número.
    - Al menos un carácter especial.
    """
    if len(password) < 6:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        return False
    return True

def get_items(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Item).offset(skip).limit(limit).all()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    if not is_password_strong(user.password):
        raise ValueError(  
            "La contraseña no cumple con los requisitos: debe tener al menos 6 caracteres, "
            "una mayúscula, un número y un carácter especial."
        )
    hashed_password = pwd_context.hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password, is_business=user.is_business)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_item(db: Session, item: schemas.ItemCreate):
    db_item = models.Item(name=item.name, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def create_actividad(db: Session, actividad: ActividadCreate):
    db_actividad = Actividad(**actividad.dict())
    db.add(db_actividad)
    db.commit()
    db.refresh(db_actividad)
    return db_actividad

def get_actividades(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Actividad).offset(skip).limit(limit).all()

def create_user_activity(db: Session, activity: schemas.UserActivityCreate, user_id: int):
    db_activity = models.UserActivity(**activity.dict(), user_id=user_id)
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

def get_user_activities(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.UserActivity).filter(models.UserActivity.user_id == user_id).offset(skip).limit(limit).all()

def get_user_activities_by_weather(db: Session, user_id: int, temperatura: float, estado: str, hum: int, viento: float):
    """Obtiene actividades personalizadas del usuario que coinciden con las condiciones climáticas."""
    return db.query(models.UserActivity).filter(
        models.UserActivity.user_id == user_id,
        models.UserActivity.temperatura_min <= temperatura,
        models.UserActivity.temperatura_max >= temperatura,
        models.UserActivity.estado_dia == estado,
        models.UserActivity.humedad_max >= hum,
        models.UserActivity.viento_max >= viento
    ).all()

def delete_user_activity(db: Session, activity_id: int, user_id: int) -> bool:
    """
    Elimina una actividad personalizada si pertenece al usuario.
    
    Retorna True si se eliminó, False si no se encontró o no pertenece al usuario.
    """
    activity = db.query(models.UserActivity).filter_by(id=activity_id, user_id=user_id).first()

    if not activity:
        return False  # No existe o no pertenece al usuario

    db.delete(activity)
    db.commit()
    return True



def get_preferencias(db: Session, usr: User):
    return db.query(models.UserPreference).filter(models.UserPreference.user_id == usr.id).all()
def create_preferencias(db: Session, pref_list: list[schemas.PreferenciasCreate], usr: User):
    if usr is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db.query(models.UserPreference).filter(models.UserPreference.user_id == usr.id).delete()
    db.commit()

    nuevas_prefs = []
    for pref in pref_list:
        nueva_pref = models.UserPreference(
            user_id=usr.id,
            activity_type_id=pref.tipo,
            modality_id=pref.modalidad
        )
        db.add(nueva_pref)
        nuevas_prefs.append(nueva_pref)

    db.commit()

    for pref in nuevas_prefs:
        db.refresh(pref)

    return nuevas_prefs



def get_favoritos(db: Session, usr: User):
    return db.query(models.Favorito).filter(models.Favorito.user_id == usr.id).all()
def create_favoritos(db: Session, fav_list: list[schemas.FavoritosCreate], usr: User):
    if usr is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db.query(models.Favorito).filter(models.Favorito.user_id == usr.id).delete()
    db.commit()

    nuevos_favs = []
    print("Fav list:", fav_list)
    print("User ID:", usr.id)
    for fav in fav_list:
        nuevo_fav = models.Favorito(
            user_id=usr.id,
            actividad_id=fav.actividad_id   #revisar bien
        )
        db.add(nuevo_fav)
        nuevos_favs.append(nuevo_fav)

    db.commit()

    for fav in nuevos_favs:
        db.refresh(fav)

    return nuevos_favs

# FILTRADO DE ACTIVIDADES con los datos de la API, instrucciones para DB (Esto le servirá a Juan).
def filtrar_actividades(db: Session, estado: str, temp: float, hum: int, viento: float):
    return (
        db.query(Actividad)
        .filter(
            Actividad.estado_dia == estado,
            Actividad.temperatura_min <= temp,
            Actividad.temperatura_max >= temp,
            Actividad.humedad_max >= hum,
            Actividad.viento_max >= viento
        )
        .all()
    )

#crud
def actividades_no_recomendadas(db: Session, estado: str, temp: float, hum: int, viento: float):
    return (
        db.query(Actividad)
        .filter(
            (Actividad.estado_dia != estado) |
            (Actividad.temperatura_min > temp) |
            (Actividad.temperatura_max < temp) |
            (Actividad.humedad_max < hum) |
            (Actividad.viento_max < viento)
        )
        .all()
    )





def get_actividades_por_clima_y_preferencias(
    db: Session,
    temperatura: float,
    estado: str,
    activity_type_ids: List[int],
    modality_ids: List[int],
    hum: int,
    viento: float
) -> List[models.Actividad]:
    return (
        db.query(models.Actividad)
        .join(models.ActivityPreference, models.Actividad.id == models.ActivityPreference.actividad_id)
        .filter(
            models.ActivityPreference.activity_type_id.in_(activity_type_ids),
            models.ActivityPreference.modality_id.in_(modality_ids),
            models.Actividad.temperatura_min <= temperatura,
            models.Actividad.temperatura_max >= temperatura,
            models.Actividad.estado_dia == estado,
            models.Actividad.humedad_max >= hum,
            models.Actividad.viento_max >= viento
        )
        .all()
    )


# --- CRUD para Proyectos de Empresa ---
def create_project(db: Session, project: schemas.ProjectCreate, user_id: int):
    db_project = models.Project(**project.dict(), user_id=user_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def get_projects_by_user(db: Session, user_id: int):
    return db.query(models.Project).filter(models.Project.user_id == user_id).all()

def get_project_by_id(db: Session, project_id: int, user_id: int):
    return db.query(models.Project).filter(models.Project.id == project_id, models.Project.user_id == user_id).first()

#--- Esto es nuevo, permite marcar un proyecto como favorito para mostrarlo en el inicio y en la pestaña de proyectos (con una estrella o algo) ---
def set_favorite_project(db: Session, project_id: int, user_id: int):
    db.query(models.Project).filter(
        models.Project.user_id == user_id,
        models.Project.is_favorite == True
    ).update({"is_favorite": False})

    project_to_favorite = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == user_id
    ).first()

    if project_to_favorite:
        project_to_favorite.is_favorite = True
        db.commit()
        db.refresh(project_to_favorite)
        return project_to_favorite
    return None

def delete_project(db: Session, project_id: int, user_id: int):
    """Elimina un proyecto y todas sus actividades laborales asociadas."""
    db_project = db.query(models.Project).filter(models.Project.id == project_id, models.Project.user_id == user_id).first()
    if db_project:
        db.delete(db_project)
        db.commit()
        return True
    return False

# --- CRUD para Favoritos de Usuario ---
def add_favorite_project(db: Session, project_id: int, user_id: int):
    """Agrega un proyecto a favoritos del usuario."""
    # Verificar que el proyecto existe y pertenece al usuario
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == user_id
    ).first()
    
    if not project:
        return None
    
    # Verificar si ya está en favoritos
    existing_favorite = db.query(models.FavoriteProject).filter(
        models.FavoriteProject.user_id == user_id,
        models.FavoriteProject.project_id == project_id
    ).first()
    
    if existing_favorite:
        return existing_favorite  # Ya está en favoritos
    
    # Crear nuevo favorito
    db_favorite = models.FavoriteProject(user_id=user_id, project_id=project_id)
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite

def get_user_favorites(db: Session, user_id: int):
    """Obtiene todos los proyectos favoritos de un usuario."""
    return db.query(models.Project).join(
        models.FavoriteProject,
        models.Project.id == models.FavoriteProject.project_id
    ).filter(
        models.FavoriteProject.user_id == user_id
    ).all()

def remove_favorite_project(db: Session, project_id: int, user_id: int):
    """Remueve un proyecto de favoritos del usuario."""
    favorite = db.query(models.FavoriteProject).filter(
        models.FavoriteProject.user_id == user_id,
        models.FavoriteProject.project_id == project_id
    ).first()
    
    if favorite:
        db.delete(favorite)
        db.commit()
        return True
    return False

def is_project_favorite(db: Session, project_id: int, user_id: int):
    """Verifica si un proyecto está en favoritos del usuario."""
    favorite = db.query(models.FavoriteProject).filter(
        models.FavoriteProject.user_id == user_id,
        models.FavoriteProject.project_id == project_id
    ).first()
    return favorite is not None

# --- CRUD para Actividades Favoritas del Usuario ---
def get_user_favorite_activities(db: Session, user_id: int):
    """Obtiene todas las actividades favoritas de un usuario."""
    return db.query(models.Actividad).join(
        models.Favorito,
        models.Actividad.id == models.Favorito.actividad_id
    ).filter(
        models.Favorito.user_id == user_id
    ).all()



#ESTO ES PARA EL JUAN
def get_user_favorite_activities_by_weather(db: Session, user_id: int, temperatura: float, estado: str, hum: int, viento: float):
    """Obtiene actividades favoritas del usuario que coinciden con las condiciones climáticas."""
    return db.query(models.Actividad).join(
        models.Favorito,
        models.Actividad.id == models.Favorito.actividad_id
    ).filter(
        models.Favorito.user_id == user_id,
        models.Actividad.temperatura_min <= temperatura,
        models.Actividad.temperatura_max >= temperatura,
        models.Actividad.estado_dia == estado,
        models.Actividad.humedad_max >= hum,
        models.Actividad.viento_max >= viento
    ).all()

def add_favorite_activity(db: Session, user_id: int, actividad_id: int):
    """Agrega una actividad a favoritos del usuario."""
    # Verificar que la actividad existe
    actividad = db.query(models.Actividad).filter(models.Actividad.id == actividad_id).first()
    if not actividad:
        return None
    
    # Verificar si ya está en favoritos
    existing_favorite = db.query(models.Favorito).filter(
        models.Favorito.user_id == user_id,
        models.Favorito.actividad_id == actividad_id
    ).first()
    
    if existing_favorite:
        return existing_favorite  # Ya está en favoritos
    
    # Crear nuevo favorito
    db_favorite = models.Favorito(user_id=user_id, actividad_id=actividad_id)
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite

def remove_favorite_activity(db: Session, user_id: int, actividad_id: int):
    """Remueve una actividad de favoritos del usuario."""
    favorite = db.query(models.Favorito).filter(
        models.Favorito.user_id == user_id,
        models.Favorito.actividad_id == actividad_id
    ).first()
    
    if favorite:
        db.delete(favorite)
        db.commit()
        return True
    return False

def is_activity_favorite(db: Session, user_id: int, actividad_id: int):
    """Verifica si una actividad está en favoritos del usuario."""
    favorite = db.query(models.Favorito).filter(
        models.Favorito.user_id == user_id,
        models.Favorito.actividad_id == actividad_id
    ).first()
    return favorite is not None

# --- CRUD para Actividades Laborales dentro de Proyectos ---
def create_project_activity(db: Session, activity: schemas.ActividadLaboralCreate, project_id: int):
    db_activity = models.ActividadLaboral(**activity.dict(), project_id=project_id)
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity




