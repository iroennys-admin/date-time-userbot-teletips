#!/usr/bin/env python3
"""
DATE TIME USERBOT - Versión Mejorada
Adaptado para Render con mejor manejo de errores, logging, y reconexión automática.

Mejoras respecto al original:
- Logging profesional con rotación
- Reconexión automática con backoff exponencial
- Generación de imágenes mejorada (fondo degradado, mejor tipografía)
- Health check con Flask para Render
- Manejo robusto de FloodWait y errores
- Configuración flexible de zona horaria
- Limpieza automática de fotos de perfil antiguas
- Soporte para variables de entorno con valores por defecto
"""

import os
import sys
import logging
import asyncio
import datetime
import random
import traceback
from pathlib import Path

from pyrogram import Client, filters
from pyrogram.errors import FloodWait, AuthKeyUnregistered, SessionRevoked
from flask import Flask, jsonify
import pytz
from PIL import Image, ImageDraw, ImageFont

# ─── Importar listas ──────────────────────────────────────────────
from lists_teletips.emojis_teletips import emojis_teletips
from lists_teletips.quotes_teletips import quotes_teletips

# ─── Configuración de Logging ────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("DateTimeUserbot")

# ─── Variables de Configuración ────────────────────────────────────
# Las variables se cargan desde entorno SI existen, sino usan los valores hardcodeados

API_ID = int(os.environ.get("API_ID", "14681595"))
API_HASH = os.environ.get("API_HASH", "a86730aab5c59953c424abb4396d32d5")
SESSION_STRING = os.environ.get("SESSION_STRING", "AQDgBfsAA1wQ2Lka011s9cskUPNHS4UIPGp8-C6KmTjZUEqoSrqL07TV_Wn4sihKBp4A5qag_e61zgJlfPdQrSfnqUhwKYVGn3rNsTCmMltVlA39AhFLWzyS_fToU3HwxYEn3VsutChqKCFArHZq08Fw_mZ__NETqeopo6zlnOKa_M-hF8xCiNeGukQ3zK076oRde9reAvF8IgRUEIUjp3OllhKU-6BFmC6WlOouJjobpBCzMc96m7QFV3p6jeauxTrhA_6fOGesFwuW65cEnXLBfI6SYtt_OgDC6iptax5UI-DgL3A12xEpje-X_EhPZ6L2ZmDF3NSy2wveIno9x90tNI-wFAAAAAHbE6seAA")
TIME_ZONE = os.environ.get("TIME_ZONE", "America/Havana")
UPDATE_INTERVAL = int(os.environ.get("UPDATE_INTERVAL", "60"))  # segundos
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "5"))
FONT_PATH = os.environ.get("FONT_PATH", "ds-digit.ttf")
BASE_IMAGE = os.environ.get("BASE_IMAGE", "image.jpg")

# Validar que las variables obligatorias estén presentes
if not API_ID or API_ID == 0:
    logger.error("❌ API_ID no configurado")
    sys.exit(1)
if not API_HASH:
    logger.error("❌ API_HASH no configurado")
    sys.exit(1)
if not SESSION_STRING:
    logger.error("❌ SESSION_STRING no configurado")
    sys.exit(1)

# ─── Flask Health Check (requerido para Render) ───────────────────
health_app = Flask(__name__)

@health_app.route("/")
def health_check():
    return jsonify({
        "status": "alive",
        "bot": "DateTimeUserbot",
        "timezone": TIME_ZONE,
        "timestamp": datetime.datetime.now(pytz.timezone(TIME_ZONE)).isoformat(),
    })

@health_app.route("/health")
def health():
    return jsonify({"status": "healthy"})

def run_flask():
    """Ejecuta Flask en un hilo separado para el health check de Render."""
    port = int(os.environ.get("PORT", 10000))
    health_app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

# ─── Cliente Pyrogram ─────────────────────────────────────────────
Date_Time_Userbot = Client(
    name="date_time_userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
)

