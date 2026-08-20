# Requirements Document

## Introduction

El Sistema de Gestión de Incidencias (SGI) es una plataforma web que permite a una organización registrar, gestionar, escalar y resolver incidencias de manera trazable y estructurada. El sistema soporta cuatro roles de usuario: **Usuario**, **Técnico**, **Supervisor** y **Administrador**, cada uno con capacidades diferenciadas. La comunicación entre el frontend (React + TypeScript) y el backend (FastAPI + Python) se realiza a través de una API REST, con PostgreSQL como base de datos. El sistema aplica autenticación basada en tokens JWT y autorización basada en roles (RBAC). Cada modificación sobre una incidencia queda registrada en un historial de auditoría.

---

## Glossary

- **SGI**: Sistema de Gestión de Incidencias — el sistema descrito en este documento.
- **Incidencia**: Evento, falla o situación que requiere atención y resolución dentro de la organización.
- **Estado**: Valor que representa la etapa actual de una incidencia. Valores válidos: `ABIERTA`, `ASIGNADA`, `EN_PROCESO`, `RESUELTA`, `CERRADA`, `CANCELADA`.
- **Prioridad**: Nivel de urgencia asignado a una incidencia. Valores válidos: `BAJA`, `MEDIA`, `ALTA`, `CRITICA`.
- **Categoría**: Clasificación temática de una incidencia (ej. hardware, software, red).
- **Usuario**: Persona con rol `USUARIO` que puede reportar incidencias y consultar su estado.
- **Técnico**: Persona con rol `TECNICO` que atiende y resuelve incidencias asignadas.
- **Supervisor**: Persona con rol `SUPERVISOR` que asigna, prioriza y monitorea incidencias.
- **Administrador**: Persona con rol `ADMINISTRADOR` que gestiona usuarios, roles y categorías del sistema.
- **Comentario**: Nota textual asociada a una incidencia, registrada por cualquier actor autorizado.
- **Historial**: Registro cronológico e inmutable de todas las modificaciones aplicadas a una incidencia.
- **Token JWT**: Token de autenticación firmado que contiene la identidad y el rol del usuario autenticado.
- **API**: Interfaz de programación de la aplicación REST expuesta por el backend del SGI.
- **RBAC**: Control de acceso basado en roles (Role-Based Access Control).

---

## Requirements

---

### Requirement 1: Autenticación de Usuarios

**User Story:** Como usuario del sistema, quiero iniciar sesión con mis credenciales, para que el sistema reconozca mi identidad y me otorgue acceso según mi rol.

#### Acceptance Criteria

1. WHEN un actor envía credenciales válidas (correo y contraseña) al endpoint de autenticación, THE SGI SHALL retornar un Token JWT firmado que contiene el identificador del usuario y su rol.
2. WHEN un actor envía credenciales inválidas al endpoint de autenticación, THE SGI SHALL retornar un código de error HTTP 401 con un mensaje genérico que no revele si el fallo fue causado por el correo o la contraseña, sin emitir ni retornar ningún Token JWT en la respuesta.
3. THE SGI SHALL expirar el Token JWT transcurridos 60 minutos desde su emisión.
4. WHEN un actor realiza una solicitud a un endpoint protegido con un Token JWT ausente o con firma inválida, THE SGI SHALL retornar un código de error HTTP 401.
5. WHEN un actor realiza una solicitud a un endpoint protegido con un Token JWT expirado, THE SGI SHALL retornar un código de error HTTP 401 con un mensaje que indique que el token ha expirado.
6. THE SGI SHALL almacenar las contraseñas de los usuarios usando un algoritmo de hash con sal (bcrypt) y nunca en texto plano.
7. WHEN un actor realiza 5 intentos de autenticación fallidos consecutivos desde la misma cuenta, THE SGI SHALL bloquear temporalmente esa cuenta durante 15 minutos y retornar HTTP 429 en cualquier intento posterior durante ese período.
8. IF un actor intenta autenticarse con un correo no registrado en el sistema, THEN THE SGI SHALL retornar la misma respuesta HTTP 401 con el mismo mensaje genérico que para una contraseña incorrecta, sin revelar si el correo existe.

