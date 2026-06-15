#!/usr/bin/env python3
"""
DATE TIME USERBOT v3.1 - Maquina Potente
FIX: Pyrogram update handling, command registration, event loop.
"""

import os
import sys
import logging
import asyncio
import datetime
import traceback
import threading
import time as time_mod
import urllib.request
from pathlib import Path

# ─── Logging ──────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("DateTimeUserbot")

# ─── Estado global del bot ──────────────────────────────────────
bot_state = {
    "started": False,
    "connected": False,
    "bot_active": True,
    "last_update": None,
    "error": None,
    "startup_log": [],
    "profile_name": None,
    "update_count": 0,
    "start_time": time_mod.time(),
    "image_style": "auto",
    "bg_theme": "",
    "bio_category": "random",
    "schedule_mode": True,
    "show_weather": True,
    "show_progress": True,
    "afk_enabled": True,
    "afk_message": "No estoy disponible ahora.",
    "afk_since": "",
    "afk_replied": set(),
    "countdown_date": "",
    "countdown_label": "",
    "weather_info": None,
    "python_version": sys.version,
    "mood": "",
    "mood_emoji": "",
    "mood_bio": "",
    "custom_bio": "",
    "custom_last_name": "",
    "update_interval": 60,
    "notes": {},
    "restart_requested": False,
    "photo_flood_wait_until": 0,
    "photo_update_counter": 0,
    "last_photo_time": 0,
    "reminders": [],
    "pm_permit": False,
    "approved_users": set(),
    "sed_count": 0,
    "command_count": 0,
}

def log_startup(msg):
    logger.info(msg)
    bot_state["startup_log"].append(f"{datetime.datetime.now().strftime('%H:%M:%S')} | {msg}")
    bot_state["startup_log"] = bot_state["startup_log"][-50:]

# ─── Flask App (arranca PRIMERO) ─────────────────────────────────
from flask import Flask, jsonify
app = Flask(__name__)

@app.route("/")
def health_check():
    return jsonify({
        "status": "alive",
        "bot": "DateTimeUserbot v3.1",
        "connected": bot_state["connected"],
        "bot_active": bot_state["bot_active"],
        "last_update": bot_state["last_update"],
        "update_count": bot_state["update_count"],
        "style": bot_state["image_style"],
        "theme": bot_state.get("bg_theme", "auto"),
        "mood": bot_state.get("mood", "none"),
        "command_count": bot_state.get("command_count", 0),
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "bot_connected": bot_state["connected"], "bot_active": bot_state["bot_active"]})

@app.route("/debug")
def debug_info():
    return jsonify({
        "status": "alive",
        "bot_started": bot_state["started"],
        "bot_connected": bot_state["connected"],
        "bot_active": bot_state["bot_active"],
        "profile_name": bot_state["profile_name"],
        "last_update": bot_state["last_update"],
        "update_count": bot_state["update_count"],
        "error": bot_state["error"],
        "image_style": bot_state["image_style"],
        "bg_theme": bot_state.get("bg_theme", ""),
        "bio_category": bot_state["bio_category"],
        "mood": bot_state.get("mood", ""),
        "show_weather": bot_state["show_weather"],
        "show_progress": bot_state["show_progress"],
        "afk_enabled": bot_state["afk_enabled"],
        "countdown": bot_state["countdown_date"],
        "update_interval": bot_state.get("update_interval", 60),
        "notes_count": len(bot_state.get("notes", {})),
        "reminders_count": len(bot_state.get("reminders", [])),
        "command_count": bot_state.get("command_count", 0),
        "python_version": sys.version,
        "startup_log": bot_state["startup_log"],
    })

log_startup("Flask app creada - v3.1")

# ─── Cargar configuracion ────────────────────────────────────────
try:
    from config import (
        API_ID, API_HASH, SESSION_STRING, TIME_ZONE, UPDATE_INTERVAL,
        MAX_RETRIES, PORT, EXTRA_TIMEZONES, FONT_PATH, BASE_IMAGE,
        IMAGE_STYLE, BIO_CATEGORY, BIO_CUSTOM_PREFIX, BIO_SHOW_COUNTER,
        BIO_SCHEDULE_MODE, WEATHER_CITY, WEATHER_SHOW, COUNTDOWN_DATE,
        COUNTDOWN_LABEL, AFK_ENABLED, AFK_MESSAGE, NOTIFY_CHAT_ID,
        SHOW_DAY_PROGRESS, DYNAMIC_HOUR_EMOJI, MONITOR_TIMEOUT,
    )
    log_startup(f"Config cargada - TZ: {TIME_ZONE}, PORT: {PORT}")
    bot_state["image_style"] = IMAGE_STYLE
    bot_state["bio_category"] = BIO_CATEGORY
    bot_state["schedule_mode"] = BIO_SCHEDULE_MODE
    bot_state["show_weather"] = WEATHER_SHOW
    bot_state["show_progress"] = SHOW_DAY_PROGRESS
    bot_state["afk_enabled"] = AFK_ENABLED
    bot_state["afk_message"] = AFK_MESSAGE
    bot_state["countdown_date"] = COUNTDOWN_DATE
    bot_state["countdown_label"] = COUNTDOWN_LABEL
    bot_state["update_interval"] = UPDATE_INTERVAL
