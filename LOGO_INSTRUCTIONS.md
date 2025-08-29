# 🎨 Instrucciones para Personalizar el Logo

## 📁 Ubicación de Archivos

El logo debe colocarse en la siguiente ubicación:
```
frontend/public/
```

## 🖼️ Formatos Soportados

- **PNG** (recomendado para transparencia)
- **SVG** (mejor calidad, escalable)
- **JPG/JPEG** (solo si no hay transparencia)

## 📝 Archivos a Crear/Reemplazar

### 1. Logo Principal
- **Archivo:** `logo.png` o `logo.svg`
- **Tamaño recomendado:** 60x60px (mínimo) a 120x120px (máximo)
- **Ubicación:** `frontend/public/logo.png`

### 2. Favicon
- **Archivo:** `favicon.ico`
- **Tamaño:** 16x16px, 32x32px, 48x48px
- **Ubicación:** `frontend/public/favicon.ico`

### 3. Logo para Apple Touch
- **Archivo:** `logo192.png`
- **Tamaño:** 192x192px
- **Ubicación:** `frontend/public/logo192.png`

## 🔧 Pasos para Implementar

### Paso 1: Preparar los archivos
1. Crear el logo en los tamaños especificados
2. Guardar en formato PNG o SVG
3. Colocar en `frontend/public/`

### Paso 2: Actualizar el componente Header
Editar `frontend/src/components/Header.js`:

```javascript
// Reemplazar el placeholder actual:
<div className="logo-placeholder">
  <span className="logo-text">LOGO</span>
</div>

// Por:
<img 
  src="/logo.png" 
  alt="Logo de la Empresa" 
  className="company-logo"
/>
```

### Paso 3: Actualizar estilos
Editar `frontend/src/components/Header.css`:

```css
/* Reemplazar .logo-placeholder por: */
.company-logo {
  width: 60px;
  height: 60px;
  object-fit: contain;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.1);
  padding: 8px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
}
```

### Paso 4: Personalizar información de la empresa
Editar `frontend/src/components/Header.js`:

```javascript
// Cambiar:
<h1 className="company-name">Nombre de la Empresa</h1>
<p className="system-title">Sistema de Control de Asistencia</p>

// Por el nombre real de la empresa:
<h1 className="company-name">TU EMPRESA S.A.</h1>
<p className="system-title">Sistema de Control de Asistencia</p>
```

## 🎯 Personalización Adicional

### Colores de la empresa
Para cambiar los colores del gradiente, editar `frontend/src/components/Header.css`:

```css
.app-header {
  /* Cambiar el gradiente por los colores de tu empresa */
  background: linear-gradient(135deg, #TU_COLOR_1 0%, #TU_COLOR_2 100%);
}
```

### Título de la página
Editar `frontend/public/index.html`:

```html
<title>TU EMPRESA - Sistema de Asistencia</title>
```

## 🚀 Después de los Cambios

1. Reconstruir el frontend:
```bash
docker-compose stop frontend
docker-compose up --build -d frontend
```

2. Verificar que el logo se muestre correctamente en `http://localhost:3000`

## 💡 Consejos

- **Mantén el logo simple** para que se vea bien en tamaños pequeños
- **Usa colores que contrasten** con el fondo del header
- **Prueba en diferentes dispositivos** para asegurar que se vea bien
- **Optimiza las imágenes** para reducir el tiempo de carga

## 🆘 Si tienes problemas

1. Verifica que los archivos estén en la ubicación correcta
2. Asegúrate de que los nombres de archivo coincidan
3. Revisa la consola del navegador para errores
4. Verifica que el formato de imagen sea compatible