---

### Requirement 2: Autorización Basada en Roles (RBAC)

**User Story:** Como actor del sistema, quiero que mis acciones estén limitadas a las permitidas por mi rol, para que el sistema sea seguro y cada actor opere solo dentro de sus responsabilidades.

#### Acceptance Criteria

1. THE SGI SHALL definir cuatro roles: `USUARIO`, `TECNICO`, `SUPERVISOR` y `ADMINISTRADOR`.
2. WHEN un actor autenticado intenta ejecutar una acción no permitida para su rol, THE SGI SHALL retornar HTTP 403. WHEN una solicitud no incluye un Token JWT válido, THE SGI SHALL retornar HTTP 401.
3. THE SGI SHALL permitir al rol `USUARIO` únicamente: crear incidencias, consultar sus propias incidencias y agregar comentarios a sus propias incidencias.
4. THE SGI SHALL permitir al rol `TECNICO` únicamente: consultar incidencias que le fueron asignadas, actualizar el estado de esas incidencias, y agregar comentarios a esas incidencias.
5. THE SGI SHALL permitir al rol `SUPERVISOR`: consultar todas las incidencias, asignar incidencias a técnicos, cambiar la prioridad de incidencias, actualizar el estado de cualquier incidencia, agregar comentarios a cualquier incidencia, y consultar indicadores del sistema.
6. THE SGI SHALL permitir al rol `ADMINISTRADOR`: gestionar usuarios (crear, editar, desactivar), asignar y revocar roles a usuarios existentes, crear y desactivar categorías, consultar todas las incidencias y agregar comentarios a cualquier incidencia.
7. THE SGI SHALL permitir al rol `ADMINISTRADOR` consultar todas las incidencias del sistema.
8. WHEN una solicitud llega sin Token JWT o con un Token JWT inválido, THE SGI SHALL retornar HTTP 401 sin ejecutar ninguna lógica de negocio.

---

### Requirement 3: Registro de Incidencias

**User Story:** Como usuario, quiero registrar una incidencia, para que el equipo técnico pueda atenderla.

#### Acceptance Criteria

1. WHEN un actor con rol `USUARIO` envía una solicitud de creación de incidencia con título, descripción y categoría válidos, THE SGI SHALL persistir la incidencia con estado `ABIERTA`, prioridad `MEDIA` por defecto, y registrar la fecha y hora de creación en UTC.
2. WHEN un actor con rol `USUARIO` envía una solicitud de creación de incidencia con al menos un campo obligatorio ausente o con un valor inválido (incluyendo categoría inexistente o inactiva), THE SGI SHALL retornar un código HTTP 422 con un listado de los campos faltantes o inválidos.
3. THE SGI SHALL requerir que el campo `titulo` tenga entre 5 y 200 caracteres.
4. THE SGI SHALL requerir que el campo `descripcion` tenga entre 10 y 2000 caracteres.
5. THE SGI SHALL requerir que el campo `categoria` corresponda a una categoría activa existente en el sistema.
6. WHEN una incidencia es creada exitosamente, THE SGI SHALL retornar el identificador único de la incidencia y el estado `ABIERTA`.
7. IF un actor sin rol `USUARIO` o sin autenticación intenta crear una incidencia, THEN THE SGI SHALL rechazar la solicitud con el código HTTP correspondiente (403 o 401) sin persistir ningún dato.

---

### Requirement 4: Consulta de Incidencias

**User Story:** Como actor del sistema, quiero consultar incidencias según mi rol, para que pueda ver la información relevante a mis responsabilidades.

#### Acceptance Criteria

