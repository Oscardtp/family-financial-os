# Family Financial OS

Un sistema operativo financiero familiar para hogares colombianos.

## Propósito

Ayudar a una familia a administrar su economía real de manera simple, privada y rápida.

## Tecnología

- Frontend: HTML5, CSS3, JavaScript moderno
- Backend: Python, FastAPI
- Base de datos: SQLite
- Validación: Pydantic
- Testing: pytest
- Control de versiones: Git

## Requisitos previos

- Python 3.10 o superior
- pip (gestor de paquetes de Python)
- Git

## Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/<usuario>/family-financial-os.git
   cd family-financial-os
   ```

2. Crea un entorno virtual:
   ```bash
   python -m venv venv
   ```

3. Activa el entorno virtual:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```

5. Configura variables de entorno (opcional):
   ```bash
   cp .env.example .env
   # Edita .env con tus configuraciones
   ```

## Ejecución

Inicia el servidor backend:
```bash
cd backend
python -m app.main
```

Abre el navegador en:
```
http://localhost:8000
```

## Testing

Ejecuta la suite de pruebas:
```bash
cd backend
python -m pytest tests/ -v
```

Para pruebas con coverage:
```bash
python -m pytest tests/ --cov=app --cov-report=term-missing
```

## Estructura del proyecto

```
family-financial-os/
├── backend/
│   ├── app/
│   │   ├── api/           # Endpoints FastAPI
│   │   ├── application/   # Casos de uso
│   │   ├── domain/        # Entidades y modelos
│   │   ├── infrastructure/# Repositorios y DB
│   │   └── main.py        # Punto de entrada
│   └── tests/             # Pruebas automatizadas
├── frontend/
│   ├── assets/
│   │   ├── css/           # Estilos
│   │   └── js/            # Módulos JavaScript
│   └── index.html         # Página principal
└── README.md
```

## Características

- Dashboard financiero con resumen del mes
- Gestión de cuentas (bancarias, digitales, efectivo)
- Registro rápido de gastos
- Control de presupuestos por categoría
- Seguimiento de deudas
- Metas de ahorro
- Pagos recurrentes
- Reportes y análisis
- Exportación de datos (JSON, CSV)

## API

La API sigue el formato:
```json
{
  "success": true,
  "data": {},
  "meta": {},
  "error": {}
}
```

Base URL: `/api/v1`

## Contribución

1. Crea una rama para tu feature:
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```

2. Realiza tus cambios y commit:
   ```bash
   git add .
   git commit -m "feat: descripción del cambio"
   ```

3. Push a la rama:
   ```bash
   git push origin feature/nueva-funcionalidad
   ```

4. Abre un Pull Request

## Licencia

MIT
