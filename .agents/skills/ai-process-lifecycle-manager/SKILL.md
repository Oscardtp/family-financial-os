---
name: ai-process-lifecycle-manager
description: Gestiona de forma segura y no bloqueante la ejecución de comandos, procesos persistentes, servidores de desarrollo, servicios locales, Docker y herramientas CLI utilizadas por agentes de IA. Detecta procesos de larga duración, aplica timeouts, monitoriza stdout/stderr, verifica condiciones reales de éxito, gestiona procesos en background y evita que el agente quede bloqueado esperando procesos que deben permanecer activos. Usa esta skill siempre que el usuario pida levantar/iniciar un servidor, backend, frontend, worker, servicio Docker, proceso en background, o mencione uvicorn, npm run dev, vite, next dev, docker compose up, o cuando un comando parezca quedarse colgado/bloqueado esperando un proceso persistente.
---

# AI Process Execution & Lifecycle Manager

## Purpose

Actuar como Ingeniero Principal de Automatización de Procesos y Runtime para Agentes de IA.

La skill debe impedir que el agente quede bloqueado debido a: servidores HTTP, Uvicorn, FastAPI, Node.js, Vite, Next.js, Docker, workers, watchers, procesos interactivos, servicios persistentes, scripts de desarrollo, o comandos que esperan indefinidamente.

El objetivo es separar:

```
Ejecución del comando
        ↓
Detección de éxito
        ↓
Liberación del agente
        ↓
Proceso continúa ejecutándose
```

## Regla Fundamental

Antes de ejecutar cualquier comando, determinar:

```
¿El proceso debería terminar?
        │
        ├── SÍ → ejecución normal
        │
        └── NO → proceso persistente
                    ↓
             ejecución asíncrona
                    ↓
             health check
                    ↓
             devolver control
```

Nunca esperar indefinidamente a que finalice un proceso que está diseñado para mantenerse activo.

## Clasificación de Procesos

Clasificar cada comando como:

- **SHORT** — termina rápidamente. Ej.: `git status`, `npm install`, `pytest`, `python script.py`.
- **LONG** — potencialmente largo pero eventualmente termina. Ej.: database migration, build, large test suite, `docker build`.
- **PERSISTENT** — diseñado para permanecer ejecutándose. Ej.: `uvicorn`, `npm run dev`, `vite`, `next dev`, `docker compose up`, `node server.js`, workers, watchers.

## Regla para Procesos Persistentes

Nunca ejecutar directamente un proceso persistente mediante una llamada bloqueante.

Evitar conceptualmente:

```
run("uvicorn app.main:app")
wait_until_exit()
```

Preferir:

```
start_process()
        ↓
capture_output()
        ↓
detect_startup()
        ↓
health_check()
        ↓
return_control_to_agent()
```

## Lifecycle Management

Todo proceso persistente debe tener:

```
START → INITIALIZING → READY → RUNNING → STOPPING → STOPPED
```

Estados adicionales: `FAILED`, `TIMEOUT`, `CRASHED`, `UNKNOWN`.

## Startup Detection

No asumir que "Process started" significa "Service ready" — son conceptos distintos:

- **Process Started**: el proceso existe.
- **Service Ready**: el servicio responde correctamente.

Para HTTP, utilizar preferentemente un health check (`GET /health` o endpoint equivalente).

## Output Monitoring

Supervisar: stdout, stderr, exit code, proceso, puerto, health endpoint.

Detectar mensajes conocidos únicamente como indicadores auxiliares (ej.: `Application startup complete`, `Uvicorn running`, `Server listening`, `Ready`, `Listening on`). Nunca considerar un texto del log como prueba definitiva cuando pueda realizarse un health check real.

## Timeout Architecture

Todo proceso debe tener un timeout apropiado, configurable según el proyecto. Ejemplo:

```
START_TIMEOUT   = 30s
HEALTH_TIMEOUT  = 10s
COMMAND_TIMEOUT = 300s
```

### Timeout Semantics

No todos los timeouts significan lo mismo — distinguir:

- **Startup Timeout**: el servicio no inició a tiempo.
- **Health Timeout**: el proceso existe pero no responde correctamente.
- **Command Timeout**: un comando finito tardó demasiado.
- **Shutdown Timeout**: el proceso no terminó correctamente.

## Ejecución en Python

Para procesos finitos:

```python
import subprocess

result = subprocess.run(
    command,
    capture_output=True,
    text=True,
    timeout=30,
    check=False,
)
```

Para procesos persistentes, utilizar una arquitectura basada en `Popen` o un supervisor dedicado en lugar de `subprocess.run()` bloqueante:

```python
process = subprocess.Popen(
    command,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
)
```

Después: `Popen → Monitor output → Detect startup → Health check → Return process metadata`.

No hacer `process.wait()` antes de devolver el control al agente.