1. WHEN un actor con rol `USUARIO` consulta el listado de incidencias, THE SGI SHALL retornar únicamente las incidencias creadas por ese usuario.
2. WHEN un actor con rol `TECNICO` consulta el listado de incidencias, THE SGI SHALL retornar únicamente las incidencias asignadas a ese técnico.
3. WHEN un actor con rol `SUPERVISOR` o `ADMINISTRADOR` consulta el listado de incidencias, THE SGI SHALL retornar todas las incidencias existentes en el sistema.
4. WHEN un actor consulta el listado de incidencias sin aplicar ningún filtro, THE SGI SHALL retornar todas las incidencias accesibles para ese actor según su rol. WHEN un actor aplica uno o más filtros explícitos (estado, prioridad, categoría o rango de fechas de creación) al listado de incidencias, THE SGI SHALL retornar únicamente las incidencias que cumplan simultáneamente todos los filtros aplicados; si ninguna incidencia cumple los filtros, THE SGI SHALL retornar una lista vacía con HTTP 200.
5. WHEN un actor consulta el listado de incidencias sin especificar parámetros de paginación, THE SGI SHALL retornar los primeros 10 registros con metadatos de paginación (página actual, tamaño de página, total de registros). WHEN un actor especifica un tamaño de página fuera del rango 10–100, THE SGI SHALL retornar HTTP 422 indicando el rango válido.
6. WHEN un actor solicita el detalle de una incidencia existente a la que no tiene acceso según su rol, THE SGI SHALL retornar HTTP 403.
7. IF la incidencia solicitada no existe en el sistema, THEN THE SGI SHALL retornar HTTP 404, independientemente del rol del actor.

---

### Requirement 5: Transiciones de Estado de Incidencias

**User Story:** Como técnico o supervisor, quiero actualizar el estado de una incidencia, para que el sistema refleje su progreso real.

#### Acceptance Criteria

1. THE SGI SHALL permitir únicamente las siguientes transiciones de estado:
   - `ABIERTA` → `ASIGNADA`, `CANCELADA`
   - `ASIGNADA` → `EN_PROCESO`, `CANCELADA`, `ABIERTA`
   - `EN_PROCESO` → `RESUELTA`, `CANCELADA`, `ASIGNADA`
   - `RESUELTA` → `CERRADA`
   - `CERRADA` → *(ninguna transición permitida)*
   - `CANCELADA` → *(ninguna transición permitida)*
2. WHEN un actor intenta realizar una transición de estado no permitida, THE SGI SHALL rechazar la solicitud, mantener el estado actual de la incidencia sin modificación y retornar un mensaje que indique los estados de destino válidos desde el estado actual.
3. WHEN un actor con rol `TECNICO` intenta actualizar el estado de una incidencia que no le está asignada, THE SGI SHALL rechazar la solicitud sin modificar el estado de la incidencia.
4. WHEN un actor con rol `TECNICO` actualiza el estado de una incidencia que le está asignada a una transición válida, THE SGI SHALL persistir el nuevo estado y registrar en el historial el identificador del técnico, el estado anterior, el nuevo estado y la marca de tiempo del cambio.
5. WHEN un actor con rol `SUPERVISOR` actualiza el estado de cualquier incidencia a una transición válida, THE SGI SHALL persistir el nuevo estado y registrar en el historial el identificador del supervisor, el estado anterior, el nuevo estado y la marca de tiempo del cambio.
6. WHEN el estado de una incidencia cambia a `RESUELTA`, THE SGI SHALL registrar la fecha y hora de resolución en UTC.
7. WHEN el estado de una incidencia cambia a `CERRADA`, THE SGI SHALL registrar la fecha y hora de cierre en UTC.

---

### Requirement 6: Asignación de Incidencias

**User Story:** Como supervisor, quiero asignar incidencias a técnicos, para que cada incidencia tenga un responsable claro.

#### Acceptance Criteria

