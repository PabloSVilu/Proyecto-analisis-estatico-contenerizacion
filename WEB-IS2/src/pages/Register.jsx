import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Register.css';//Css para Register

const Register = () => {
  // Estados para almacenar valores del formulario
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false); // Para mostrar/ocultar contraseña
  const [error, setError] = useState(''); // Para mensajes de error
  const [is_business, setIsBusiness] = useState(false);
  const navigate = useNavigate();

  // Función que se ejecuta al enviar el formulario
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(''); // Limpiar errores previos

    // Validación básica del correo electrónico
    if (!email.match(/^[^@]+@[^@]+\.[^@]+$/)) {
      setError('El correo no es válido (ej. usuario@dominio.com).');
      return; // Detiene el envío si falla la validación
    }

    // Validaciones para la contraseña
    if (password.length < 6||!/[A-Z]/.test(password || !/[0-9]/.test(password) ||!/[!@#$%^&*(),.?":{}|<>]/.test(password))) {
      setError('La contraseña debe tener al menos 6 caracteres, al menos una letra mayúscula, al menos un numero y un carácter especial');
      return;
    }

    // Validar que ambas contraseñas coincidan
    if (password !== confirmPassword) {
      setError('Las contraseñas no coinciden.');
      return;
    }

    // Intentar hacer la petición POST al backend para registrar
    try {
      const response = await fetch('http://localhost:8000/register/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, is_business }), // Enviar datos como JSON
      });

      console.log({ email, password, is_business });

      if (response.ok) {
        alert('Registro exitoso!');
        navigate('/login'); // Redirigir al login tras registro exitoso
      } else {
        // Manejo de errores provenientes del backend
        let errorText = 'El registro falló. Intenta de nuevo.';
        const contentType = response.headers.get('content-type');

        if (contentType && contentType.includes('application/json')) {
          const errorData = await response.json();

          // Si el error es un array de errores (p. ej. de validación)
          if (Array.isArray(errorData)) {
            errorText = errorData.map((e) => e.msg).join(', ');
          } else if (errorData.detail) {
            errorText = errorData.detail; // Mensaje detallado del error
          }
        } else {
          // En caso que no sea JSON, mostrar texto plano
          errorText = await response.text();
        }

        setError(errorText);
      }
    } catch (err) {
      // Error de red u otro error inesperado
      console.error('Error al enviar el formulario:', err);
      setError('Error inesperado al registrar. Intenta más tarde.');
    }
  };

  return (
    <div className="register-container">
      <div className="register-card">
        <h2>Registrarse</h2>
        <p>Crea tu cuenta para continuar</p>

        {/* Formulario de registro */}
        <form onSubmit={handleSubmit} autoComplete="off" className="form">
          {/* Mostrar mensaje de error si existe */}
          {error && <p style={{ color: 'red' }}>{error}</p>}

          {/* Input para email */}
          <input
            type="email"
            placeholder="Correo electrónico"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email" // Indica al navegador qué tipo de dato es
          />

          {/* Input para contraseña con botón para mostrar/ocultar */}
          <div className="password-input-container">
            <input
              type={showPassword ? 'text' : 'password'} // Cambia tipo según estado showPassword
              placeholder="Contraseña"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="new-password" // Evita sugerencias/autocompletado
            />
            <button
              type="button"
              className="show-password-btn"
              onClick={() => setShowPassword(!showPassword)} // Alterna mostrar/ocultar
              aria-label="Mostrar/ocultar contraseña"
            >
              👁
            </button>
          </div>

          {/* Input para confirmar contraseña con botón para mostrar/ocultar */}
          <div className="password-input-container">
            <input
              type={showPassword ? 'text' : 'password'}
              placeholder="Confirmar contraseña"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              autoComplete="new-password"
            />
            <button
              type="button"
              className="show-password-btn"
              onClick={() => setShowPassword(!showPassword)}
              aria-label="Mostrar/ocultar contraseña"
            >
              👁
            </button>
          </div>

          <div className="checkbox-container">
            <label>
              <input
              type="checkbox"
              checked={is_business}
              onChange={(e) => setIsBusiness(e.target.checked)}
              />
            <font color="black">Registrarse como usuario empresa</font>
            </label>
          </div>
          
          {/* Botón para enviar formulario */}
          <button type="submit">Registrarse</button>
        </form>
      </div>
    </div>
  );
};

export default Register;
