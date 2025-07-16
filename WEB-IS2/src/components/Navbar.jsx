import React from 'react';
import { Link } from 'react-router-dom';
import Ubicacion from '../pages/Ubicacion';

function Navbar({ onUbicacionChange }) {
  return (
    <nav style={styles.navbar}>
      {/*Ubicacion, acá se llama al compontente, un detalle es que cuando se muestra la lista está hace crecer Navbar, quien haga el 
      diseño debe ver como acomodar esto... gl hf :) */}
      <div style={styles.left}>
        <Ubicacion onUbicacionChange={onUbicacionChange} />
      </div>

      {/*Login/Register */}
      <div style={styles.right}>
        <Link to="/preferences" className={styles.authLink}>Preferencias</Link>
        <Link to="/login" style={styles.link}>Login</Link>
        <Link to="/register" style={styles.link}>Register</Link>
      </div>
    </nav>
  );
}

//Esto deben moverlo a un .css y darle un estilo fachero
const styles = {
  navbar: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    background: '#ccc',
    padding: '0.5rem 1rem',
  },
  left: {
    display: 'flex',
  },
  right: {
    display: 'flex',
    gap: '1rem',
  },
  link: {
    textDecoration: 'none',
    color: 'blue',
  },
};

export default Navbar;