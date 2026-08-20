SISTEMA-INCIDENCIAS/
│
├── .kiro/
│
├── alembic/
│   ├── versions/
│   ├── env.py
│   ├── README
│   └── script.py.mako
│
├── fastapi_app/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── repositories/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   ├── __init__.py
│   └── main.py
│
├── tests/
│   ├── integration/
│   ├── properties/
│   ├── unit/
│   ├── __init__.py
│   └── conftest.py
│
├── venv/
│
├── .env.example
├── alembic.ini
├── pyproject.toml
└── requirements.txt
----------------------------------------------------------------------------------------------
Carpeta	                                           Función
fastapi_app/core	              Configuración, seguridad y componentes centrales
fastapi_app/db	                Conexión y configuración de BD
fastapi_app/models	            Modelos de base de datos
fastapi_app/repositories	      Acceso a datos
fastapi_app/routers	            Endpoints/API
fastapi_app/schemas	            Validación de datos
fastapi_app/services	          Lógica de negocio
tests/unit	                    Pruebas unitarias
tests/integration	              Pruebas de integración
tests/properties	              Pruebas basadas en propiedades
alembic	                        Migraciones de PostgreSQL

