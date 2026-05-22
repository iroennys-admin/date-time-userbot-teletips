#!/usr/bin/env python3
"""Comandos de Telegram para controlar el bot. Prefijos: . / !"""

from pyrogram import Client, filters
from pyrogram.raw.functions.account import UpdateProfile
from config import (
    BIO_CATEGORY, IMAGE_STYLE, WEATHER_SHOW, SHOW_DAY_PROGRESS,
    DYNAMIC_HOUR_EMOJI, AFK_ENABLED, BIO_SCHEDULE_MODE, BIO_CUSTOM_PREFIX,
    BIO_SHOW_COUNTER, COUNTDOWN_DATE, COUNTDOWN_LABEL
)
from image_generator import BACKGROUND_THEMES
import datetime
import time as time_mod

CMD_PREFIXES = [".", "/", "!"]


def register_commands(app: Client, bot_state: dict):
    """Registra todos los comandos del bot."""

    # ═══════════════════════════════════════════════════════════════
    # ENCENDIDO / APAGADO
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("on", prefixes=CMD_PREFIXES) & filters.me)
    async def bot_on(client, message):
        """Activa el bot para que actualice el perfil."""
        bot_state["bot_active"] = True
        bot_state["start_time"] = time_mod.time()
        await message.edit("✅ **Bot ACTIVADO** - Actualizando perfil")

    @app.on_message(filters.command("off", prefixes=CMD_PREFIXES) & filters.me)
    async def bot_off(client, message):
        """Desactiva el bot, deja de actualizar el perfil."""
        bot_state["bot_active"] = False
        await message.edit("⏸️ **Bot PAUSADO** - Perfil congelado. Usa `.on` para reanudar")

    # ═══════════════════════════════════════════════════════════════
    # ESTILOS DE IMAGEN
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("style", prefixes=CMD_PREFIXES) & filters.me)
    async def style_command(client, message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            styles = "auto, neon, retro, minimal, gradient"
            await message.edit(f"📋 Estilos: {styles}\nUso: `.style neon`")
            return
        
        new_style = args[1].strip().lower()
        valid = ["auto", "neon", "retro", "minimal", "gradient"]
        if new_style not in valid:
            await message.edit(f"❌ Estilo invalido. Opciones: {', '.join(valid)}")
            return
        
        bot_state["image_style"] = new_style
        bot_state["bg_theme"] = ""  # Reset tema al cambiar estilo
        await message.edit(f"✅ Estilo cambiado a: **{new_style}**")

    # ═══════════════════════════════════════════════════════════════
    # TEMAS DE FONDO
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("theme", prefixes=CMD_PREFIXES) & filters.me)
    async def theme_command(client, message):
        """Cambia el tema de fondo de la imagen."""
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            themes_list = "\n".join(
                f"  {v['emoji']} `{k}` - {v['name']}" 
                for k, v in BACKGROUND_THEMES.items()
            )
            current = bot_state.get("bg_theme", "auto")
            await message.edit(
                f"🎨 **Temas disponibles:**\n{themes_list}\n\n"
                f"Uso: `.theme anime`\n"
                f"Quitar tema: `.theme off`\n"
                f"Tema actual: **{current or 'auto'}**"
            )
            return
        
        new_theme = args[1].strip().lower()
        if new_theme in ("off", "auto", "none", "clear"):
            bot_state["bg_theme"] = ""
            await message.edit("🎨 Tema eliminado. Usando estilo normal.")
            return
        
        if new_theme not in BACKGROUND_THEMES:
            await message.edit(f"❌ Tema invalido. Usa `.theme` para ver la lista.")
            return
        
        bot_state["bg_theme"] = new_theme
        td = BACKGROUND_THEMES[new_theme]
        await message.edit(f"✅ Tema cambiado a: {td['emoji']} **{td['name']}**")

    @app.on_message(filters.command("themes", prefixes=CMD_PREFIXES) & filters.me)
    async def themes_list_command(client, message):
        """Lista todos los temas disponibles."""
        themes_list = "\n".join(
            f"{v['emoji']} `{k}` - {v['name']}" 
            for k, v in BACKGROUND_THEMES.items()
        )
        await message.edit(f"🎨 **Temas de fondo:**\n\n{themes_list}\n\nUsa `.theme anime` para activar")

    # ═══════════════════════════════════════════════════════════════
    # FRASES / BIO
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("quote", prefixes=CMD_PREFIXES) & filters.me)
    async def quote_command(client, message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            cats = "random, motivation, humor, philosophy, love, tech, life, schedule"
            await message.edit(f"📋 Categorias: {cats}\nUso: `.quote humor`")
            return
        
        new_cat = args[1].strip().lower()
        valid = ["random", "motivation", "humor", "philosophy", "love", "tech", "life", "schedule"]
        if new_cat not in valid:
            await message.edit(f"❌ Categoria invalida. Opciones: {', '.join(valid)}")
            return
        
        if new_cat == "schedule":
            bot_state["schedule_mode"] = True
            bot_state["bio_category"] = "random"
        else:
            bot_state["schedule_mode"] = False
            bot_state["bio_category"] = new_cat
        
        await message.edit(f"✅ Categoria de frases: **{new_cat}**")

    # ═══════════════════════════════════════════════════════════════
    # CLIMA / PROGRESO / COUNTDOWN
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("weather", prefixes=CMD_PREFIXES) & filters.me)
    async def weather_command(client, message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            status = "✅ ON" if bot_state.get("show_weather", True) else "❌ OFF"
            await message.edit(f"🌤 Clima: {status}\nUso: `.weather on` o `.weather off`")
            return
        val = args[1].strip().lower()
        bot_state["show_weather"] = val in ("on", "yes", "true", "1", "si")
        await message.edit(f"🌤 Clima {'✅ activado' if bot_state['show_weather'] else '❌ desactivado'}")

    @app.on_message(filters.command("progress", prefixes=CMD_PREFIXES) & filters.me)
    async def progress_command(client, message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            status = "✅ ON" if bot_state.get("show_progress", True) else "❌ OFF"
            await message.edit(f"📊 Progreso: {status}\nUso: `.progress on` o `.progress off`")
            return
        val = args[1].strip().lower()
        bot_state["show_progress"] = val in ("on", "yes", "true", "1", "si")
        await message.edit(f"📊 Progreso {'✅ activado' if bot_state['show_progress'] else '❌ desactivado'}")

    @app.on_message(filters.command("countdown", prefixes=CMD_PREFIXES) & filters.me)
    async def countdown_command(client, message):
        args = message.text.split(maxsplit=2)
        if len(args) < 2:
            current = bot_state.get("countdown_date", "") or "No configurado"
            await message.edit(f"📅 Countdown: {current}\nUso: `.countdown 2027-01-01 Mi evento`")
            return
        if args[1].lower() in ("off", "clear", "remove"):
            bot_state["countdown_date"] = ""
            bot_state["countdown_label"] = ""
            await message.edit("📅 Countdown eliminado")
            return
        bot_state["countdown_date"] = args[1]
        bot_state["countdown_label"] = args[2] if len(args) > 2 else ""
        await message.edit(f"📅 Countdown: **{args[1]}** - {bot_state['countdown_label']}")

    # ═══════════════════════════════════════════════════════════════
    # MOOD (ESTADO DE ANIMO)
    # ═══════════════════════════════════════════════════════════════

    MOODS = {
        "happy": {"emoji": "😊", "name": "Feliz", "bio": "Feeling great! 😊"},
        "sad": {"emoji": "😢", "name": "Triste", "bio": "Having a tough day 😢"},
        "busy": {"emoji": "🔥", "name": "Ocupado", "bio": "Working hard! 🔥"},
        "sleeping": {"emoji": "😴", "name": "Durmiendo", "bio": "ZZZ... 😴"},
        "love": {"emoji": "❤️", "name": "Enamorado", "bio": "Love is in the air ❤️"},
        "gaming": {"emoji": "🎮", "name": "Gaming", "bio": "In the zone 🎮"},
        "coding": {"emoji": "💻", "name": "Programando", "bio": "In flow state 💻"},
        "music": {"emoji": "🎵", "name": "Escuchando musica", "bio": "Vibing to music 🎵"},
        "coffee": {"emoji": "☕", "name": "Cafe time", "bio": "Coffee break ☕"},
        "vibes": {"emoji": "✨", "name": "Good vibes", "bio": "Good vibes only ✨"},
        "angry": {"emoji": "😠", "name": "Enfadado", "bio": "Don't mess with me 😠"},
        "chill": {"emoji": "🧊", "name": "Relajado", "bio": "Chilling 🧊"},
    }

    @app.on_message(filters.command("mood", prefixes=CMD_PREFIXES) & filters.me)
    async def mood_command(client, message):
        """Cambia el mood (estado de animo) que aparece en la imagen y bio."""
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            moods_list = "\n".join(f"  {v['emoji']} `{k}` - {v['name']}" for k, v in MOODS.items())
            current = bot_state.get("mood", "none")
            await message.edit(
                f"🎭 **Moods disponibles:**\n{moods_list}\n\n"
                f"Uso: `.mood happy`\nQuitar: `.mood off`\nActual: **{current}**"
            )
            return
        
        new_mood = args[1].strip().lower()
        if new_mood in ("off", "clear", "none"):
            bot_state["mood"] = ""
            bot_state["mood_emoji"] = ""
            bot_state["mood_bio"] = ""
            await message.edit("🎭 Mood eliminado")
            return
        
        if new_mood not in MOODS:
            await message.edit(f"❌ Mood invalido. Usa `.mood` para ver la lista.")
            return
        
        m = MOODS[new_mood]
        bot_state["mood"] = new_mood
        bot_state["mood_emoji"] = m["emoji"]
        bot_state["mood_bio"] = m["bio"]
        await message.edit(f"🎭 Mood: {m['emoji']} **{m['name']}**")

    # ═══════════════════════════════════════════════════════════════
    # AFK
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("afk", prefixes=CMD_PREFIXES) & filters.me)
    async def afk_command(client, message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            status = "✅ ON" if bot_state.get("afk_enabled", False) else "❌ OFF"
            afk_since = bot_state.get("afk_since", "")
            await message.edit(f"📴 AFK: {status}\nUso: `.afk on`, `.afk off`, `.afk Estoy ocupado`")
            return
        
        val = args[1].strip().lower()
        if val in ("on", "yes", "true", "1", "si"):
            bot_state["afk_enabled"] = True
            bot_state["afk_since"] = datetime.datetime.now().strftime("%H:%M")
            bot_state["afk_replied"] = set()
            await message.edit("📴 Modo AFK **activado**")
        elif val in ("off", "no", "false", "0"):
            bot_state["afk_enabled"] = False
            afk_count = len(bot_state.get("afk_replied", set()))
            bot_state["afk_replied"] = set()
            await message.edit(f"📴 Modo AFK **desactivado** ({afk_count} personas te escribieron)")
        else:
            bot_state["afk_enabled"] = True
            bot_state["afk_message"] = args[1]
            bot_state["afk_since"] = datetime.datetime.now().strftime("%H:%M")
            bot_state["afk_replied"] = set()
            await message.edit(f"📴 AFK **activado**: {args[1]}")

    # ═══════════════════════════════════════════════════════════════
    # NOTAS (SAVE/RECALL)
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("note", prefixes=CMD_PREFIXES) & filters.me)
    async def note_command(client, message):
        """Guarda o recupera notas. .note save nombre texto | .note get nombre | .note list | .note del nombre"""
        args = message.text.split(maxsplit=2)
        
        if len(args) < 2:
            await message.edit(
                "📝 **Notas**\n\n"
                "`.note save <nombre> <texto>` - Guardar nota\n"
                "`.note get <nombre>` - Leer nota\n"
                "`.note list` - Ver todas\n"
                "`.note del <nombre>` - Eliminar nota"
            )
            return
        
        action = args[1].strip().lower()
        notes = bot_state.setdefault("notes", {})
        
        if action == "save" and len(args) >= 3:
            parts = args[2].split(maxsplit=1)
            if len(parts) < 2:
                await message.edit("❌ Uso: `.note save <nombre> <texto>`")
                return
            name, text = parts[0].lower(), parts[1]
            notes[name] = text
            await message.edit(f"📝 Nota **{name}** guardada")
        
        elif action == "get":
            if len(args) < 3:
                await message.edit("❌ Uso: `.note get <nombre>`")
                return
            name = args[2].strip().lower()
            if name in notes:
                await message.edit(f"📝 **{name}:** {notes[name]}")
            else:
                await message.edit(f"❌ Nota `{name}` no encontrada")
        
        elif action == "list":
            if not notes:
                await message.edit("📝 No hay notas guardadas")
                return
            notes_list = "\n".join(f"  📌 `{name}` - {text[:40]}..." for name, text in notes.items())
            await message.edit(f"📝 **Notas guardadas:**\n{notes_list}")
        
        elif action in ("del", "delete", "rm"):
            if len(args) < 3:
                await message.edit("❌ Uso: `.note del <nombre>`")
                return
            name = args[2].strip().lower()
            if name in notes:
                del notes[name]
                await message.edit(f"🗑 Nota **{name}** eliminada")
            else:
                await message.edit(f"❌ Nota `{name}` no encontrada")
        
        else:
            await message.edit("❌ Accion invalida. Usa save, get, list o del")

    # ═══════════════════════════════════════════════════════════════
    # BIO PERSONALIZADA
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("bio", prefixes=CMD_PREFIXES) & filters.me)
    async def bio_command(client, message):
        """Cambia la bio directamente. .bio Mi nueva bio"""
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            current = bot_state.get("custom_bio", "")
            await message.edit(f"💬 Bio personalizada: {current or 'Ninguna'}\nUso: `.bio Mi texto aqui`\nQuitar: `.bio off`")
            return
        
        text = args[1].strip()
        if text.lower() in ("off", "clear", "none"):
            bot_state["custom_bio"] = ""
            await message.edit("💬 Bio personalizada eliminada (usando frase automatica)")
        else:
            bot_state["custom_bio"] = text
            await message.edit(f"💬 Bio personalizada: **{text}**")

    # ═══════════════════════════════════════════════════════════════
    # NOMBRE PERSONALIZADO
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("name", prefixes=CMD_PREFIXES) & filters.me)
    async def name_command(client, message):
        """Cambia el apellido. .name Mi apellido"""
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            current = bot_state.get("custom_last_name", "")
            await message.edit(f"👤 Apellido personalizado: {current or 'Automatico (hora)'}\nUso: `.name Mi apellido`\nQuitar: `.name off`")
            return
        
        text = args[1].strip()
        if text.lower() in ("off", "clear", "auto", "none"):
            bot_state["custom_last_name"] = ""
            await message.edit("👤 Apellido automatico (hora/fecha)")
        else:
            bot_state["custom_last_name"] = text
            await message.edit(f"👤 Apellido: **{text}**")

    # ═══════════════════════════════════════════════════════════════
    # INTERVALO DE ACTUALIZACION
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("interval", prefixes=CMD_PREFIXES) & filters.me)
    async def interval_command(client, message):
        """Cambia el intervalo de actualizacion en segundos."""
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            current = bot_state.get("update_interval", 60)
            await message.edit(f"⏱️ Intervalo actual: **{current}s**\nUso: `.interval 120` (min 30s, max 600s)")
            return
        
        try:
            val = int(args[1].strip())
            val = max(30, min(600, val))  # Entre 30s y 10min
            bot_state["update_interval"] = val
            await message.edit(f"⏱️ Intervalo cambiado a: **{val}s**")
        except ValueError:
            await message.edit("❌ Ingresa un numero valido. Ej: `.interval 120`")

    # ═══════════════════════════════════════════════════════════════
    # PING / UPTIME
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("ping", prefixes=CMD_PREFIXES) & filters.me)
    async def ping_command(client, message):
        """Verifica la latencia del bot."""
        start = time_mod.time()
        await message.edit("🏓 Pong!")
        end = time_mod.time()
        latency = round((end - start) * 1000)
        
        start_time = bot_state.get("start_time", time_mod.time())
        uptime_s = int(time_mod.time() - start_time)
        hours = uptime_s // 3600
        minutes = (uptime_s % 3600) // 60
        seconds = uptime_s % 60
        uptime_str = f"{hours}h {minutes}m {seconds}s"
        
        await message.edit(
            f"🏓 **Pong!**\n\n"
            f"⚡ Latencia: **{latency}ms**\n"
            f"⏱️ Uptime: **{uptime_str}**\n"
            f"🔄 Updates: **{bot_state.get('update_count', 0)}**"
        )

    # ═══════════════════════════════════════════════════════════════
    # WHOIS (INFO DE USUARIO)
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("whois", prefixes=CMD_PREFIXES) & filters.me)
    async def whois_command(client, message):
        """Muestra info de un usuario. Responde a un mensaje o .whois @username"""
        try:
            args = message.text.split(maxsplit=1)
            
            if message.reply_to_message:
                user = message.reply_to_message.from_user
            elif len(args) >= 2:
                user = await client.get_users(args[1])
            else:
                user = message.from_user
            
            status_map = {
                "online": "🟢 En linea",
                "offline": "🔴 Desconectado", 
                "recently": "🟡 Recientemente",
                "last_week": "🟠 Hace una semana",
                "last_month": "⚪ Hace un mes",
            }
            
            status = "❓ Desconocido"
            try:
                full_user = await client.get_chat(user.id)
                status = status_map.get(str(full_user.status), str(full_user.status))
            except:
                pass
            
            text = (
                f"👤 **Info de usuario**\n\n"
                f"📌 Nombre: {user.first_name} {user.last_name or ''}\n"
                f"🆔 ID: `{user.id}`\n"
                f"📌 Username: @{user.username or 'N/A'}\n"
                f"🤖 Bot: {'Si' if user.is_bot else 'No'}\n"
                f"🔵 Status: {status}\n"
                f"🏅 Premium: {'Si' if getattr(user, 'is_premium', False) else 'No'}"
            )
            await message.edit(text)
            
        except Exception as e:
            await message.edit(f"❌ Error: {e}")

    # ═══════════════════════════════════════════════════════════════
    # ID (OBTENER IDS)
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("id", prefixes=CMD_PREFIXES) & filters.me)
    async def id_command(client, message):
        """Muestra el ID del chat o usuario."""
        if message.reply_to_message:
            user = message.reply_to_message.from_user
            chat_id = message.chat.id
            await message.edit(
                f"👤 Usuario: `{user.id}`\n"
                f"💬 Chat: `{chat_id}`\n"
                f"📨 Mensaje: `{message.reply_to_message.id}`"
            )
        else:
            await message.edit(
                f"💬 Chat ID: `{message.chat.id}`\n"
                f"👤 Tu ID: `{message.from_user.id}`\n"
                f"📨 Msg ID: `{message.id}`"
            )

    # ═══════════════════════════════════════════════════════════════
    # ESTADO COMPLETO
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("status", prefixes=CMD_PREFIXES) & filters.me)
    async def status_command(client, message):
        state = bot_state
        start_time = state.get("start_time", time_mod.time())
        uptime_s = int(time_mod.time() - start_time)
        hours = uptime_s // 3600
        minutes = (uptime_s % 3600) // 60
        uptime_str = f"{hours}h {minutes}m"
        
        active = "✅ ACTIVO" if state.get("bot_active", True) else "⏸️ PAUSADO"
        
        text = (
            f"🤖 **DateTime Userbot v2.0**\n\n"
            f"⚡ Estado: {active}\n"
            f"🔌 Conectado: {'✅' if state.get('connected') else '❌'}\n"
            f"⏱️ Uptime: {uptime_str}\n"
            f"🎨 Estilo: {state.get('image_style', 'auto')}\n"
            f"🖼️ Tema: {state.get('bg_theme', 'auto') or 'auto'}\n"
            f"💬 Frases: {state.get('bio_category', 'random')}\n"
            f"🎭 Mood: {state.get('mood', 'none')}\n"
            f"🌤 Clima: {'✅' if state.get('show_weather') else '❌'}\n"
            f"📊 Progreso: {'✅' if state.get('show_progress') else '❌'}\n"
            f"📴 AFK: {'✅' if state.get('afk_enabled') else '❌'}\n"
            f"📅 Countdown: {state.get('countdown_date', 'No') or 'No'}\n"
            f"⏱️ Intervalo: {state.get('update_interval', 60)}s\n"
            f"🔄 Updates: {state.get('update_count', 0)}\n"
            f"📝 Notas: {len(state.get('notes', {}))}"
        )
        await message.edit(text)

    # ═══════════════════════════════════════════════════════════════
    # AYUDA
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("help", prefixes=CMD_PREFIXES) & filters.me)
    async def help_command(client, message):
        text = (
            "🤖 **DateTime Userbot v2.0 - Comandos**\n\n"
            "**⚡ Control:**\n"
            "`.on` - Activar bot\n"
            "`.off` - Pausar bot\n"
            "`.ping` - Latencia + uptime\n"
            "`.status` - Estado completo\n"
            "`.restart` - Reiniciar bot\n\n"
            "**🎨 Apariencia:**\n"
            "`.style [auto|neon|retro|minimal|gradient]` - Estilo\n"
            "`.theme [anime|code|gaming|nature|cyberpunk|ocean|sunset|galaxy|retro|minimal|off]` - Tema\n"
            "`.themes` - Lista de temas\n"
            "`.mood [happy|sad|busy|sleeping|love|gaming|coding|music|coffee|vibes|angry|chill|off]` - Estado animo\n\n"
            "**💬 Bio y perfil:**\n"
            "`.quote [random|motivation|humor|philosophy|love|tech|life|schedule]` - Frases\n"
            "`.bio [texto|off]` - Bio personalizada\n"
            "`.name [texto|off]` - Apellido personalizado\n"
            "`.interval [30-600]` - Segundos entre updates\n\n"
            "**📊 Extras:**\n"
            "`.weather [on|off]` - Clima\n"
            "`.progress [on|off]` - Barra progreso\n"
            "`.countdown [fecha|off] [label]` - Cuenta regresiva\n"
            "`.afk [on|off|mensaje]` - Modo AFK\n\n"
            "**🛠️ Utilidades:**\n"
            "`.note [save|get|list|del]` - Notas\n"
            "`.whois` - Info de usuario\n"
            "`.id` - IDs de chat/usuario\n\n"
            "💡 Tambien funciona con / y ! (ej: /help o !status)"
        )
        await message.edit(text)

    # ═══════════════════════════════════════════════════════════════
    # REINICIAR
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("restart", prefixes=CMD_PREFIXES) & filters.me)
    async def restart_command(client, message):
        """Reinicia la conexion del bot."""
        await message.edit("🔄 Reiniciando bot...")
        bot_state["connected"] = False
        bot_state["restart_requested"] = True
        # El bucle principal detectara esto y reconectara

    # ═══════════════════════════════════════════════════════════════
    # HANDLER AFK
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.private & ~filters.me)
    async def afk_handler(client, message):
        if not bot_state.get("afk_enabled", False):
            return
        
        user_id = message.from_user.id
        replied_set = bot_state.get("afk_replied", set())
        
        if user_id not in replied_set:
            afk_msg = bot_state.get("afk_message", "No estoy disponible ahora. Te respondere lo antes posible.")
            afk_since = bot_state.get("afk_since", "")
            try:
                extra = f"\nAFK desde: {afk_since}" if afk_since else ""
                await message.reply(f"📴 {afk_msg}{extra}")
                replied_set.add(user_id)
                bot_state["afk_replied"] = replied_set
            except Exception:
                pass

    logger = __import__('logging').getLogger("DateTimeUserbot")
    logger.info("Comandos registrados con prefijos: . / !")
