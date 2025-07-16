import React from 'react';
import styles from './HourlyForecastDisplay.module.css';

const HourlyForecastDisplay = ({ allHourlyData, selectedDayDt, timezoneOffset }) => {
  if (!allHourlyData || allHourlyData.length === 0 || !selectedDayDt || timezoneOffset === undefined) {
    // Si timezoneOffset es undefined, no podemos procesar las fechas correctamente.
    return (
        <section className={styles.hourlyForecastSection}>
            <h3 className={styles.sectionTitle}>Pronóstico por Hora</h3>
            <p className={styles.loading}>
                {timezoneOffset === undefined ? "Esperando datos completos..." : "Selecciona un día para ver el pronóstico por hora."}
            </p>
        </section>
    );
  }

  const getLocalDateString = (dt, offsetSeconds) => {
    const dateUtc = new Date(dt * 1000);
    const localTimeBasedOnOffset = new Date(dateUtc.getTime() + offsetSeconds * 1000);
    return localTimeBasedOnOffset.toISOString().split('T')[0];
  };
  
  const selectedDayDateString = getLocalDateString(selectedDayDt, timezoneOffset);

  const filteredHourlyData = allHourlyData.filter(hour => {
    const hourDateString = getLocalDateString(hour.dt, timezoneOffset);
    return hourDateString === selectedDayDateString;
  });

  if (filteredHourlyData.length === 0) {
    // Intentamos obtener el nombre del día seleccionado para el mensaje
    let selectedDayName = "el día seleccionado";
    try {
        const tempDate = new Date(selectedDayDt * 1000);
        tempDate.setSeconds(tempDate.getSeconds() + timezoneOffset); // Ajustar a la zona horaria
        selectedDayName = tempDate.toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', timeZone: 'UTC' });
    } catch (e) {
        // No hacer nada si falla la obtención del nombre
    }

    return (
        <section className={styles.hourlyForecastSection}>
            <h3 className={styles.sectionTitle}>Pronóstico por Hora</h3>
            <p className={styles.noData}>
                No hay datos horarios detallados disponibles para {selectedDayName}.
            </p>
        </section>
    );
  }

  const formatHour = (dt, offsetSeconds) => {
    const dateUtc = new Date(dt * 1000);
    const localTimeBasedOnOffset = new Date(dateUtc.getTime() + offsetSeconds * 1000);
    return localTimeBasedOnOffset.toLocaleTimeString('es-ES', { hour: 'numeric', hour12: true, timeZone: 'UTC' });
  };
  
  let titleDayName = "el día seleccionado";
    try {
        const tempDate = new Date(selectedDayDt * 1000);
        tempDate.setSeconds(tempDate.getSeconds() + timezoneOffset); // Ajustar a la zona horaria
        titleDayName = tempDate.toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', timeZone: 'UTC' });
    } catch (e) {
        //
    }


  return (
    <section className={styles.hourlyForecastSection}>
      <h3 className={styles.sectionTitle}>Pronóstico por Hora para {titleDayName}</h3>
      <div className={styles.hourlyScrollContainer}>
        {filteredHourlyData.map((hour) => (
          <div key={hour.dt} className={styles.hourItem}>
            <span className={styles.hourTime}>{formatHour(hour.dt, timezoneOffset)}</span>
            <img
              src={`http://openweathermap.org/img/wn/${hour.icono}@2x.png`}
              alt="icon"
              className={styles.hourIcon}
            />
            <span className={styles.hourTemp}>{Math.round(hour.temp)}°C</span>
            {typeof hour.pop === 'number' && hour.pop > 0 && (
              <span className={styles.hourPop}>
                💧 {Math.round(hour.pop)}% 
              </span>
            )}
          </div>
        ))}
      </div>
    </section>
  );
};

export default HourlyForecastDisplay;