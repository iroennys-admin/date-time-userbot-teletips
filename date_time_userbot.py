#!/usr/bin/env python3
"""
DATE TIME USERBOT v2.0 - Versión Completa con 18 mejoras
Flask como servidor principal, Pyrogram en mismo event loop.

Mejoras incluidas:
1. Tema día/noche automático
2. Barra de progreso del día
3. Estilos de imagen (neon, retro, minimal, gradient, auto)
4. Emoji dinámico por hora
5. Clima real en imagen
6. Frases por categoría
7. Bio por horario
8. Contador en bio
9. Bio personalizada con prefijo
10. Comandos por Telegram
11. Modo AFK
12. Notificaciones de errores
13. Web Dashboard
14. Countdown
15. Múltiples zonas horarias
16. Monitoreo proactivo
17. Keep-alive para Render
18. Reconexión automática mejorada
"""

import os
import sys
import logging
import asyncio
import datetime
import random
import traceback
import threading
import urllib.request
from pathlib import Path

# ─── Event loop ANTES de importar Pyrogram ─────────────────────────
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

from pyrogram import Client, filters
from pyrogram.errors import FloodWait, AuthKeyUnregistered, SessionRevoked
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, jsonify
import pytz

from config import *
from image_generator import generate_profile_image
from weather import get_weather
from lists_teletips.emojis_teletips import get_emoji, general_emojis
from lists_teletips.quotes_teletips import get_quote, quotes_by_category

# ─── Logging ──────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("DateTimeUserbot")

# ─── Estado global del bot (modificable vía comandos) ──────────────
bot_state = {
    "started": False,
    "connected": False,
    "last_update": None,
    "error": None,
    "profile_name": None,
    "update_count": 0,
    # Configuración dinámica
    "image_style": IMAGE_STYLE,
    "bio_category": BIO_CATEGORY,
    "schedule_mode": BIO_SCHEDULE_MODE,
    "show_weather": WEATHER_SHOW,
    "show_progress": SHOW_DAY_PROGRESS,
    "afk_enabled": AFK_ENABLED,
    "afk_message": AFK_MESSAGE,
    "afk_replied": set(),
    "countdown_date": COUNTDOWN_DATE,
    "countdown_label": COUNTDOWN_LABEL,
    "weather_info": None,
}

# ─── Cliente Pyrogram ─────────────────────────────────────────────
userbot = Client(
    name="date_time_userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
)

# ─── Flask App ─────────────────────────────────────────────────────
app = Flask(__name__)

@app.route("/")
def health_check():
    return jsonify({
        "status": "alive",
        "bot": "DateTimeUserbot v2.0",
        "connected": bot_state["connected"],
        "timezone": TIME_ZONE,
        "last_update": bot_state["last_update"],
        "update_count": bot_state["update_count"],
        "style": bot_state["image_style"],
        "timestamp": datetime.datetime.now(pytz.timezone(TIME_ZONE)).isoformat(),
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "bot_connected": bot_state["connected"]})

@app.route("/debug")
def debug_info():
    return jsonify({
        "status": "alive",
        "bot_started": bot_state["started"],
        "bot_connected": bot_state["connected"],
        "profile_name": bot_state["profile_name"],
        "last_update": bot_state["last_update"],
        "update_count": bot_state["update_count"],
        "error": bot_state["error"],
        "image_style": bot_state["image_style"],
        "bio_category": bot_state["bio_category"],
        "show_weather": bot_state["show_weather"],
        "show_progress": bot_state["show_progress"],
        "afk_enabled": bot_state["afk_enabled"],
        "countdown": bot_state["countdown_date"],
        "python_version": sys.version,
    })

# ─── Registrar Dashboard ──────────────────────────────────────────
from dashboard import register_dashboard
register_dashboard(app, bot_state, config=__import__('config'))

# ─── Registrar Comandos ───────────────────────────────────────────
from commands import register_commands
register_commands(userbot, bot_state)

# ─── Notificaciones ───────────────────────────────────────────────
async def send_notification(message: str):
    """Envía una notificación al chat configurado."""
    if not NOTIFY_CHAT_ID:
        return
    try:
        await userbot.send_message(NOTIFY_CHAT_ID, f"🤖 {message}")
    except Exception as e:
        logger.debug(f"No se pudo enviar notificación: {e}")

