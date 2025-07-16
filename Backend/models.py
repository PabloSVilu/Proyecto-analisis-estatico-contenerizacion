from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)

class Actividad(Base):
    __tablename__ = "actividades"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    temperatura_min = Column(Float)
    temperatura_max = Column(Float)
    humedad_max = Column(Integer)
    viento_max = Column(Float)
    estado_dia = Column(String)  # Por ejemplo: "rain", "snow", "cloud"
    descripcion = Column(String)
    favorited_by = relationship("Favorito", back_populates="actividad")
    
    
# Tabla para Proyectos de Empresas ''''''''''''''' Esto es nuevo, es la "carpeta" Proyecto
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    is_favorite = Column(Boolean, default=False, nullable=False)

    owner = relationship("User", back_populates="projects")
    labor_activities = relationship("ActividadLaboral", back_populates="project", cascade="all, delete-orphan")

#Tabla para actividades laborales
class ActividadLaboral(Base):
    __tablename__ = "actividades_laborales"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    temperatura_min = Column(Float)
    temperatura_max = Column(Float)
    humedad_max = Column(Integer)
    viento_max = Column(Float)
    estado_dia = Column(String)  # Por ejemplo: "rain", "snow", "cloud"
    descripcion = Column(String)
    
    project_id = Column(Integer, ForeignKey("projects.id"))
    project = relationship("Project", back_populates="labor_activities") #Relación con proyecto


# La clase User representa a los usuarios en la base de datos
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True) 
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_business = Column(Boolean, default=False)

    preferences = relationship("UserPreference", back_populates="user")
    #Esta linea rompe el codigo
    user_activities = relationship("UserActivity", back_populates="owner") #Esto permite hacer la relación entre los usuarios y sus actividades :)
    #Esto lo arregla, no se si es correcto
    favoritos = relationship("Favorito", back_populates="user")
    
    projects = relationship("Project", back_populates="owner")



# Esta es la tabla para las actividades de los usuarios, nuevo. :)
class UserActivity(Base):
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True, nullable=False)  # Obligatorio
    descripcion = Column(String, nullable=False)  # Obligatorio
    temperatura_min = Column(Float, nullable=True)
    temperatura_max = Column(Float, nullable=True)
    humedad_max = Column(Float, nullable=True)
    viento_max = Column(Float, nullable=True)
    estado_dia = Column(String, nullable=True)
    consejos = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="user_activities")
    #favoritos = relationship("Favorito", back_populates="user")#relacion con tabla de favorito 


class ActivityType(Base):
    __tablename__ = "activity_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)

class Modality(Base):
    __tablename__ = "modalities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)


class UserPreference(Base):
    __tablename__ = "user_preferences"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    activity_type_id = Column(Integer, ForeignKey("activity_types.id"), primary_key=True)
    modality_id = Column(Integer, ForeignKey("modalities.id"), primary_key=True)

    user = relationship("User", back_populates="preferences")
    activity_type = relationship("ActivityType")
    modality = relationship("Modality")

#Tablita para preferencias actividades
class ActivityPreference(Base):
    __tablename__ = "activity_preferences"

    actividad_id = Column(Integer, ForeignKey("actividades.id"), primary_key=True)
    activity_type_id = Column(Integer, ForeignKey("activity_types.id"), primary_key=True)
    modality_id = Column(Integer, ForeignKey("modalities.id"), primary_key=True)

    actividad = relationship("Actividad", backref="preferences")
    activity_type = relationship("ActivityType")
    modality = relationship("Modality")
    
#Tabla de favoritos
class Favorito(Base):
    __tablename__ = "favoritos"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    actividad_id = Column(Integer, ForeignKey("actividades.id"), primary_key=True)

    user = relationship("User", back_populates="favoritos")
    actividad = relationship("Actividad", back_populates="favorited_by")

