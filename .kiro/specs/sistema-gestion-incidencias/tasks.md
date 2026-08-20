# Implementation Plan: Sistema de Gestión de Incidencias (SGI)

## Overview

Plan de implementación incremental para el SGI. El backend se construye con FastAPI + Python sobre PostgreSQL; el frontend con React + TypeScript. Las tareas se ordenan de infraestructura base a funcionalidades avanzadas, garantizando que cada paso compile e integre con los anteriores antes de continuar. Los property-based tests con Hypothesis se colocan junto a las implementaciones que validan, permitiendo capturar errores temprano.

---

## Tasks

- [ ] 1. Configuración del proyecto y estructura base
  - [ ] 1.1 Inicializar estructura de directorios del backend FastAPI
    - Crear `fastapi_app/` con subdirectorios: `core/`, `db/`, `models/`, `schemas/`, `repositories/`, `services/`, `routers/`
    - Crear `__init__.py` en cada subdirectorio
    - Crear `fastapi_app/main.py` con instancia mínima de FastAPI (sin rutas aún)
    - Crear `requirements.txt` con dependencias: `fastapi`, `uvicorn[standard]`, `sqlalchemy`, `psycopg2-binary`, `pydantic-settings`, `python-jose[cryptography]`, `passlib[bcrypt]`, `alembic`, `hypothesis`, `pytest`, `pytest-asyncio`, `httpx`
    - _Requirements: todos (base de proyecto)_

  - [ ] 1.2 Configurar settings y variables de entorno
    - Implementar `fastapi_app/core/config.py` con `Settings` usando `pydantic-settings`
    - Campos mínimos: `DATABASE_URL`, `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES=60`, `ALGORITHM="HS256"`
    - Crear `.env.example` con todas las variables requeridas (sin valores reales)
    - _Requirements: 1.3, 1.6_

  - [ ] 1.3 Configurar SQLAlchemy y Alembic
    - Implementar `fastapi_app/db/base.py` con `DeclarativeBase`
    - Implementar `fastapi_app/db/session.py` con engine, `SessionLocal` y dependencia `get_db`
    - Inicializar Alembic (`alembic init alembic/`) y configurar `alembic.ini` y `alembic/env.py` para apuntar a `DATABASE_URL` del settings
    - _Requirements: todos (base de datos)_

  - [ ] 1.4 Configurar infraestructura de tests
    - Crear `tests/conftest.py` con fixtures: `db_session` (SQLite in-memory), `client` (`httpx.AsyncClient` + `TestClient`), factories de usuarios y categorías
    - Crear `tests/unit/`, `tests/properties/`, `tests/integration/` con `__init__.py`
    - Crear `pyproject.toml` con sección `[tool.pytest.ini_options]` y perfiles de Hypothesis (`ci`: 200 ejemplos, `dev`: 50)
    - _Requirements: todos (infraestructura de testing)_

- [ ] 2. Enumeraciones, modelos ORM y migraciones
  - [ ] 2.1 Definir enumeraciones de dominio
    - Implementar `fastapi_app/models/enums.py` con `RolEnum`, `EstadoEnum`, `PrioridadEnum`, `TipoAccionEnum` (usando `str, Enum`)
    - _Requirements: 1.1, 2.1, 5.1, 7.1_

  - [ ] 2.2 Implementar modelos ORM SQLAlchemy
    - Implementar `fastapi_app/models/usuario.py`: campos `id (UUID PK)`, `nombre`, `email (unique)`, `password_hash`, `rol`, `is_active`, `temp_password_hash`, `temp_password_expires_at`, `failed_login_attempts`, `locked_until`, `created_at`, `updated_at`
    - Implementar `fastapi_app/models/categoria.py`: campos `id`, `nombre (unique)`, `is_active`, `created_at`
    - Implementar `fastapi_app/models/incidencia.py`: campos `id`, `titulo`, `descripcion`, `estado`, `prioridad`, `categoria_id (FK)`, `creado_por (FK)`, `asignado_a (FK nullable)`, `fecha_creacion`, `fecha_resolucion`, `fecha_cierre`, `updated_at`
    - Implementar `fastapi_app/models/comentario.py`: campos `id`, `incidencia_id (FK)`, `autor_id (FK)`, `contenido`, `created_at`
    - Implementar `fastapi_app/models/historial.py`: campos `id`, `incidencia_id (FK)`, `actor_id (FK)`, `tipo_accion`, `valor_anterior`, `valor_nuevo`, `timestamp_utc (TIMESTAMP WITH TIME ZONE)`; sin `updated_at`
    - Actualizar `fastapi_app/db/base.py` para importar todos los modelos (necesario para Alembic)
    - _Requirements: 3.1, 5.4, 6.4, 7.1, 8.1, 9.2, 10.1, 11.1_

  - [ ] 2.3 Generar y aplicar migración inicial con Alembic
    - Ejecutar `alembic revision --autogenerate -m "initial schema"`
    - Verificar el script generado y ajustar tipo de columna `timestamp_utc` a `TIMESTAMP(3) WITH TIME ZONE`
    - _Requirements: todos (base de datos)_