1. WHEN un actor con rol `SUPERVISOR` asigna una incidencia en estado `ABIERTA` a un usuario con rol `TECNICO` cuya cuenta está en estado `ACTIVO`, THE SGI SHALL actualizar el campo `asignado_a` de la incidencia con el identificador único del técnico asignado y cambiar el estado a `ASIGNADA`.
2. WHEN un actor con rol `SUPERVISOR` intenta asignar una incidencia a un usuario que no tiene rol `TECNICO`, THE SGI SHALL rechazar la solicitud con un mensaje de error que indique que el destinatario debe tener rol `TECNICO`.
3. WHEN un actor con rol `SUPERVISOR` intenta asignar una incidencia que se encuentra en un estado distinto a `ABIERTA` o `ASIGNADA`, THE SGI SHALL rechazar la solicitud indicando que la incidencia no puede ser asignada en su estado actual.
4. WHEN una incidencia en estado `ASIGNADA` es reasignada a un técnico diferente al técnico actualmente asignado, THE SGI SHALL actualizar el campo `asignado_a` con el identificador único del nuevo técnico, registrar en el historial el identificador del técnico anterior, el identificador del técnico nuevo, el identificador del actor que realizó el cambio y la marca de tiempo. IF el técnico nuevo es el mismo que el técnico actualmente asignado, THEN THE SGI SHALL rechazar la solicitud con HTTP 422 indicando que el técnico ya está asignado a la incidencia, sin modificar la incidencia.
5. WHEN un actor con rol distinto a `SUPERVISOR` intenta asignar o reasignar una incidencia, THE SGI SHALL rechazar la solicitud con HTTP 403 sin modificar la incidencia.

---

### Requirement 7: Gestión de Prioridades

**User Story:** Como supervisor, quiero cambiar la prioridad de una incidencia, para que los técnicos atiendan primero las situaciones más críticas.

#### Acceptance Criteria

1. WHEN un actor con rol `SUPERVISOR` actualiza la prioridad de una incidencia existente a un valor válido (`BAJA`, `MEDIA`, `ALTA`, `CRITICA`), THE SGI SHALL persistir el nuevo valor de prioridad y registrar en el historial de la incidencia el valor anterior, el nuevo valor, el identificador del actor que realizó el cambio y la marca de tiempo del momento del cambio.
2. WHEN un actor con rol `SUPERVISOR` envía un valor de prioridad no válido, THE SGI SHALL retornar un error HTTP 422 con un mensaje que indique el valor rechazado y el listado de valores aceptados (`BAJA`, `MEDIA`, `ALTA`, `CRITICA`), sin modificar la prioridad actual de la incidencia.
3. WHEN un actor con rol distinto a `SUPERVISOR` o `ADMINISTRADOR` intenta cambiar la prioridad de una incidencia, THE SGI SHALL retornar un error HTTP 403 sin modificar la prioridad actual de la incidencia.
4. IF la incidencia sobre la que se intenta cambiar la prioridad no existe, THEN THE SGI SHALL retornar un error HTTP 404 sin registrar ningún cambio en el historial.

---

### Requirement 8: Comentarios en Incidencias

**User Story:** Como actor del sistema, quiero agregar comentarios a una incidencia, para que el historial de la atención quede documentado.

#### Acceptance Criteria

1. WHEN un actor con rol `USUARIO` o `TECNICO` envía un comentario con contenido entre 1 y 1000 caracteres asociado a una incidencia a la que tiene acceso, THE SGI SHALL persistir el comentario con el identificador del autor, el contenido y la marca de tiempo de creación en UTC. WHEN un actor con rol `SUPERVISOR` o `ADMINISTRADOR` envía un comentario con contenido de al menos 1 caracter asociado a una incidencia a la que tiene acceso, THE SGI SHALL persistir el comentario con el identificador del autor, el contenido y la marca de tiempo de creación en UTC, sin aplicar límite máximo de caracteres.
2. WHEN un actor con rol `USUARIO` o `TECNICO` envía un comentario con contenido vacío o con más de 1000 caracteres, THE SGI SHALL rechazar la solicitud con HTTP 422 e indicar la restricción de longitud (entre 1 y 1000 caracteres). WHEN un actor con rol `SUPERVISOR` o `ADMINISTRADOR` envía un comentario con contenido vacío, THE SGI SHALL rechazar la solicitud con HTTP 422 indicando que el comentario no puede estar vacío.
3. IF un actor con rol `USUARIO` intenta agregar un comentario a una incidencia que no le pertenece o que se encuentra en estado `CERRADA` o `CANCELADA`, THEN THE SGI SHALL rechazar la solicitud con HTTP 403 sin persistir el comentario.
4. IF un actor con rol `TECNICO` intenta agregar un comentario a una incidencia que no le está asignada o que se encuentra en estado `CERRADA` o `CANCELADA`, THEN THE SGI SHALL rechazar la solicitud con HTTP 403 sin persistir el comentario.
5. IF un actor con rol `SUPERVISOR` o `ADMINISTRADOR` intenta agregar un comentario a una incidencia en estado `CERRADA` o `CANCELADA`, THEN THE SGI SHALL rechazar la solicitud con HTTP 403 sin persistir el comentario.
6. WHEN un actor autorizado solicita los comentarios de una incidencia a la que tiene acceso, THE SGI SHALL retornar la lista de comentarios ordenados cronológicamente de más antiguo a más reciente.