except Exception as e:
    log_startup(f"ERROR cargando config: {e}")
    API_ID = int(os.environ.get("API_ID", "14681595"))
    API_HASH = os.environ.get("API_HASH", "a86730aab5c59953c424abb4396d32d5")
    SESSION_STRING = os.environ.get("SESSION_STRING", "")
    TIME_ZONE = os.environ.get("TIME_ZONE", "America/Havana")
    UPDATE_INTERVAL = int(os.environ.get("UPDATE_INTERVAL", "60"))
    MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "5"))
    PORT = int(os.environ.get("PORT", 10000))
    EXTRA_TIMEZONES = os.environ.get("EXTRA_TIMEZONES", "")
    FONT_PATH = os.environ.get("FONT_PATH", "ds-digit.ttf")
    BASE_IMAGE = os.environ.get("BASE_IMAGE", "image.jpg")
    IMAGE_STYLE = os.environ.get("IMAGE_STYLE", "auto")
    BIO_CUSTOM_PREFIX = os.environ.get("BIO_CUSTOM_PREFIX", "")
    BIO_SHOW_COUNTER = True
    BIO_SCHEDULE_MODE = True
    WEATHER_CITY = os.environ.get("WEATHER_CITY", "Havana")
    WEATHER_SHOW = True
    COUNTDOWN_DATE = ""
    COUNTDOWN_LABEL = ""
    AFK_ENABLED = True
    AFK_MESSAGE = "No estoy disponible ahora."
    NOTIFY_CHAT_ID = 0
    SHOW_DAY_PROGRESS = True
    DYNAMIC_HOUR_EMOJI = True
    MONITOR_TIMEOUT = 300

# ─── Imports pesados (con manejo de errores) ─────────────────────
pyrogram_ok = False
try:
    from pyrogram import Client, filters
    from pyrogram.errors import FloodWait, AuthKeyUnregistered, SessionRevoked
    pyrogram_ok = True
    log_startup("Pyrogram importado OK")
except Exception as e:
    log_startup(f"ERROR importando Pyrogram: {e}")

pil_ok = False
try:
    from PIL import Image, ImageDraw, ImageFont
    pil_ok = True
    log_startup("PIL importado OK")
except Exception as e:
    log_startup(f"ERROR importando PIL: {e}")

try:
    import pytz
    log_startup("pytz importado OK")
except Exception as e:
    log_startup(f"ERROR importando pytz: {e}")

image_gen_ok = False
try:
    from image_generator import generate_profile_image
    image_gen_ok = True
    log_startup("Image generator importado OK")
except Exception as e:
    log_startup(f"ERROR importando image_generator: {e}")

weather_ok = False
try:
    from weather import get_weather
    weather_ok = True
    log_startup("Weather importado OK")
except Exception as e:
    log_startup(f"ERROR importando weather: {e}")

emojis_ok = False
try:
    from lists_teletips.emojis_teletips import get_emoji, general_emojis
    emojis_ok = True
    log_startup("Emojis importado OK")
except Exception as e:
    log_startup(f"ERROR importando emojis: {e}")

quotes_ok = False
try:
    from lists_teletips.quotes_teletips import get_quote, quotes_by_category
    quotes_ok = True
    log_startup("Quotes importado OK")
except Exception as e:
    log_startup(f"ERROR importando quotes: {e}")

# ─── Cliente Pyrogram ─────────────────────────────────────────────
userbot = None
if pyrogram_ok:
    try:
        userbot = Client(
            name="date_time_userbot",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=SESSION_STRING,
        )
        log_startup("Pyrogram Client creado")
    except Exception as e:
        log_startup(f"ERROR creando Pyrogram Client: {e}")

# ─── Registrar Dashboard ──────────────────────────────────────────
try:
    from dashboard import register_dashboard
    register_dashboard(app, bot_state, config_module=__import__('config'))
    log_startup("Dashboard registrado")