- [ ] 3. Schemas Pydantic v2 y excepciones de dominio
  - [ ] 3.1 Implementar excepciones de dominio
    - Crear `fastapi_app/services/exceptions.py` con jerarquía: `SGIException`, `TransicionEstadoInvalidaError`, `RecursoNoEncontradoError`, `AccesoNoPermitidoError`, `ConflictoError`, `ValidacionError`
    - _Requirements: 5.2, 6.2, 6.3, 10.2, 11.2_

  - [ ] 3.2 Implementar schemas de autenticación y usuarios
    - Implementar `fastapi_app/schemas/auth.py`: `LoginRequest`, `TokenResponse`
    - Implementar `fastapi_app/schemas/usuario.py`: `UsuarioCreate`, `UsuarioResponse`, `UsuarioUpdate`, `RolUpdate`, `UsuarioResumen`
    - _Requirements: 1.1, 10.1, 10.5, 10.6, 10.7_

  - [ ] 3.3 Implementar schemas de incidencias, comentarios, historial e indicadores
    - Implementar `fastapi_app/schemas/incidencia.py`: `IncidenciaCreate` (validadores de longitud en título y descripción), `IncidenciaResponse`, `IncidenciaResumen`, `EstadoUpdate`, `PrioridadUpdate`, `AsignacionUpdate`, `IncidenciaFiltros`, `Page[T]`
    - Implementar `fastapi_app/schemas/comentario.py`: `ComentarioCreate` (validador 1–1000 chars), `ComentarioResponse`
    - Implementar `fastapi_app/schemas/historial.py`: `HistorialEntry`, `HistorialResponse`
    - Implementar `fastapi_app/schemas/categoria.py`: `CategoriaCreate` (validador 3–100 chars), `CategoriaResponse`
    - Implementar `fastapi_app/schemas/indicadores.py`: `IndicadoresResponse`
    - _Requirements: 3.2, 3.3, 3.4, 7.2, 8.2, 11.1_

- [ ] 4. Seguridad: hashing, JWT y dependencias de autenticación
  - [ ] 4.1 Implementar utilidades de seguridad
    - Implementar `fastapi_app/core/security.py`: `hash_password(plain) -> str`, `verify_password(plain, hashed) -> bool`, `create_access_token(data, expires_delta) -> str`, `decode_access_token(token) -> dict` (lanza `JWTError` si inválido/expirado)
    - Usar `passlib[bcrypt]` para hashing y `python-jose` para JWT
    - _Requirements: 1.1, 1.3, 1.6_

  - [ ]* 4.2 Escribir property test — Property 2: Hashing no reversible
    - **Property 2: Hashing de contraseñas no reversible**
    - Generar contraseñas arbitrarias con Hypothesis; verificar que `hash_password(p) != p` y `verify_password(p, hash_password(p)) == True`
    - **Validates: Requirements 1.6**

  - [ ] 4.3 Implementar dependencias FastAPI de autenticación y RBAC
    - Implementar `fastapi_app/core/dependencies.py`: `get_current_user(token, db) -> Usuario` (decodifica JWT, carga usuario de DB, verifica `is_active`), `require_role(*roles) -> Callable` (factory de Depends que retorna 403 si el rol no coincide)
    - _Requirements: 1.4, 1.5, 2.2, 2.3, 2.4, 2.5, 2.6, 10.3_

  - [ ]* 4.4 Escribir property test — Property 3: Token inválido → 401
    - **Property 3: Token inválido → 401 en cualquier endpoint protegido**
    - Generar strings arbitrarios que no sean JWTs válidos; verificar HTTP 401 sin lógica de negocio ejecutada
    - **Validates: Requirements 1.4, 2.8**

  - [ ]* 4.5 Escribir property test — Property 4: RBAC universal
    - **Property 4: Aplicación universal de RBAC**
    - Para pares (rol, endpoint) donde el rol no tiene permiso, verificar HTTP 403 con token válido
    - **Validates: Requirements 2.2, 2.3, 2.4, 2.5, 2.6**

- [ ] 5. Repositorios de acceso a datos
  - [ ] 5.1 Implementar repositorios de usuario y categoría
    - Implementar `fastapi_app/repositories/usuario_repo.py`: `get_by_id`, `get_by_email`, `create`, `update`, `list_all`, `deactivate`
    - Implementar `fastapi_app/repositories/categoria_repo.py`: `get_by_id`, `get_by_nombre`, `create`, `list_activas`, `list_todas`, `deactivate`
    - _Requirements: 10.1, 10.2, 11.1, 11.2, 11.5_

  - [ ] 5.2 Implementar repositorios de incidencia, comentario e historial
    - Implementar `fastapi_app/repositories/incidencia_repo.py`: `create`, `get_by_id`, `list_by_filters(actor, filtros, paginacion)` con lógica de aislamiento por rol, `update`
    - Implementar `fastapi_app/repositories/comentario_repo.py`: `create`, `list_by_incidencia` (ordenados por `created_at ASC`)
    - Implementar `fastapi_app/repositories/historial_repo.py`: `create`, `list_by_incidencia` (ordenados por `timestamp_utc ASC`)
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 8.1, 8.6, 9.2, 9.3, 9.4_

