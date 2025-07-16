import React from 'react';
import styles from './ToggleButton.module.css';

const ToggleButton = ({ label, isActive, onClick }) => {
  return (
    <button
      className={`${styles.toggleButton} ${isActive ? styles.active : ''}`}
      onClick={onClick}
      aria-pressed={isActive} // Para accesibilidad
    >
      {label}
    </button>
  );
};

export default ToggleButton;