import React from 'react';
import styles from './DailyForecastNav.module.css'; // Crearemos este archivo CSS

const DailyForecastNav = ({ dailyData, onDaySelect, selectedDayDt }) => {
  if (!dailyData || dailyData.length === 0) {
    return <p className={styles.loading}>Cargando pronóstico diario...</p>;
  }

  return (
    <nav className={styles.dailyNav}>
      {dailyData.map((day) => (
        <button
          key={day.dt}
          onClick={() => onDaySelect(day.dt)}
          className={`${styles.dayButton} ${selectedDayDt === day.dt ? styles.selected : ''}`}
        >
          <span className={styles.dayLabel}>{day.dayLabel}</span>
          <img
            src={`http://openweathermap.org/img/wn/${day.icono}@2x.png`}
            alt={day.descripcion}
            className={styles.dayIcon}
          />
          <div className={styles.dayTemps}>
            <span className={styles.tempMax}>{Math.round(day.temp_max)}°</span>
            <span className={styles.tempMin}>{Math.round(day.temp_min)}°</span>
          </div>
        </button>
      ))}
    </nav>
  );
};

export default DailyForecastNav;