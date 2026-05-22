#!/usr/bin/env python3
"""Dashboard web para monitorear y configurar el bot."""

from flask import Blueprint, jsonify, request
import datetime
import time as time_mod
import pytz

dashboard_bp = Blueprint("dashboard", __name__)


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
        uptime_str = f"{hours}h {minutes}m"
        
        active = bot_state.get("bot_active", True)
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>DateTime Userbot Dashboard</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ 
                    font-family: 'Segoe UI', system-ui, sans-serif;
                    background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
                    color: #e0e0e0; min-height: 100vh; padding: 20px;
                }}
                .container {{ max-width: 950px; margin: 0 auto; }}
                h1 {{ text-align: center; margin-bottom: 25px; color: #00d4ff; font-size: 26px; }}
                .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; }}
                .card {{ 
                    background: rgba(255,255,255,0.05); border-radius: 12px; padding: 16px;
                    border: 1px solid rgba(255,255,255,0.1);
                }}
                .card h3 {{ color: #00d4ff; margin-bottom: 8px; font-size: 12px; text-transform: uppercase; }}
                .card .value {{ font-size: 22px; font-weight: bold; color: #fff; }}
                .card .sub {{ font-size: 11px; color: #888; margin-top: 4px; }}
                .on {{ color: #00ff88; }} .off {{ color: #ff4444; }}
                .active {{ color: #00ff88; font-size: 22px; }}
                .paused {{ color: #ffaa00; font-size: 22px; }}
                .section {{ margin-top: 25px; }}
                .section h2 {{ color: #00d4ff; margin-bottom: 12px; font-size: 16px; }}
                .cmd {{ 
                    background: rgba(255,255,255,0.03); border-radius: 6px; padding: 8px 12px;
                    margin: 4px 0; font-family: 'Courier New', monospace; font-size: 12px; color: #aaa;
                }}
                .cmd b {{ color: #00d4ff; }}
                .refresh {{ text-align: center; margin-top: 15px; color: #555; font-size: 11px; }}
                .badges {{ display: flex; gap: 6px; flex-wrap: wrap; margin-top: 8px; }}
                .badge {{ 
                    background: rgba(0,212,255,0.15); border: 1px solid rgba(0,212,255,0.3);
                    border-radius: 12px; padding: 3px 10px; font-size: 11px; color: #00d4ff;
                }}
            </style>
            <meta http-equiv="refresh" content="30">
        </head>
        <body>
            <div class="container">
                <h1>🤖 DateTime Userbot v2.0</h1>
                
                <div class="grid">
                    <div class="card">
                        <h3>⚡ Estado</h3>
                        <div class="{"active" if active else "paused"}">
                            {"✅ Activo" if active else "⏸️ Pausado"}
                        </div>
                        <div class="sub">{"Conectado: " + str(bot_state.get("profile_name", "?")) if bot_state.get("connected") else "Desconectado"}</div>
                    </div>
                    <div class="card">
                        <h3>🕐 Hora</h3>
                        <div class="value">{now.strftime("%I:%M %p")}</div>
                        <div class="sub">{now.strftime("%A, %b %d")} | {TIME_ZONE}</div>
                    </div>
                    <div class="card">
                        <h3>⏱️ Uptime</h3>
                        <div class="value">{uptime_str}</div>
                        <div class="sub">Updates: {bot_state.get("update_count", 0)}</div>
                    </div>
                    <div class="card">
                        <h3>🎨 Estilo</h3>
                        <div class="value">{bot_state.get("image_style", "auto")}</div>
                        <div class="sub">Tema: {bot_state.get("bg_theme", "auto") or "auto"}</div>
                    </div>
                    <div class="card">
                        <h3>🎭 Mood</h3>
                        <div class="value">{bot_state.get("mood_emoji", "") or "—"} {bot_state.get("mood", "none")}</div>
                        <div class="sub">{bot_state.get("mood_bio", "") or "Sin mood"}</div>
                    </div>
                    <div class="card">
                        <h3>💬 Frases</h3>
                        <div class="value">{bot_state.get("bio_category", "random")}</div>
                        <div class="sub">{"Horario" if bot_state.get("schedule_mode") else "Fijo"}</div>
                    </div>
                    <div class="card">
                        <h3>🌤 Clima</h3>
                        <div class="{"on" if bot_state.get("show_weather") else "off"}">{"ON" if bot_state.get("show_weather") else "OFF"}</div>
                        <div class="sub">{bot_state.get("weather_info", "N/A")}</div>
                    </div>
                    <div class="card">
                        <h3>📊 Progreso</h3>
                        <div class="{"on" if bot_state.get("show_progress") else "off"}">{"ON" if bot_state.get("show_progress") else "OFF"}</div>
                        <div class="sub">Barra del dia</div>
                    </div>
                    <div class="card">
                        <h3>📴 AFK</h3>
                        <div class="{"on" if bot_state.get("afk_enabled") else "off"}">{"ON" if bot_state.get("afk_enabled") else "OFF"}</div>
                        <div class="sub">{bot_state.get("afk_since", "") or ""}</div>
                    </div>
                    <div class="card">
                        <h3>⏱️ Intervalo</h3>
                        <div class="value">{bot_state.get("update_interval", 60)}s</div>
                        <div class="sub">Entre actualizaciones</div>
                    </div>
                    <div class="card">
                        <h3>📅 Countdown</h3>
                        <div class="value">{bot_state.get("countdown_date", "No") or "No"}</div>
                        <div class="sub">{bot_state.get("countdown_label", "")}</div>
                    </div>
                    <div class="card">
                        <h3>📝 Notas</h3>
                        <div class="value">{len(bot_state.get("notes", {{}}))}</div>
                        <div class="sub">Guardadas</div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>📋 Comandos de Telegram</h2>
                    <div class="cmd"><b>.on</b> / <b>.off</b> — Activar/Pausar bot</div>
                    <div class="cmd"><b>.style</b> [auto|neon|retro|minimal|gradient] — Estilo de imagen</div>
                    <div class="cmd"><b>.theme</b> [anime|code|gaming|nature|cyberpunk|ocean|sunset|galaxy|retro|minimal|off] — Tema de fondo</div>
                    <div class="cmd"><b>.mood</b> [happy|sad|busy|sleeping|love|gaming|coding|music|coffee|vibes|angry|chill|off] — Estado de animo</div>
                    <div class="cmd"><b>.quote</b> [random|motivation|humor|philosophy|love|tech|life|schedule] — Categoria frases</div>
                    <div class="cmd"><b>.bio</b> [texto|off] — Bio personalizada</div>
                    <div class="cmd"><b>.name</b> [texto|off] — Apellido personalizado</div>
                    <div class="cmd"><b>.interval</b> [30-600] — Segundos entre updates</div>
                    <div class="cmd"><b>.weather</b> [on|off] — Clima en imagen</div>
                    <div class="cmd"><b>.progress</b> [on|off] — Barra de progreso</div>
                    <div class="cmd"><b>.countdown</b> [fecha|off] [label] — Cuenta regresiva</div>
                    <div class="cmd"><b>.afk</b> [on|off|mensaje] — Modo AFK</div>
                    <div class="cmd"><b>.note</b> [save|get|list|del] — Notas personales</div>
                    <div class="cmd"><b>.whois</b> — Info de usuario</div>
                    <div class="cmd"><b>.id</b> — IDs de chat/usuario</div>
                    <div class="cmd"><b>.ping</b> — Latencia + uptime</div>
                    <div class="cmd"><b>.status</b> — Estado completo</div>
                    <div class="cmd"><b>.restart</b> — Reiniciar conexion</div>
                    <div class="cmd"><b>.help</b> — Ayuda completa</div>
                </div>
                <div class="refresh">Auto-refresh 30s | 🤖 v2.0</div>
            </div>
        </body>
        </html>
        """
    
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
