# Project Structure

> Project is in early setup. Update this file as directories and modules are created.

## Expected Layout

```
sistema-incidencias/
├── .kiro/                  # Kiro IDE configuration (steering, hooks, specs)
│   └── steering/
├── venv/                   # Python virtual environment (not committed)
├── requirements.txt        # Python dependencies
├── manage.py               # Entry point (if Django)
└── <app_modules>/          # Application source code (TBD)
```

## Conventions (to follow as project grows)
- Keep business logic out of views/controllers; use service or use-case layers
- Name modules and files in **snake_case** (Python convention)
- Group code by feature/domain (e.g., `incidencias/`, `usuarios/`, `reportes/`) rather than by technical layer
- Store configuration in environment variables, not hardcoded in source
- Do not commit `venv/`, `.env`, or secrets

## Domain Modules (anticipated)
| Module | Responsibility |
|---|---|
| `incidencias` | Core incident CRUD, status transitions |
| `usuarios` | User management and roles |
| `reportes` | Reporting and statistics |
| `notificaciones` | Alerts and notifications |