## Process Registry

Mantener un registro de procesos iniciados por el agente:

```json
{
  "service": "backend",
  "pid": 12345,
  "command": "uvicorn app.main:app --port 8000",
  "host": "127.0.0.1",
  "port": 8000,
  "status": "running",
  "started_at": "2026-08-19T17:00:00"
}
```

Esto permite posteriormente: status, logs, restart, stop, health.

## PID Management

Guardar el PID del proceso cuando el sistema operativo lo permita. Nunca matar indiscriminadamente procesos por nombre.

Preferir `Known PID → Validate process → Stop process`, en lugar de `kill every process named python`.

## Port Management

Antes de iniciar un servidor:

1. Verificar si el puerto está ocupado.
2. Determinar qué proceso lo utiliza.
3. Comprobar si corresponde al servicio esperado.
4. Reutilizarlo si ya está funcionando correctamente.
5. Solo iniciar otro proceso si es necesario.

## Idempotency

La skill debe ser idempotente. Si el agente ejecuta "start backend" dos veces: la primera inicia el backend, la segunda debe detectar que ya existe. No debe crear innecesariamente `backend #1`, `backend #2`, `backend #3`.

## Health Checks

Para servicios HTTP: `GET http://127.0.0.1:8000/health`, esperando `HTTP 200` o el comportamiento definido por el proyecto. Si no existe `/health`, identificar un endpoint seguro y apropiado.

## Readiness vs Liveness

Diferenciar:

- **Liveness**: ¿el proceso está vivo?
- **Readiness**: ¿el servicio está preparado para recibir trabajo?

Un proceso puede estar vivo pero todavía no estar listo.

## PowerShell (Windows)

Preferir mecanismos controlables para procesos en background y supervisión. No asumir que `Start-Job` es siempre la mejor opción — evaluar `Start-Process`, Jobs, procesos hijos, servicios, Docker o scripts `.ps1` según si el proceso necesita sobrevivir a la sesión, compartir entorno, conservar logs, devolver PID o recibir señales de parada.

Ejemplo con `Start-Process`:

```powershell
$process = Start-Process `
    -FilePath "python" `
    -ArgumentList "-m uvicorn app.main:app --port 8000" `
    -PassThru

$process.Id
```

Conservar `$process.Id` para poder supervisarlo posteriormente.

## Logs

Los procesos persistentes deben disponer de logs accesibles, por ejemplo:

```
logs/
├── backend.stdout.log
└── backend.stderr.log
```

Nunca depender exclusivamente de la terminal interactiva del agente.

## Docker

Cuando el proyecto utilice Docker, preferir `docker compose up -d` para servicios persistentes cuando esa sea la arquitectura prevista. Después: `docker compose ps`, y posteriormente health check.

No considerar "container running" como equivalente automático a "application healthy".

## Service Startup Strategy

Orden de preferencia: `Docker Compose → Service Manager → Dedicated startup script → Background process`.

Evitar que cada agente tenga que reconstruir manualmente la infraestructura en cada ejecución.

## Separation of Concerns

El agente debe separar infraestructura (Database, Backend, Frontend, Workers) de sus propias tareas (Tests / Tasks / Operations). El agente no debería bloquear su propio runtime ejecutando infraestructura persistente.

## Arquitectura Recomendada

```
                ┌─────────────────────┐
                │      AI Agent       │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Process Supervisor  │
                └──────────┬──────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
       Backend          Frontend          Worker
       Uvicorn            Vite             Celery
          │                │                │
          ▼                ▼                ▼
       Health           Health           Health
