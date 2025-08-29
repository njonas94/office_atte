import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import Header from './components/Header';
import ComplianceChecker from './components/ComplianceChecker';

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
      <Header />
      
      <main className="main">
        <section className="welcome-section">
          <h2>Bienvenido al Sistema de Verificación de Cumplimiento</h2>
          <p>Selecciona empleados y verifica su cumplimiento con las reglas de asistencia a la oficina</p>
        </section>

        {/* Componente de verificación de cumplimiento */}
        <ComplianceChecker />
      </main>
    </div>
  );
}

export default App;
