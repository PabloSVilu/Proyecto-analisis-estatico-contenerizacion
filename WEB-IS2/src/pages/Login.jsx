import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css';//Css para el front del login

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    if (token) navigate('/');
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const response = await fetch('http://localhost:8000/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ username, password }),
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('accessToken', data.access_token);
      localStorage.setItem('userEmail', username);
      localStorage.setItem('is_business', data.is_business);
      navigate('/');
    } else {
      alert('Error al iniciar sesión');
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        
        <h2>Iniciar sesión</h2>
        <p>Usa tu cuenta para acceder</p>
        <form onSubmit={handleSubmit} className="form">
          <input
            type="email"
            placeholder="Correo electrónico"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Contraseña"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit">Siguiente</button>
        </form>
      </div>
    </div>
  );
};

export default Login;
