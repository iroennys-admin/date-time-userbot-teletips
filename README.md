<h1 align="center">DATE_TIME_USERBOT - Mejorado</h1>
<h3 align="center">Userbot de Telegram que convierte tu FOTO DE PERFIL y APELLIDO en un reloj en tiempo real, y cambia tu BIO automáticamente.</h3>
<p align="center">
<a href="https://python.org"><img src="http://forthebadge.com/images/badges/made-with-python.svg" alt="made-with-python"></a>
<br>
    <img src="https://img.shields.io/github/stars/iroennys-admin/date-time-userbot-teletips?style=for-the-badge" alt="Stars">
    <img src="https://img.shields.io/github/forks/iroennys-admin/date-time-userbot-teletips?style=for-the-badge" alt="Forks">
    <img src="https://img.shields.io/github/license/iroennys-admin/date-time-userbot-teletips?style=for-the-badge" alt="License">
    <img src="https://img.shields.io/github/repo-size/iroennys-admin/date-time-userbot-teletips?style=for-the-badge" alt="Repository Size">
</p>

## Novedades de esta versión mejorada

- Logging profesional con formato detallado
- Reconexión automática con backoff exponencial
- Generación de imágenes mejorada (fondo degradado, overlay, sombra de texto)
- Health check con Flask compatible con Render
- Manejo robusto de FloodWait y errores de sesión
- Limpieza automática de fotos de perfil antiguas
- Más de 80 frases motivacionales y 48 emojis
- Zona horaria configurable (por defecto: America/Havana)
- Deploy directo en Render

## Config Vars

| Variable | Descripción | Requerida | Valor por defecto |
|---|---|---|---|
| `API_ID` | Telegram API_ID, obtener en [my.telegram.org/apps](https://my.telegram.org/apps) | ✅ | - |
| `API_HASH` | Telegram API_HASH, obtener en [my.telegram.org/apps](https://my.telegram.org/apps) | ✅ | - |
| `SESSION_STRING` | Sesión válida de Pyrogram | ✅ | - |
| `TIME_ZONE` | Zona horaria | ❌ | `America/Havana` |
| `UPDATE_INTERVAL` | Intervalo de actualización en segundos | ❌ | `60` |
| `MAX_RETRIES` | Máximo de reintentos ante errores | ❌ | `5` |

## Deploy en Render

### Método 1: Blueprint (recomendado)

1. Haz fork de este repositorio
2. Ve a [Render Dashboard](https://dashboard.render.com)
3. Click en **New** → **Blueprint**
4. Selecciona tu repositorio fork
5. Configura las variables de entorno:
   - `API_ID` = tu API ID
   - `API_HASH` = tu API Hash
   - `SESSION_STRING` = tu session string de Pyrogram
6. Click en **Apply**

### Método 2: Manual

1. Ve a [Render Dashboard](https://dashboard.render.com)
2. Click en **New** → **Web Service**
3. Conecta tu repositorio
4. Configura:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python3 date_time_userbot.py`
5. Agrega las variables de entorno
6. Click en **Create Web Service**

## Generar SESSION_STRING

Ejecuta este script en tu máquina local o Termux:

```python
from pyrogram import Client

api_id = TU_API_ID
api_hash = "TU_API_HASH"

with Client(":memory:", api_id=api_id, api_hash=api_hash) as app:
    print(app.export_session_string())
```

## Funcionamiento

El bot actualiza tu perfil de Telegram cada 60 segundos:

1. **Foto de perfil**: Genera una imagen con la hora actual en formato digital
2. **Apellido**: `| ⏰ 02:30 PM | 📅 May 22, 2026`
3. **Bio**: Emoji aleatorio + Frase motivacional aleatoria

## Créditos

- [TeLe TiPs](https://github.com/teletips) - Proyecto original
- [Pyrogram](https://github.com/pyrogram/pyrogram) - Framework de Telegram
- [Thakshaka](https://t.me/thakshakar) - Colaborador original

## Licencia

[GNU Affero General Public License v3.0](https://github.com/iroennys-admin/date-time-userbot-teletips/blob/main/LICENSE)