---

### Requirement 9: Historial de Trazabilidad

**User Story:** Como supervisor o administrador, quiero consultar el historial completo de cambios de una incidencia, para que pueda auditar cada modificación realizada.

#### Acceptance Criteria

1. WHEN ocurre cualquiera de las siguientes acciones sobre una incidencia y el valor resultante es distinto al valor anterior — cambio de estado, cambio de prioridad, asignación o reasignación a técnico, o edición de los campos `titulo` o `descripcion` — THE SGI SHALL registrar una entrada de historial. Si el valor nuevo es igual al valor anterior, THE SGI SHALL omitir el registro de la entrada.
2. THE SGI SHALL incluir en cada entrada de historial: el identificador del actor que realizó la acción, el tipo de acción, el valor anterior, el valor nuevo y la marca de tiempo en UTC con precisión de milisegundos.
3. THE SGI SHALL garantizar que las entradas del historial sean inmutables; ningún actor ni proceso automatizado del sistema podrá modificar ni eliminar registros del historial una vez creados.
4. WHEN un actor con rol `SUPERVISOR` o `ADMINISTRADOR` solicita el historial de una incidencia existente, THE SGI SHALL retornar todas las entradas ordenadas cronológicamente de más antiguo a más reciente.
5. WHEN un actor con rol `USUARIO` o `TECNICO` solicita el historial de una incidencia, THE SGI SHALL retornar un código HTTP 403.
6. IF un actor solicita el historial de una incidencia que no existe, THEN THE SGI SHALL retornar HTTP 404 sin exponer información sobre otras incidencias.

---

### Requirement 10: Gestión de Usuarios

**User Story:** Como administrador, quiero gestionar los usuarios del sistema, para que el acceso esté controlado y actualizado.

#### Acceptance Criteria

1. WHEN un actor con rol `ADMINISTRADOR` crea un nuevo usuario con nombre, correo electrónico único y rol válido (`USUARIO`, `TECNICO`, `SUPERVISOR` o `ADMINISTRADOR`), THE SGI SHALL persistir el usuario en estado activo, generar una contraseña temporal de un solo uso y marcarla para expirar en 24 horas.
2. WHEN un actor con rol `ADMINISTRADOR` intenta crear un usuario con un correo electrónico ya registrado en el sistema, THE SGI SHALL retornar un código HTTP 409 con un mensaje de error que indique el conflicto de correo duplicado.
3. WHEN un actor con rol `ADMINISTRADOR` desactiva un usuario, THE SGI SHALL impedir que ese usuario autentique en el sistema a partir de ese momento.
4. WHEN un actor desactivado intenta autenticar, THE SGI SHALL verificar el estado de la cuenta (`is_active`) antes de comprobar la contraseña y, si la cuenta está desactivada, retornar un código HTTP 403 con un mensaje que indique que la cuenta está desactivada, sin validar si la contraseña proporcionada es correcta o no.
5. WHEN un actor con rol `ADMINISTRADOR` actualiza el rol de un usuario existente, THE SGI SHALL persistir el nuevo rol y registrar en el historial de auditoría el rol anterior, el rol nuevo, el identificador del administrador que realizó el cambio y la marca de tiempo.
6. THE SGI SHALL requerir que el correo electrónico de cada usuario sea único en el sistema y tenga formato válido (conforme a RFC 5321).
7. IF un actor con rol `ADMINISTRADOR` intenta crear un usuario con campos obligatorios ausentes o con valores inválidos (nombre vacío, correo con formato incorrecto o rol no reconocido), THEN THE SGI SHALL retornar HTTP 422 con un detalle de cada campo inválido sin persistir ningún dato.

