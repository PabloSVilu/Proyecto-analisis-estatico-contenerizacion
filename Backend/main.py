# main.py

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, crud 
from database import SessionLocal, engine 
import requests
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta, date, timezone 
from passlib.context import CryptContext
import math 
from urllib.parse import quote as encodeURIComponent
import locale as pylocale # Para formatear nombres de días
from typing import Optional, List, Dict, Any
# Cargar variables de entorno (API_KEY, SECRET_KEY, etc.)
load_dotenv()
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise EnvironmentError("FATAL: No se encontró API_KEY en el archivo .env. La aplicación no puede iniciarse.")

SECRET_KEY = os.getenv("SECRET_KEY", "una_clave_secreta_por_defecto_muy_larga_y_dificil_de_adivinar_cambiame_en_produccion")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 120))


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Crear las tablas en la base de datos si no existen
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Clima y Actividades",
    description="Provee datos del clima y sugerencias de actividades basadas en el clima.",
    version="1.0.1" # Incrementada la versión
)

# Configuración CORS para permitir solicitudes desde el frontend
origins = [
    "http://localhost:5173", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes
    allow_credentials=False,  # Obligatorio si se usa "*"
    allow_methods=["*"],      # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],      # Permite todos los encabezados
)


# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Funciones auxiliares para el procesamiento de datos del clima ---
def mps_to_kmh(mps: Optional[float]) -> Optional[float]:
    if mps is None:
        return None
    return round(mps * 3.6, 1)

def calculate_dew_point(temp_c: Optional[float], humidity_percent: Optional[float]) -> Optional[float]:
    if temp_c is None or humidity_percent is None or humidity_percent <= 0: # Evitar log(0) o negativo
        return None
    try:
        # Fórmula aproximada de Magnus-Tetens
        a = 17.27
        b = 237.7
        alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity_percent / 100.0)
        dew_point = (b * alpha) / (a - alpha)
        return round(dew_point, 1)
    except (ValueError, TypeError, ZeroDivisionError) as e:
        print(f"Error calculando punto de rocío: temp={temp_c}, hum={humidity_percent}, error={e}")
        return None

def get_air_quality_data(lat: float, lon: float, api_key: str) -> Dict[str, Any]:
    aq_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
    try:
        response = requests.get(aq_url)
        response.raise_for_status()
        aq_data = response.json()
        if aq_data and aq_data.get("list") and len(aq_data["list"]) > 0:
            components = aq_data["list"][0]["components"]
            # Usamos pm2_5 como valor principal si está, si no, un valor por defecto.
            return {"value": round(components.get("pm2_5", 0), 1) if components else "N/A"}
    except requests.exceptions.RequestException as e:
        print(f"Error obteniendo calidad del aire: {e}")
    except (KeyError, IndexError, TypeError) as e: # TypeError por si components es None
        print(f"Error parseando datos de calidad del aire: {e}")
    return {"value": "N/A"}


# --- Endpoints ---