- [ ] 6. Servicio de autenticación
  - [ ] 6.1 Implementar `auth_service`
    - Implementar `fastapi_app/services/auth_service.py`: `login(db, email, password) -> TokenResponse`
    - Lógica: verificar `is_active`, verificar `locked_until`, llamar `verify_password`, incrementar `failed_login_attempts` en fallo (bloquear a los 5 con `locked_until = now + 15min`), resetear contador en éxito, emitir JWT
    - Todos los errores de credenciales inválidas deben retornar el mismo mensaje genérico (no revelar campo fallido)
    - _Requirements: 1.1, 1.2, 1.6, 1.7, 1.8, 10.3, 10.4_

  - [ ]* 6.2 Escribir property test — Property 1: Invarianza del mensaje de error de autenticación
    - **Property 1: Invarianza del mensaje de error de autenticación**
    - Generar combinaciones de (email_incorrecto, password_correcta), (email_correcto, password_incorrecta), (email_no_registrado, cualquier_password); verificar que el body de respuesta 401 sea idéntico en todos los casos
    - **Validates: Requirements 1.2, 1.8**

  - [ ]* 6.3 Escribir property test — Property 22: Usuario desactivado no puede autenticar
    - **Property 22: Usuario desactivado no puede autenticar**
    - Para usuarios con `is_active = False`, verificar HTTP 403 incluso con credenciales correctas
    - **Validates: Requirements 10.3, 10.4**

- [ ] 7. Router de autenticación
  - [ ] 7.1 Implementar `routers/auth.py`
    - `POST /api/v1/auth/login` → invocar `auth_service.login`, mapear excepciones a HTTP
    - Registrar manejadores de excepción globales en `main.py` para toda la jerarquía `SGIException` y `JWTError`
    - _Requirements: 1.1, 1.2, 1.4, 1.7_

- [ ] 8. Gestión de usuarios (servicio + router)
  - [ ] 8.1 Implementar `usuario_service`
    - Implementar `fastapi_app/services/usuario_service.py`: `crear_usuario`, `listar_usuarios`, `obtener_usuario`, `actualizar_usuario`, `cambiar_rol`, `desactivar_usuario`
    - `crear_usuario`: generar contraseña temporal aleatoria, hashearla, marcar `temp_password_expires_at = now + 24h`; lanzar `ConflictoError` si email duplicado
    - `cambiar_rol`: registrar entrada de historial (`CAMBIO_ROL`) con valores anterior/nuevo
    - _Requirements: 10.1, 10.2, 10.3, 10.5, 10.6, 10.7_

  - [ ]* 8.2 Escribir property test — Property 23: Unicidad de correo electrónico
    - **Property 23: Unicidad de correo electrónico (incluye duplicados)**
    - Generar emails válidos aleatorios; crear primer usuario exitosamente y verificar HTTP 409 al intentar crear segundo con el mismo email (también variaciones de capitalización si aplica)
    - **Validates: Requirements 10.2, 10.6**

  - [ ] 8.3 Implementar `routers/usuarios.py`
    - `POST /api/v1/usuarios` (ADMINISTRADOR), `GET /api/v1/usuarios` (ADMINISTRADOR), `GET /api/v1/usuarios/{id}` (ADMINISTRADOR), `PATCH /api/v1/usuarios/{id}` (ADMINISTRADOR), `PATCH /api/v1/usuarios/{id}/rol` (ADMINISTRADOR), `DELETE /api/v1/usuarios/{id}/desactivar` (ADMINISTRADOR)
    - Aplicar `require_role(RolEnum.ADMINISTRADOR)` en todos los endpoints
    - _Requirements: 2.6, 10.1–10.7_

- [ ] 9. Gestión de categorías (servicio + router)
  - [ ] 9.1 Implementar `categoria_service`
    - Implementar `fastapi_app/services/categoria_service.py`: `crear_categoria`, `listar_activas`, `listar_todas`, `desactivar_categoria`
    - `crear_categoria`: comparación case-insensitive del nombre; lanzar `ConflictoError` si ya existe
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

  - [ ]* 9.2 Escribir property test — Property 24: Unicidad de nombre de categoría (case-insensitive)
    - **Property 24: Unicidad de nombre de categoría (case-insensitive)**
    - Generar nombres de categoría con variaciones de capitalización; verificar HTTP 409 al intentar crear duplicado
    - **Validates: Requirements 11.2**

  - [ ] 9.3 Implementar `routers/categorias.py`
    - `POST /api/v1/categorias` (ADMINISTRADOR), `GET /api/v1/categorias` (Autenticado), `GET /api/v1/categorias/todas` (ADMINISTRADOR), `DELETE /api/v1/categorias/{id}/desactivar` (ADMINISTRADOR)
    - _Requirements: 2.6, 11.1–11.5_

  - [ ]* 9.4 Escribir property test — Property 25: Propagación de desactivación de categoría
    - **Property 25: Propagación de desactivación de categoría a nuevas incidencias**
    - Desactivar categoría; verificar HTTP 422 en nueva incidencia que la referencia; verificar que incidencias existentes siguen accesibles
    - **Validates: Requirements 11.3, 11.4**

  - [ ]* 9.5 Escribir property test — Property 26: Filtro de categorías activas en listado público
    - **Property 26: Filtro de categorías activas en listado público**
    - Crear mix de categorías activas/inactivas; verificar que `GET /categorias` retorna solo las activas
    - **Validates: Requirements 11.5**

