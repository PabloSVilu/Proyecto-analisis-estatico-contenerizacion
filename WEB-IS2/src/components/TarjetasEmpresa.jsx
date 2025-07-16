import React, { useState, useEffect } from 'react';
import styles from '../App.module.css';

// Objeto para mapear estados del clima a español
const CLIMA_TRADUCCIONES = {
    "Clear": "despejados",
    "Clouds": "nublados", 
    "Rain": "lluviosos",
    "Snow": "con nieve",
    "Mist": "con niebla",
    "Drizzle": "con llovizna",
    "Thunderstorm": "con tormenta",
};

const TarjetasEmpresa = ({ actividades, clima }) => {
  const [popupVisible, setPopupVisible] = useState(false);
  const [actividadSeleccionada, setActividadSeleccionada] = useState(null);

  // Manejar tecla Escape para cerrar el popup
  useEffect(() => {
    const handleEsc = (event) => {
       if (event.key === 'Escape' && popupVisible) {
          cerrarPopup();
       }
    };
    window.addEventListener('keydown', handleEsc);
    return () => {
       window.removeEventListener('keydown', handleEsc);
    };
  }, [popupVisible]);

  if (!clima) {
    return <p className={styles.loadingMessage}>Esperando datos del clima...</p>;
  }

  if (!Array.isArray(actividades) || actividades.length === 0) {
    return <p className={styles.loadingMessage}>No hay actividades en el proyecto favorito.</p>;
  }

  const esRecomendada = (actividad) => {
    const temp = clima.temperatura ?? clima.temp_max ?? 0;
    return (
      console.log(temp, clima.humedad, clima.viento_velocidad, clima.main, actividad.estado_dia),
      temp >= actividad.temperatura_min &&
      temp <= actividad.temperatura_max &&
      (actividad.humedad_max === null || clima.humedad <= actividad.humedad_max) &&
      (actividad.viento_max === null || clima.viento_velocidad <= actividad.viento_max) &&
      clima.main === actividad.estado_dia
    );
  };

  const obtenerRazonesRecomendacion = (actividad) => {
    const razones = [];
    const temp = clima.temperatura ?? clima.temp_max ?? 0;
    
    if (temp >= actividad.temperatura_min && temp <= actividad.temperatura_max) {
      razones.push(`La temperatura actual (${temp}°C) está dentro del rango ideal (${actividad.temperatura_min}°C - ${actividad.temperatura_max}°C)`);
    }
    
    if (actividad.humedad_max === null || clima.humedad <= actividad.humedad_max) {
      if (actividad.humedad_max !== null) {
        razones.push(`La humedad actual (${clima.humedad}%) está por debajo del máximo permitido (${actividad.humedad_max}%)`);
      } else {
        razones.push(`No hay restricciones de humedad para esta actividad`);
      }
    }
    
    if (actividad.viento_max === null || clima.viento_velocidad <= actividad.viento_max) {
      if (actividad.viento_max !== null) {
        razones.push(`La velocidad del viento actual (${clima.viento_velocidad} km/h) está por debajo del máximo permitido (${actividad.viento_max} km/h)`);
      } else {
        razones.push(`No hay restricciones de viento para esta actividad`);
      }
    }
    
    if (clima.main === actividad.estado_dia) {
      razones.push(`El estado del tiempo actual (${clima.main}) coincide perfectamente con el requerido (${actividad.estado_dia})`);
    }
    
    return razones;
  };

  const obtenerRazonesNoRecomendacion = (actividad) => {
    const razones = [];
    const temp = clima.temperatura ?? clima.temp_max ?? 0;
    if (temp < actividad.temperatura_min) {
      razones.push(`La temperatura actual (${temp}°C) está por debajo del mínimo requerido (${actividad.temperatura_min}°C)`);
    }
    
    if (temp > actividad.temperatura_max) {
      razones.push(`La temperatura actual (${temp}°C) está por encima del máximo permitido (${actividad.temperatura_max}°C)`);
    }
    
    if (actividad.humedad_max !== null && clima.humedad > actividad.humedad_max) {
      razones.push(`La humedad actual (${clima.humedad}%) supera el máximo permitido (${actividad.humedad_max}%)`);
    }
    
    if (actividad.viento_max !== null && clima.viento_velocidad > actividad.viento_max) {
      razones.push(`La velocidad del viento actual (${clima.viento_velocidad} km/h) supera el máximo permitido (${actividad.viento_max} km/h)`);
    }
    
    if (clima.main !== actividad.estado_dia) {
      razones.push(`El estado del tiempo actual (${clima.main}) no coincide con el requerido (${actividad.estado_dia})`);
    }
    
    return razones;
  };

  const handleCardClick = (actividad) => {
    setActividadSeleccionada(actividad);
    setPopupVisible(true);
  };

  const cerrarPopup = () => {
    setPopupVisible(false);
    setActividadSeleccionada(null);
  };

  const getEstadoClimaTraducido = (estadoIngles) => {
    return CLIMA_TRADUCCIONES[estadoIngles] || estadoIngles.toLowerCase();
  };

  return (
    <>
      <section className={styles.cardGrid}>
        {actividades.map((act) => {
          const recomendada = esRecomendada(act);
          const cardClass = recomendada ? styles.card : `${styles.card} ${styles.cardNoRecomendada}`;
          
          return (
            <div 
              key={act.id} 
              className={cardClass} 
              onClick={() => handleCardClick(act)}
              tabIndex={0}
              onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') handleCardClick(act) }}
              role="button"
              style={{ cursor: 'pointer' }}
            >
              <h3 className={styles.cardTitleWithEmoji}>
                {act.nombre}
                {!recomendada && <span className={styles.noRecomendadaBadge}>No Recomendada</span>}
              </h3>
              <p>{act.descripcion}</p>
              <p className={styles.clickInfo}>
                <small>Haz clic para ver más detalles</small>
              </p>
            </div>
          );
        })}
      </section>

      {/* Modal para mostrar razones de no recomendación */}
      {popupVisible && actividadSeleccionada && (
        <div className={styles.modalOverlay} onClick={cerrarPopup} role="dialog" aria-modal="true" aria-labelledby="modalTitle">
          <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <button 
              className={styles.modalCloseButton} 
              onClick={cerrarPopup}
              aria-label="Cerrar modal"
            >
              ×
            </button>
            <h2 id="modalTitle" className={styles.modalTitleWithEmoji}>
              {esRecomendada(actividadSeleccionada) ? '¿Por qué es recomendada esta actividad?' : '¿Por qué no es recomendada esta actividad?'}
            </h2>
            
            <div className={styles.modalSection}>
              <h3>{actividadSeleccionada.nombre}</h3>
              <p className={styles.modalDescription}>{actividadSeleccionada.descripcion}</p>
            </div>
            
            <div className={styles.modalSection}>
              <h4>{esRecomendada(actividadSeleccionada) ? 'Condiciones que se cumplen:' : 'Condiciones que no se cumplen:'}</h4>
              <ul>
                {esRecomendada(actividadSeleccionada) 
                  ? obtenerRazonesRecomendacion(actividadSeleccionada).map((razon, index) => (
                      <li key={index}>{razon}</li>
                    ))
                  : obtenerRazonesNoRecomendacion(actividadSeleccionada).map((razon, index) => (
                      <li key={index}>{razon}</li>
                    ))
                }
              </ul>
            </div>

            <div className={styles.modalSection}>
              <h4>Condiciones climáticas actuales:</h4>
              <ul>
                <li>Temperatura: <strong className={styles.highlightedText}>{clima.temperatura ?? clima.temp_max ?? 0}°C</strong></li>
                <li>Humedad: <strong className={styles.highlightedText}>{clima.humedad}%</strong></li>
                <li>Viento: <strong className={styles.highlightedText}>{clima.viento_velocidad} km/h</strong></li>
                <li>Estado: <strong className={styles.highlightedText}>{getEstadoClimaTraducido(clima.main)}</strong></li>
              </ul>
            </div>

            <div className={styles.modalIdealConditions}>
              <p>
                Esta actividad es ideal para días <strong className={styles.highlightedText}>{getEstadoClimaTraducido(actividadSeleccionada.estado_dia)}</strong>,
                con temperatura entre <strong className={styles.highlightedText}>{actividadSeleccionada.temperatura_min}°C</strong> y <strong className={styles.highlightedText}>{actividadSeleccionada.temperatura_max}°C</strong>
                {actividadSeleccionada.humedad_max !== null && (
                  <>, humedad máxima de <strong className={styles.highlightedText}>{actividadSeleccionada.humedad_max}%</strong></>
                )}
                {actividadSeleccionada.viento_max !== null && (
                  <> y viento máximo de <strong className={styles.highlightedText}>{actividadSeleccionada.viento_max} km/h</strong></>
                )}.
              </p>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default TarjetasEmpresa;