```

## Startup Workflow

Ante "Levanta el backend", la skill debe:

1. Comprobar si ya existe.
2. Comprobar el puerto.
3. Comprobar el proceso.
4. Si existe y está saludable → informar `Backend already running`.
5. Si no existe → iniciar el proceso.
6. Monitorizar el startup.
7. Realizar health check.
8. Devolver inmediatamente el control.

## Failure Workflow

Si falla:

```
Start → Process exits → Collect stderr → Determine exit code → Report failure
```

Mostrar al agente algo como:

```
❌ Backend failed to start
Exit code: 1
Relevant error: ...
Suggested next diagnostic: ...
```

## Hung Process

Si un proceso no termina y tampoco se comporta como servicio:

```
TIMEOUT → Capture output → Inspect process → Attempt graceful termination → Report
```

Nunca mantener el agente esperando indefinidamente.

## Graceful Shutdown

Preferir `SIGTERM` / graceful stop antes que force kill:

```
Stop request → Wait → Process exits
```

Si excede el shutdown timeout → force termination, registrando el evento.

## Agent Tool Contract

La herramienta de ejecución debería devolver algo como:

```json
{
  "status": "ready",
  "pid": 12345,
  "port": 8000,
  "url": "http://127.0.0.1:8000",
  "health": "healthy",
  "startup_time_ms": 1840
}
```

En lugar de mantener la llamada abierta indefinidamente.

## Command Execution Policy

Todo comando debe tener, cuando corresponda: timeout, stdout capture, stderr capture, exit code, process tracking.

## Never Wait Forever

**Regla crítica**: ninguna herramienta de ejecución del agente debe tener una espera infinita por defecto. Si un timeout infinito es realmente necesario, debe ser una decisión explícita del sistema y no el comportamiento predeterminado.

## Security

Antes de ejecutar comandos destructivos: confirmar contexto, revisar el comando, evitar expansión peligrosa, no borrar datos indiscriminadamente, no ejecutar comandos obtenidos de fuentes no confiables.

Especial cuidado con: `Remove-Item`, `rm -rf`, `DROP DATABASE`, `git reset --hard`, `docker system prune`.

## Database Protection

Si el agente necesita reiniciar una base de datos:

1. Verificar que sea entorno de desarrollo/test.
2. Confirmar ruta.
3. Confirmar proceso que utiliza la base.
4. Detener dependencias si es necesario.
5. Realizar la operación.
6. Verificar integridad.
7. Reiniciar servicio.

Nunca borrar una base de datos de producción como parte de una rutina automática.

## Logging del Supervisor

Registrar: `PROCESS_START`, `PROCESS_READY`, `HEALTH_CHECK`, `PROCESS_EXIT`, `PROCESS_TIMEOUT`, `PROCESS_STOP`, `PROCESS_CRASH`. Esto permite diagnosticar problemas del agente.

## Recovery

Si un servicio falla:

```
Detect failure → Collect logs → Check dependencies → Restart if policy allows → Health check → Report result
```

Limitar los reinicios automáticos para evitar loops: `MAX_RESTARTS = 3`.

## Environment Awareness

Detectar: Windows, Linux, macOS, Docker, WSL, CI, local development. No asumir que un comando PowerShell funciona en Linux, ni que un comando Bash funciona en Windows.

## CI/CD Behavior

En CI: evitar procesos persistentes sin supervisor, utilizar servicios declarados por el pipeline, utilizar Docker cuando corresponda, definir health checks, garantizar cleanup.

## Output Format

Cuando gestione un proceso, responder con este formato:

```
## Process Manager

### Service
Backend

### Action
START

### Process
Uvicorn

### PID
12345

### Port
8000

### Status
🟢 READY

### Health
🟢 HEALTHY

### URL
http://127.0.0.1:8000

### Agent Status
Control returned successfully.

### Logs
[ubicación de logs]
```

### Error Format

```
## Process Error

### Service
Backend

### Status
🔴 FAILED

### Exit Code
1

### Startup Timeout
No

### Error
[stderr relevante]

### Diagnosis
[posible causa basada en evidencia]

### Next Action
[acción recomendada]
```

## Production Rules

La skill debe ser: no bloqueante, observable, idempotente, segura, multiplataforma, configurable, tolerante a fallos, consciente del ciclo de vida, compatible con CI/CD.

## Regla Especial para Agentes de IA

Cuando el agente necesite ejecutar `uvicorn`, `npm run dev`, `vite`, `next dev`, `docker compose up`, debe reconocer automáticamente que probablemente se trata de un proceso persistente.

Por defecto:

- **NO**: `execute → wait forever`
- **SÍ**: `execute → monitor → detect ready → health check → return`

## Definition of Done

La skill considera correctamente gestionado un servicio cuando: el proceso inició; se conoce su PID o mecanismo equivalente; existe una forma de consultar su estado; existe un mecanismo de logs; el servicio está ready; el health check responde correctamente; el agente recuperó el control; existe un método de shutdown; no queda ningún proceso huérfano innecesario.

## Regla Maestra

Un agente de IA no debe confundir "proceso ejecutándose" con "comando sin terminar". Un servidor que permanece activo no es un comando bloqueado — es un recurso persistente que debe ser administrado mediante un ciclo de vida explícito.

```
              COMMAND
                 │
                 ▼
          CLASSIFY PROCESS
                 │
        ┌────────┴────────┐
        │                 │
      FINITE          PERSISTENT
        │                 │
        ▼                 ▼
     TIMEOUT          BACKGROUND
        │                 │
        ▼                 ▼
     RESULT          STARTUP MONITOR
                          │
                          ▼
                     HEALTH CHECK
                          │
                          ▼
                    RETURN CONTROL
                          │
                          ▼
                    PROCESS MANAGED
```

Esta skill convierte el problema concreto de un proceso (por ejemplo, Uvicorn) bloqueando la terminal del agente, en una arquitectura general para gestionar correctamente cualquier servidor, worker o proceso persistente sin quedarse esperando indefinidamente.
