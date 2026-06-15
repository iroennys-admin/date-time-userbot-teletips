#!/usr/bin/env python3
"""Comandos de Telegram para el DateTime Userbot v3.2 - Maquina Potente"""

from pyrogram import Client, filters
import datetime
import time as time_mod
import asyncio
import re
import json
import sys
import logging
import urllib.request

logger = logging.getLogger("DateTimeUserbot")

CMD_PREFIXES = ".!/"

def register_commands(app: Client, bot_state: dict):
    """Registra todos los comandos del bot."""

    # ═══════════════════════════════════════════════════════════════
    # COMMAND TRACKING (grupo -10 = se ejecuta antes que los demas)
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.regex(r'^[\.\/!]\w+') & filters.me, group=-10)
    async def track_commands(client, message):
        """Cuenta cada comando recibido para diagnostico."""
        bot_state["command_count"] = bot_state.get("command_count", 0) + 1
        cmd = message.text.split()[0] if message.text else "?"
        logger.info(f"[CMD] Comando recibido: {cmd} (total: {bot_state['command_count']})")

    # ═══════════════════════════════════════════════════════════════
    # ENCENDIDO / APAGADO
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("on", prefixes=CMD_PREFIXES) & filters.me)
    async def bot_on(client, message):
        """Activa el bot para que actualice el perfil."""
        try:
            bot_state["bot_active"] = True
            bot_state["start_time"] = time_mod.time()
            await message.edit("✅ **Bot ACTIVADO** - Actualizando perfil")
            logger.info("Comando .on ejecutado")
        except Exception as e:
            logger.error(f"Error en .on: {e}")

    @app.on_message(filters.command("off", prefixes=CMD_PREFIXES) & filters.me)
    async def bot_off(client, message):
        """Desactiva el bot, deja de actualizar el perfil."""
        try:
            bot_state["bot_active"] = False
            await message.edit("⏸️ **Bot PAUSADO** - Perfil congelado. Usa `.on` para reanudar")
            logger.info("Comando .off ejecutado")
        except Exception as e:
            logger.error(f"Error en .off: {e}")

    # ═══════════════════════════════════════════════════════════════
    # ESTILOS DE IMAGEN
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("style", prefixes=CMD_PREFIXES) & filters.me)
    async def style_command(client, message):
        try:
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
            bot_state["bg_theme"] = ""
            await message.edit(f"✅ Estilo cambiado a: **{new_style}**")
        except Exception as e:
            logger.error(f"Error en .style: {e}")
            try: await message.edit(f"❌ Error: {e}")
            except: pass

    # ═══════════════════════════════════════════════════════════════
    # TEMAS DE FONDO
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("theme", prefixes=CMD_PREFIXES) & filters.me)
    async def theme_command(client, message):
        """Cambia el tema de fondo de la imagen."""
        try:
            from image_generator import BACKGROUND_THEMES
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
        except Exception as e:
            logger.error(f"Error en .theme: {e}")
            try: await message.edit(f"❌ Error: {e}")
            except: pass

    @app.on_message(filters.command("themes", prefixes=CMD_PREFIXES) & filters.me)
    async def themes_list_command(client, message):
        try:
            from image_generator import BACKGROUND_THEMES
            themes_list = "\n".join(
                f"{v['emoji']} `{k}` - {v['name']}" 
                for k, v in BACKGROUND_THEMES.items()
            )
            await message.edit(f"🎨 **Temas de fondo:**\n\n{themes_list}\n\nUsa `.theme anime` para activar")
        except Exception as e:
            logger.error(f"Error en .themes: {e}")

    # ═══════════════════════════════════════════════════════════════
    # FRASES / BIO
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("quote", prefixes=CMD_PREFIXES) & filters.me)
    async def quote_command(client, message):
        try:
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
        except Exception as e:
            logger.error(f"Error en .quote: {e}")

    # ═══════════════════════════════════════════════════════════════
    # CLIMA / PROGRESO / COUNTDOWN
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("weather", prefixes=CMD_PREFIXES) & filters.me)
    async def weather_command(client, message):
        try:
            args = message.text.split(maxsplit=1)
            if len(args) < 2:
                status = "✅ ON" if bot_state.get("show_weather", True) else "❌ OFF"
                await message.edit(f"🌤 Clima: {status}\nUso: `.weather on` o `.weather off`")
                return
            val = args[1].strip().lower()
            bot_state["show_weather"] = val in ("on", "yes", "true", "1", "si")
            await message.edit(f"🌤 Clima {'✅ activado' if bot_state['show_weather'] else '❌ desactivado'}")
        except Exception as e:
            logger.error(f"Error en .weather: {e}")

    @app.on_message(filters.command("progress", prefixes=CMD_PREFIXES) & filters.me)
    async def progress_command(client, message):
        try:
            args = message.text.split(maxsplit=1)
            if len(args) < 2:
                status = "✅ ON" if bot_state.get("show_progress", True) else "❌ OFF"
                await message.edit(f"📊 Progreso: {status}\nUso: `.progress on` o `.progress off`")
                return
            val = args[1].strip().lower()
            bot_state["show_progress"] = val in ("on", "yes", "true", "1", "si")
            await message.edit(f"📊 Progreso {'✅ activado' if bot_state['show_progress'] else '❌ desactivado'}")
        except Exception as e:
            logger.error(f"Error en .progress: {e}")

    @app.on_message(filters.command("countdown", prefixes=CMD_PREFIXES) & filters.me)
    async def countdown_command(client, message):
        try:
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
        except Exception as e:
            logger.error(f"Error en .countdown: {e}")

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
        try:
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
        except Exception as e:
            logger.error(f"Error en .mood: {e}")

    # ═══════════════════════════════════════════════════════════════
    # AFK
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("afk", prefixes=CMD_PREFIXES) & filters.me)
    async def afk_command(client, message):
        try:
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
        except Exception as e:
            logger.error(f"Error en .afk: {e}")

    # ═══════════════════════════════════════════════════════════════
    # NOTAS (SAVE/RECALL)
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("note", prefixes=CMD_PREFIXES) & filters.me)
    async def note_command(client, message):
        try:
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
        except Exception as e:
            logger.error(f"Error en .note: {e}")

    # ═══════════════════════════════════════════════════════════════
    # BIO / NOMBRE PERSONALIZADO
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("bio", prefixes=CMD_PREFIXES) & filters.me)
    async def bio_command(client, message):
        try:
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
        except Exception as e:
            logger.error(f"Error en .bio: {e}")

    @app.on_message(filters.command("name", prefixes=CMD_PREFIXES) & filters.me)
    async def name_command(client, message):
        try:
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
        except Exception as e:
            logger.error(f"Error en .name: {e}")

    # ═══════════════════════════════════════════════════════════════
    # INTERVALO DE ACTUALIZACION
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("interval", prefixes=CMD_PREFIXES) & filters.me)
    async def interval_command(client, message):
        try:
            args = message.text.split(maxsplit=1)
            if len(args) < 2:
                current = bot_state.get("update_interval", 60)
                await message.edit(f"⏱️ Intervalo actual: **{current}s**\nUso: `.interval 120` (min 30s, max 600s)")
                return
            
            try:
                val = int(args[1].strip())
                val = max(30, min(600, val))
                bot_state["update_interval"] = val
                await message.edit(f"⏱️ Intervalo cambiado a: **{val}s**")
            except ValueError:
                await message.edit("❌ Ingresa un numero valido. Ej: `.interval 120`")
        except Exception as e:
            logger.error(f"Error en .interval: {e}")

    # ═══════════════════════════════════════════════════════════════
    # PING / UPTIME
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("ping", prefixes=CMD_PREFIXES) & filters.me)
    async def ping_command(client, message):
        try:
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
        except Exception as e:
            logger.error(f"Error en .ping: {e}")

    # ═══════════════════════════════════════════════════════════════
    # WHOIS (INFO DE USUARIO)
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("whois", prefixes=CMD_PREFIXES) & filters.me)
    async def whois_command(client, message):
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
            
            common_count = 0
            try:
                async for _ in client.get_common_chats(user.id):
                    common_count += 1
                    if common_count >= 50:
                        break
            except:
                pass
            
            text = (
                f"👤 **Info de usuario**\n\n"
                f"📌 Nombre: {user.first_name} {user.last_name or ''}\n"
                f"🆔 ID: `{user.id}`\n"
                f"📌 Username: @{user.username or 'N/A'}\n"
                f"🤖 Bot: {'Si' if user.is_bot else 'No'}\n"
                f"🔵 Status: {status}\n"
                f"🏅 Premium: {'Si' if getattr(user, 'is_premium', False) else 'No'}\n"
                f"👥 Grupos en comun: {common_count}"
            )
            await message.edit(text)
            
        except Exception as e:
            await message.edit(f"❌ Error: {e}")

    # ═══════════════════════════════════════════════════════════════
    # ID (OBTENER IDS)
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("id", prefixes=CMD_PREFIXES) & filters.me)
    async def id_command(client, message):
        try:
            if message.reply_to_message:
                user = message.reply_to_message.from_user
                chat_id = message.chat.id
                fwd_from = message.reply_to_message.forward_from
                fwd_text = f"\n📤 Reenviado de: `{fwd_from.id}`" if fwd_from else ""
                await message.edit(
                    f"👤 Usuario: `{user.id}`\n"
                    f"💬 Chat: `{chat_id}`\n"
                    f"📨 Mensaje: `{message.reply_to_message.id}`"
                    f"{fwd_text}"
                )
            else:
                await message.edit(
                    f"💬 Chat ID: `{message.chat.id}`\n"
                    f"👤 Tu ID: `{message.from_user.id}`\n"
                    f"📨 Msg ID: `{message.id}`"
                )
        except Exception as e:
            logger.error(f"Error en .id: {e}")

    # ═══════════════════════════════════════════════════════════════
    # PURGE - Borrar mensajes en masa
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("purge", prefixes=CMD_PREFIXES) & filters.me)
    async def purge_command(client, message):
        if not message.reply_to_message:
            await message.edit("❌ Responde a un mensaje para indicar desde donde borrar.\nUso: Responde + `.purge`")
            return
        
        try:
            start_id = message.reply_to_message.id
            end_id = message.id
            deleted = 0
            
            status_msg = await message.edit("🗑️ Borrando mensajes...")
            
            for msg_id in range(start_id, end_id + 1):
                try:
                    await client.delete_messages(message.chat.id, msg_id)
                    deleted += 1
                except Exception:
                    pass
                if deleted % 20 == 0:
                    await asyncio.sleep(0.5)
            
            try:
                await status_msg.edit(f"🗑️ **{deleted}** mensajes borrados")
                await asyncio.sleep(3)
                await status_msg.delete()
            except:
                pass
                
        except Exception as e:
            await message.edit(f"❌ Error al purgar: {e}")

    # ═══════════════════════════════════════════════════════════════
    # DEL - Borrar mensaje respondido
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("del", prefixes=CMD_PREFIXES) & filters.me)
    async def del_command(client, message):
        if not message.reply_to_message:
            await message.edit("❌ Responde a un mensaje para borrarlo.\nUso: Responde + `.del`")
            return
        
        try:
            await client.delete_messages(message.chat.id, message.reply_to_message.id)
            await message.delete()
        except Exception as e:
            await message.edit(f"❌ Error: {e}")

    # ═══════════════════════════════════════════════════════════════
    # DELME - Borrar mis ultimos N mensajes
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("delme", prefixes=CMD_PREFIXES) & filters.me)
    async def delme_command(client, message):
        args = message.text.split(maxsplit=1)
        count = 5
        if len(args) >= 2:
            try:
                count = min(int(args[1]), 100)
            except ValueError:
                await message.edit("❌ Ingresa un numero. Ej: `.delme 10`")
                return
        
        deleted = 0
        status_msg = await message.edit(f"🗑️ Buscando y borrando {count} mensajes...")
        
        try:
            async for msg in client.get_chat_history(message.chat.id, limit=count * 3):
                if msg.from_user and msg.from_user.id == message.from_user.id:
                    try:
                        await msg.delete()
                        deleted += 1
                    except:
                        pass
                    if deleted >= count:
                        break
                await asyncio.sleep(0.1)
            
            await status_msg.edit(f"🗑️ **{deleted}** mensajes borrados")
            await asyncio.sleep(3)
            try:
                await status_msg.delete()
            except:
                pass
        except Exception as e:
            await status_msg.edit(f"❌ Error: {e}")

    # ═══════════════════════════════════════════════════════════════
    # CALC - Calculadora
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("calc", prefixes=CMD_PREFIXES) & filters.me)
    async def calc_command(client, message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.edit("🧮 **Calculadora**\n\nUso: `.calc 2+2` o `.calc 15*3/4`\nSoporta: +, -, *, /, **, (), %")
            return
        
        expr = args[1].strip()
        allowed = set("0123456789+-*/.()% ")
        if not all(c in allowed for c in expr):
            await message.edit("❌ Solo se permiten numeros y operadores (+, -, *, /, %, ())")
            return
        
        try:
            result = eval(expr, {"__builtins__": {}}, {})
            await message.edit(f"🧮 `{expr}` = **{result}**")
        except ZeroDivisionError:
            await message.edit("❌ Error: Division por cero")
        except Exception as e:
            await message.edit(f"❌ Error: {e}")

    # ═══════════════════════════════════════════════════════════════
    # REMIND - Recordatorios
    # ═══════════════════════════════════════════════════════════════

    def _parse_time(time_str: str):
        """Parsea tiempo tipo 30s, 5m, 2h, 1d"""
        try:
            if time_str.endswith('s'):
                return int(time_str[:-1])
            elif time_str.endswith('m'):
                return int(time_str[:-1]) * 60
            elif time_str.endswith('h'):
                return int(time_str[:-1]) * 3600
            elif time_str.endswith('d'):
                return int(time_str[:-1]) * 86400
            else:
                return int(time_str) * 60
        except (ValueError, IndexError):
            return None

    def _format_seconds(seconds: float) -> str:
        """Formatea segundos a texto legible"""
        seconds = int(max(0, seconds))
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}m {seconds % 60}s"
        elif seconds < 86400:
            return f"{seconds // 3600}h {(seconds % 3600) // 60}m"
        else:
            return f"{seconds // 86400}d {(seconds % 86400) // 3600}h"

    @app.on_message(filters.command("remind", prefixes=CMD_PREFIXES) & filters.me)
    async def remind_command(client, message):
        """Programa un recordatorio. .remind 30m Llamar a mama"""
        args = message.text.split(maxsplit=2)
        
        if len(args) < 2:
            reminders = bot_state.get("reminders", [])
            if reminders:
                rem_list = "\n".join(
                    f"  ⏰ {r['text'][:30]} (en {_format_seconds(r['trigger_time'] - time_mod.time())})"
                    for r in reminders[:5]
                )
            else:
                rem_list = "  Ninguno"
            await message.edit(
                f"⏰ **Recordatorios**\n\n{rem_list}\n\n"
                "Uso: `.remind 30m Llamar a mama`\n"
                "`.remind 2h Reunion importante`\n"
                "`.remind 10s Prueba rapida`\n"
                "`.remind list` - Ver todos\n"
                "`.remind clear` - Borrar todos"
            )
            return
        
        if args[1].lower() == "list":
            reminders = bot_state.get("reminders", [])
            if not reminders:
                await message.edit("⏰ No hay recordatorios pendientes")
                return
            rem_list = "\n".join(
                f"  {i+1}. ⏰ {r['text'][:40]} (en {_format_seconds(r['trigger_time'] - time_mod.time())})"
                for i, r in enumerate(reminders[:10])
            )
            await message.edit(f"⏰ **Recordatorios pendientes:**\n{rem_list}")
            return
        
        if args[1].lower() == "clear":
            bot_state["reminders"] = []
            await message.edit("⏰ Todos los recordatorios eliminados")
            return
        
        time_str = args[1].lower()
        text = args[2] if len(args) > 2 else "Recordatorio!"
        
        seconds = _parse_time(time_str)
        if seconds is None:
            await message.edit("❌ Formato invalido. Usa: 30s, 5m, 2h, 1d\nEj: `.remind 30m Llamar a mama`")
            return
        
        if seconds < 10:
            await message.edit("❌ Minimo 10 segundos para un recordatorio")
            return
        
        trigger_time = time_mod.time() + seconds
        reminder = {
            "text": text,
            "trigger_time": trigger_time,
            "chat_id": message.chat.id,
        }
        bot_state.setdefault("reminders", []).append(reminder)
        
        await message.edit(f"⏰ Recordatorio en **{_format_seconds(seconds)}**: {text}")

    # ═══════════════════════════════════════════════════════════════
    # EXEC / EVAL - Ejecutar codigo Python
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("exec", prefixes=CMD_PREFIXES) & filters.me)
    async def exec_command(client, message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.edit("🖥️ **Ejecutar Python**\n\nUso: `.exec print('Hola')`\n⚠️ Ten cuidado con lo que ejecutas")
            return
        
        code = args[1].strip()
        try:
            import io
            import contextlib
            
            output = io.StringIO()
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                try:
                    result = eval(code, {"__builtins__": {}, "client": client, "message": message, "bot_state": bot_state})
                    if result is not None:
                        print(repr(result))
                except SyntaxError:
                    exec(code, {"__builtins__": {}, "client": client, "message": message, "bot_state": bot_state})
            
            result_text = output.getvalue().strip()
            if not result_text:
                result_text = "✅ Ejecutado (sin output)"
            elif len(result_text) > 4000:
                result_text = result_text[:4000] + "\n... (truncado)"
            
            await message.edit(f"🖥️ **Output:**\n```\n{result_text}\n```")
        except Exception as e:
            await message.edit(f"❌ **Error:**\n```\n{type(e).__name__}: {e}\n```")

    @app.on_message(filters.command("eval", prefixes=CMD_PREFIXES) & filters.me)
    async def eval_command(client, message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.edit("🖥️ **Evaluar expresion**\n\nUso: `.eval 2+2`\n`.eval len('hola')`")
            return
        
        expr = args[1].strip()
        try:
            result = eval(expr, {"__builtins__": {}, "client": client, "message": message, "bot_state": bot_state})
            await message.edit(f"🖥️ `{expr}` = **{repr(result)}**")
        except Exception as e:
            await message.edit(f"❌ **Error:** `{type(e).__name__}: {e}`")

    # ═══════════════════════════════════════════════════════════════
    # SED - Reemplazar texto en mensajes (s/old/new)
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.regex(r"^[\.\/!]s/") & filters.me)
    async def sed_command(client, message):
        """Reemplaza texto en tu ultimo mensaje o en el respondido. s/old/new/flags"""
        text = message.text
        if not re.match(r'^[\.\/!]s/', text):
            return
        
        sed_text = text[2:]
        parts = sed_text.split('/')
        if len(parts) < 3:
            return
        
        old = parts[1]
        new = parts[2]
        flags = parts[3] if len(parts) > 3 else ""
        
        if not old:
            return
        
        target_msg = None
        if message.reply_to_message:
            if message.reply_to_message.from_user and message.reply_to_message.from_user.id == message.from_user.id:
                target_msg = message.reply_to_message
        else:
            try:
                async for msg in client.get_chat_history(message.chat.id, limit=10):
                    if msg.from_user and msg.from_user.id == message.from_user.id and msg.id != message.id:
                        target_msg = msg
                        break
            except:
                pass
        
        if not target_msg or not target_msg.text:
            await message.edit("❌ No se encontro un mensaje para editar")
            await asyncio.sleep(3)
            try:
                await message.delete()
            except:
                pass
            return
        
        original = target_msg.text
        re_flags = 0
        count = 0
        
        if 'i' in flags:
            re_flags |= re.IGNORECASE
        
        if 'g' not in flags:
            count = 1
        
        try:
            new_text = re.sub(re.escape(old), new, original, count=count, flags=re_flags)
        except re.error as e:
            await message.edit(f"❌ Error regex: {e}")
            return
        
        if new_text == original:
            await message.edit("❌ No se encontraron coincidencias")
            await asyncio.sleep(3)
            try:
                await message.delete()
            except:
                pass
            return
        
        try:
            await target_msg.edit(new_text)
            bot_state["sed_count"] = bot_state.get("sed_count", 0) + 1
            await message.delete()
        except Exception as e:
            await message.edit(f"❌ Error editando: {e}")

    # ═══════════════════════════════════════════════════════════════
    # TRADUCIR - Traductor
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("tr", prefixes=CMD_PREFIXES) & filters.me)
    async def translate_command(client, message):
        args = message.text.split(maxsplit=2)
        
        target_lang = "es"
        
        if message.reply_to_message and message.reply_to_message.text:
            text_to_translate = message.reply_to_message.text
            if len(args) >= 2:
                target_lang = args[1].strip().lower()
        elif len(args) >= 3:
            target_lang = args[1].strip().lower()
            text_to_translate = args[2]
        elif len(args) == 2:
            target_lang = args[1].strip().lower()
            await message.edit("🌐 Uso: `.tr es Hello World` o responde a un mensaje con `.tr es`")
            return
        else:
            await message.edit("🌐 **Traductor**\n\nUso: `.tr es Hello World`\nResponde + `.tr es`\nIdiomas: es, en, fr, de, pt, it, ja, ko, zh, ru, ar")
            return
        
        if len(text_to_translate) > 2000:
            await message.edit("❌ Texto muy largo (max 2000 caracteres)")
            return
        
        try:
            encoded_text = urllib.request.quote(text_to_translate)
            url = f"https://api.mymemory.translated.net/get?q={encoded_text}&langpair=auto|{target_lang}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            translated = data.get("responseData", {}).get("translatedText", "Error al traducir")
            detected_lang = data.get("responseData", {}).get("language", "auto")
            
            await message.edit(
                f"🌐 **Traduccion** ({detected_lang} → {target_lang})\n\n"
                f"**Original:** {text_to_translate[:500]}\n\n"
                f"**Traducido:** {translated[:500]}"
            )
        except Exception as e:
            await message.edit(f"❌ Error traduciendo: {e}")

    # ═══════════════════════════════════════════════════════════════
    # QR - Generador de codigos QR
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("qr", prefixes=CMD_PREFIXES) & filters.me)
    async def qr_command(client, message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.edit("📱 **Codigo QR**\n\nUso: `.qr https://ejemplo.com`\n`.qr Hola mundo!`")
            return
        
        text = args[1].strip()
        if len(text) > 2000:
            await message.edit("❌ Texto muy largo (max 2000 caracteres)")
            return
        
        try:
            import qrcode
            from PIL import Image as PILImage
            
            qr = qrcode.QRCode(version=1, box_size=10, border=2)
            qr.add_data(text)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            qr_path = f"qr_{message.id}.png"
            img.save(qr_path)
            
            await message.delete()
            await client.send_photo(message.chat.id, qr_path, caption=f"📱 QR: `{text[:100]}`")
            
            try:
                from pathlib import Path
                Path(qr_path).unlink(missing_ok=True)
            except:
                pass
            
        except ImportError:
            try:
                encoded = urllib.request.quote(text)
                url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={encoded}"
                qr_path = f"qr_{message.id}.png"
                urllib.request.urlretrieve(url, qr_path)
                
                await message.delete()
                await client.send_photo(message.chat.id, qr_path, caption=f"📱 QR: `{text[:100]}`")
                
                try:
                    from pathlib import Path
                    Path(qr_path).unlink(missing_ok=True)
                except:
                    pass
            except Exception as e:
                await message.edit(f"❌ Error generando QR: {e}")
        except Exception as e:
            await message.edit(f"❌ Error: {e}")

    # ═══════════════════════════════════════════════════════════════
    # CLONE - Clonar perfil de usuario
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("clone", prefixes=CMD_PREFIXES) & filters.me)
    async def clone_command(client, message):
        if not message.reply_to_message:
            await message.edit("❌ Responde al mensaje de un usuario para clonar su perfil.\nUso: Responde + `.clone`")
            return
        
        try:
            user = message.reply_to_message.from_user
            full_user = await client.get_chat(user.id)
            
            first_name = user.first_name or ""
            last_name = user.last_name or ""
            bio = getattr(full_user, 'bio', '') or ""
            
            await client.update_profile(
                first_name=first_name,
                last_name=last_name,
                bio=bio,
            )
            
            photo_copied = False
            try:
                photos = client.get_chat_photos(user.id)
                async for photo in photos:
                    photo_path = await client.download_media(photo)
                    await client.set_profile_photo(photo=photo_path)
                    try:
                        from pathlib import Path
                        Path(photo_path).unlink(missing_ok=True)
                    except:
                        pass
                    photo_copied = True
                    break
            except:
                pass
            
            result = f"👤 **Perfil clonado!**\n\n📌 Nombre: {first_name}\n📌 Apellido: {last_name}\n💬 Bio: {bio[:50]}"
            if photo_copied:
                result += "\n🖼️ Foto: Copiada"
            
            await message.edit(result)
            
        except Exception as e:
            await message.edit(f"❌ Error clonando: {e}")

    # ═══════════════════════════════════════════════════════════════
    # SPEEDTEST - Test de velocidad
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("speedtest", prefixes=CMD_PREFIXES) & filters.me)
    async def speedtest_command(client, message):
        await message.edit("📡 Ejecutando test de velocidad...")
        
        try:
            import socket
            import time
            
            start = time_mod.time()
            sock = socket.create_connection(("8.8.8.8", 53), timeout=5)
            latency = round((time_mod.time() - start) * 1000)
            sock.close()
            
            start_dl = time_mod.time()
            try:
                req = urllib.request.Request("https://speed.cloudflare.com/__down?bytes=1000000", headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = resp.read()
                dl_time = time_mod.time() - start_dl
                dl_speed = round(len(data) / dl_time / 1024 / 1024, 2)
            except:
                dl_speed = "N/A"
            
            await message.edit(
                f"📡 **Speedtest**\n\n"
                f"🏓 Latencia: **{latency}ms**\n"
                f"⬇️ Descarga: **{dl_speed} MB/s**\n"
                f"🖥️ Host: Render (Oregon)"
            )
        except Exception as e:
            await message.edit(f"❌ Error en speedtest: {e}")

    # ═══════════════════════════════════════════════════════════════
    # URL - Acortar URLs
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("short", prefixes=CMD_PREFIXES) & filters.me)
    async def short_url_command(client, message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.edit("🔗 **Acortador de URLs**\n\nUso: `.short https://ejemplo.com`")
            return
        
        url = args[1].strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        try:
            encoded = urllib.request.quote(url)
            api_url = f"https://is.gd/create.php?format=json&url={encoded}"
            req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            short_url = data.get("shorturl", "Error al acortar")
            
            await message.edit(
                f"🔗 **URL Acortada**\n\n"
                f"📎 Original: {url}\n"
                f"✂️ Corta: {short_url}"
            )
        except Exception as e:
            await message.edit(f"❌ Error: {e}")

    # ═══════════════════════════════════════════════════════════════
    # KANG - Robar stickers
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("kang", prefixes=CMD_PREFIXES) & filters.me)
    async def kang_command(client, message):
        if not message.reply_to_message:
            await message.edit("❌ Responde a un sticker o imagen para robarlo.\nUso: Responde + `.kang` o `.kang emoji`")
            return
        
        try:
            emoji = "🤔"
            args = message.text.split(maxsplit=1)
            if len(args) >= 2:
                emoji = args[1].strip()[:2]
            
            reply = message.reply_to_message
            sticker_path = None
            
            if reply.sticker:
                sticker_path = await client.download_media(reply.sticker)
            elif reply.photo:
                sticker_path = await client.download_media(reply.photo)
            elif reply.document:
                sticker_path = await client.download_media(reply.document)
            else:
                await message.edit("❌ Responde a un sticker, imagen o documento")
                return
            
            if not sticker_path:
                await message.edit("❌ No se pudo descargar el archivo")
                return
            
            try:
                from PIL import Image as PILImage
                img = PILImage.open(sticker_path)
                if img.mode != "RGBA":
                    img = img.convert("RGBA")
                img = img.resize((512, 512), PILImage.Resampling.LANCZOS)
                png_path = sticker_path.rsplit('.', 1)[0] + ".png"
                img.save(png_path, "PNG")
                sticker_path = png_path
            except:
                pass
            
            pack_name = f"kang_{message.from_user.id}_by_{client.me.username or 'user'}"
            
            try:
                await client.add_sticker_to_set(
                    name=pack_name,
                    sticker=sticker_path,
                    emoji=emoji,
                )
                await message.edit(f"🎨 Sticker agregado a tu pack! {emoji}\n📌 Pack: `{pack_name}`")
            except Exception:
                try:
                    await client.create_sticker_set(
                        user_id=message.from_user.id,
                        name=pack_name,
                        title=f"@{client.me.username or 'User'} Kang Pack",
                        stickers=[sticker_path],
                        emoji=emoji,
                    )
                    await message.edit(f"🎨 Nuevo pack creado y sticker agregado! {emoji}\n📌 Pack: `{pack_name}`")
                except Exception as e2:
                    await message.edit(f"❌ Error creando pack: {e2}")
            
            try:
                from pathlib import Path
                Path(sticker_path).unlink(missing_ok=True)
            except:
                pass
                
        except Exception as e:
            await message.edit(f"❌ Error kang: {e}")

    # ═══════════════════════════════════════════════════════════════
    # SAVE - Guardar contenido restringido
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("save", prefixes=CMD_PREFIXES) & filters.me)
    async def save_command(client, message):
        if not message.reply_to_message:
            await message.edit("❌ Responde a un mensaje con media para guardarlo.\nUso: Responde + `.save`")
            return
        
        reply = message.reply_to_message
        status_msg = await message.edit("📥 Descargando...")
        
        try:
            media = None
            media_type = None
            
            if reply.photo:
                media = reply.photo
                media_type = "foto"
            elif reply.video:
                media = reply.video
                media_type = "video"
            elif reply.document:
                media = reply.document
                media_type = "archivo"
            elif reply.audio:
                media = reply.audio
                media_type = "audio"
            elif reply.voice:
                media = reply.voice
                media_type = "nota de voz"
            elif reply.sticker:
                media = reply.sticker
                media_type = "sticker"
            elif reply.animation:
                media = reply.animation
                media_type = "GIF"
            else:
                await status_msg.edit("❌ No se encontro media en el mensaje")
                return
            
            file_path = await client.download_media(media)
            
            if file_path:
                caption = f"📥 {media_type.capitalize()} guardado"
                if reply.caption:
                    caption += f"\n\n{reply.caption[:500]}"
                
                await client.send_document(
                    "me",
                    file_path,
                    caption=caption,
                )
                await status_msg.edit(f"✅ {media_type.capitalize()} guardado en Saved Messages")
                
                try:
                    from pathlib import Path
                    Path(file_path).unlink(missing_ok=True)
                except:
                    pass
            else:
                await status_msg.edit("❌ No se pudo descargar el archivo")
                
        except Exception as e:
            await status_msg.edit(f"❌ Error: {e}")

    # ═══════════════════════════════════════════════════════════════
    # PM PERMIT - Anti-spam en mensajes privados
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("pmpermit", prefixes=CMD_PREFIXES) & filters.me)
    async def pmpermit_command(client, message):
        args = message.text.split(maxsplit=1)
        
        if len(args) < 2:
            status = "✅ ON" if bot_state.get("pm_permit", False) else "❌ OFF"
            approved = len(bot_state.get("approved_users", set()))
            await message.edit(
                f"🛡️ **PM Permit:** {status}\n"
                f"👤 Usuarios aprobados: {approved}\n\n"
                f"Uso:\n"
                f"`.pmpermit on` - Activar filtro\n"
                f"`.pmpermit off` - Desactivar\n"
                f"`.pmpermit approve @user` - Aprobar usuario\n"
                f"`.pmpermit disapprove @user` - Desaprobar"
            )
            return
        
        action = args[1].strip().lower()
        
        if action == "on":
            bot_state["pm_permit"] = True
            await message.edit("🛡️ PM Permit **activado** - Solo usuarios aprobados pueden escribirte")
        elif action == "off":
            bot_state["pm_permit"] = False
            await message.edit("🛡️ PM Permit **desactivado** - Todos pueden escribirte")
        elif action.startswith("approve"):
            parts = args[1].split(maxsplit=1)
            if len(parts) < 2:
                await message.edit("❌ Uso: `.pmpermit approve @user`")
                return
            try:
                user = await client.get_users(parts[1])
                bot_state.setdefault("approved_users", set()).add(user.id)
                await message.edit(f"✅ @{user.username or user.id} aprobado para PM")
            except:
                await message.edit("❌ Usuario no encontrado")
        elif action.startswith("disapprove"):
            parts = args[1].split(maxsplit=1)
            if len(parts) < 2:
                await message.edit("❌ Uso: `.pmpermit disapprove @user`")
                return
            try:
                user = await client.get_users(parts[1])
                bot_state.get("approved_users", set()).discard(user.id)
                await message.edit(f"❌ @{user.username or user.id} desaprobado")
            except:
                await message.edit("❌ Usuario no encontrado")

    # ═══════════════════════════════════════════════════════════════
    # INFO DEL SISTEMA - FIX: import sys added at top
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("sysinfo", prefixes=CMD_PREFIXES) & filters.me)
    async def sysinfo_command(client, message):
        try:
            import platform
            
            start_time = bot_state.get("start_time", time_mod.time())
            uptime_s = int(time_mod.time() - start_time)
            hours = uptime_s // 3600
            minutes = (uptime_s % 3600) // 60
            uptime_str = f"{hours}h {minutes}m"
            
            await message.edit(
                f"🖥️ **System Info**\n\n"
                f"🐍 Python: `{sys.version.split()[0]}`\n"
                f"🖥️ OS: `{platform.system()} {platform.release()}`\n"
                f"🏗️ Arch: `{platform.machine()}`\n"
                f"⏱️ Uptime: **{uptime_str}**\n"
                f"🔄 Updates: **{bot_state.get('update_count', 0)}**\n"
                f"📝 Notas: **{len(bot_state.get('notes', {}))}**\n"
                f"⏰ Recordatorios: **{len(bot_state.get('reminders', []))}**\n"
                f"🔀 SED edits: **{bot_state.get('sed_count', 0)}**\n"
                f"📡 Connected: **{'✅' if bot_state.get('connected') else '❌'}**"
            )
        except Exception as e:
            logger.error(f"Error en .sysinfo: {e}")
            try: await message.edit(f"❌ Error en sysinfo: {e}")
            except: pass

    # ═══════════════════════════════════════════════════════════════
    # ESTADO COMPLETO
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("status", prefixes=CMD_PREFIXES) & filters.me)
    async def status_command(client, message):
        try:
            state = bot_state
            start_time = state.get("start_time", time_mod.time())
            uptime_s = int(time_mod.time() - start_time)
            hours = uptime_s // 3600
            minutes = (uptime_s % 3600) // 60
            uptime_str = f"{hours}h {minutes}m"
            
            active = "✅ ACTIVO" if state.get("bot_active", True) else "⏸️ PAUSADO"
            
            text = (
                f"🤖 **DateTime Userbot v3.1**\n\n"
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
                f"📝 Notas: {len(state.get('notes', {}))}\n"
                f"⏰ Recordatorios: {len(state.get('reminders', []))}\n"
                f"🛡️ PM Permit: {'✅' if state.get('pm_permit') else '❌'}"
            )
            await message.edit(text)
        except Exception as e:
            logger.error(f"Error en .status: {e}")

    # ═══════════════════════════════════════════════════════════════
    # AYUDA COMPLETA v3.1
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("help", prefixes=CMD_PREFIXES) & filters.me)
    async def help_command(client, message):
        try:
            text = (
                "🤖 **DateTime Userbot v3.1 - Comandos**\n\n"
                "**⚡ Control:**\n"
                "`.on` - Activar bot\n"
                "`.off` - Pausar bot\n"
                "`.ping` - Latencia + uptime\n"
                "`.status` - Estado completo\n"
                "`.restart` - Reiniciar bot\n"
                "`.sysinfo` - Info del sistema\n\n"
                "**🎨 Apariencia:**\n"
                "`.style [auto|neon|retro|minimal|gradient]` - Estilo\n"
                "`.theme [anime|code|gaming|nature|cyberpunk|ocean|sunset|galaxy|retro|minimal|off]` - Tema\n"
                "`.themes` - Lista de temas\n"
                "`.mood [happy|sad|busy|sleeping|love|gaming|coding|music|coffee|vibes|angry|chill|off]` - Mood\n\n"
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
                "`.remind [30m|2h|1d] [texto]` - Recordatorios\n"
                "`.calc [expresion]` - Calculadora\n"
                "`.tr [idioma] [texto]` - Traductor\n"
                "`.qr [texto]` - Codigo QR\n"
                "`.short [url]` - Acortar URL\n"
                "`.whois` - Info de usuario\n"
                "`.id` - IDs de chat/usuario\n\n"
                "**🔥 Poder:**\n"
                "`.purge` - Borrar mensajes en masa\n"
                "`.del` - Borrar mensaje respondido\n"
                "`.delme [N]` - Borrar mis ultimos N mensajes\n"
                "`.save` - Guardar media (chats restringidos)\n"
                "`.kang` - Robar sticker\n"
                "`.clone` - Clonar perfil de usuario\n"
                "`.exec [codigo]` - Ejecutar Python\n"
                "`.eval [expr]` - Evaluar expresion\n"
                "`.speedtest` - Test de velocidad\n"
                "`.pmpermit [on|off|approve|disapprove]` - Anti-spam PM\n"
                "`s/old/new/` - Reemplazar texto\n\n"
                "💡 Tambien funciona con / y ! (ej: /help o !status)"
            )
            await message.edit(text)
        except Exception as e:
            logger.error(f"Error en .help: {e}")

    # ═══════════════════════════════════════════════════════════════
    # REINICIAR
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.command("restart", prefixes=CMD_PREFIXES) & filters.me)
    async def restart_command(client, message):
        """Reinicia la conexion del bot."""
        try:
            await message.edit("🔄 Reiniciando bot...")
            bot_state["connected"] = False
            bot_state["restart_requested"] = True
        except Exception as e:
            logger.error(f"Error en .restart: {e}")

    # ═══════════════════════════════════════════════════════════════
    # HANDLER AFK - FIX: proper filter
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.private & ~filters.me)
    async def afk_handler(client, message):
        try:
            if not bot_state.get("afk_enabled", False) and not bot_state.get("pm_permit", False):
                return
            
            user_id = message.from_user.id
            
            # PM Permit check
            if bot_state.get("pm_permit", False) and user_id not in bot_state.get("approved_users", set()):
                try:
                    await message.reply(
                        "🛡️ **PM Permit Activo**\n\n"
                        "Este usuario no acepta mensajes de personas no aprobadas.\n"
                        "Por favor, espera a que te apruebe."
                    )
                except:
                    pass
                return
            
            # AFK check
            if bot_state.get("afk_enabled", False):
                replied_set = bot_state.get("afk_replied", set())
                
                if user_id not in replied_set:
                    afk_msg = bot_state.get("afk_message", "No estoy disponible ahora.")
                    afk_since = bot_state.get("afk_since", "")
                    try:
                        extra = f"\nAFK desde: {afk_since}" if afk_since else ""
                        await message.reply(f"📴 {afk_msg}{extra}")
                        replied_set.add(user_id)
                        bot_state["afk_replied"] = replied_set
                    except:
                        pass
        except Exception as e:
            logger.error(f"Error en afk_handler: {e}")

    # ═══════════════════════════════════════════════════════════════
    # LOG: Desactivar AFK al escribir - FIX: proper filter
    # ═══════════════════════════════════════════════════════════════

    @app.on_message(filters.private & filters.me)
    async def auto_disable_afk(client, message):
        """Desactiva AFK automaticamente cuando escribes."""
        try:
            if bot_state.get("afk_enabled", False):
                afk_count = len(bot_state.get("afk_replied", set()))
                bot_state["afk_enabled"] = False
                bot_state["afk_replied"] = set()
                try:
                    await message.reply(f"📴 AFK desactivado automaticamente ({afk_count} personas te escribieron)")
                except:
                    pass
        except Exception as e:
            logger.error(f"Error en auto_disable_afk: {e}")

    logger.info(f"Comandos v3.1 registrados con prefijos: {CMD_PREFIXES}")