- [ ] 10. Máquina de estados e historial (servicio)
  - [ ] 10.1 Implementar la máquina de estados de incidencias
    - Implementar `TRANSICIONES_VALIDAS` en `fastapi_app/services/incidencia_service.py`
    - Función `validar_transicion(estado_actual, estado_destino)` que lanza `TransicionEstadoInvalidaError` con `destinos_validos` si la transición no es válida
    - _Requirements: 5.1, 5.2_

  - [ ]* 10.2 Escribir property test — Property 10: Rechazo de transiciones inválidas
    - **Property 10: Rechazo de transiciones de estado inválidas**
    - Generar pares `(estado_actual, estado_destino)` fuera de `TRANSICIONES_VALIDAS`; verificar rechazo, estado sin modificar, mensaje con destinos válidos
    - **Validates: Requirements 5.1, 5.2**

  - [ ] 10.3 Implementar `historial_service`
    - Implementar `fastapi_app/services/historial_service.py`: `registrar_cambio(db, actor_id, incidencia_id, tipo, valor_anterior, valor_nuevo) -> None`
    - Omitir registro si `valor_anterior == valor_nuevo`
    - `timestamp_utc` generado con `datetime.utcnow()` en la capa de servicio (no DEFAULT de BD)
    - _Requirements: 9.1, 9.2, 9.3_

  - [ ]* 10.4 Escribir property test — Property 20: Omisión de historial cuando el valor no cambia
    - **Property 20: Omisión de registro de historial cuando el valor no cambia**
    - Intentar actualizar estado, prioridad o técnico al mismo valor actual; verificar que no se crea nueva entrada en historial
    - **Validates: Requirements 9.1**

- [ ] 11. Checkpoint — Base y autenticación funcionando
  - Asegurar que todos los tests del módulo de autenticación y seguridad pasen. Verificar que Alembic genera la migración correctamente. Consultar al usuario si surge alguna duda.

- [ ] 12. Servicio de incidencias — creación y consulta
  - [ ] 12.1 Implementar `crear_incidencia` y `obtener_incidencia`
    - Implementar en `fastapi_app/services/incidencia_service.py`: `crear_incidencia(db, actor, payload) -> Incidencia` con `estado=ABIERTA`, `prioridad=MEDIA`, validar `categoria_id` activa
    - Implementar `obtener_incidencia(db, actor, incidencia_id)` con verificación de acceso por rol (lanzar `AccesoNoPermitidoError` si no corresponde, `RecursoNoEncontradoError` si no existe)
    - _Requirements: 3.1, 3.2, 3.5, 3.6, 3.7, 4.6, 4.7_

  - [ ]* 12.2 Escribir property test — Property 5: Incidencia creada con valores por defecto correctos
    - **Property 5: Incidencia creada con valores por defecto correctos**
    - Generar combinaciones de `(titulo, descripcion, categoria_id_activa)`; verificar `estado=ABIERTA`, `prioridad=MEDIA`, `id` no nulo
    - **Validates: Requirements 3.1, 3.6**

  - [ ]* 12.3 Escribir property test — Property 6: Validación de longitud de campos
    - **Property 6: Validación de longitud de campos de incidencia**
    - Generar títulos fuera de [5, 200] y descripciones fuera de [10, 2000]; verificar HTTP 422 sin persistencia
    - **Validates: Requirements 3.2, 3.3, 3.4**

  - [ ] 12.4 Implementar `listar_incidencias`
    - Implementar `listar_incidencias(db, actor, filtros, paginacion) -> Page[Incidencia]`
    - Aislamiento de datos: USUARIO ve solo sus incidencias, TECNICO ve solo las asignadas, SUPERVISOR/ADMINISTRADOR ven todas
    - Aplicar filtros multidimensionales (estado, prioridad, categoria_id, rango de fechas) con AND lógico
    - Validar `page_size` en rango [10, 100]; lanzar `ValidacionError` fuera de rango
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [ ]* 12.5 Escribir property test — Property 7: Aislamiento de datos por rol
    - **Property 7: Aislamiento de datos por rol en consultas de incidencias**
    - Crear incidencias de distintos usuarios; verificar que USUARIO solo ve las suyas y TECNICO solo las asignadas
    - **Validates: Requirements 4.1, 4.2**

  - [ ]* 12.6 Escribir property test — Property 8: Corrección de filtros multidimensionales
    - **Property 8: Corrección de filtros multidimensionales**
    - Aplicar combinaciones de filtros simultáneos; verificar que cada ítem del resultado satisface todos los filtros
    - **Validates: Requirements 4.4**

  - [ ]* 12.7 Escribir property test — Property 9: Invariantes de paginación
    - **Property 9: Invariantes de paginación**
    - Generar `page_size` fuera de [10, 100]; verificar HTTP 422. Para llamadas válidas, verificar presencia de `total`, `page`, `page_size`, `pages` y `len(items) <= page_size`
    - **Validates: Requirements 4.5**

