import React from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';
import './ComplianceCharts.css';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

const ComplianceCharts = ({ complianceResults, period }) => {
  if (!complianceResults || complianceResults.length === 0) {
    return null;
  }

  // Preparar datos para las gráficas
  const totalEmployees = complianceResults.length;
  const compliantEmployees = complianceResults.filter(r => r.compliance).length;
  const nonCompliantEmployees = totalEmployees - compliantEmployees;

  // Datos para gráfica de pastel
  const pieData = {
    labels: ['Cumple', 'No Cumple'],
    datasets: [
      {
        data: [compliantEmployees, nonCompliantEmployees],
        backgroundColor: [
          'rgba(39, 174, 96, 0.8)',
          'rgba(231, 76, 60, 0.8)'
        ],
        borderColor: [
          'rgba(39, 174, 96, 1)',
          'rgba(231, 76, 60, 1)'
        ],
        borderWidth: 2,
      },
    ],
  };

  // Datos para gráfica de barras por regla
  const ruleComplianceData = {
    labels: ['Regla 1: Mínimo días', 'Regla 2: Distribución semanal', 'Regla 3: Horas mínimas'],
    datasets: [
      {
        label: 'Empleados que cumplen',
        data: [
          complianceResults.filter(r => r.details?.rule_1_minimum_days?.compliant).length,
          complianceResults.filter(r => r.details?.rule_2_weekly_distribution?.compliant).length,
          complianceResults.filter(r => r.details?.rule_3_minimum_hours?.compliant).length,
        ],
        backgroundColor: 'rgba(39, 174, 96, 0.8)',
        borderColor: 'rgba(39, 174, 96, 1)',
        borderWidth: 1,
      },
      {
        label: 'Empleados que no cumplen',
        data: [
          complianceResults.filter(r => !r.details?.rule_1_minimum_days?.compliant).length,
          complianceResults.filter(r => !r.details?.rule_2_weekly_distribution?.compliant).length,
          complianceResults.filter(r => !r.details?.rule_3_minimum_hours?.compliant).length,
        ],
        backgroundColor: 'rgba(231, 76, 60, 0.8)',
        borderColor: 'rgba(231, 76, 60, 1)',
        borderWidth: 1,
      },
    ],
  };

  // Configuración de opciones para gráfica de barras
  const barOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Cumplimiento por Regla',
        font: {
          size: 16,
          weight: 'bold'
        }
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: totalEmployees,
        ticks: {
          stepSize: 1
        }
      },
    },
  };

  // Configuración de opciones para gráfica de pastel
  const pieOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom',
      },
      title: {
        display: true,
        text: 'Resumen General de Cumplimiento',
        font: {
          size: 16,
          weight: 'bold'
        }
      },
    },
  };

  // Calcular estadísticas adicionales
  const complianceRate = totalEmployees > 0 ? ((compliantEmployees / totalEmployees) * 100).toFixed(1) : 0;
  
  // Análisis por regla
  const rule1Stats = {
    compliant: complianceResults.filter(r => r.details?.rule_1_minimum_days?.compliant).length,
    total: totalEmployees,
    percentage: totalEmployees > 0 ? ((complianceResults.filter(r => r.details?.rule_1_minimum_days?.compliant).length / totalEmployees) * 100).toFixed(1) : 0
  };

  const rule2Stats = {
    compliant: complianceResults.filter(r => r.details?.rule_2_weekly_distribution?.compliant).length,
    total: totalEmployees,
    percentage: totalEmployees > 0 ? ((complianceResults.filter(r => r.details?.rule_2_weekly_distribution?.compliant).length / totalEmployees) * 100).toFixed(1) : 0
  };

  const rule3Stats = {
    compliant: complianceResults.filter(r => r.details?.rule_3_minimum_hours?.compliant).length,
    total: totalEmployees,
    percentage: totalEmployees > 0 ? ((complianceResults.filter(r => r.details?.rule_3_minimum_hours?.compliant).length / totalEmployees) * 100).toFixed(1) : 0
  };

  return (
    <div className="compliance-charts">
      <h3>Análisis Gráfico de Cumplimiento</h3>
      
      {/* Estadísticas resumidas */}
      <div className="stats-summary">
        <div className="stat-card">
          <div className="stat-number">{complianceRate}%</div>
          <div className="stat-label">Tasa de Cumplimiento</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{compliantEmployees}</div>
          <div className="stat-label">Empleados que Cumplen</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{nonCompliantEmployees}</div>
          <div className="stat-label">Empleados que No Cumplen</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{totalEmployees}</div>
          <div className="stat-label">Total de Empleados</div>
        </div>
      </div>

      {/* Gráficas */}
      <div className="charts-container">
        <div className="chart-section">
          <div className="chart-wrapper">
            <Pie data={pieData} options={pieOptions} />
          </div>
        </div>
        
        <div className="chart-section">
          <div className="chart-wrapper">
            <Bar data={ruleComplianceData} options={barOptions} />
          </div>
        </div>
      </div>

      {/* Análisis detallado por regla */}
      <div className="rule-analysis">
        <h4>Análisis Detallado por Regla</h4>
        <div className="rule-stats-grid">
          <div className="rule-stat-card">
            <h5>Regla 1: Mínimo de Días</h5>
            <div className="rule-stat-numbers">
              <span className="compliant-count">{rule1Stats.compliant}</span>
              <span className="separator">/</span>
              <span className="total-count">{rule1Stats.total}</span>
            </div>
            <div className="rule-stat-percentage">{rule1Stats.percentage}%</div>
            <div className="rule-stat-label">empleados cumplen</div>
          </div>

          <div className="rule-stat-card">
            <h5>Regla 2: Distribución Semanal</h5>
            <div className="rule-stat-numbers">
              <span className="compliant-count">{rule2Stats.compliant}</span>
              <span className="separator">/</span>
              <span className="total-count">{rule2Stats.total}</span>
            </div>
            <div className="rule-stat-percentage">{rule2Stats.percentage}%</div>
            <div className="rule-stat-label">empleados cumplen</div>
          </div>

          <div className="rule-stat-card">
            <h5>Regla 3: Horas Mínimas</h5>
            <div className="rule-stat-numbers">
              <span className="compliant-count">{rule3Stats.compliant}</span>
              <span className="separator">/</span>
              <span className="total-count">{rule3Stats.total}</span>
            </div>
            <div className="rule-stat-percentage">{rule3Stats.percentage}%</div>
            <div className="rule-stat-label">empleados cumplen</div>
          </div>
        </div>
      </div>

      {/* Información del período */}
      <div className="period-info">
        <p><strong>Período analizado:</strong> {period}</p>
        <p><strong>Fecha de análisis:</strong> {new Date().toLocaleDateString('es-ES')}</p>
      </div>
    </div>
  );
};

export default ComplianceCharts;
