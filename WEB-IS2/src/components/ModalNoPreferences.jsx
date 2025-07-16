import React from 'react';
import styles from '../App.module.css';

const ModalAviso = ({ mensaje, onClose }) => {
  return (
    <div className={styles.modalOverlay}>
      <div className={styles.modalContent}>
        <button className={styles.modalCloseButton} onClick={onClose}>
          ×
        </button>
        <h2 className={styles.modalTitle}>Aviso</h2>
        <p className={styles.modalDescription}>{mensaje}</p>
      </div>
    </div>
  );
};

export default ModalAviso;