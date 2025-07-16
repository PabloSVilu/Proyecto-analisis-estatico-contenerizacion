import React, { useState, useEffect } from 'react';
import styles from './Notification.module.css';

const Notification = ({
  message,
  type = 'success',
  duration = 2000, // Duración total visible (antes de empezar a desvanecer)
  fadeOutTime = 300, // Duración de la animación de fadeOut en ms
  onClose,
  isVisible, // Prop del padre para iniciar la aparición
  buttonText 
}) => {
  const [renderState, setRenderState] = useState('idle'); // 'idle', 'entering', 'visible', 'leaving'

  useEffect(() => {
    let phaseTimer;
    let cleanupTimer;

    if (isVisible && message && renderState !== 'entering' && renderState !== 'visible') {

      setRenderState('entering');

      // Asumimos que la animación de entrada @keyframes (scaleUpAndWobble) dura 0.6s = 600ms
      const entryAnimationDuration = 600; 
      phaseTimer = setTimeout(() => {
        setRenderState('visible');
      }, entryAnimationDuration);

      cleanupTimer = setTimeout(() => {
        setRenderState('leaving'); // Aplicar clase .fadeOut
        setTimeout(() => {
          if (onClose) {
            onClose(); // Notificar al padre
          }
          setRenderState('idle'); // Resetear para la próxima vez
        }, fadeOutTime); // Esperar que la animación de fadeOut termine
      }, duration + entryAnimationDuration); // Duración total antes de llamar a onClose

    } else if (!isVisible && (renderState === 'visible' || renderState === 'entering')) {
      // Si el padre lo oculta prematuramente, forzar la salida
      setRenderState('leaving');
      cleanupTimer = setTimeout(() => {
        if (onClose) {
          onClose();
        }
        setRenderState('idle');
      }, fadeOutTime);
    }
    
    return () => {
      clearTimeout(phaseTimer);
      clearTimeout(cleanupTimer);
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps 
  }, [isVisible, message, duration, fadeOutTime, onClose]); // No incluir renderState aquí para evitar bucles

  // No renderizar si está 'idle'
  if (renderState === 'idle') {
    return null;
  }

  const notificationClasses = [
    styles.buttonLikeNotification,
    styles[type],
    (renderState === 'entering' || renderState === 'visible') ? styles.show : '', // Aplica animación de entrada y estado visible
    renderState === 'leaving' ? styles.fadeOut : '' // Aplica animación de salida
  ].join(' ');

  return (
    <div className={notificationClasses}>
      {message || buttonText} 
    </div>
  );
};

export default Notification;