# ─── Generador de Imágenes Mejorado ──────────────────────────────
def generate_profile_image(time_str: str, date_str: str) -> str:
    """
    Genera una imagen de perfil con la hora y fecha.
    Usa la imagen base si existe, o crea un fondo degradado profesional.
    """
    output_path = "profile_output.jpg"
    
    try:
        # Intentar usar imagen base del proyecto
        if Path(BASE_IMAGE).exists():
            img = Image.open(BASE_IMAGE)
            # Redimensionar a 512x512 (tamaño óptimo para foto de perfil de Telegram)
            img = img.resize((512, 512), Image.Resampling.LANCZOS)
        else:
            # Crear fondo degradado profesional si no hay imagen base
            img = create_gradient_background(512, 512)
        
        draw = ImageDraw.Draw(img)
        
        # Cargar fuente
        try:
            if Path(FONT_PATH).exists():
                font_large = ImageFont.truetype(FONT_PATH, 72)
                font_small = ImageFont.truetype(FONT_PATH, 36)
            else:
                # Fuente por defecto del sistema
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
        except Exception:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Dibujar overlay semitransparente para mejor legibilidad
        overlay = Image.new("RGBA", (512, 512), (0, 0, 0, 100))
        img_rgba = img.convert("RGBA")
        img_rgba = Image.alpha_composite(img_rgba, overlay)
        img = img_rgba.convert("RGB")
        draw = ImageDraw.Draw(img)
        
        # Centrar texto de hora
        img_width, img_height = img.size
        
        # Hora
        time_bbox = draw.textbbox((0, 0), time_str, font=font_large)
        time_w = time_bbox[2] - time_bbox[0]
        time_x = (img_width - time_w) // 2
        time_y = img_height // 2 - 60
        
        # Sombra del texto
        draw.text((time_x + 2, time_y + 2), time_str, (0, 0, 0), font=font_large)
        # Texto principal
        draw.text((time_x, time_y), time_str, (0, 255, 255), font=font_large)
        
        # Fecha
        date_bbox = draw.textbbox((0, 0), date_str, font=font_small)
        date_w = date_bbox[2] - date_bbox[0]
        date_x = (img_width - date_w) // 2
        date_y = time_y + 90
        
        draw.text((date_x + 2, date_y + 2), date_str, (0, 0, 0), font=font_small)
        draw.text((date_x, date_y), date_str, (255, 255, 255), font=font_small)
        
        img.save(output_path, "JPEG", quality=95)
        return output_path
        
    except Exception as e:
        logger.error(f"Error generando imagen: {e}")
        return None


def create_gradient_background(width: int, height: int) -> Image.Image:
    """Crea un fondo degradado profesional."""
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)
    
    # Degradado de azul oscuro a púrpura
    for y in range(height):
        r = int(20 + (80 - 20) * y / height)
        g = int(10 + (20 - 10) * y / height)
        b = int(60 + (120 - 60) * y / height)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    return img


