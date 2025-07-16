import React from 'react'
import styles from '../App.module.css'; 

const ImagenNombreClima = ({clima}) => {
    
    return (
        <div className={styles.climaCircleContainer}>
        <div className={styles.climaInfo}>
          {clima && clima.icono ? (
                <img src={`http://openweathermap.org/img/wn/${clima.icono}@2x.png`} alt="icono clima" className={styles.iconoClima} />
                ) : ( <p>Cargando imagen...</p> )}
          <div className={styles.descripcionClima}> {clima ? clima.descripcion : 'Cargando...'} </div>
          <div className={styles.descripcionClima}> en {clima ? clima.ciudad : 'Cargando...'} </div>
        </div>
      </div>
    );
  };
  
  export default ImagenNombreClima;