# ─── Calcular Countdown ───────────────────────────────────────────
def get_countdown_days() -> tuple:
    """Retorna (días_restantes, label) o (None, None)."""
    cd_date = bot_state.get("countdown_date", "")
    if not cd_date:
        return None, None
    try:
        target = datetime.datetime.strptime(cd_date, "%Y-%m-%d").date()
        today = datetime.date.today()
        days = (target - today).days
        return days, bot_state.get("countdown_label", "")
    except Exception:
        return None, None

# ─── Zonas horarias adicionales ───────────────────────────────────
def get_extra_tz_times() -> list:
    """Obtiene la hora en zonas horarias adicionales."""
    extra_tz = EXTRA_TIMEZONES
    if not extra_tz:
        return []
    
    results = []
    for tz_name in extra_tz.split(","):
        tz_name = tz_name.strip()
        if not tz_name:
            continue
        try:
            tz = pytz.timezone(tz_name)
            now_tz = datetime.datetime.now(tz)
            # Nombre corto de la zona
            short_name = tz_name.split("/")[-1].replace("_", " ")
            results.append((short_name, now_tz.strftime("%I:%M %p")))
        except Exception:
            pass
    return results

# ─── Bucle Principal del Bot ──────────────────────────────────────
async def main_bot():
    """Bucle principal que actualiza el perfil periódicamente."""
    retry_count = 0
    base_delay = 5
    last_success_time = 0

    bot_status_copy = bot_state  # Referencia al estado global
    bot_status_copy["started"] = True
    logger.info("Iniciando DateTime Userbot v2.0...")

    # Conectar
    try:
        await userbot.start()
        me = await userbot.get_me()
        bot_status_copy["connected"] = True
        bot_status_copy["profile_name"] = me.first_name
        logger.info(f"Conectado como: {me.first_name} (ID: {me.id})")
        await send_notification(f"Bot iniciado ✅\nConectado como: {me.first_name}")
    except (AuthKeyUnregistered, SessionRevoked) as e:
        logger.critical(f"Sesión inválida: {e}")
        bot_status_copy["error"] = str(e)
        await send_notification(f"Bot ERROR ❌\nSesión inválida: {e}")
        return
    except Exception as e:
        logger.error(f"Error al iniciar: {e}")
        bot_status_copy["error"] = str(e)

    while True:
        try:
            # ── Reconexión si está desconectado ──
            if not bot_status_copy["connected"]:
                logger.info("Intentando reconectar...")
                try:
                    await userbot.stop()
                except Exception:
                    pass
                await userbot.start()
                me = await userbot.get_me()
                bot_status_copy["connected"] = True
                bot_status_copy["profile_name"] = me.first_name
                retry_count = 0
                logger.info(f"Reconectado como: {me.first_name}")
                await send_notification("Bot reconectado ✅")

            # ── Monitoreo proactivo ──
            import time
            current_time = time.time()
            if last_success_time > 0 and (current_time - last_success_time) > MONITOR_TIMEOUT:
                logger.warning(f"No se actualizó en {MONITOR_TIMEOUT}s. Forzando reconexión...")
                bot_status_copy["connected"] = False
                continue

            # ── Obtener hora ──
            tz = pytz.timezone(TIME_ZONE)
            now = datetime.datetime.now(tz)
            hour = now.hour

            time_str = now.strftime("%I:%M %p")
            date_str = now.strftime("%b %d, %Y")
            day_name = now.strftime("%A")
            day_of_year = now.timetuple().tm_yday

            # ── Emoji ──
            emoji = get_emoji(hour, dynamic=DYNAMIC_HOUR_EMOJI)

            # ── Frase ──
            quote = get_quote(
                category=bot_status_copy.get("bio_category", "random"),
                hour=hour,
                schedule_mode=bot_status_copy.get("schedule_mode", True),
            )

            # ── Clima ──
            weather_data = None
            if bot_status_copy.get("show_weather", True):
                weather_data = get_weather(WEATHER_CITY)
                bot_status_copy["weather_info"] = f"{weather_data['emoji']} {weather_data['temp']}"

            # ── Countdown ──
            countdown_days, countdown_label = get_countdown_days()

            # ── Zonas horarias extra ──
            extra_tz = get_extra_tz_times()

            # ── Generar imagen ──
            image_path = generate_profile_image(
                time_str=time_str,
                date_str=date_str,
                hour=hour,
                style=bot_status_copy.get("image_style", "auto"),
                base_image=BASE_IMAGE,
                font_path=FONT_PATH,
                weather=weather_data,
                show_progress=bot_status_copy.get("show_progress", True),
                countdown_days=countdown_days,
                countdown_label=countdown_label,
                extra_tz_times=extra_tz,
            )

            if image_path:
                try:
                    await userbot.set_profile_photo(photo=image_path)
                    logger.info("Foto de perfil actualizada")
                except FloodWait as e:
                    logger.warning(f"FloodWait en foto: {e.value}s")
                    await asyncio.sleep(e.value)
                    continue
                except Exception as e:
                    logger.error(f"Error actualizando foto: {e}")

                # Eliminar foto anterior
                try:
                    photos = userbot.get_chat_photos("me")
                    async for i, photo in enumerate(photos):
                        if i >= 1:
                            await userbot.delete_profile_photos(photo.file_id)
                            break
                except Exception:
                    pass

                try:
                    Path(image_path).unlink(missing_ok=True)
                except Exception:
                    pass

            # ── Actualizar apellido y bio ──
            last_name = f"| {time_str} | {date_str}"
            
            # Construir bio con todas las opciones
            bio_parts = []
            
            # Prefijo personalizado
            if BIO_CUSTOM_PREFIX:
                bio_parts.append(BIO_CUSTOM_PREFIX)
            
            # Emoji + frase
            bio_parts.append(f"{emoji} {quote}")
            
            # Contador
            if BIO_SHOW_COUNTER:
                bio_parts.append(f"Día {day_of_year}")
            
            bio = " | ".join(bio_parts)

            try:
                await userbot.update_profile(last_name=last_name, bio=bio)
                bot_status_copy["last_update"] = now.isoformat()
                bot_status_copy["update_count"] += 1
                last_success_time = time.time()
                logger.info(f"Perfil actualizado: {day_name} {time_str}")
            except FloodWait as e:
                logger.warning(f"FloodWait en perfil: {e.value}s")
                await asyncio.sleep(e.value)
                continue

            retry_count = 0
            await asyncio.sleep(UPDATE_INTERVAL)

        except FloodWait as e:
            logger.warning(f"FloodWait global: {e.value}s")
            await asyncio.sleep(e.value)

        except (AuthKeyUnregistered, SessionRevoked) as e:
            logger.critical(f"Sesión inválida: {e}")
            bot_state["connected"] = False
            bot_state["error"] = str(e)
            await send_notification(f"Bot DETENIDO ❌\nSesión revocada: {e}")
            break

        except ConnectionError as e:
            retry_count += 1
            delay = min(base_delay * (2 ** retry_count), 300)
            logger.error(f"Error de conexión (intento {retry_count}): {e}")
            bot_state["connected"] = False
            await asyncio.sleep(delay)

        except Exception as e:
            retry_count += 1
            delay = min(base_delay * (2 ** retry_count), 300)
            logger.error(f"Error inesperado (intento {retry_count}): {e}")
            logger.debug(traceback.format_exc())

            if retry_count >= MAX_RETRIES:
                logger.critical("Máximo reintentos. Reiniciando cliente...")
                await send_notification(f"Bot reiniciándose ⚠️\nError: {e}")
                try:
                    await userbot.stop()
                except Exception:
                    pass
                retry_count = 0
                bot_state["connected"] = False

            await asyncio.sleep(delay)


# ─── Keep-Alive ────────────────────────────────────────────────────
def keep_alive():
    """Auto-ping cada 14 minutos para Render free."""
    render_url = os.environ.get("RENDER_EXTERNAL_URL", "")
    if not render_url:
        render_url = os.environ.get("RENDER_SERVICE_URL", "")
    
    if render_url:
        def ping():
            while True:
                try:
                    urllib.request.urlopen(f"{render_url}/health", timeout=10)
                except Exception:
                    pass
                threading.Event().wait(14 * 60)
        
        t = threading.Thread(target=ping, daemon=True)
        t.start()
        logger.info(f"Keep-alive activado: {render_url}/health")
    else:
        logger.warning("Keep-alive: RENDER_EXTERNAL_URL no encontrada")


# ─── Punto de Entrada ─────────────────────────────────────────────
if __name__ == "__main__":
    async def run_all():
        bot_task = asyncio.ensure_future(main_bot())
        
        flask_thread = threading.Thread(
            target=lambda: app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False),
            daemon=True
        )
        flask_thread.start()
        logger.info(f"Flask en puerto {PORT}")
        
        keep_alive()
        
        await bot_task

    logger.info("🚀 DateTime Userbot v2.0 iniciando...")
    loop.run_until_complete(run_all())