# ─── Función Principal ────────────────────────────────────────────
async def update_profile():
    """Bucle principal que actualiza el perfil periódicamente."""
    retry_count = 0
    base_delay = 5  # segundos base para backoff
    
    while True:
        try:
            if not Date_Time_Userbot.is_connected:
                logger.warning("⚠️ Cliente desconectado. Intentando reconectar...")
                await Date_Time_Userbot.connect()
                retry_count = 0
                logger.info("✅ Reconectado exitosamente")
            
            # Obtener hora actual en la zona horaria configurada
            tz = pytz.timezone(TIME_ZONE)
            now = datetime.datetime.now(tz)
            
            time_str = now.strftime("%I:%M %p")
            date_str = now.strftime("%b %d, %Y")
            day_name = now.strftime("%A")
            
            # Seleccionar emoji y frase aleatorios
            emoji = random.choice(emojis_teletips)
            quote = random.choice(quotes_teletips)
            
            # Generar imagen de perfil
            image_path = generate_profile_image(time_str, date_str)
            
            if image_path:
                # Actualizar foto de perfil
                try:
                    await Date_Time_Userbot.set_profile_photo(photo=image_path)
                    logger.info("📸 Foto de perfil actualizada")
                except FloodWait as e:
                    logger.warning(f"⏳ FloodWait en foto: {e.value}s. Esperando...")
                    await asyncio.sleep(e.value)
                    continue
                except Exception as e:
                    logger.error(f"Error actualizando foto: {e}")
                
                # Eliminar foto anterior (mantener solo la más reciente)
                try:
                    photos = Date_Time_Userbot.get_chat_photos("me")
                    async for i, photo in enumerate(photos):
                        if i >= 1:  # Mantener solo la primera (la nueva)
                            await Date_Time_Userbot.delete_profile_photos(photo.file_id)
                            logger.debug("🗑️ Foto anterior eliminada")
                            break
                except Exception as e:
                    logger.debug(f"No se pudo eliminar foto anterior: {e}")
                
                # Limpiar archivo temporal
                try:
                    Path(image_path).unlink(missing_ok=True)
                except Exception:
                    pass
            
            # Actualizar apellido y bio
            last_name = f"| ⏰ {time_str} | 📅 {date_str}"
            bio = f"{emoji} {quote}"
            
            try:
                await Date_Time_Userbot.update_profile(
                    last_name=last_name,
                    bio=bio
                )
                logger.info(f"✅ Perfil actualizado: {day_name} {time_str} | Bio: {emoji}")
            except FloodWait as e:
                logger.warning(f"⏳ FloodWait en perfil: {e.value}s. Esperando...")
                await asyncio.sleep(e.value)
                continue
            
            # Reset retry counter on success
            retry_count = 0
            
            # Esperar antes de la próxima actualización
            await asyncio.sleep(UPDATE_INTERVAL)
            
        except FloodWait as e:
            logger.warning(f"⏳ FloodWait global: {e.value}s. Esperando...")
            await asyncio.sleep(e.value)
            
        except (AuthKeyUnregistered, SessionRevoked) as e:
            logger.critical(f"❌ Sesión inválida o revocada: {e}")
            logger.critical("Necesitas generar un nuevo SESSION_STRING")
            break
            
        except ConnectionError as e:
            retry_count += 1
            delay = min(base_delay * (2 ** retry_count), 300)  # Max 5 minutos
            logger.error(f"🔌 Error de conexión (intento {retry_count}/{MAX_RETRIES}): {e}")
            logger.info(f"Reintentando en {delay}s...")
            await asyncio.sleep(delay)
            
        except Exception as e:
            retry_count += 1
            delay = min(base_delay * (2 ** retry_count), 300)
            logger.error(f"❌ Error inesperado (intento {retry_count}/{MAX_RETRIES}): {e}")
            logger.debug(traceback.format_exc())
            
            if retry_count >= MAX_RETRIES:
                logger.critical("❌ Máximo de reintentos alcanzado. Reiniciando cliente...")
                try:
                    await Date_Time_Userbot.disconnect()
                except Exception:
                    pass
                retry_count = 0
            
            await asyncio.sleep(delay)


# ─── Punto de Entrada ─────────────────────────────────────────────
async def main():
    """Función principal que inicia el bot y el health check."""
    logger.info("🚀 Iniciando DateTime Userbot...")
    logger.info(f"🕐 Zona horaria: {TIME_ZONE}")
    logger.info(f"⏱️  Intervalo de actualización: {UPDATE_INTERVAL}s")
    
    # Iniciar Flask en segundo plano (health check para Render)
    import threading
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("🌐 Health check disponible en / y /health")
    
    # Iniciar cliente Pyrogram
    await Date_Time_Userbot.start()
    me = await Date_Time_Userbot.get_me()
    logger.info(f"✅ Conectado como: {me.first_name} (ID: {me.id})")
    
    # Ejecutar bucle de actualización
    await update_profile()


if __name__ == "__main__":
    asyncio.run(main())