- [ ] 13. Servicio de incidencias — transiciones de estado
  - [ ] 13.1 Implementar `actualizar_estado`
    - Implementar `actualizar_estado(db, actor, incidencia_id, nuevo_estado)` en `incidencia_service`
    - Validar transición con `validar_transicion`; verificar permisos por rol (TECNICO solo sus asignadas)
    - Registrar en historial (`CAMBIO_ESTADO`); actualizar `fecha_resolucion` al pasar a `RESUELTA`, `fecha_cierre` al pasar a `CERRADA`
    - _Requirements: 5.1–5.7_

  - [ ]* 13.2 Escribir property test — Property 11: Registro de historial en transiciones válidas
    - **Property 11: Registro de historial en transiciones de estado válidas**
    - Para toda transición válida, verificar entrada de historial con `tipo_accion=CAMBIO_ESTADO`, valores anterior/nuevo correctos, `actor_id` y `timestamp_utc` no nulo
    - **Validates: Requirements 5.4, 5.5, 9.1, 9.2**

  - [ ]* 13.3 Escribir property test — Property 12: Registro de fecha_resolucion y fecha_cierre
    - **Property 12: Registro de fecha_resolucion y fecha_cierre al cambiar estado**
    - Mover incidencia a `RESUELTA`; verificar `fecha_resolucion` UTC no nulo. Mover a `CERRADA`; verificar `fecha_cierre` UTC no nulo
    - **Validates: Requirements 5.6, 5.7**

- [ ] 14. Servicio de incidencias — asignación y prioridad
  - [ ] 14.1 Implementar `asignar_tecnico`
    - Implementar `asignar_tecnico(db, actor, incidencia_id, tecnico_id)` en `incidencia_service`
    - Verificar que la incidencia esté en `ABIERTA` o `ASIGNADA`; verificar que el destinatario tenga rol `TECNICO` y `is_active=True`
    - Si `ABIERTA`: cambiar a `ASIGNADA`, registrar historial `ASIGNACION`. Si `ASIGNADA`: registrar historial `REASIGNACION` con técnico anterior y nuevo
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [ ]* 14.2 Escribir property test — Property 13: Invariante de asignación de técnico
    - **Property 13: Invariante de asignación de técnico**
    - Para incidencias en `ABIERTA` con técnico activo, verificar `asignado_a == tecnico.id` y `estado == ASIGNADA`. Para estados distintos a `ABIERTA`/`ASIGNADA`, verificar rechazo sin modificación
    - **Validates: Requirements 6.1, 6.3**

  - [ ]* 14.3 Escribir property test — Property 14: Completitud del historial de reasignación
    - **Property 14: Completitud del historial de reasignación**
    - Reasignar de técnico A a técnico B; verificar entrada `REASIGNACION` con `valor_anterior=str(A.id)`, `valor_nuevo=str(B.id)`, `actor_id` y timestamp no nulo
    - **Validates: Requirements 6.4**

  - [ ] 14.4 Implementar `actualizar_prioridad`
    - Implementar `actualizar_prioridad(db, actor, incidencia_id, nueva_prioridad)` en `incidencia_service`
    - Registrar historial `CAMBIO_PRIORIDAD` con valores anterior/nuevo
    - Lanzar `ValidacionError` si el valor no está en `PrioridadEnum` (Pydantic lo captura antes con 422)
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [ ]* 14.5 Escribir property test — Property 15: Validación de prioridad inválida
    - **Property 15: Validación de prioridad inválida**
    - Generar strings que no sean `{BAJA, MEDIA, ALTA, CRITICA}`; verificar HTTP 422 con listado de valores válidos sin modificar prioridad actual
    - **Validates: Requirements 7.2**

  - [ ]* 14.6 Escribir property test — Property 16: Registro de historial al cambiar prioridad
    - **Property 16: Registro de historial al cambiar prioridad**
    - Para cambios de prioridad válidos por supervisor, verificar entrada `CAMBIO_PRIORIDAD` con valores correctos, `actor_id` del supervisor y `timestamp_utc` no nulo
    - **Validates: Requirements 7.1, 9.1, 9.2**

