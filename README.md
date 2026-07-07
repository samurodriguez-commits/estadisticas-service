# estadisticas-service

Microservicio de **estadísticas / dashboards** del casino (FastAPI, **solo lectura**).
Comparte la base de datos PostgreSQL y el `JWT_SECRET` con `casino-backend` (valida
el JWT del backend). Agrega KPIs sobre `transacciones`, `usuarios` y `apuestas`.

- Prefijo de rutas: `/api/estadisticas` · Docs: `/docs`

## Endpoints
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/estadisticas/mias` | KPIs, desglose por tipo y línea de saldo del usuario |
| GET | `/api/estadisticas/globales` | Usuarios, GGR, top jugadores, métricas de apuestas |

## Ejecutar en local
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# variables: copia .env.example a .env y ajústalas
uvicorn app.main:app --reload --port 8006
```
Requiere una PostgreSQL accesible con las tablas compartidas que crea `casino-backend`.
Es de solo lectura: no crea ni modifica tablas.

## Entrega (lo que debes implementar)
1. **Rutas de salud** para Kubernetes (ver el `TODO` en `app/main.py`):
   *liveness* (¿el proceso vive?) y *readiness* (¿listo para tráfico? verifica la BD, responde 200/503).
2. **Dockerfile** para contenerizar el servicio.
3. **Workflow de CI/CD** (GitHub Actions) que construya la imagen, la publique en ECR y despliegue en **EKS**.
4. **Manifiestos de Kubernetes** (Deployment + Service) con las probes apuntando a tus rutas de salud.
5. **Pruebas de carga** que evidencien el correcto funcionamiento en EKS (escalado, disponibilidad).
