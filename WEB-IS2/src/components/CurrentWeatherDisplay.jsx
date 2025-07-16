import React from 'react';
import styles from './CurrentWeatherDisplay.module.css';

const CurrentWeatherDisplay = ({ weatherData, cityName }) => {
  if (!weatherData) {
    return <p className={styles.loading}>Cargando clima actual...</p>;
  }

  // Usar temp_max para pronóstico, temperatura para actual.
  const displayTemp = weatherData.temperatura !== undefined ? weatherData.temperatura : weatherData.temp_max;
  // Usar sensacion_termica para actual, sensacion_termica_dia para pronóstico.
  const feelsLike = weatherData.sensacion_termica !== undefined ? weatherData.sensacion_termica : weatherData.sensacion_termica_dia;
  
  // Para Calidad del aire, no mostrar si el valor es "N/A" o no existe
  const airQualityValue = weatherData.calidad_aire?.value;
  const showAirQuality = airQualityValue !== undefined && airQualityValue !== null && airQualityValue !== "N/A";

  // Para Visibilidad, no mostrar si no existe o es un valor por defecto que indica "no disponible"
  const visibilityValue = weatherData.visibilidad; // Asumimos que 10000 es un valor por defecto si no hay datos reales.
  const showVisibility = visibilityValue !== undefined && visibilityValue !== null && visibilityValue < 100000; // Ajusta 100000 si tu API devuelve un valor muy alto para "ilimitada" o "no especificada"

  // Para Punto de rocío, no mostrar si no existe
  const dewPointValue = weatherData.punto_rocio;
  const showDewPoint = dewPointValue !== undefined && dewPointValue !== null;


  return (
    <section className={styles.currentWeather}>
      <div className={styles.mainInfo}>
        <div className={styles.locationTime}>
          <h2>{cityName}</h2>
          {/* Asegurarse que weatherData.dt exista antes de usarlo */}
          <h1>
            {weatherData.dayLabel && <p>{weatherData.dayLabel}</p>}
          </h1>
        </div>
        <div className={styles.tempIcon}>
          {weatherData.icono && (
            <img
              src={`http://openweathermap.org/img/wn/${weatherData.icono}@4x.png`}
              alt={weatherData.descripcion || 'Icono del clima'}
              className={styles.weatherIcon}
            />
          )}
          <span className={styles.temperature}>{Math.round(displayTemp)}°C</span>
          <div className={styles.descriptionFeelsLike}>
            <p className={styles.description}>{weatherData.descripcion}</p>
            {feelsLike !== undefined && <p className={styles.feelsLike}>Sensación térmica: {Math.round(feelsLike)}°</p>}
          </div>
        </div>
      </div>

      <div className={styles.detailsGrid}>
        {showAirQuality && (
          <div className={styles.detailItem}>
            <span>Calidad del aire</span>
            <strong>{airQualityValue}</strong>
          </div>
        )}
        {weatherData.viento_velocidad !== undefined && (
          <div className={styles.detailItem}>
            <span>Viento</span>
            <strong>{weatherData.viento_velocidad} km/h</strong>
          </div>
        )}
        {weatherData.humedad !== undefined && (
          <div className={styles.detailItem}>
            <span>Humedad</span>
            <strong>{weatherData.humedad}%</strong>
          </div>
        )}
        {showVisibility && (
          <div className={styles.detailItem}>
            <span>Visibilidad</span> 
            <strong>{`${visibilityValue / 1000} km`}</strong>
          </div>
        )}
        {weatherData.presion !== undefined && (
          <div className={styles.detailItem}>
            <span>Presión</span>
            <strong>{weatherData.presion} mbar</strong>
          </div>
        )}
        {showDewPoint && (
          <div className={styles.detailItem}>
            <span>Punto de rocío</span>
            <strong>{dewPointValue}°</strong>
          </div>
        )}
      </div>
    </section>
  );
};

export default CurrentWeatherDisplay;