- [ ] 15. Servicio de comentarios
  - [ ] 15.1 Implementar `comentario_service`
    - Implementar `fastapi_app/services/comentario_service.py`: `agregar_comentario(db, actor, incidencia_id, payload)`, `listar_comentarios(db, actor, incidencia_id)`
    - Aplicar reglas de acceso: USUARIO solo en sus incidencias y no en `CERRADA`/`CANCELADA`; TECNICO solo en las asignadas y no en `CERRADA`/`CANCELADA`; SUPERVISOR/ADMINISTRADOR no en `CERRADA`/`CANCELADA`
    - Orden cronológico ascendente en `listar_comentarios`
    - _Requirements: 8.1–8.6_

  - [ ]* 15.2 Escribir property test — Property 17: Invariante de comentario persistido
    - **Property 17: Invariante de comentario persistido**
    - Generar contenidos de 1–1000 chars; verificar `autor_id`, contenido exacto y `created_at` UTC no nulo
    - **Validates: Requirements 8.1**

  - [ ]* 15.3 Escribir property test — Property 18: Rechazo de comentarios fuera de límites
    - **Property 18: Rechazo de comentarios fuera de límites de longitud**
    - Generar contenidos con `len==0` y `len>1000`; verificar HTTP 422 sin persistencia
    - **Validates: Requirements 8.2**

  - [ ]* 15.4 Escribir property test — Property 19: Orden cronológico de comentarios
    - **Property 19: Orden cronológico de comentarios**
    - Crear N comentarios en orden conocido; verificar `items[i].created_at <= items[i+1].created_at` para todo i
    - **Validates: Requirements 8.6**

- [ ] 16. Servicio de historial e indicadores
  - [ ] 16.1 Implementar `historial_service` — consulta y acceso
    - Agregar a `historial_service.py`: `listar_historial(db, actor, incidencia_id)` con verificación de rol (`AccesoNoPermitidoError` para USUARIO/TECNICO, `RecursoNoEncontradoError` si incidencia no existe), orden cronológico ascendente
    - _Requirements: 9.4, 9.5, 9.6_

  - [ ]* 16.2 Escribir property test — Property 21: Orden cronológico del historial
    - **Property 21: Orden cronológico del historial**
    - Crear N eventos sobre una incidencia; verificar `items[i].timestamp_utc <= items[i+1].timestamp_utc` para todo i
    - **Validates: Requirements 9.4**

  - [ ] 16.3 Implementar `indicadores_service`
    - Implementar `fastapi_app/services/indicadores_service.py`: `obtener_indicadores(db, actor, fecha_desde, fecha_hasta) -> IndicadoresResponse`
    - Calcular contadores por estado, prioridad, categoría dentro del rango de fechas (extremos inclusivos)
    - Calcular `tiempo_promedio_resolucion_horas` solo sobre incidencias con `fecha_resolucion` no nula
    - Retornar ceros si no hay incidencias para el rango dado
    - Validar `fecha_desde <= fecha_hasta`; lanzar `ValidacionError` si no
    - _Requirements: 12.1–12.6_

  - [ ]* 16.4 Escribir property test — Property 27: Corrección de indicadores por rango de fechas
    - **Property 27: Corrección del cálculo de indicadores por rango de fechas**
    - Generar incidencias con fechas conocidas; aplicar rangos variados; verificar que los contadores solo incluyen incidencias dentro del rango
    - **Validates: Requirements 12.2**

  - [ ]* 16.5 Escribir property test — Property 28: Cálculo de tiempo promedio excluyendo no resueltas
    - **Property 28: Cálculo de tiempo promedio excluyendo no resueltas**
    - Mezclar incidencias con/sin `fecha_resolucion`; verificar que el promedio solo considera las que tienen `fecha_resolucion` no nulo
    - **Validates: Requirements 12.5**

- [ ] 17. Routers REST del backend
  - [ ] 17.1 Implementar `routers/incidencias.py`
    - `POST /api/v1/incidencias` (USUARIO), `GET /api/v1/incidencias` (Autenticado), `GET /api/v1/incidencias/{id}` (Autenticado), `PATCH /api/v1/incidencias/{id}/estado` (TECNICO, SUPERVISOR), `PATCH /api/v1/incidencias/{id}/prioridad` (SUPERVISOR), `PATCH /api/v1/incidencias/{id}/asignar` (SUPERVISOR)
    - _Requirements: 3.1–3.7, 4.1–4.7, 5.1–5.7, 6.1–6.5, 7.1–7.4_

  - [ ] 17.2 Implementar `routers/comentarios.py` y `routers/historial.py`
    - `POST /api/v1/incidencias/{id}/comentarios` (Autenticado), `GET /api/v1/incidencias/{id}/comentarios` (Autenticado)
    - `GET /api/v1/incidencias/{id}/historial` (SUPERVISOR, ADMINISTRADOR)
    - _Requirements: 8.1–8.6, 9.1–9.6_

  - [ ] 17.3 Implementar `routers/indicadores.py` y registrar todos los routers en `main.py`
    - `GET /api/v1/indicadores` (SUPERVISOR, ADMINISTRADOR) con query params `fecha_desde`, `fecha_hasta`
    - Registrar todos los routers en `main.py` bajo prefijo `/api/v1`; configurar CORS y middleware
    - _Requirements: 12.1–12.6_

- [ ] 18. Checkpoint — Backend completo
  - Asegurar que todos los tests unitarios y de propiedades del backend pasen. Verificar que el servidor levanta correctamente con `uvicorn fastapi_app.main:app --reload`. Consultar al usuario si surge alguna duda.