except Exception as e:
    log_startup(f"ERROR registrando dashboard: {e}")

# ─── Registrar Comandos ───────────────────────────────────────────
try:
    from commands import register_commands
    log_startup("Modulo de comandos importado")
except Exception as e:
    register_commands = None
    log_startup(f"ERROR importando modulo de comandos: {e}")

# ─── Notificaciones ───────────────────────────────────────────────
async def send_notification(message: str):
    if not NOTIFY_CHAT_ID or not userbot:
        return
    try:
        await userbot.send_message(NOTIFY_CHAT_ID, f"🤖 {message}")
    except Exception as e:
        logger.debug(f"No se pudo enviar notificacion: {e}")

# ─── Procesar recordatorios ───────────────────────────────────────
async def process_reminders():
    """Verifica y envia recordatorios pendientes."""
    if not userbot or not bot_state["connected"]:
        return
    
    now = time_mod.time()
    remaining = []
    for rem in bot_state.get("reminders", []):
        if now >= rem["trigger_time"]:
            try:
                await userbot.send_message(
                    rem["chat_id"],
                    f"⏰ **Recordatorio!**\n\n{rem['text']}"
                )
            except Exception as e:
                logger.debug(f"Error enviando recordatorio: {e}")
        else:
            remaining.append(rem)
    bot_state["reminders"] = remaining

# ─── Calcular Countdown ───────────────────────────────────────────
def get_countdown_days() -> tuple:
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
            short_name = tz_name.split("/")[-1].replace("_", " ")
            results.append((short_name, now_tz.strftime("%I:%M %p")))
        except Exception:
            pass
    return results

# ─── Calcular uptime ──────────────────────────────────────────────
def get_uptime_str() -> str:
    uptime_s = int(time_mod.time() - bot_state.get("start_time", time_mod.time()))
    hours = uptime_s // 3600
    minutes = (uptime_s % 3600) // 60
    if hours > 0:
        return f"{hours}h{minutes}m"
    return f"{minutes}m"

