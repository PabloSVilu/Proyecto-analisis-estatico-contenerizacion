import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './Proyectos.module.css';

function Proyectos() {
  const [isBusiness, setIsBusiness] = useState(false);
  const [userEmail, setUserEmail] = useState('');

  const [proyectos, setProyectos] = useState([]);
  
  const [nuevoTitulo, setNuevoTitulo] = useState('');
  const [nuevaDescripcion, setNuevaDescripcion] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [proyectoAEliminar, setProyectoAEliminar] = useState(null);
  const [columnLayout, setColumnLayout] = useState(2);
  const [animationState, setAnimationState] = useState('idle');

  const navigate = useNavigate();

  // Función para obtener proyectos desde el backend
  const fetchProyectos = async () => {
    const token = localStorage.getItem("accessToken");
    if (!token) return;

    try {
      const response = await fetch('http://localhost:8000/projects/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setProyectos(data);
      } else if (response.status === 403) {
        alert("Acceso denegado. Debes ser un usuario de empresa.");
        navigate("/login");
      } else {
        console.error('Error al cargar proyectos:', response.status);
      }
    } catch (error) {
      console.error('Error al cargar proyectos:', error);
    }
  };

  useEffect(() => {
    const businessFlag = localStorage.getItem("is_business") === 'true';
    const email = localStorage.getItem("userEmail");

    if (!businessFlag || !email) {
        alert("Acceso denegado. Debes ser un usuario de empresa e iniciar sesión.");
        navigate("/login");
        return; 
    }

    setIsBusiness(true);
    setUserEmail(email);
    setIsLoading(false);
    
    // Cargar proyectos desde el backend
    fetchProyectos();
    
  }, [navigate]);

  const handleLayoutChange = (newLayout) => {
    if (newLayout === columnLayout || animationState !== 'idle') return;
    setAnimationState('shrinking');
    setTimeout(() => {
      setColumnLayout(newLayout);
      setAnimationState('growing');
      setTimeout(() => {
        setAnimationState('idle');
      }, 20);
    }, 350);
  };

  const handleCrearProyecto = async (e) => {
    e.preventDefault();
    if (!nuevoTitulo.trim()) {
      alert("El título del proyecto es obligatorio.");
      return;
    }

    const token = localStorage.getItem("accessToken");
    if (!token) {
      alert("No autorizado. Por favor inicia sesión.");
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/projects/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          name: nuevoTitulo,
          description: nuevaDescripcion || ""
        })
      });

      if (response.ok) {
        const nuevoProyecto = await response.json();
        setProyectos(proyectosActuales => [nuevoProyecto, ...proyectosActuales]);
        setNuevoTitulo('');
        setNuevaDescripcion('');
        alert("Proyecto creado exitosamente.");
      } else {
        const errorData = await response.json();
        alert(`Error al crear el proyecto: ${errorData.detail || 'Error desconocido'}`);
      }
    } catch (error) {
      console.error('Error al crear proyecto:', error);
      alert("Error de conexión al crear el proyecto.");
    }
  };

  const handleAbrirModal = (proyecto) => {
    setProyectoAEliminar(proyecto);
  };

  const handleCerrarModal = () => {
    setProyectoAEliminar(null);
  };

  const handleConfirmarEliminacion = async () => {
    if (!proyectoAEliminar) return;

    const token = localStorage.getItem("accessToken");
    if (!token) {
      alert("No autorizado. Por favor inicia sesión.");
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/projects/${proyectoAEliminar.id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        setProyectos(proyectosActuales =>
          proyectosActuales.filter(p => p.id !== proyectoAEliminar.id)
        );
        handleCerrarModal();
        alert("Proyecto eliminado exitosamente.");
      } else {
        const errorData = await response.json();
        alert(`Error al eliminar el proyecto: ${errorData.detail || 'Error desconocido'}`);
      }
    } catch (error) {
      console.error('Error al eliminar proyecto:', error);
      alert("Error de conexión al eliminar el proyecto.");
    }
  };
  // Función para marcar un proyecto como favorito :)
  const handleSetFavorite = async (projectId, e) => {
    e.stopPropagation(); 
    const token = localStorage.getItem("accessToken");
    if (!token) return;

    try {
      const response = await fetch(`http://localhost:8000/projects/${projectId}/favorite`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {

        fetchProyectos();
      } else {
        alert("Error al marcar como favorito.");
      }
    } catch (error) {
      console.error("Error al marcar como favorito:", error);
    }
  };

  if (isLoading) {
    return (
        <div className={styles.proyectosPageContainer}>
            <p className={styles.noProyectosMessage}>Cargando datos del usuario...</p>
        </div>
    );
  }

  const username = userEmail.split('@')[0];

  return (
    <>
      <div className={styles.proyectosPageContainer}>
        {/* -- ENCABEZADO DE LA PÁGINA -- */}
        <div className={styles.header}>
            <h1 className={styles.pageTitle}>Proyectos de <span>{username || 'Empresa'}</span></h1>
            <button onClick={() => navigate("/")} className={styles.backButton}>
                <span className={styles.backButtonArrow}>⬅</span>
                Volver al Inicio
            </button>
        </div>

        {/* -- FORMULARIO PARA CREAR PROYECTOS -- */}
        <section className={styles.formSection}>
            <h3>Crear nuevo proyecto</h3>
            <form onSubmit={handleCrearProyecto} className={styles.form}>
                <input type="text" placeholder="Título del proyecto" value={nuevoTitulo} onChange={(e) => setNuevoTitulo(e.target.value)} required className={styles.input} />
                <textarea placeholder="Descripción del proyecto (opcional)" value={nuevaDescripcion} onChange={(e) => setNuevaDescripcion(e.target.value)} rows={4} className={styles.textarea} />
                <button type="submit" className={styles.submitButton}>+ Guardar Proyecto</button>
            </form>
        </section>

        {/* -- LISTA DE PROYECTOS EXISTENTES -- */}
        <section className={styles.proyectosListContainer}>
          <div className={styles.listHeader}>
            <h3>Proyectos existentes</h3>
            <div className={styles.layoutControls}>
              <button
                className={`${styles.layoutButton} ${columnLayout === 2 ? styles.active : ''}`}
                onClick={() => handleLayoutChange(2)}
                aria-label="Ver en 2 columnas"
              >
                2 Columnas
              </button>
              <button
                className={`${styles.layoutButton} ${columnLayout === 4 ? styles.active : ''}`}
                onClick={() => handleLayoutChange(4)}
                aria-label="Ver en 4 columnas"
              >
                4 Columnas
              </button>
            </div>
          </div>
          
          {proyectos.length === 0 ? (
            <p className={styles.noProyectosMessage}>No hay proyectos registrados aún. ¡Crea el primero!</p>
          ) : (
            <div className={`${styles.proyectosGrid} ${columnLayout === 4 ? styles.gridFourColumns : styles.gridTwoColumns} ${animationState !== 'idle' ? styles[animationState] : ''}`}>
              {proyectos.map(p => (
                <div
                  key={p.id}
                  className={`${styles.proyectoCard} ${p.is_favorite ? styles.favoriteCard : ''}`}
                  onClick={() => navigate(`/proyectos/${p.id}/actividades`)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => e.key === 'Enter' && navigate(`/proyectos/${p.id}/actividades`)}
                >
                  <button 
                    className={`${styles.favoriteButton} ${p.is_favorite ? styles.isFavorite : ''}`}
                    onClick={(e) => handleSetFavorite(p.id, e)}
                    aria-label={`Marcar ${p.name} como favorito`}
                  >
                    ★
                  </button>
                  <button 
                    className={styles.deleteButton} 
                    onClick={(e) => {e.stopPropagation(); handleAbrirModal(p);}}
                    aria-label={`Eliminar el proyecto ${p.name}`}
                  >
                    ×
                  </button>
                  <h4>{p.name}</h4>
                  <p>{p.description}</p>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>

      {proyectoAEliminar && (
        <div className={styles.modalOverlay} onClick={handleCerrarModal}>
          <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <h4>Confirmar Eliminación</h4>
            <p>¿Estás seguro de que quieres eliminar el proyecto <strong>"{proyectoAEliminar.name}"</strong>? Esta acción no se puede deshacer.</p>
            <div className={styles.modalActions}>
              <button className={`${styles.modalButton} ${styles.cancelButton}`} onClick={handleCerrarModal}>Cancelar</button>
              <button className={`${styles.modalButton} ${styles.confirmButton}`} onClick={handleConfirmarEliminacion}>Sí, Eliminar</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default Proyectos;