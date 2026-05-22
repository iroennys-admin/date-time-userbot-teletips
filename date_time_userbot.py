#!/usr/bin/env python3
"""
DATE TIME USERBOT - Versión Mejorada para Render
Flask como servidor principal (bind al puerto), Pyrogram en hilo secundario.
"""

import os
import sys
import logging
import asyncio
import datetime
import random
import traceback
import threading
from pathlib import Path

from flask import Flask, jsonify
import pytz

# ─── Configuración de Logging ────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("DateTimeUserbot")

# ─── Variables de Configuración ────────────────────────────────────
API_ID = int(os.environ.get("API_ID", "14681595"))
API_HASH = os.environ.get("API_HASH", "a86730aab5c59953c424abb4396d32d5")
SESSION_STRING = os.environ.get("SESSION_STRING", "AQDgBfsAA1wQ2Lka011s9cskUPNHS4UIPGp8-C6KmTjZUEqoSrqL07TV_Wn4sihKBp4A5qag_e61zgJlfPdQrSfnqUhwKYVGn3rNsTCmMltVlA39AhFLWzyS_fToU3HwxYEn3VsutChqKCFArHZq08Fw_mZ__NETqeopo6zlnOKa_M-hF8xCiNeGukQ3zK076oRde9reAvF8IgRUEIUjp3OllhKU-6BFmC6WlOouJjobpBCzMc96m7QFV3p6jeauxTrhA_6fOGesFwuW65cEnXLBfI6SYtt_OgDC6iptax5UI-DgL3A12xEpje-X_EhPZ6L2ZmDF3NSy2wveIno9x90tNI-wFAAAAAHbE6seAA")
TIME_ZONE = os.environ.get("TIME_ZONE", "America/Havana")
UPDATE_INTERVAL = int(os.environ.get("UPDATE_INTERVAL", "60"))
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "5"))
FONT_PATH = os.environ.get("FONT_PATH", "ds-digit.ttf")
BASE_IMAGE = os.environ.get("BASE_IMAGE", "image.jpg")

# ─── Estado global del bot ─────────────────────────────────────────
bot_status = {
    "started": False,
    "connected": False,
    "last_update": None,
    "error": None,
    "profile_name": None,
}

# ─── Flask App (servidor principal) ────────────────────────────────
app = Flask(__name__)

@app.route("/")
def health_check():
    return jsonify({
        "status": "alive",
        "bot": "DateTimeUserbot",
        "connected": bot_status["connected"],
        "timezone": TIME_ZONE,
        "last_update": bot_status["last_update"],
        "timestamp": datetime.datetime.now(pytz.timezone(TIME_ZONE)).isoformat(),
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "bot_connected": bot_status["connected"]})