- [ ] 19. Tests de integración del backend
  - [ ] 19.1 Escribir test de integración — flujo completo de autenticación
    - Cubrir: login exitoso → obtener token → usar token → expirar/invalidar
    - Verificar bloqueo tras 5 intentos fallidos
    - _Requirements: 1.1–1.8_

  - [ ] 19.2 Escribir test de integración — ciclo de vida completo de incidencia
    - Cubrir: crear incidencia → asignar técnico (`ABIERTA→ASIGNADA`) → iniciar (`ASIGNADA→EN_PROCESO`) → resolver (`EN_PROCESO→RESUELTA`) → cerrar (`RESUELTA→CERRADA`)
    - Verificar historial completo al final del flujo
    - _Requirements: 3.1, 5.1–5.7, 6.1, 9.1–9.4_

  - [ ] 19.3 Escribir test de integración — indicadores con datos conocidos
    - Crear dataset controlado de incidencias con fechas y estados conocidos; verificar que los indicadores devuelven los valores exactos esperados
    - _Requirements: 12.1–12.6_

- [ ] 20. Configuración del proyecto frontend (React + TypeScript)
  - [ ] 20.1 Inicializar proyecto React con TypeScript y Vite
    - Crear `frontend/` con proyecto Vite + React + TypeScript
    - Instalar dependencias: `axios`, `react-router-dom`, `@tanstack/react-query`, `zustand`
    - Configurar alias de paths en `vite.config.ts` y `tsconfig.json`
    - _Requirements: todos (base frontend)_

  - [ ] 20.2 Configurar cliente HTTP y manejo de tokens
    - Crear `frontend/src/api/client.ts` con instancia Axios configurada con `baseURL=/api/v1`
    - Agregar interceptor de request para inyectar `Authorization: Bearer <token>` desde el store
    - Agregar interceptor de response para manejar 401 (redirigir a login) y 403
    - _Requirements: 1.1, 1.4, 1.5, 2.2, 2.8_

  - [ ] 20.3 Implementar store de autenticación
    - Crear `frontend/src/store/authStore.ts` con Zustand: estado `{ token, user, isAuthenticated }`, acciones `login`, `logout`
    - Persistir token en `localStorage`; sincronizar con el cliente HTTP
    - _Requirements: 1.1, 1.3_

- [ ] 21. Módulo de autenticación frontend
  - [ ] 21.1 Implementar página de Login
    - Crear `frontend/src/pages/Login.tsx` con formulario de email y contraseña
    - Llamar `POST /api/v1/auth/login`; almacenar token en `authStore`; redirigir al dashboard
    - Mostrar error genérico en credenciales inválidas; mostrar mensaje de cuenta bloqueada en 429/403
    - _Requirements: 1.1, 1.2, 1.4, 1.7, 10.4_

  - [ ] 21.2 Implementar `ProtectedRoute` y redirección por rol
    - Crear `frontend/src/components/ProtectedRoute.tsx` que verifica `isAuthenticated` y redirige a `/login` si no
    - Crear `frontend/src/components/RoleGuard.tsx` que verifica el rol del usuario y muestra 403 si no tiene permiso
    - _Requirements: 2.2–2.6_

- [ ] 22. Módulo de incidencias frontend
  - [ ] 22.1 Implementar tipos TypeScript y servicios API de incidencias
    - Crear `frontend/src/types/incidencia.ts` con interfaces para `Incidencia`, `IncidenciaResumen`, `Page<T>`, `IncidenciaFiltros`
    - Crear `frontend/src/api/incidencias.ts` con funciones: `crearIncidencia`, `listarIncidencias`, `obtenerIncidencia`, `actualizarEstado`, `asignarTecnico`, `actualizarPrioridad`
    - _Requirements: 3.1–3.7, 4.1–4.7_

  - [ ] 22.2 Implementar página de listado de incidencias
    - Crear `frontend/src/pages/Incidencias/ListaIncidencias.tsx`
    - Mostrar listado paginado con filtros (estado, prioridad, categoría, rango de fechas)
    - Usar `@tanstack/react-query` para fetching y cache; adaptar columnas visibles según rol del usuario
    - _Requirements: 4.1–4.5_

  - [ ] 22.3 Implementar formulario de creación de incidencia
    - Crear `frontend/src/pages/Incidencias/CrearIncidencia.tsx`
    - Validación de cliente: título 5–200 chars, descripción 10–2000 chars, categoría requerida (select con categorías activas)
    - Visible solo para rol `USUARIO`
    - _Requirements: 3.1–3.7_

  - [ ] 22.4 Implementar página de detalle de incidencia
    - Crear `frontend/src/pages/Incidencias/DetalleIncidencia.tsx`
    - Mostrar toda la información de la incidencia; mostrar botones de acción según rol (cambiar estado, asignar, cambiar prioridad)
    - Incluir sección de comentarios con formulario de creación
    - _Requirements: 4.6, 5.1, 6.1, 7.1, 8.1–8.6_

