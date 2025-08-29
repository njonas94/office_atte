import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ComplianceChecker.css';
import EmployeeSearch from './EmployeeSearch';
import ComplianceCharts from './ComplianceCharts';

const ComplianceChecker = () => {
  const [employees, setEmployees] = useState([]);
  const [selectedEmployees, setSelectedEmployees] = useState([]);
  const [period, setPeriod] = useState(1);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [complianceResults, setComplianceResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [rules, setRules] = useState([]);
  const [periods, setPeriods] = useState([]);

  const API_BASE_URL = process.env.NODE_ENV === 'production' ? 'http://localhost:8000' : '';

  useEffect(() => {
    fetchEmployees();
    fetchRules();
    fetchPeriods();
  }, []);

  const fetchEmployees = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/employees`);
      setEmployees(response.data);
    } catch (err) {
      console.error('Error fetching employees:', err);
      setError('Error al cargar empleados');
    }
  };

  const fetchRules = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/compliance/rules`);
      setRules(response.data.rules);
    } catch (err) {
      console.error('Error fetching rules:', err);
    }
  };

  const fetchPeriods = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/compliance/periods`);
      setPeriods(response.data.available_periods);
    } catch (err) {
      console.error('Error fetching periods:', err);
    }
  };

  const handleEmployeeSelection = (employeeId) => {
    setSelectedEmployees(prev => 
      prev.includes(employeeId)
        ? prev.filter(id => id !== employeeId)
        : [...prev, employeeId]
    );
  };

  const handleSelectAll = (employeeIds) => {
    setSelectedEmployees(employeeIds);
  };

  const handleClearAll = () => {
    setSelectedEmployees([]);
  };

  const getPeriodDescription = () => {
    if (startDate && endDate) {
      return `Personalizado: ${startDate} a ${endDate}`;
    }
    const periodObj = periods.find(p => p.months === period);
    return periodObj ? periodObj.name : 'Período no especificado';
  };

  const handlePeriodChange = (newPeriod) => {
    setPeriod(newPeriod);
    // Limpiar fechas personalizadas
    setStartDate('');
    setEndDate('');
  };

  const checkCompliance = async () => {
    if (selectedEmployees.length === 0) {
      setError('Debe seleccionar al menos un empleado');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      let response;
      
      if (selectedEmployees.length === 1) {
        // Verificar un solo empleado
        const params = new URLSearchParams();
        if (startDate && endDate) {
          params.append('start_date', startDate);
          params.append('end_date', endDate);
        } else {
          params.append('months', period);
        }
        
        response = await axios.get(
          `${API_BASE_URL}/api/compliance/employee/${selectedEmployees[0]}?${params}`
        );
        
        setComplianceResults([response.data]);
      } else {
        // Verificar múltiples empleados
        const params = new URLSearchParams();
        if (startDate && endDate) {
          params.append('start_date', startDate);
          params.append('end_date', endDate);
        } else {
          params.append('months', period);
        }
        
        response = await axios.post(
          `${API_BASE_URL}/api/compliance/multiple-employees?${params}`,
          selectedEmployees
        );
        
        setComplianceResults(response.data.results);
      }
    } catch (err) {
      console.error('Error checking compliance:', err);
      setError('Error al verificar cumplimiento: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const getEmployeeName = (employeeId) => {
    const employee = employees.find(emp => emp.ID_PERSONA === employeeId);
    return employee ? `${employee.NOMBRE} ${employee.APELLIDO}` : `Empleado ${employeeId}`;
  };

  return (
    <div className="compliance-checker">
      <h2>Verificador de Cumplimiento de Asistencia</h2>
      
      {/* Reglas de cumplimiento */}
      <div className="rules-section">
        <h3>Reglas de Cumplimiento</h3>
        <div className="rules-grid">
          {rules.map(rule => (
            <div key={rule.rule_id} className="rule-card">
              <h4>{rule.name}</h4>
              <p>{rule.description}</p>
              <strong>Requisito: {rule.requirement}</strong>
            </div>
          ))}
        </div>
      </div>

      {/* Selección de empleados con búsqueda */}
      <EmployeeSearch
        employees={employees}
        selectedEmployees={selectedEmployees}
        onEmployeeSelection={handleEmployeeSelection}
        onSelectAll={handleSelectAll}
        onClearAll={handleClearAll}
      />

      {/* Período de consulta */}
      <div className="period-selection">
        <h3>Período de Consulta</h3>
        
        <div className="period-options">
          <h4>Períodos Predefinidos:</h4>
          <div className="period-buttons">
            {periods.map(p => (
              <button
                key={p.months}
                className={period === p.months ? 'active' : ''}
                onClick={() => handlePeriodChange(p.months)}
              >
                {p.name}
              </button>
            ))}
          </div>
        </div>

        <div className="custom-period">
          <h4>Período Personalizado:</h4>
          <div className="date-inputs">
            <div>
              <label>Fecha de inicio:</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>
            <div>
              <label>Fecha de fin:</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Botón de verificación */}
      <div className="check-button">
        <button 
          onClick={checkCompliance}
          disabled={loading || selectedEmployees.length === 0}
          className="primary-button"
        >
          {loading ? 'Verificando...' : 'Verificar Cumplimiento'}
        </button>
      </div>

      {/* Resultados */}
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {complianceResults && (
        <div className="compliance-results">
          <h3>Resultados de Cumplimiento</h3>
          
          {/* Gráficas de cumplimiento */}
          <ComplianceCharts 
            complianceResults={complianceResults}
            period={getPeriodDescription()}
          />
          
          {/* Resultados detallados por empleado */}
          <div className="detailed-results">
            <h4>Resultados Detallados por Empleado</h4>
            {complianceResults.map((result, index) => (
              <div key={index} className={`result-card ${result.compliance ? 'compliant' : 'non-compliant'}`}>
                <h5>{getEmployeeName(result.employee_id)}</h5>
                <p><strong>Período:</strong> {result.period}</p>
                <p><strong>Estado:</strong> 
                  <span className={result.compliance ? 'status-compliant' : 'status-non-compliant'}>
                    {result.compliance ? 'CUMPLE' : 'NO CUMPLE'}
                  </span>
                </p>
                {result.reason && (
                  <p><strong>Razón:</strong> {result.reason}</p>
                )}
                
                {result.details && (
                  <div className="details-section">
                    <h6>Detalles por Regla:</h6>
                    <div className="rule-details">
                      <div className="rule-detail">
                        <strong>Regla 1 - Mínimo de días:</strong>
                        <span className={result.details.rule_1_minimum_days?.compliant ? 'compliant' : 'non-compliant'}>
                          {result.details.rule_1_minimum_days?.compliant ? '✓' : '✗'}
                        </span>
                        <p>{result.details.rule_1_minimum_days?.reason || 'Sin información'}</p>
                      </div>
                      
                      <div className="rule-detail">
                        <strong>Regla 2 - Distribución semanal:</strong>
                        <span className={result.details.rule_2_weekly_distribution?.compliant ? 'compliant' : 'non-compliant'}>
                          {result.details.rule_2_weekly_distribution?.compliant ? '✓' : '✗'}
                        </span>
                        <p>{result.details.rule_2_weekly_distribution?.reason || 'Sin información'}</p>
                      </div>
                      
                      <div className="rule-detail">
                        <strong>Regla 3 - Horas mínimas:</strong>
                        <span className={result.details.rule_3_minimum_hours?.compliant ? 'compliant' : 'non-compliant'}>
                          {result.details.rule_3_minimum_hours?.compliant ? '✓' : '✗'}
                        </span>
                        <p>{result.details.rule_3_minimum_hours?.reason || 'Sin información'}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ComplianceChecker;