@app.post("/items/", response_model=schemas.Item, tags=["Items (Ejemplo)"])
def create_item_endpoint(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    return crud.create_item(db=db, item=item)

@app.get("/items/", response_model=list[schemas.Item], tags=["Items (Ejemplo)"])
def read_items_endpoint(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_items(db=db, skip=skip, limit=limit)

@app.post("/actividades/", response_model=schemas.Actividad, tags=["Actividades"])
def create_actividad_endpoint(actividad: schemas.ActividadCreate, db: Session = Depends(get_db)):
    return crud.create_actividad(db=db, actividad=actividad)

@app.get("/actividades/", response_model=list[schemas.Actividad], tags=["Actividades"])
def read_actividades_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_actividades(db=db, skip=skip, limit=limit)

@app.get("/actividades/filtrar", response_model=list[schemas.Actividad], tags=["Actividades"])
def filtrar_actividades_endpoint(
    estado: str,
    temp: float,
    hum: int,
    viento: float,
    db: Session = Depends(get_db)
):
    estado = estado.capitalize()
    return crud.filtrar_actividades(db=db, estado=estado, temp=temp, hum=hum, viento=viento)



@app.get("/preferencias/", response_model=List[schemas.Preferencias], tags=["Preferencias"])
def read_preferencias(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception

    return crud.get_preferencias(db=db, usr=user)


from fastapi import APIRouter, Depends, HTTPException
from typing import List

@app.post("/preferencias/", response_model=List[schemas.Preferencias], tags=["Preferencias"])
def crear_preferencias(
    pref_list: List[schemas.PreferenciasCreate],  # <--- Aquí el cambio
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    # Validar token y usuario
    credentials_exception = HTTPException(
        status_code=401,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception

    nuevas_prefs = crud.create_preferencias(db=db, pref_list=pref_list, usr=user)

    return nuevas_prefs


@app.get("/favoritos/", response_model=List[schemas.Favoritos], tags=["Favoritos"])
def read_favoritos(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception

    return crud.get_favoritos(db=db, usr=user)


@app.post("/favoritos/", tags=["Favoritos"])
def crear_favoritos(
    fav_list: List[schemas.FavoritosCreate],
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    # Validar token y usuario (tu código de autenticación se mantiene igual)
    credentials_exception = HTTPException(
        status_code=401,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    
    # La lógica de guardado sigue siendo la misma
    crud.create_favoritos(db=db, fav_list=fav_list, usr=user)

    # Devolvemos una respuesta JSON simple y explícita en lugar de la lista
    return {"message": "Favoritos guardados con éxito"}



@app.get("/clima/por-coordenadas", response_model=schemas.FullWeatherReport, tags=["Clima"])
def obtener_pronostico_por_coordenadas(lat: float, lon: float):
    # Endpoint de OpenWeatherMap para pronóstico por coordenadas
    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=es"
    
    try:
        response = requests.get(forecast_url)
        response.raise_for_status() # Lanza HTTPError para códigos 4xx/5xx
        datos_forecast = response.json()
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Coordenadas {lat},{lon} no encontradas por el proveedor de clima.")
        elif response.status_code == 401: # Unauthorized
            raise HTTPException(status_code=500, detail="Error de configuración del servidor: API Key de clima inválida.")
        else:
            raise HTTPException(status_code=response.status_code, detail=f"Error del proveedor de clima: {http_err}")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"No se pudo contactar al proveedor de clima: {e}")
    
    if not datos_forecast or "list" not in datos_forecast or not datos_forecast["list"]:
        raise HTTPException(status_code=404, detail=f"No se encontraron datos de pronóstico para las coordenadas {lat},{lon}.")

    # Información de la ciudad y zona horaria
    city_info = datos_forecast["city"]
    city_timezone_offset_seconds = city_info["timezone"]

    # Obtener calidad del aire
    air_quality = get_air_quality_data(lat, lon, API_KEY)

    # Procesar datos "actuales"
    current_raw = datos_forecast["list"][0]
    current_processed = schemas.CurrentWeather(
        dt=current_raw["dt"],
        temperatura=round(current_raw["main"]["temp"]),
        sensacion_termica=round(current_raw["main"]["feels_like"]),
        presion=current_raw["main"]["pressure"],
        humedad=current_raw["main"]["humidity"],
        visibilidad=current_raw.get("visibility", 10000),
        punto_rocio=calculate_dew_point(current_raw["main"]["temp"], current_raw["main"]["humidity"]),
        viento_velocidad=mps_to_kmh(current_raw["wind"]["speed"]),
        descripcion=current_raw["weather"][0]["description"],
        icono=current_raw["weather"][0]["icon"],
        main=current_raw["weather"][0]["main"],
        calidad_aire=air_quality
    )

    # Procesar datos horarios
    hourly_processed = [
        schemas.HourlyForecastItem(
            dt=item["dt"],
            temp=round(item["main"]["temp"]),
            icono=item["weather"][0]["icon"],
            pop=round(item.get("pop", 0) * 100)
        ) for item in datos_forecast["list"]
    ]

    # Agrupar datos por día local (mismo código que antes)
    daily_aggregation = {}
    for item in datos_forecast["list"]:
        item_datetime_utc = datetime.fromtimestamp(item["dt"], tz=timezone.utc)
        item_datetime_local = item_datetime_utc + timedelta(seconds=city_timezone_offset_seconds)
        item_date_local_str = item_datetime_local.date().isoformat()

        if item_date_local_str not in daily_aggregation:
            start_of_local_day_naive = datetime.combine(item_datetime_local.date(), datetime.min.time())
            start_of_local_day_utc = start_of_local_day_naive - timedelta(seconds=city_timezone_offset_seconds)
            daily_aggregation[item_date_local_str] = {
                "dt_utc_start_day": int(start_of_local_day_utc.timestamp()),
                "temps_min": [], "temps_max": [], "feels_like_temps": [],
                "icons_weighted": {}, "descriptions_weighted": {}, "mains_weighted": {},
                "pops": [], "humidities": [], "pressures": [], "wind_speeds": []
            }
        
        agg = daily_aggregation[item_date_local_str]
        agg["temps_min"].append(item["main"]["temp_min"])
        agg["temps_max"].append(item["main"]["temp_max"])
        agg["feels_like_temps"].append(item["main"]["feels_like"])
        
        icon = item["weather"][0]["icon"]
        agg["icons_weighted"][icon] = agg["icons_weighted"].get(icon, 0) + 1
        desc = item["weather"][0]["description"]
        agg["descriptions_weighted"][desc] = agg["descriptions_weighted"].get(desc, 0) + 1
        main_w = item["weather"][0]["main"]
        agg["mains_weighted"][main_w] = agg["mains_weighted"].get(main_w, 0) + 1

        agg["pops"].append(item.get("pop", 0) * 100)
        agg["humidities"].append(item["main"]["humidity"])
        agg["pressures"].append(item["main"]["pressure"])
        agg["wind_speeds"].append(mps_to_kmh(item["wind"]["speed"]))

    # Construir pronóstico diario (mismo código que antes)
    daily_final_list = []
    now_utc = datetime.now(timezone.utc)
    city_today_local = (now_utc + timedelta(seconds=city_timezone_offset_seconds)).date()

    original_locale = pylocale.getlocale(pylocale.LC_TIME)
    try:
        pylocale.setlocale(pylocale.LC_TIME, "es_ES.UTF-8")
    except pylocale.Error:
        try:
            pylocale.setlocale(pylocale.LC_TIME, "Spanish_Spain.1252")
        except pylocale.Error:
            pass

    for day_iso_str, data in sorted(daily_aggregation.items())[:7]:
        day_date_local = date.fromisoformat(day_iso_str)
        
        day_label = ""
        if day_date_local == city_today_local:
            day_label = "Today"
        elif (day_date_local - city_today_local).days == 1:
            day_label = "Tomorrow"
        else:
            day_label = day_date_local.strftime("%A").capitalize().replace(".","")

        daily_final_list.append(schemas.DailyForecastItem(
            dt=data["dt_utc_start_day"],
            dayLabel=day_label,
            temp_min=round(min(data["temps_min"])),
            temp_max=round(max(data["temps_max"])),
            sensacion_termica_dia=round(sum(data["feels_like_temps"]) / len(data["feels_like_temps"])),
            icono=max(data["icons_weighted"], key=data["icons_weighted"].get),
            descripcion=max(data["descriptions_weighted"], key=data["descriptions_weighted"].get),
            main=max(data["mains_weighted"], key=data["mains_weighted"].get),
            pop=round(max(data["pops"])),
            humedad=round(sum(data["humidities"]) / len(data["humidities"])),
            presion=round(sum(data["pressures"]) / len(data["pressures"])),
            viento_velocidad=round(sum(data["wind_speeds"]) / len(data["wind_speeds"]), 1),
            calidad_aire=None
        ))
    
    pylocale.setlocale(pylocale.LC_TIME, original_locale)

    return schemas.FullWeatherReport(
        ciudad=city_info["name"],  # Nombre de la ciudad devuelto por OpenWeatherMap
        lat=lat,  # Usamos las coordenadas que recibimos como parámetro
        lon=lon,
        timezone_offset=city_timezone_offset_seconds,
        current=current_processed,
        hourly=hourly_processed,
        daily=daily_final_list
    )

# --- Autenticación ---


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: Optional[str] = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    user = crud.get_user_by_email(db, email)
    if not user or not pwd_context.verify(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@app.post("/register/", response_model=schemas.User, tags=["Autenticación"])
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    print(user)  # Agrega esto para inspeccionar los datos recibidos
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")
    try:
        return crud.create_user(db=db, user=user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/token", response_model=schemas.Token, tags=["Autenticación"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password) 
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Correo electrónico o contraseña incorrectos", 
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires 
    )
    return {"access_token": access_token, "token_type": "bearer", "is_business": user.is_business}


@app.get("/users/me", response_model=schemas.User, tags=["Usuarios"])
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# --- Endpoints para Actividades Favoritas ---
@app.get("/favorites/activities/", response_model=List[schemas.Actividad], tags=["Favoritos"])
def get_user_favorite_activities_endpoint(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene todas las actividades favoritas del usuario autenticado."""
    return crud.get_user_favorite_activities(db=db, user_id=current_user.id)

@app.post("/favorites/activities/{actividad_id}", tags=["Favoritos"])
def add_favorite_activity_endpoint(
    actividad_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    
    
    """Agrega una actividad a favoritos del usuario."""
    favorite = crud.add_favorite_activity(db=db, user_id=current_user.id, actividad_id=actividad_id)
    if favorite is None:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    return {"message": "Actividad agregada a favoritos exitosamente"}

@app.delete("/favorites/activities/{actividad_id}", tags=["Favoritos"])
def remove_favorite_activity_endpoint(
    actividad_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remueve una actividad de favoritos del usuario."""
    success = crud.remove_favorite_activity(db=db, user_id=current_user.id, actividad_id=actividad_id)
    if not success:
        raise HTTPException(status_code=404, detail="Actividad no encontrada en favoritos")
    return {"message": "Actividad removida de favoritos exitosamente"}

@app.get("/favorites/activities/{actividad_id}/check", tags=["Favoritos"])
def check_favorite_activity_endpoint(
    actividad_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verifica si una actividad está en favoritos del usuario."""
    is_favorite = crud.is_activity_favorite(db=db, user_id=current_user.id, actividad_id=actividad_id)
    return {"is_favorite": is_favorite}

@app.get("/favorites/activities/filtrar", response_model=List[schemas.Actividad], tags=["Favoritos"])
def get_filtered_favorite_activities(
    temperatura: float,
    estado: str,
    hum: int,
    viento: float,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Devuelve las actividades favoritas del usuario que coinciden con el clima actual."""
    return crud.get_user_favorite_activities_by_weather(
        db=db,
        user_id=current_user.id,
        temperatura=temperatura,
        estado=estado.capitalize(),
        hum=hum,
        viento=viento
    )


# --- Endpoints para Actividades Personalizadas, esto es lo nuevo que deben usar en el frontend!! ---
@app.post("/user-activities/", response_model=schemas.UserActivity, tags=["Actividades Personalizadas"])
def create_user_activity_endpoint(
    activity: schemas.UserActivityCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Crea una nueva actividad personalizada para el usuario autenticado.
    """
    return crud.create_user_activity(db=db, activity=activity, user_id=current_user.id)

@app.get("/user-activities/", response_model=List[schemas.UserActivity], tags=["Actividades Personalizadas"])
def read_user_activities_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Obtiene la lista de actividades personalizadas creadas por el usuario autenticado.
    """
    activities = crud.get_user_activities(db=db, user_id=current_user.id, skip=skip, limit=limit)
    return activities

@app.delete("/user-activities/{activity_id}", tags=["Actividades Personalizadas"])
def delete_user_activity_endpoint(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Elimina una actividad personalizada del usuario autenticado.
    """
    success = crud.delete_user_activity(db=db, activity_id=activity_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Actividad no encontrada o no pertenece al usuario")
    return {"message": "Actividad eliminada exitosamente"}

#---------- HASTA AQUI ------------


#incluir actividades personalizadas (user-activities) en las recomendaciones
@app.get("/actividades/recomendadas", response_model=List[schemas.ActividadRecomendada], tags=["Actividades"])
def get_actividades_recomendadas(
    temperatura: float,
    estado: str,
    hum: int,
    viento: float,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # <-- CAMBIO CLAVE AQUÍ
):
    estado = estado.capitalize()
    user = current_user # Ya tenemos el usuario validado desde la dependencia

    # Obtener preferencias del usuario
    preferencias = db.query(models.UserPreference).filter_by(user_id=user.id).all()
    
    print(f"Usuario ID: {user.id}")
    print(f"Parámetros de clima recibidos: temperatura={temperatura}, estado={estado}, humedad={hum}, viento={viento}")
    
    # Primero, obtener TODAS las actividades personalizadas del usuario (sin filtro de clima)
    todas_actividades_usuario = crud.get_user_activities(db=db, user_id=user.id)
    print(f"Total de actividades personalizadas del usuario: {len(todas_actividades_usuario)}")
    for act in todas_actividades_usuario:
        print(f"  - {act.nombre}: temp_min={act.temperatura_min}, temp_max={act.temperatura_max}, estado={act.estado_dia}, hum_max={act.humedad_max}, viento_max={act.viento_max}")
    
    # Obtener actividades personalizadas del usuario que coincidan con el clima
    actividades_personalizadas = crud.get_user_activities_by_weather(
        db=db, 
        user_id=user.id, 
        temperatura=temperatura, 
        estado=estado, 
        hum=hum, 
        viento=viento
    )
    existen_actividades_favoritas = crud.get_user_favorite_activities(
        db=db, 
        user_id=user.id
    )

    
    print(f"Actividades personalizadas que coinciden con el clima: {len(actividades_personalizadas)}")
    for act in actividades_personalizadas:
        print(f"  - {act.nombre}: cumple condiciones climáticas")
    
    # Verificar si el usuario tiene preferencias o actividades personalizadas
    if not preferencias and not actividades_personalizadas and not existen_actividades_favoritas:
        raise HTTPException(
            status_code=404, 
            detail="El usuario no tiene preferencias registradas ni actividades personalizadas que coincidan con el clima actual"
        )
    
    
    # print(f"Preferencias del usuario {user.username} (id={user.id}):")
    # for p in preferencias:
    #     print(f" - activity_type_id={p.activity_type_id}, modality_id={p.modality_id}")

    # Obtener actividades del sistema basadas en preferencias (si las tiene)
    actividades_sistema = []
    if preferencias:
        activity_type_ids = [p.activity_type_id for p in preferencias]
        modality_ids = [p.modality_id for p in preferencias]

        print(f"Filtrando actividades del sistema con:")
        print(f" - temperatura={temperatura}")
        print(f" - estado_dia={estado}")
        print(f" - activity_type_ids={activity_type_ids}")
        print(f" - modality_ids={modality_ids}")

        actividades_sistema = crud.get_actividades_por_clima_y_preferencias(
            db=db,
            temperatura=temperatura,
            estado=estado,
            hum=hum, 
            viento=viento,
            activity_type_ids=activity_type_ids,
            modality_ids=modality_ids
        )

    print(f"Actividades del sistema encontradas: {len(actividades_sistema)}")
    print(f"Actividades personalizadas encontradas: {len(actividades_personalizadas)}")

    # Convertir actividades del sistema al formato unificado
    actividades_recomendadas = []
    
    for actividad in actividades_sistema:
        actividades_recomendadas.append(schemas.ActividadRecomendada(
            id=actividad.id,
            nombre=actividad.nombre,
            descripcion=actividad.descripcion,
            temperatura_min=getattr(actividad, 'temperatura_min', None),
            temperatura_max=getattr(actividad, 'temperatura_max', None),
            humedad_max=getattr(actividad, 'humedad_max', None),
            viento_max=getattr(actividad, 'viento_max', None),
            estado_dia=getattr(actividad, 'estado_dia', None),
            consejos=None,
            es_personalizada=False
        ))
    
    # Convertir actividades personalizadas al formato unificado
    for actividad in actividades_personalizadas:
        actividades_recomendadas.append(schemas.ActividadRecomendada(
            id=actividad.id,
            nombre=actividad.nombre,
            descripcion=actividad.descripcion,
            temperatura_min=actividad.temperatura_min,
            temperatura_max=actividad.temperatura_max,
            humedad_max=actividad.humedad_max,
            viento_max=actividad.viento_max,
            estado_dia=actividad.estado_dia,
            consejos=actividad.consejos,
            es_personalizada=True
        ))
    
    return actividades_recomendadas

# --- Endpoints para Proyectos de Empresa ---
async def get_current_business_user(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_business:
        raise HTTPException(status_code=403, detail="Acceso denegado: se requiere una cuenta de empresa.")
    return current_user

#Actualizado para las actividades laborales de empresas (Filtro antiguo ahora remasterizado en 4k)
@app.get("/actividades/empresa/filtrar", response_model=List[schemas.ActividadLaboral], tags=["Actividades (Empresa)"])
def filtrar_actividades_empresa(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_business_user)
):
    """
    Obtiene TODAS las actividades laborales del proyecto marcado como favorito
    para el usuario de empresa autenticado.
    """
    favorite_project = db.query(models.Project).filter(
        models.Project.user_id == current_user.id,
        models.Project.is_favorite == True
    ).first()

    if not favorite_project:
        return [] # Si no hay proyecto favorito, devuelve una lista vacía

    return favorite_project.labor_activities


@app.post("/projects/", response_model=schemas.Project, tags=["Proyectos (Empresa)"]) 
def create_project_endpoint(
    project: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_business_user)
):
    """Crea un nuevo proyecto para el usuario de empresa autenticado."""
    return crud.create_project(db=db, project=project, user_id=current_user.id)

@app.get("/projects/", response_model=List[schemas.Project], tags=["Proyectos (Empresa)"]) #Esto devuelve la lista de proyectos para mostrarlas
def read_projects_endpoint(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_business_user)
):
    """Obtiene todos los proyectos del usuario de empresa autenticado."""
    return crud.get_projects_by_user(db=db, user_id=current_user.id)

@app.get("/projects/{project_id}", response_model=schemas.Project, tags=["Proyectos (Empresa)"]) #Esto retorna la info de un proyecto específico
def read_single_project_endpoint(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_business_user)
):
    """Obtiene un proyecto específico por su ID, incluyendo sus actividades laborales."""
    db_project = crud.get_project_by_id(db, project_id=project_id, user_id=current_user.id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado o no pertenece al usuario.")
    return db_project

#Esto es nuevo, endpoint para marcar un proyecto como favorito y eliminar el favorito anterior si lo hubiera
@app.post("/projects/{project_id}/favorite", response_model=schemas.Project, tags=["Proyectos (Empresa)"])
def set_favorite_project_endpoint(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_business_user)
):
    """Marca un proyecto como el favorito del usuario."""
    db_project = crud.set_favorite_project(db=db, project_id=project_id, user_id=current_user.id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado o no pertenece al usuario.")
    return db_project

@app.delete("/projects/{project_id}", tags=["Proyectos (Empresa)"])
def delete_project_endpoint(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_business_user)
):
    """Elimina un proyecto específico y todas sus actividades laborales asociadas."""
    success = crud.delete_project(db=db, project_id=project_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado o no pertenece al usuario.")
    return {"message": "Proyecto eliminado exitosamente"}

#'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

@app.post("/projects/{project_id}/activities/", response_model=schemas.ActividadLaboral, tags=["Proyectos (Empresa)"]) #Esto permite crear una actividad laboral en un proyecto
def create_project_activity_endpoint(
    project_id: int,
    activity: schemas.ActividadLaboralCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_business_user)
):
    """Crea una actividad laboral dentro de un proyecto específico."""
    print(f"Creando actividad en proyecto {project_id}: {activity.dict()}")  # Debug logging
    db_project = crud.get_project_by_id(db, project_id=project_id, user_id=current_user.id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado o no pertenece al usuario.")
    return crud.create_project_activity(db=db, activity=activity, project_id=project_id)

@app.delete("/projects/{project_id}/activities/{activity_id}", tags=["Proyectos (Empresa)"])
def delete_project_activity_endpoint(
    project_id: int,
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_business_user)
):
    """Elimina una actividad laboral de un proyecto específico."""
    # Verificar que el proyecto pertenece al usuario
    db_project = crud.get_project_by_id(db, project_id=project_id, user_id=current_user.id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado o no pertenece al usuario.")
    
    # Verificar que la actividad existe y pertenece al proyecto
    db_activity = db.query(models.ActividadLaboral).filter(
        models.ActividadLaboral.id == activity_id,
        models.ActividadLaboral.project_id == project_id
    ).first()
    
    if db_activity is None:
        raise HTTPException(status_code=404, detail="Actividad no encontrada en este proyecto.")
    
    # Eliminar la actividad
    db.delete(db_activity)
    db.commit()
    
    return {"message": "Actividad eliminada exitosamente"}


# Para ejecutar con `python main.py
if __name__ == "__main__":
    import uvicorn
    print(f"Iniciando servidor Uvicorn en http://localhost:8000")
    print(f"API Key de clima cargada: {'Sí' if API_KEY else 'No (¡CONFIGURAR .env!)'}")
    print(f"Documentación de la API disponible en http://localhost:8000/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) # reload=True para desarrollo
