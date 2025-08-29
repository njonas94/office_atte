import React, { useState, useEffect } from 'react';
import './EmployeeSearch.css';

const EmployeeSearch = ({ employees, selectedEmployees, onEmployeeSelection, onSelectAll, onClearAll }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredEmployees, setFilteredEmployees] = useState([]);
  const [showSelectedOnly, setShowSelectedOnly] = useState(false);

  useEffect(() => {
    filterEmployees();
  }, [searchTerm, employees, showSelectedOnly]);

  const filterEmployees = () => {
    let filtered = employees;
    
    // Filtrar por término de búsqueda
    if (searchTerm) {
      filtered = filtered.filter(employee => 
        employee.NOMBRE.toLowerCase().includes(searchTerm.toLowerCase()) ||
        employee.APELLIDO.toLowerCase().includes(searchTerm.toLowerCase()) ||
        employee.ID_PERSONA.toString().includes(searchTerm)
      );
    }
    
    // Mostrar solo seleccionados si está activado
    if (showSelectedOnly) {
      filtered = filtered.filter(employee => 
        selectedEmployees.includes(employee.ID_PERSONA)
      );
    }
    
    setFilteredEmployees(filtered);
  };

  const handleSelectAll = () => {
    const allIds = filteredEmployees.map(emp => emp.ID_PERSONA);
    onSelectAll(allIds);
  };

  const handleClearAll = () => {
    onClearAll();
  };

  const getSelectedCount = () => {
    return selectedEmployees.length;
  };

  const getTotalCount = () => {
    return employees.length;
  };

  return (
    <div className="employee-search">
      <div className="search-header">
        <h3>Selección de Empleados</h3>
        <div className="search-stats">
          <span className="selected-count">{getSelectedCount()}</span>
          <span className="separator">/</span>
          <span className="total-count">{getTotalCount()}</span>
          <span className="label">empleados seleccionados</span>
        </div>
      </div>

      <div className="search-controls">
        <div className="search-input-group">
          <input
            type="text"
            placeholder="Buscar por nombre, apellido o ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <button
            className={`filter-button ${showSelectedOnly ? 'active' : ''}`}
            onClick={() => setShowSelectedOnly(!showSelectedOnly)}
            title={showSelectedOnly ? 'Mostrar todos' : 'Mostrar solo seleccionados'}
          >
            {showSelectedOnly ? '👁️ Todos' : '👁️ Seleccionados'}
          </button>
        </div>

        <div className="bulk-actions">
          <button
            className="bulk-button select-all"
            onClick={handleSelectAll}
            disabled={filteredEmployees.length === 0}
          >
            Seleccionar Todos
          </button>
          <button
            className="bulk-button clear-all"
            onClick={handleClearAll}
            disabled={selectedEmployees.length === 0}
          >
            Limpiar Selección
          </button>
        </div>
      </div>

      <div className="employees-container">
        {filteredEmployees.length === 0 ? (
          <div className="no-results">
            {searchTerm ? 
              `No se encontraron empleados que coincidan con "${searchTerm}"` :
              'No hay empleados disponibles'
            }
          </div>
        ) : (
          <div className="employees-list">
            {filteredEmployees.map(employee => (
              <div 
                key={employee.ID_PERSONA} 
                className={`employee-row ${selectedEmployees.includes(employee.ID_PERSONA) ? 'selected' : ''}`}
                onClick={() => onEmployeeSelection(employee.ID_PERSONA)}
              >
                <div className="employee-selector">
                  <div className={`selection-circle ${selectedEmployees.includes(employee.ID_PERSONA) ? 'selected' : ''}`}>
                    {selectedEmployees.includes(employee.ID_PERSONA) && <span className="checkmark">✓</span>}
                  </div>
                </div>
                <div className="employee-info">
                  <div className="employee-name">
                    {employee.NOMBRE} {employee.APELLIDO}
                  </div>
                  <div className="employee-details">
                    <span className="employee-id">ID: {employee.ID_PERSONA}</span>
                    {employee.EMAIL && <span className="employee-email">{employee.EMAIL}</span>}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {filteredEmployees.length > 0 && (
        <div className="results-info">
          Mostrando {filteredEmployees.length} de {employees.length} empleados
          {searchTerm && ` que coinciden con "${searchTerm}"`}
        </div>
      )}
    </div>
  );
};

export default EmployeeSearch;
