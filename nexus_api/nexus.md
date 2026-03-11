# Nexus Integration Guide (Towebs)

## Objetivo
Documento rápido para que otro agente/equipo pueda:

1. Bajar el proyecto `twgetclientstatus` desde Git.
2. Entender cómo consulta Nexus.
3. Probarlo localmente.
4. Entender cómo lo usa el agente de soporte en `/opt/soporton/rag`.

---

## 1) Clonar desde Git

```bash
cd /opt/soporton
git clone https://git.towebs.com/<owner>/twgetclientstatus.git
```

Si ya existe:

```bash
cd /opt/soporton/twgetclientstatus
git pull
```

Nota: reemplazar `<owner>` por el namespace real del repo en Git Towebs.

---

## 2) Estructura relevante del repo

- `src/routes.py`: endpoint `GET /<domain>` + validación de `X-API-Key`.
- `src/utils.py`: hace `GET` a `https://nexus.towebs.com/api-client-info/?domain=<domain>` con Basic Auth.
- `.env.example`: variables de entorno base.

Flujo:

1. entra request al endpoint local.
2. valida API key.
3. consulta Nexus con usuario/clave.
4. devuelve JSON simplificado (`servidor`, `status`, `usuario`).

---

## 3) Variables de entorno

Crear `.env` desde `.env.example`:

```bash
cd /opt/soporton/twgetclientstatus
cp .env.example .env
```

Completar con valores reales (ejemplo):

```env
TWNEXUS_USER=towebs
TWNEXUS_PASS=<CLAVE_NEXUS_REAL>
APP_DEBUG=True
APP_PORT=8000
API_KEY=<API_KEY_INTERNA>
```

Importante: no commitear secretos en Git.

---

## 4) Ejecutar local

```bash
cd /opt/soporton/twgetclientstatus
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 src/app.py
```

---

## 5) Probar endpoint local

```bash
curl -sS "http://127.0.0.1:8000/plantascarnivoras.com" \
  -H "X-API-Key: <API_KEY_INTERNA>"
```

Respuesta esperada (formato):

```json
{
  "status": true,
  "data": {
    "servidor": "...",
    "status": "...",
    "usuario": "..."
  },
  "error": null
}
```

---

## 6) Cómo lo usa HOY el agente de soporte

El agente principal no llama al microservicio local, sino a Nexus directo desde:

- `/opt/soporton/rag/nexus_client.py`

Variables usadas por el backend del chat:

- `TWNEXUS_USER`
- `TWNEXUS_PASS`

Ejecución típica del backend:

```bash
TWNEXUS_USER='<USER>' TWNEXUS_PASS='<PASS>' python3 /opt/soporton/rag/chat_server.py
```

En runtime:

1. Detecta dominio en mensaje/perfil.
2. Consulta Nexus.
3. Enriquece perfil (`status`, `servidor`, `plan`, etc.).
4. Aplica reglas (por ejemplo, pagos/deuda, ruteo por área, respuestas de soporte).

---

## 7) Notas técnicas importantes

- Si Nexus devuelve 401 o timeout, el flujo de chat continúa con chequeos técnicos (probe de dominio/SSL), pero marca estado Nexus en error/timeout.
- `twgetclientstatus/src/utils.py` hoy no maneja bien todos los errores de `response` vacío; conviene endurecer ese parseo si se va a usar en producción.
- Para agentes automáticos: priorizar siempre `domain` válido antes de intentar acciones.

---

## 8) Checklist para otro agente

1. Clonar o actualizar `twgetclientstatus`.
2. Configurar `.env` con credenciales Nexus válidas.
3. Levantar y probar endpoint local con `curl`.
4. Verificar que backend RAG tenga `TWNEXUS_USER/PASS` activos.
5. Validar un dominio real en chat (`plantascarnivoras.com`, por ejemplo).

