import React, { useState, useEffect } from 'react';
import styles from '../App.module.css'; 

import { DUMMY_DETALLES_ACTIVIDADES } from '../data/activitiesMockData';

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


const Tarjetas = ({ recomendaciones }) => {
    const [selectedActivity, setSelectedActivity] = useState(null);

    useEffect(() => {
        const handleEsc = (event) => {
           if (event.key === 'Escape' && selectedActivity) {
              closeModal();
           }
        };
        window.addEventListener('keydown', handleEsc);
        return () => {
           window.removeEventListener('keydown', handleEsc);
        };
    }, [selectedActivity]);

    if (!Array.isArray(recomendaciones) || recomendaciones.length === 0) {
        return <p className={styles.loadingMessage}>No se encontraron recomendaciones disponibles.</p>;
    }

    const handleCardClick = (actividad) => {
        const detallesCompletos = DUMMY_DETALLES_ACTIVIDADES[actividad.nombre] || {};
        const actividadConDetalles = { 
            ...actividad, 
            emoji: detallesCompletos.emoji || "✨", 
            consejos: detallesCompletos.consejos || ["No hay consejos específicos disponibles."],
            observaciones: detallesCompletos.observaciones || ["No hay observaciones específicas disponibles."]
        };
        setSelectedActivity(actividadConDetalles);
    };

    const closeModal = () => {
        setSelectedActivity(null);
    };

    const getEstadoClimaTraducido = (estadoIngles) => {
        return CLIMA_TRADUCCIONES[estadoIngles] || estadoIngles.toLowerCase();
    };

    // Función para obtener el emoji de una actividad, usado en las tarjetas
    const getActivityEmoji = (nombreActividad) => {
        const detalles = DUMMY_DETALLES_ACTIVIDADES[nombreActividad];
        return detalles ? detalles.emoji : null; // Devuelve null si no hay emoji para que no renderice un span vacío
    };

    return (
        <>
            <section className={styles.cardGrid}>
                {recomendaciones.map((rec) => {
                    const emoji = getActivityEmoji(rec.nombre);
                    return (
                        <div 
                            key={rec.id} 
                            className={styles.card} 
                            onClick={() => handleCardClick(rec)}
                            tabIndex={0}
                            onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') handleCardClick(rec) }}
                            role="button"
                        >
                           <h3 className={styles.cardTitleWithEmoji}>
                            {rec.nombre}
                            {rec.isFavorite && <span className={styles.favoriteStar} title="Actividad favorita">⭐</span>}
                            {emoji && <span className={styles.cardEmoji} aria-hidden="true">{emoji}</span>}
                            </h3>

                            <p>{rec.descripcion}</p>
                        </div>
                    );
                })}
            </section>

            {selectedActivity && (
                <div className={styles.modalOverlay} onClick={closeModal} role="dialog" aria-modal="true" aria-labelledby="modalTitle">
                    <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
                        <button 
                            className={styles.modalCloseButton} 
                            onClick={closeModal}
                            aria-label="Cerrar modal"
                        >
                            ×
                        </button>
                        <h2 id="modalTitle" className={styles.modalTitleWithEmoji}>
                           {selectedActivity.nombre}
                           {selectedActivity.emoji && <span className={styles.modalEmoji} aria-hidden="true">{selectedActivity.emoji}</span>}
                        </h2>
                        <p className={styles.modalDescription}>{selectedActivity.descripcion}</p>
                        
                        <div className={styles.modalSection}>
                            <h4>Consejos:</h4>
                            <ul>
                                {selectedActivity.consejos.map((consejo, index) => (
                                    <li key={`consejo-${index}`}>{consejo}</li>
                                ))}
                            </ul>
                        </div>

                        <div className={styles.modalSection}>
                            <h4>Observaciones:</h4>
                            <ul>
                                {selectedActivity.observaciones.map((obs, index) => (
                                    <li key={`obs-${index}`}>{obs}</li>
                                ))}
                            </ul>
                        </div>
                        
                        <div className={styles.modalIdealConditions}>
                            <p>
                                Esta actividad es perfecta para días <strong className={styles.highlightedText}>{getEstadoClimaTraducido(selectedActivity.estado_dia)}</strong>,
                                especialmente cuando la temperatura se encuentra entre <strong className={styles.highlightedText}>{selectedActivity.temperatura_min}°C</strong> y <strong className={styles.highlightedText}>{selectedActivity.temperatura_max}°C</strong>.
                            </p>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};
  
export default Tarjetas;