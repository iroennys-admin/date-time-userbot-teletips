#!/usr/bin/env python3
"""Configuración centralizada del DateTime Userbot."""

import os

# ─── Credenciales de Telegram ──────────────────────────────────────
API_ID = int(os.environ.get("API_ID", "14681595"))
API_HASH = os.environ.get("API_HASH", "a86730aab5c59953c424abb4396d32d5")
SESSION_STRING = os.environ.get("SESSION_STRING", "AQDgBfsAA1wQ2Lka011s9cskUPNHS4UIPGp8-C6KmTjZUEqoSrqL07TV_Wn4sihKBp4A5qag_e61zgJlfPdQrSfnqUhwKYVGn3rNsTCmMltVlA39AhFLWzyS_fToU3HwxYEn3VsutChqKCFArHZq08Fw_mZ__NETqeopo6zlnOKa_M-hF8xCiNeGukQ3zK076oRde9reAvF8IgRUEIUjp3OllhKU-6BFmC6WlOouJjobpBCzMc96m7QFV3p6jeauxTrhA_6fOGesFwuW65cEnXLBfI6SYtt_OgDC6iptax5UI-DgL3A12xEpje-X_EhPZ6L2ZmDF3NSy2wveIno9x90tNI-wFAAAAAHbE6seAA")

# ─── Configuración General ─────────────────────────────────────────
TIME_ZONE = os.environ.get("TIME_ZONE", "America/Havana")
UPDATE_INTERVAL = int(os.environ.get("UPDATE_INTERVAL", "60"))
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "5"))
PORT = int(os.environ.get("PORT", 10000))

# ─── Zonas horarias adicionales (separadas por coma) ───────────────
EXTRA_TIMEZONES = os.environ.get("EXTRA_TIMEZONES", "")  # ej: "Europe/Madrid,Asia/Tokyo"

# ─── Configuración de Imagen ───────────────────────────────────────
FONT_PATH = os.environ.get("FONT_PATH", "ds-digit.ttf")
BASE_IMAGE = os.environ.get("BASE_IMAGE", "image.jpg")
IMAGE_STYLE = os.environ.get("IMAGE_STYLE", "auto")  # auto, neon, retro, minimal, gradient, emoji

# ─── Configuración de Bio ──────────────────────────────────────────
BIO_CATEGORY = os.environ.get("BIO_CATEGORY", "random")  # random, motivation, humor, philosophy, love, tech, life
BIO_CUSTOM_PREFIX = os.environ.get("BIO_CUSTOM_PREFIX", "")  # Texto fijo antes de la frase
BIO_SHOW_COUNTER = os.environ.get("BIO_SHOW_COUNTER", "true").lower() == "true"
BIO_SCHEDULE_MODE = os.environ.get("BIO_SCHEDULE_MODE", "true").lower() == "true"  # Frases según horario

# ─── Configuración de Clima ────────────────────────────────────────
WEATHER_CITY = os.environ.get("WEATHER_CITY", "Havana")
WEATHER_SHOW = os.environ.get("WEATHER_SHOW", "true").lower() == "true"

# ─── Countdown ─────────────────────────────────────────────────────
COUNTDOWN_DATE = os.environ.get("COUNTDOWN_DATE", "")  # Formato: "2027-01-01"
COUNTDOWN_LABEL = os.environ.get("COUNTDOWN_LABEL", "")  # Ej: "Mi cumpleaños"

# ─── Modo AFK ──────────────────────────────────────────────────────
AFK_ENABLED = os.environ.get("AFK_ENABLED", "true").lower() == "true"
AFK_MESSAGE = os.environ.get("AFK_MESSAGE", "No estoy disponible ahora. Te responderé lo antes posible.")

# ─── Notificaciones ────────────────────────────────────────────────
NOTIFY_CHAT_ID = int(os.environ.get("NOTIFY_CHAT_ID", "0"))  # Tu ID de Telegram para notificaciones

# ─── Barra de progreso del día ─────────────────────────────────────
SHOW_DAY_PROGRESS = os.environ.get("SHOW_DAY_PROGRESS", "true").lower() == "true"

# ─── Emoji dinámico por hora ───────────────────────────────────────
DYNAMIC_HOUR_EMOJI = os.environ.get("DYNAMIC_HOUR_EMOJI", "true").lower() == "true"

# ─── Monitoreo proactivo ───────────────────────────────────────────
MONITOR_TIMEOUT = int(os.environ.get("MONITOR_TIMEOUT", "300"))  # 5 min sin update = reconectar
