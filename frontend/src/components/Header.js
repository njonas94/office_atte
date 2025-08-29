import React from 'react';
import './Header.css';

const Header = () => {
  return (
    <header className="app-header">
      <div className="header-content">
        <div className="logo-section">
          <div className="logo-container">
            <img 
              src="/logo.svg" 
              alt="Logo Cabal" 
              className="company-logo"
            />
          </div>
          <div className="company-info">
            <h1 className="company-name">CABAL</h1>
            <p className="system-title">Sistema de Control de Asistencia</p>
          </div>
        </div>
        <div className="header-actions">
          <div className="user-info">
            <span className="user-name">Usuario</span>
            <span className="user-role">Administrador</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
