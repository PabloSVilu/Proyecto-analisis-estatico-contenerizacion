import React from 'react'
import styles from '../App.module.css'; 

const ClimaInfo = ({ climaInfo }) => {
    if (!climaInfo) {
        return <p>Cargando clima...</p>;
      }
    return (
      <section className={styles.climaInfoSection}>
        <ul>
          <li>Temp: {climaInfo.temperatura}</li>
          <li>Viento: {climaInfo.viento}</li>
        </ul>
        <ul>
          <li>Humedad: {climaInfo.humedad}</li>
          <li>Presión: {climaInfo.presion}</li>
        </ul>
      </section>
    );
  };
  
  export default ClimaInfo;