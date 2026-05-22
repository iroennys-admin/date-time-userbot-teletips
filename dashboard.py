#!/usr/bin/env python3
"""Dashboard web para monitorear y configurar el bot."""

import datetime
import time as time_mod
import pytz
from flask import jsonify, request


def register_dashboard(app, bot_state, config_module=None):
    """Registra las rutas del dashboard en la app Flask."""
    
    @app.route("/dashboard")
    def dashboard():
        from config import TIME_ZONE
        tz = pytz.timezone(TIME_ZONE)
        now = datetime.datetime.now(tz)
        
        start_time = bot_state.get("start_time", time_mod.time())
        uptime_s = int(time_mod.time() - start_time)
        hours = uptime_s // 3600
        minutes = (uptime_s % 3600) // 60
        uptime_str = "{}h {}m".format(hours, minutes)
        
        active = bot_state.get("bot_active", True)
        connected = bot_state.get("connected", False)
        profile_name = bot_state.get("profile_name", "?")
        update_count = bot_state.get("update_count", 0)
        image_style = bot_state.get("image_style", "auto")
        bg_theme = bot_state.get("bg_theme", "") or "auto"
        mood_emoji = bot_state.get("mood_emoji", "") or ""
        mood_name = bot_state.get("mood", "none")
        mood_bio = bot_state.get("mood_bio", "") or "Sin mood"
        bio_cat = bot_state.get("bio_category", "random")
        schedule = "Horario" if bot_state.get("schedule_mode") else "Fijo"
        show_w = bot_state.get("show_weather", True)
        weather_info = bot_state.get("weather_info", "N/A")
        show_p = bot_state.get("show_progress", True)
        afk_on = bot_state.get("afk_enabled", False)
        afk_since = bot_state.get("afk_since", "")
        interval = bot_state.get("update_interval", 60)
        cd_date = bot_state.get("countdown_date", "") or "No"
        cd_label = bot_state.get("countdown_label", "")
        notes_count = len(bot_state.get("notes", {}))
        
        # Status classes
        state_class = "active" if active else "paused"
        state_text = "✅ Activo" if active else "⏸️ Pausado"
        state_sub = ("Conectado: " + str(profile_name)) if connected else "Desconectado"
        
        w_class = "on" if show_w else "off"
        w_text = "ON" if show_w else "OFF"
        p_class = "on" if show_p else "off"
        p_text = "ON" if show_p else "OFF"
        a_class = "on" if afk_on else "off"
        a_text = "ON" if afk_on else "OFF"
        
        html = """<!DOCTYPE html>
<html>
<head>
    <title>DateTime Userbot Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
            color: #e0e0e0; min-height: 100vh; padding: 20px;
        }
        .container { max-width: 950px; margin: 0 auto; }
        h1 { text-align: center; margin-bottom: 25px; color: #00d4ff; font-size: 26px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; }
        .card { 
            background: rgba(255,255,255,0.05); border-radius: 12px; padding: 16px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .card h3 { color: #00d4ff; margin-bottom: 8px; font-size: 12px; text-transform: uppercase; }
        .card .value { font-size: 22px; font-weight: bold; color: #fff; }
        .card .sub { font-size: 11px; color: #888; margin-top: 4px; }
        .on { color: #00ff88; } .off { color: #ff4444; }
        .active { color: #00ff88; font-size: 22px; }
        .paused { color: #ffaa00; font-size: 22px; }
        .section { margin-top: 25px; }
        .section h2 { color: #00d4ff; margin-bottom: 12px; font-size: 16px; }
        .cmd { 
            background: rgba(255,255,255,0.03); border-radius: 6px; padding: 8px 12px;
            margin: 4px 0; font-family: 'Courier New', monospace; font-size: 12px; color: #aaa;
        }
        .cmd b { color: #00d4ff; }
        .refresh { text-align: center; margin-top: 15px; color: #555; font-size: 11px; }
    </style>
    <meta http-equiv="refresh" content="30">
</head>
<body>
    <div class="container">
        <h1>🤖 DateTime Userbot v2.0</h1>
        <div class="grid">
            <div class="card">
                <h3>⚡ Estado</h3>
                <div class="%s">%s</div>
                <div class="sub">%s</div>
            </div>
            <div class="card">
                <h3>🕐 Hora</h3>
                <div class="value">%s</div>
                <div class="sub">%s | %s</div>
            </div>
            <div class="card">
                <h3>⏱️ Uptime</h3>
                <div class="value">%s</div>
                <div class="sub">Updates: %s</div>
            </div>
            <div class="card">
                <h3>🎨 Estilo</h3>
                <div class="value">%s</div>
                <div class="sub">Tema: %s</div>
            </div>
            <div class="card">
                <h3>🎭 Mood</h3>
                <div class="value">%s %s</div>
                <div class="sub">%s</div>
            </div>
            <div class="card">
                <h3>💬 Frases</h3>
                <div class="value">%s</div>
                <div class="sub">%s</div>
            </div>
            <div class="card">
                <h3>🌤 Clima</h3>
                <div class="%s">%s</div>
                <div class="sub">%s</div>
            </div>
            <div class="card">
                <h3>📊 Progreso</h3>
                <div class="%s">%s</div>
                <div class="sub">Barra del dia</div>
            </div>
            <div class="card">
                <h3>📴 AFK</h3>
                <div class="%s">%s</div>
                <div class="sub">%s</div>
            </div>
            <div class="card">
                <h3>⏱️ Intervalo</h3>
                <div class="value">%ss</div>
                <div class="sub">Entre updates</div>
            </div>
            <div class="card">
                <h3>📅 Countdown</h3>
                <div class="value">%s</div>
                <div class="sub">%s</div>
            </div>
            <div class="card">
                <h3>📝 Notas</h3>
                <div class="value">%s</div>
                <div class="sub">Guardadas</div>
            </div>
        </div>
        <div class="section">
            <h2>📋 Comandos de Telegram</h2>
            <div class="cmd"><b>.on</b> / <b>.off</b> — Activar/Pausar bot</div>
            <div class="cmd"><b>.style</b> [auto|neon|retro|minimal|gradient] — Estilo</div>
            <div class="cmd"><b>.theme</b> [anime|code|gaming|nature|cyberpunk|ocean|sunset|galaxy|retro|minimal|off] — Tema</div>
            <div class="cmd"><b>.mood</b> [happy|sad|busy|sleeping|love|gaming|coding|music|coffee|vibes|angry|chill|off] — Mood</div>
            <div class="cmd"><b>.quote</b> [random|motivation|humor|philosophy|love|tech|life|schedule] — Frases</div>
            <div class="cmd"><b>.bio</b> [texto|off] — Bio personalizada</div>
            <div class="cmd"><b>.name</b> [texto|off] — Apellido personalizado</div>
            <div class="cmd"><b>.interval</b> [30-600] — Segundos entre updates</div>
            <div class="cmd"><b>.weather</b> [on|off] / <b>.progress</b> [on|off] — Clima y progreso</div>
            <div class="cmd"><b>.countdown</b> [fecha|off] [label] / <b>.afk</b> [on|off|msg] — Extras</div>
            <div class="cmd"><b>.note</b> [save|get|list|del] — Notas personales</div>
            <div class="cmd"><b>.whois</b> / <b>.id</b> / <b>.ping</b> — Utilidades</div>
            <div class="cmd"><b>.status</b> / <b>.restart</b> / <b>.help</b> — Control</div>
        </div>
        <div class="refresh">Auto-refresh 30s | 🤖 v2.1</div>
    </div>
</body>
</html>""" % (
            state_class, state_text, state_sub,
            now.strftime("%I:%M %p"),
            now.strftime("%A, %b %d"), TIME_ZONE,
            uptime_str, update_count,
            image_style, bg_theme,
            mood_emoji, mood_name, mood_bio,
            bio_cat, schedule,
            w_class, w_text, weather_info,
            p_class, p_text,
            a_class, a_text, afk_since,
            interval,
            cd_date, cd_label,
            notes_count,
        )
        return html
    
    @app.route("/api/status")
    def api_status():
        return jsonify(bot_state)
    
    @app.route("/api/config", methods=["POST"])
    def api_config():
        data = request.get_json(force=True)
        changed = []
        for key in ["image_style", "bg_theme", "bio_category", "show_weather", "show_progress", 
                     "afk_enabled", "afk_message", "countdown_date", "countdown_label",
                     "schedule_mode", "mood", "custom_bio", "custom_last_name",
                     "update_interval", "bot_active"]:
            if key in data:
                bot_state[key] = data[key]
                changed.append(key)
        return jsonify({"success": True, "changed": changed})