# ─── Bucle del Bot en Hilo Separado ────────────────────────────────
def run_bot():
    """Ejecuta el bot de Telegram en su propio hilo con su propio event loop."""
    # Importar dentro del hilo para evitar conflictos
    from pyrogram import Client
    from pyrogram.errors import FloodWait, AuthKeyUnregistered, SessionRevoked
    from PIL import Image, ImageDraw, ImageFont
    from lists_teletips.emojis_teletips import emojis_teletips
    from lists_teletips.quotes_teletips import quotes_teletips

    # Crear event loop propio para este hilo
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # ─── Generador de Imágenes ──────────────────────────────────────
    def generate_profile_image(time_str: str, date_str: str) -> str:
        output_path = "profile_output.jpg"
        try:
            if Path(BASE_IMAGE).exists():
                img = Image.open(BASE_IMAGE).resize((512, 512), Image.Resampling.LANCZOS)
            else:
                img = create_gradient_background(512, 512)

            draw = ImageDraw.Draw(img)

            # Cargar fuente
            try:
                if Path(FONT_PATH).exists():
                    font_large = ImageFont.truetype(FONT_PATH, 72)
                    font_small = ImageFont.truetype(FONT_PATH, 36)
                else:
                    font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
                    font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
            except Exception:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()

            # Overlay semitransparente
            overlay = Image.new("RGBA", (512, 512), (0, 0, 0, 100))
            img_rgba = img.convert("RGBA")
            img_rgba = Image.alpha_composite(img_rgba, overlay)
            img = img_rgba.convert("RGB")
            draw = ImageDraw.Draw(img)

            img_width, img_height = img.size

            # Hora centrada
            time_bbox = draw.textbbox((0, 0), time_str, font=font_large)
            time_w = time_bbox[2] - time_bbox[0]
            time_x = (img_width - time_w) // 2
            time_y = img_height // 2 - 60
            draw.text((time_x + 2, time_y + 2), time_str, (0, 0, 0), font=font_large)
            draw.text((time_x, time_y), time_str, (0, 255, 255), font=font_large)

            # Fecha centrada
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

    def create_gradient_background(width: int, height: int):
        img = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(img)
        for y in range(height):
            r = int(20 + (80 - 20) * y / height)
            g = int(10 + (20 - 10) * y / height)
            b = int(60 + (120 - 60) * y / height)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        return img

    # ─── Cliente Pyrogram ─────────────────────────────────────────────
    userbot = Client(
        name="date_time_userbot",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION_STRING,
    )

    # ─── Bucle Principal ──────────────────────────────────────────────
    async def main_bot():
        retry_count = 0
        base_delay = 5

        logger.info("Iniciando cliente Pyrogram...")

        try:
            await userbot.start()
            me = await userbot.get_me()
            bot_status["connected"] = True
            bot_status["profile_name"] = me.first_name
            logger.info(f"Conectado como: {me.first_name} (ID: {me.id})")
        except (AuthKeyUnregistered, SessionRevoked) as e:
            logger.critical(f"Sesion invalida o revocada: {e}")
            bot_status["error"] = str(e)
            return
        except Exception as e:
            logger.error(f"Error al iniciar: {e}")
            bot_status["error"] = str(e)
            return

        while True:
            try:
                tz = pytz.timezone(TIME_ZONE)
                now = datetime.datetime.now(tz)

                time_str = now.strftime("%I:%M %p")
                date_str = now.strftime("%b %d, %Y")
                day_name = now.strftime("%A")

                emoji = random.choice(emojis_teletips)
                quote = random.choice(quotes_teletips)

                # Generar y actualizar foto de perfil
                image_path = generate_profile_image(time_str, date_str)
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

                # Actualizar apellido y bio
                last_name = f"| {time_str} | {date_str}"
                bio = f"{emoji} {quote}"

                try:
                    await userbot.update_profile(last_name=last_name, bio=bio)
                    bot_status["last_update"] = now.isoformat()
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
                logger.critical(f"Sesion invalida: {e}")
                bot_status["connected"] = False
                bot_status["error"] = str(e)
                break

            except ConnectionError as e:
                retry_count += 1
                delay = min(base_delay * (2 ** retry_count), 300)
                logger.error(f"Error de conexion (intento {retry_count}/{MAX_RETRIES}): {e}")
                bot_status["connected"] = False
                await asyncio.sleep(delay)

            except Exception as e:
                retry_count += 1
                delay = min(base_delay * (2 ** retry_count), 300)
                logger.error(f"Error inesperado (intento {retry_count}/{MAX_RETRIES}): {e}")
                logger.debug(traceback.format_exc())

                if retry_count >= MAX_RETRIES:
                    logger.critical("Maximo de reintentos alcanzado. Reiniciando...")
                    try:
                        await userbot.stop()
                    except Exception:
                        pass
                    retry_count = 0
                    bot_status["connected"] = False

                    # Intentar reconectar
                    try:
                        await userbot.start()
                        bot_status["connected"] = True
                        logger.info("Reconectado exitosamente")
                    except Exception as re:
                        logger.error(f"Error reconectando: {re}")

                await asyncio.sleep(delay)

    # Ejecutar el bot
    bot_status["started"] = True
    loop.run_until_complete(main_bot())

# ─── Punto de Entrada ─────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    # Iniciar el bot en un hilo daemon
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info("Hilo del bot iniciado en segundo plano")

    # Flask como servidor principal (Render necesita que bind al puerto)
    logger.info(f"Iniciando Flask health check en puerto {port}")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