- [ ] 23. Módulos de administración frontend
  - [ ] 23.1 Implementar módulo de gestión de usuarios (ADMINISTRADOR)
    - Crear `frontend/src/pages/Admin/Usuarios.tsx`: tabla con listado, botón para crear, editar rol y desactivar
    - Crear `frontend/src/pages/Admin/CrearUsuario.tsx`: formulario con nombre, email y rol
    - Crear `frontend/src/api/usuarios.ts` con funciones de CRUD de usuarios
    - _Requirements: 10.1–10.7_

  - [ ] 23.2 Implementar módulo de gestión de categorías (ADMINISTRADOR)
    - Crear `frontend/src/pages/Admin/Categorias.tsx`: tabla con listado de todas las categorías, botón crear y desactivar
    - Crear `frontend/src/api/categorias.ts`
    - _Requirements: 11.1–11.5_

- [ ] 24. Módulo de indicadores frontend
  - [ ] 24.1 Implementar página de indicadores (SUPERVISOR, ADMINISTRADOR)
    - Crear `frontend/src/pages/Indicadores.tsx` con selectores de rango de fechas
    - Mostrar contadores por estado, prioridad, categoría y tiempo promedio de resolución
    - Usar `@tanstack/react-query` con refetch al cambiar el rango
    - _Requirements: 12.1–12.6_

- [ ] 25. Módulo de historial frontend
  - [ ] 25.1 Implementar sección de historial en detalle de incidencia (SUPERVISOR, ADMINISTRADOR)
    - Agregar tab o sección en `DetalleIncidencia.tsx` que cargue `GET /incidencias/{id}/historial`
    - Mostrar entradas ordenadas cronológicamente con actor, tipo de acción, valores anterior/nuevo y timestamp
    - Visible solo para roles `SUPERVISOR` y `ADMINISTRADOR`
    - _Requirements: 9.1–9.6_

- [ ] 26. Checkpoint final — Sistema completo integrado
  - Asegurar que todos los tests (unitarios, propiedades, integración) del backend pasen. Verificar que el frontend compila sin errores TypeScript. Consultar al usuario si surge alguna duda antes de cerrar.

---

## Notes

- Las tareas marcadas con `*` son opcionales y pueden omitirse para un MVP más rápido, aunque se recomienda mantener los property tests críticos (Properties 1, 4, 5, 7, 10).
- Cada tarea referencia los requisitos específicos para trazabilidad completa.
- Los property tests con Hypothesis usan el perfil `ci` (200 ejemplos) en CI y `dev` (50 ejemplos) en desarrollo local.
- Los checkpoints (tareas 11, 18, 26) son puntos de sincronización donde se valida el estado del sistema antes de continuar.
- Las propiedades 1–28 del documento de diseño están cubiertas por los property tests distribuidos en las tareas 4.2, 4.4, 4.5, 6.2, 6.3, 8.2, 9.2, 9.4, 9.5, 10.2, 10.4, 12.2, 12.3, 12.5, 12.6, 12.7, 13.2, 13.3, 14.2, 14.3, 14.5, 14.6, 15.2, 15.3, 15.4, 16.2, 16.4, 16.5.
- El frontend utiliza React + TypeScript con Vite, Axios, React Query y Zustand según el diseño aprobado.

---

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2", "1.3", "1.4"] },
    { "id": 2, "tasks": ["2.1", "3.1"] },
    { "id": 3, "tasks": ["2.2"] },
    { "id": 4, "tasks": ["2.3", "3.2", "3.3"] },
    { "id": 5, "tasks": ["4.1", "5.1"] },
    { "id": 6, "tasks": ["4.2", "4.3", "5.2"] },
    { "id": 7, "tasks": ["4.4", "4.5", "6.1"] },
    { "id": 8, "tasks": ["6.2", "6.3", "7.1", "8.1", "9.1"] },
    { "id": 9, "tasks": ["8.2", "8.3", "9.2", "10.1"] },
    { "id": 10, "tasks": ["9.3", "9.4", "9.5", "10.2", "10.3"] },
    { "id": 11, "tasks": ["10.4", "12.1"] },
    { "id": 12, "tasks": ["12.2", "12.3", "12.4"] },
    { "id": 13, "tasks": ["12.5", "12.6", "12.7", "13.1"] },
    { "id": 14, "tasks": ["13.2", "13.3", "14.1"] },
    { "id": 15, "tasks": ["14.2", "14.3", "14.4", "15.1"] },
    { "id": 16, "tasks": ["14.5", "14.6", "15.2", "15.3", "15.4", "16.1"] },
    { "id": 17, "tasks": ["16.2", "16.3"] },
    { "id": 18, "tasks": ["16.4", "16.5", "17.1"] },
    { "id": 19, "tasks": ["17.2", "17.3"] },
    { "id": 20, "tasks": ["19.1", "19.2", "19.3", "20.1"] },
    { "id": 21, "tasks": ["20.2", "20.3"] },
    { "id": 22, "tasks": ["21.1", "21.2"] },
    { "id": 23, "tasks": ["22.1"] },
    { "id": 24, "tasks": ["22.2", "22.3", "22.4", "23.1", "23.2"] },
    { "id": 25, "tasks": ["24.1", "25.1"] }
  ]
}
```