# ─── Bucle Principal del Bot ──────────────────────────────────────
async def main_bot():
    if not userbot:
        log_startup("No se puede iniciar bot: Pyrogram no disponible")
        return

    retry_count = 0
    base_delay = 5
    last_success_time = 0
    monitor_enabled = False
    consecutive_failures = 0

    bot_state["started"] = True
    log_startup("Iniciando bucle principal v3.1...")

    # Conectar
    try:
        await userbot.start()
        me = await userbot.get_me()
        bot_state["connected"] = True
        bot_state["profile_name"] = me.first_name
        bot_state["start_time"] = time_mod.time()
        last_success_time = time_mod.time()
        log_startup(f"Conectado como: {me.first_name} (ID: {me.id})")
        
        # CRITICAL: Registrar comandos DESPUES de start()
        # Esto asegura que el dispatcher este correctamente inicializado
        try:
            if register_commands:
                register_commands(userbot, bot_state)
                log_startup("Comandos registrados DESPUES de start() - OK")
        except Exception as e:
            log_startup(f"ERROR registrando comandos despues de start(): {e}")
        
        await send_notification(f"Bot iniciado! Conectado como {me.first_name}")
    except (AuthKeyUnregistered, SessionRevoked) as e:
        log_startup(f"Sesion invalida: {e}")
        bot_state["error"] = str(e)
        return
    except Exception as e:
        log_startup(f"Error al iniciar: {e}")
        bot_state["error"] = str(e)

    log_startup("Entrando al bucle principal de actualizaciones...")
    while True:
        try:
            # Verificar reinicio solicitado
            if bot_state.get("restart_requested", False):
                log_startup("Reinicio solicitado via comando...")
                bot_state["restart_requested"] = False
                try:
                    await userbot.stop()
                except:
                    pass
                bot_state["connected"] = False
                await asyncio.sleep(3)
                await userbot.start()
                me = await userbot.get_me()
                bot_state["connected"] = True
                bot_state["profile_name"] = me.first_name
                last_success_time = time_mod.time()
                consecutive_failures = 0
                monitor_enabled = True
                log_startup(f"Reiniciado como: {me.first_name}")
                # Re-registrar handlers despues de reinicio
                try:
                    register_commands(userbot, bot_state)
                    log_startup("Comandos re-registrados tras reinicio")
                except Exception as e:
                    log_startup(f"Error re-registrando comandos: {e}")
                continue

            # Reconexion si esta desconectado (con backoff)
            if not bot_state["connected"]:
                retry_count += 1
                delay = min(base_delay * (2 ** min(retry_count, 6)), 300)
                log_startup(f"Intentando reconectar (intento {retry_count}, esperando {delay}s)...")
                try:
                    await userbot.stop()
                except:
                    pass
                await asyncio.sleep(delay)
                try:
                    await userbot.start()
                    me = await userbot.get_me()
                    bot_state["connected"] = True
                    bot_state["profile_name"] = me.first_name
                    last_success_time = time_mod.time()
                    retry_count = 0
                    consecutive_failures = 0
                    monitor_enabled = True
                    log_startup(f"Reconectado como: {me.first_name}")
                    # Re-registrar handlers despues de reconectar
                    try:
                        register_commands(userbot, bot_state)
                        log_startup("Comandos re-registrados tras reconexion")
                    except Exception as e:
                        log_startup(f"Error re-registrando comandos: {e}")
                except (AuthKeyUnregistered, SessionRevoked) as e:
                    log_startup(f"Sesion invalida al reconectar: {e}")
                    bot_state["error"] = str(e)
                    bot_state["connected"] = False
                    await asyncio.sleep(60)
                    continue
                except Exception as e:
                    log_startup(f"Error reconectando: {e}")
                    bot_state["connected"] = False
                    continue

            # Monitoreo proactivo
            if monitor_enabled and last_success_time > 0:
                current_time = time_mod.time()
                time_since_last = current_time - last_success_time
                if time_since_last > MONITOR_TIMEOUT:
                    log_startup(f"No se actualizo en {int(time_since_last)}s. Forzando reconexion...")
                    bot_state["connected"] = False
                    monitor_enabled = False
                    continue

            # Procesar recordatorios
            await process_reminders()

            # Si el bot esta PAUSADO (.off), solo dormir
            if not bot_state.get("bot_active", True):
                await asyncio.sleep(10)
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
            emoji = get_emoji(hour, dynamic=DYNAMIC_HOUR_EMOJI) if emojis_ok else "✨"

            # ── Frase ──
            quote = get_quote(
                category=bot_state.get("bio_category", "random"),
                hour=hour,
                schedule_mode=bot_state.get("schedule_mode", True),
            ) if quotes_ok else "Live your best life"

            # ── Clima ──
            weather_data = None
            if bot_state.get("show_weather", True) and weather_ok:
                weather_data = get_weather(WEATHER_CITY)
                bot_state["weather_info"] = f"{weather_data['emoji']} {weather_data['temp']}"

            # ── Countdown ──
            countdown_days, countdown_label = get_countdown_days()

            # ── Zonas horarias extra ──
            extra_tz = get_extra_tz_times()

            # ── Uptime ──
            uptime_str = get_uptime_str()

            # ── Generar imagen ──
            image_path = None
            if image_gen_ok:
                image_path = generate_profile_image(
                    time_str=time_str,
                    date_str=date_str,
                    hour=hour,
                    style=bot_state.get("image_style", "auto"),
                    bg_theme=bot_state.get("bg_theme", ""),
                    base_image=BASE_IMAGE,
                    font_path=FONT_PATH,
                    weather=weather_data,
                    show_progress=bot_state.get("show_progress", True),
                    countdown_days=countdown_days,
                    countdown_label=countdown_label,
                    extra_tz_times=extra_tz,
                    mood_emoji=bot_state.get("mood_emoji", ""),
                    uptime_str=uptime_str,
                )

            # Solo subir foto cada 5 ciclos (5 min) o si nunca se ha subido
            current_time = time_mod.time()
            should_upload_photo = (
                bot_state.get("last_photo_time", 0) == 0 or
                (current_time - bot_state.get("last_photo_time", 0)) >= 300
            )

            # No subir si estamos en FloodWait
            if current_time < bot_state.get("photo_flood_wait_until", 0):
                remaining = int(bot_state["photo_flood_wait_until"] - current_time)
                should_upload_photo = False
                if bot_state.get("photo_update_counter", 0) % 10 == 0:
                    log_startup(f"FloodWait activo ({remaining}s restantes)")
            
            if image_path and should_upload_photo:
                try:
                    await asyncio.wait_for(userbot.set_profile_photo(photo=image_path), timeout=30)
                    bot_state["last_photo_time"] = time_mod.time()
                    log_startup("Foto subida OK")
                except asyncio.TimeoutError:
                    log_startup("TIMEOUT subiendo foto (30s)")
                except FloodWait as e:
                    flood_until = time_mod.time() + e.value
                    bot_state["photo_flood_wait_until"] = flood_until
                    log_startup(f"FloodWait foto: {e.value}s")
                    await asyncio.sleep(5)
                except Exception as e:
                    log_startup(f"Error subiendo foto: {e}")

                # Eliminar foto anterior
                if bot_state.get("last_photo_time", 0) > 0:
                    try:
                        photos = userbot.get_chat_photos("me")
                        async for i, photo in enumerate(photos):
                            if i >= 1:
                                await asyncio.wait_for(userbot.delete_profile_photos(photo.file_id), timeout=15)
                                break
                    except Exception:
                        pass

                try:
                    Path(image_path).unlink(missing_ok=True)
                except Exception:
                    pass
            else:
                if image_path:
                    try:
                        Path(image_path).unlink(missing_ok=True)
                    except Exception:
                        pass
            
            bot_state["photo_update_counter"] = bot_state.get("photo_update_counter", 0) + 1

            # ── Actualizar apellido ──
            custom_ln = bot_state.get("custom_last_name", "")
            if custom_ln:
                last_name = custom_ln
            else:
                last_name = f"| {time_str} | {date_str}"
            
            # ── Actualizar bio ──
            custom_bio = bot_state.get("custom_bio", "")
            if custom_bio:
                bio = custom_bio
            else:
                bio_parts = []
                mood_bio = bot_state.get("mood_bio", "")
                if mood_bio:
                    bio_parts.append(mood_bio)
                else:
                    if BIO_CUSTOM_PREFIX:
                        bio_parts.append(BIO_CUSTOM_PREFIX)
                    bio_parts.append(f"{emoji} {quote}")
                
                if BIO_SHOW_COUNTER:
                    bio_parts.append(f"Dia {day_of_year}")
                bio = " | ".join(bio_parts)

            try:
                await userbot.update_profile(last_name=last_name, bio=bio)
                bot_state["last_update"] = now.isoformat()
                bot_state["update_count"] += 1
                last_success_time = time_mod.time()
                consecutive_failures = 0
                monitor_enabled = True
                if bot_state["update_count"] % 10 == 0:
                    log_startup(f"Perfil actualizado #{bot_state['update_count']}: {day_name} {time_str}")
            except FloodWait as e:
                logger.warning(f"FloodWait en perfil: {e.value}s")
                await asyncio.sleep(min(e.value, 60))
                continue

            retry_count = 0
            interval = bot_state.get("update_interval", UPDATE_INTERVAL)
            await asyncio.sleep(interval)

        except FloodWait as e:
            logger.warning(f"FloodWait global: {e.value}s")
            await asyncio.sleep(min(e.value, 120))

        except (AuthKeyUnregistered, SessionRevoked) as e:
            logger.critical(f"Sesion invalida: {e}")
            bot_state["connected"] = False
            bot_state["error"] = str(e)
            break

        except ConnectionError as e:
            retry_count += 1
            consecutive_failures += 1
            delay = min(base_delay * (2 ** min(retry_count, 6)), 300)
            logger.error(f"Error de conexion (intento {retry_count}): {e}")
            bot_state["connected"] = False
            await asyncio.sleep(delay)

        except Exception as e:
            retry_count += 1
            consecutive_failures += 1
            delay = min(base_delay * (2 ** min(retry_count, 6)), 300)
            log_startup(f"ERROR en bucle (intento {retry_count}): {e}")
            logger.error(f"Error inesperado (intento {retry_count}): {e}")
            logger.debug(traceback.format_exc())

            if consecutive_failures >= MAX_RETRIES * 3:
                logger.critical("Demasiados fallos consecutivos. Reiniciando cliente...")
                try:
                    await userbot.stop()
                except:
                    pass
                retry_count = 0
                consecutive_failures = 0
                bot_state["connected"] = False
                monitor_enabled = False

            await asyncio.sleep(delay)


# ─── Keep-Alive ────────────────────────────────────────────────────
def keep_alive():
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
    log_startup("=== DateTime Userbot v3.1 iniciando ===")
    
    async def run_all():
        # Iniciar Flask en thread separado
        flask_thread = threading.Thread(
            target=lambda: app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False),
            daemon=True
        )
        flask_thread.start()
        log_startup(f"Flask iniciando en puerto {PORT}")
        
        keep_alive()
        
        # Ejecutar el bot
        await main_bot()

    # CRITICAL FIX: Use asyncio.run() for proper event loop handling
    # This ensures Pyrogram's update dispatcher works correctly
    try:
        asyncio.run(run_all())
    except KeyboardInterrupt:
        logger.info("Bot detenido por usuario")
    except Exception as e:
        logger.critical(f"Error fatal: {e}")
        logger.debug(traceback.format_exc())
