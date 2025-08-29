import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

// Configuración de la API
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'http://localhost:8000' 
  : '';

function App() {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/api/employees`);
      setEmployees(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching employees:', err);
      setError('Error al cargar empleados: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="app">
        <div className="loading">Cargando...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app">
        <div className="error">{error}</div>
        <button onClick={fetchEmployees}>Reintentar</button>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Dashboard de Asistencia</h1>
        <p>Gestión de empleados y control de asistencia</p>
      </header>
      
      <main className="main">
        <section className="stats-section">
          <h2>Resumen General</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <h3>Total Empleados</h3>
              <p className="stat-number">{employees.length}</p>
            </div>
            <div className="stat-card">
              <h3>Total Empleados Activos</h3>
              <p className="stat-number">{employees.length}</p>
            </div>
          </div>
        </section>

        <section className="employees-section">
          <h2>Lista de Empleados</h2>
          <div className="employees-grid">
            {employees.map((employee) => (
              <div key={employee.ID_PERSONA} className="employee-card">
                <h3>{employee.NOMBRE} {employee.APELLIDO}</h3>
                <p><strong>ID:</strong> {employee.ID_PERSONA}</p>
                <p><strong>Email:</strong> {employee.EMAIL || 'N/A'}</p>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
