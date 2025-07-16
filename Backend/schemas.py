from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any


# --- Schemas existentes ---
class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    class Config:
        from_attributes = True # Reemplazo de orm_mode para Pydantic V2

class ActividadBase(BaseModel):
    nombre: str
    temperatura_min: float
    temperatura_max: float
    humedad_max: int
    viento_max: float
    estado_dia: str
    descripcion: str

class ActividadCreate(ActividadBase):
    pass

class Actividad(ActividadBase):
    id: int
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr

from pydantic import BaseModel, Field

class Preferencias(BaseModel):
    user_id: int
    tipo: int = Field(..., alias="activity_type_id")
    modalidad: int = Field(..., alias="modality_id")

    class Config:
        from_attributes = True
        populate_by_name = True


class PreferenciasCreate(BaseModel):
    tipo: int = Field(..., alias="activity_type_id")
    modalidad: int = Field(..., alias="modality_id")

    class Config:
        populate_by_name = True
        from_attributes = True

class Favoritos(BaseModel):
    user_id: int
    actividad_id: int

    class Config:
        from_attributes = True
        populate_by_name = True

class FavoritosCreate(BaseModel):
    actividad_id: int

    class Config:
        populate_by_name = True
        from_attributes = True

class UserCreate(UserBase):
    password: str = Field(min_length=6)  # Mínimo de 6 caracteres para la contraseña
    is_business: bool = False

class User(UserBase):
    id: int
    is_active: bool
    is_business: bool
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    is_business: bool
    
# Esto es el modelo de las actividades de los usuarios, todo eso deberia pedirse en el frontend :)
class UserActivityBase(BaseModel):
    nombre: str  # Obligatorio
    descripcion: str  # Obligatorio
    temperatura_min: Optional[float] = None
    temperatura_max: Optional[float] = None
    humedad_max: Optional[float] = None
    viento_max: Optional[float] = None
    estado_dia: Optional[str] = None
    consejos: Optional[str] = None
    
class UserActivityCreate(UserActivityBase):
    pass

class UserActivity(UserActivityBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# Modelo unificado para recomendaciones que incluye tanto actividades del sistema como personalizadas
class ActividadRecomendada(BaseModel):
    id: int
    nombre: str  # Obligatorio
    descripcion: str  # Obligatorio
    temperatura_min: Optional[float] = None
    temperatura_max: Optional[float] = None
    humedad_max: Optional[float] = None
    viento_max: Optional[float] = None
    estado_dia: Optional[str] = None
    consejos: Optional[str] = None  # Solo las actividades personalizadas tienen consejos
    es_personalizada: bool = False  # Para distinguir el tipo
    
    class Config:
        from_attributes = True
        
# --- Nuevos Schemas para el pronóstico completo ---
class AirQuality(BaseModel):
    value: Any # Puede ser número o "N/A"

class CurrentWeather(BaseModel):
    dt: int
    temperatura: float
    sensacion_termica: float
    presion: int
    humedad: int
    visibilidad: int
    punto_rocio: Optional[float] = None
    viento_velocidad: float
    descripcion: str
    icono: str
    main: str
    calidad_aire: AirQuality

class HourlyForecastItem(BaseModel):
    dt: int
    temp: float
    icono: str
    pop: float # Probabilidad de precipitación

class DailyForecastItem(BaseModel):
    dt: int
    dayLabel: str
    temp_min: float
    temp_max: float
    sensacion_termica_dia: Optional[float] = None # Añadido
    icono: str
    descripcion: str
    main: str
    pop: float
    humedad: float
    presion: float
    viento_velocidad: float
    calidad_aire: Optional[AirQuality] = None # Calidad del aire para el día puede ser N/A

class FullWeatherReport(BaseModel):
    ciudad: str
    lat: float
    lon: float
    timezone_offset: int
    current: CurrentWeather
    hourly: List[HourlyForecastItem]
    daily: List[DailyForecastItem]

# --- Schemas para Actividades Laborales (dentro de un Proyecto) ---
class ActividadLaboralBase(BaseModel):
    nombre: str
    temperatura_min: float
    temperatura_max: float
    estado_dia: str
    descripcion: str

class ActividadLaboralCreate(ActividadLaboralBase):
    humedad_max: int
    viento_max: float

class ActividadLaboral(ActividadLaboralBase):
    id: int
    project_id: int
    humedad_max: Optional[int] = None
    viento_max: Optional[float] = None
    class Config:
        from_attributes = True

# --- Schemas para Proyectos de Empresa ---
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    user_id: int
    labor_activities: List[ActividadLaboral] = []
    class Config:
        from_attributes = True