---

### Requirement 11: Gestión de Categorías

**User Story:** Como administrador, quiero gestionar las categorías de incidencias, para que los usuarios puedan clasificar correctamente sus reportes.

#### Acceptance Criteria

1. WHEN un actor con rol `ADMINISTRADOR` crea una categoría con un nombre único de entre 3 y 100 caracteres, THE SGI SHALL persistir la categoría en estado activo y retornar su identificador único.
2. WHEN un actor con rol `ADMINISTRADOR` intenta crear una categoría con un nombre ya existente (comparación sin distinción de mayúsculas/minúsculas), THE SGI SHALL retornar HTTP 409 con un mensaje que indique que ya existe una categoría con ese nombre.
3. WHEN un actor con rol `ADMINISTRADOR` desactiva una categoría activa, THE SGI SHALL cambiar su estado a inactivo y rechazar cualquier solicitud posterior de creación de incidencias que referencie esa categoría con HTTP 422.
4. WHILE una categoría está en estado inactivo, THE SGI SHALL mantener el acceso de lectura a todas las incidencias existentes que la referencian, sin ocultar ni eliminar esa información.
5. WHEN un actor consulta el listado de categorías disponibles para crear una incidencia, THE SGI SHALL retornar únicamente las categorías en estado activo.

---

### Requirement 12: Indicadores y Reportes del Supervisor

**User Story:** Como supervisor, quiero consultar indicadores del sistema, para que pueda tomar decisiones basadas en datos sobre la operación del equipo.

#### Acceptance Criteria

1. WHEN un actor con rol `SUPERVISOR` o `ADMINISTRADOR` solicita los indicadores del sistema sin proporcionar rango de fechas, THE SGI SHALL retornar los indicadores calculados sobre todas las incidencias del sistema sin aplicar ningún filtro de fecha: total de incidencias por estado, total de incidencias por prioridad, total de incidencias por categoría y tiempo promedio de resolución en horas calculado sobre incidencias en estado `RESUELTA` o `CERRADA` cuyo campo `fecha_resolucion` no sea nulo.
2. WHEN un actor con rol `SUPERVISOR` o `ADMINISTRADOR` solicita los indicadores con un rango de fechas de creación válido (fecha inicio ≤ fecha fin), THE SGI SHALL retornar únicamente los indicadores correspondientes a incidencias cuya `fecha_creacion` esté dentro del rango especificado, con ambos extremos inclusivos.
3. IF un actor proporciona un rango de fechas inválido (fecha inicio > fecha fin), THEN THE SGI SHALL retornar HTTP 422 con un mensaje que indique que la fecha de inicio debe ser anterior o igual a la fecha de fin.
4. IF un actor con rol distinto a `SUPERVISOR` o `ADMINISTRADOR` solicita los indicadores, THEN THE SGI SHALL retornar HTTP 403 sin procesar la solicitud.
5. THE SGI SHALL calcular el tiempo promedio de resolución como el promedio aritmético de las diferencias en horas entre `fecha_creacion` y `fecha_resolucion` de cada incidencia considerada, excluyendo aquellas cuyo campo `fecha_resolucion` sea nulo.
6. WHEN los indicadores se calculan sobre un conjunto de incidencias vacío (sin datos para el rango o filtro aplicado), THE SGI SHALL retornar todos los contadores en cero y el tiempo promedio de resolución en cero.
