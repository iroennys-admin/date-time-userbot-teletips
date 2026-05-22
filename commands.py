#!/usr/bin/env python3
"""Comandos de Telegram para controlar el bot."""

from pyrogram import Client, filters
from config import (
    BIO_CATEGORY, IMAGE_STYLE, WEATHER_SHOW, SHOW_DAY_PROGRESS,
    DYNAMIC_HOUR_EMOJI, AFK_ENABLED, BIO_SCHEDULE_MODE, BIO_CUSTOM_PREFIX,
    BIO_SHOW_COUNTER, COUNTDOWN_DATE, COUNTDOWN_LABEL
)


def register_commands(app: Client, bot_state: dict):
    """Registra todos los comandos del bot."""
    
    @app.on_message(filters.command("style") & filters.me)
    async def style_command(client, message):
        """Cambia el estilo de imagen. Uso: .style neon|retro|minimal|gradient|auto"""
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            styles = "auto, neon, retro, minimal, gradient"
            await message.edit(f"📋 Estilos disponibles: {styles}\nUso: `.style neon`")
            return
        
        new_style = args[1].strip().lower()
        valid = ["auto", "neon", "retro", "minimal", "gradient"]
        if new_style not in valid:
            await message.edit(f"❌ Estilo inválido. Opciones: {', '.join(valid)}")
            return
        
        bot_state["image_style"] = new_style
        await message.edit(f"✅ Estilo cambiado a: **{new_style}**")
    
    @app.on_message(filters.command("quote") & filters.me)
    async def quote_command(client, message):
        """Cambia categoría de frases. Uso: .quote motivation|humor|philosophy|love|tech|life|random|schedule"""
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            cats = "random, motivation, humor, philosophy, love, tech, life, schedule"
            await message.edit(f"📋 Categorías: {cats}\nUso: `.quote humor`")
            return
        
        new_cat = args[1].strip().lower()
        valid = ["random", "motivation", "humor", "philosophy", "love", "tech", "life", "schedule"]
        if new_cat not in valid:
            await message.edit(f"❌ Categoría inválida. Opciones: {', '.join(valid)}")
            return
        
        if new_cat == "schedule":
            bot_state["schedule_mode"] = True
            bot_state["bio_category"] = "random"
        else:
            bot_state["schedule_mode"] = False
            bot_state["bio_category"] = new_cat
        
        await message.edit(f"✅ Categoría de frases: **{new_cat}**")
    
    @app.on_message(filters.command("weather") & filters.me)
    async def weather_command(client, message):
        """Activa/desactiva clima. Uso: .weather on|off"""
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            status = "✅ ON" if bot_state.get("show_weather", True) else "❌ OFF"
            await message.edit(f"🌤 Clima en imagen: {status}\nUso: `.weather on` o `.weather off`")
            return
        
        val = args[1].strip().lower()
        bot_state["show_weather"] = val in ("on", "yes", "true", "1", "si")
        status = "✅ activado" if bot_state["show_weather"] else "❌ desactivado"
        await message.edit(f"🌤 Clima {status}")
    
    @app.on_message(filters.command("progress") & filters.me)
    async def progress_command(client, message):
        """Activa/desactiva barra de progreso. Uso: .progress on|off"""
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            status = "✅ ON" if bot_state.get("show_progress", True) else "❌ OFF"
            await message.edit(f"📊 Progreso del día: {status}\nUso: `.progress on` o `.progress off`")
            return
        
        val = args[1].strip().lower()
        bot_state["show_progress"] = val in ("on", "yes", "true", "1", "si")
        status = "✅ activado" if bot_state["show_progress"] else "❌ desactivado"
        await message.edit(f"📊 Progreso {status}")
    
    @app.on_message(filters.command("countdown") & filters.me)
    async def countdown_command(client, message):
        """Configura countdown. Uso: .countdown 2027-01-01 Mi cumpleaños"""
        args = message.text.split(maxsplit=2)
        if len(args) < 2:
            current = f"{COUNTDOWN_DATE}" if COUNTDOWN_DATE else "No configurado"
            await message.edit(f"📅 Countdown actual: {current}\nUso: `.countdown 2027-01-01 Mi cumpleaños`")
            return
        
        if args[1].lower() in ("off", "clear", "remove"):
            bot_state["countdown_date"] = ""
            bot_state["countdown_label"] = ""
            await message.edit("📅 Countdown eliminado")
            return
        
        bot_state["countdown_date"] = args[1]
        bot_state["countdown_label"] = args[2] if len(args) > 2 else ""
        await message.edit(f"📅 Countdown: **{args[1]}** - {bot_state['countdown_label']}")
    
    @app.on_message(filters.command("afk") & filters.me)
    async def afk_command(client, message):
        """Activa/desactiva modo AFK. Uso: .afk on|off o .afk Mi mensaje personalizado"""
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            status = "✅ ON" if bot_state.get("afk_enabled", False) else "❌ OFF"
            await message.edit(f"📴 Modo AFK: {status}\nUso: `.afk on`, `.afk off`, `.afk Estoy ocupado`")
            return
        
        val = args[1].strip().lower()
        if val in ("on", "yes", "true", "1", "si"):
            bot_state["afk_enabled"] = True
            await message.edit("📴 Modo AFK **activado**")
        elif val in ("off", "no", "false", "0"):
            bot_state["afk_enabled"] = False
            bot_state["afk_replied"] = set()
            await message.edit("📴 Modo AFK **desactivado**")
        else:
            bot_state["afk_enabled"] = True
            bot_state["afk_message"] = args[1]
            await message.edit(f"📴 Modo AFK **activado** con mensaje: {args[1]}")
    
    @app.on_message(filters.command("status") & filters.me)
    async def status_command(client, message):
        """Muestra el estado actual del bot."""
        state = bot_state
        text = (
            f"🤖 **DateTime Userbot - Estado**\n\n"
            f"🔌 Conectado: {'✅' if state.get('connected') else '❌'}\n"
            f"🎨 Estilo: {state.get('image_style', 'auto')}\n"
            f"💬 Categoría frases: {state.get('bio_category', 'random')}\n"
            f"🕐 Horario mode: {'✅' if state.get('schedule_mode', True) else '❌'}\n"
            f"🌤 Clima: {'✅' if state.get('show_weather', True) else '❌'}\n"
            f"📊 Progreso: {'✅' if state.get('show_progress', True) else '❌'}\n"
            f"📴 AFK: {'✅' if state.get('afk_enabled', False) else '❌'}\n"
            f"📅 Countdown: {state.get('countdown_date', 'No')}\n"
            f"🔄 Actualizaciones: {state.get('update_count', 0)}\n"
            f"⏰ Última: {state.get('last_update', 'N/A')}"
        )
        await message.edit(text)
    
    @app.on_message(filters.command("help") & filters.me)
    async def help_command(client, message):
        """Muestra la ayuda."""
        text = (
            "🤖 **DateTime Userbot - Comandos**\n\n"
            "🎨 `.style [auto|neon|retro|minimal|gradient]` - Cambiar estilo\n"
            "💬 `.quote [random|motivation|humor|philosophy|love|tech|life|schedule]` - Categoría frases\n"
            "🌤 `.weather [on|off]` - Mostrar clima\n"
            "📊 `.progress [on|off]` - Barra de progreso\n"
            "📅 `.countdown [fecha|off] [label]` - Cuenta regresiva\n"
            "📴 `.afk [on|off|mensaje]` - Modo AFK\n"
            "📋 `.status` - Estado del bot\n"
            "❓ `.help` - Esta ayuda"
        )
        await message.edit(text)
    
    # ─── Handler AFK ───────────────────────────────────────────────
    @app.on_message(filters.private & ~filters.me)
    async def afk_handler(client, message):
        """Responde automáticamente cuando AFK está activo."""
        if not bot_state.get("afk_enabled", False):
            return
        
        user_id = message.from_user.id
        replied_set = bot_state.get("afk_replied", set())
        
        if user_id not in replied_set:
            afk_msg = bot_state.get("afk_message", "No estoy disponible ahora. Te responderé lo antes posible.")
            try:
                await message.reply(f"📴 {afk_msg}")
                replied_set.add(user_id)
                bot_state["afk_replied"] = replied_set
            except Exception:
                pass
    
    logger = __import__('logging').getLogger("DateTimeUserbot")
    logger.info("Comandos de Telegram registrados")
