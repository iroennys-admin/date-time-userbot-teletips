#!/usr/bin/env python3
"""Dashboard web para monitorear y configurar el bot."""

from flask import Blueprint, jsonify, request
import datetime
import pytz

dashboard_bp = Blueprint("dashboard", __name__)


def register_dashboard(app, bot_state, config_module):
    """Registra las rutas del dashboard en la app Flask."""
    
    @app.route("/dashboard")
    def dashboard():
        """Panel de control del bot."""
        from config import TIME_ZONE
        tz = pytz.timezone(TIME_ZONE)
        now = datetime.datetime.now(tz)
        
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
                .container {{ max-width: 900px; margin: 0 auto; }}
                h1 {{ text-align: center; margin-bottom: 30px; color: #00d4ff; font-size: 28px; }}
                .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
                .card {{ 
                    background: rgba(255,255,255,0.05); border-radius: 12px; padding: 20px;
                    border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(10px);
                }}
                .card h3 {{ color: #00d4ff; margin-bottom: 10px; font-size: 14px; text-transform: uppercase; }}
                .card .value {{ font-size: 24px; font-weight: bold; color: #fff; }}
                .card .sub {{ font-size: 12px; color: #888; margin-top: 5px; }}
                .status-on {{ color: #00ff88; }} .status-off {{ color: #ff4444; }}
                .connected {{ color: #00ff88; font-size: 28px; }}
                .disconnected {{ color: #ff4444; font-size: 28px; }}
                .commands {{ margin-top: 30px; }}
                .cmd {{ 
                    background: rgba(255,255,255,0.03); border-radius: 8px; padding: 10px 15px;
                    margin: 5px 0; font-family: monospace; color: #aaa;
                }}
                .cmd b {{ color: #00d4ff; }}
                .refresh {{ 
                    text-align: center; margin-top: 20px; color: #555; font-size: 12px;
                }}
            </style>
            <meta http-equiv="refresh" content="30">
        </head>
        <body>
            <div class="container">
                <h1>🤖 DateTime Userbot</h1>
                <div class="grid">
                    <div class="card">
                        <h3>🔌 Estado</h3>
                        <div class="value {"connected" if bot_state.get("connected") else "disconnected"}">
                            {"✅ Online" if bot_state.get("connected") else "❌ Offline"}
                        </div>
                        <div class="sub">{"Conectado como: " + str(bot_state.get("profile_name", "?")) if bot_state.get("connected") else "Desconectado"}</div>
                    </div>
                    <div class="card">
                        <h3>🕐 Hora Actual</h3>
                        <div class="value">{now.strftime("%I:%M %p")}</div>
                        <div class="sub">{now.strftime("%A, %b %d, %Y")} | {TIME_ZONE}</div>
                    </div>
                    <div class="card">
                        <h3>🔄 Actualizaciones</h3>
                        <div class="value">{bot_state.get("update_count", 0)}</div>
                        <div class="sub">Última: {bot_state.get("last_update", "N/A")[:19] if bot_state.get("last_update") else "N/A"}</div>
                    </div>
                    <div class="card">
                        <h3>🎨 Estilo Imagen</h3>
                        <div class="value">{bot_state.get("image_style", "auto")}</div>
                        <div class="sub">auto | neon | retro | minimal | gradient</div>
                    </div>
                    <div class="card">
                        <h3>💬 Frases</h3>
                        <div class="value">{bot_state.get("bio_category", "random")}</div>
                        <div class="sub">{"Horario mode ON" if bot_state.get("schedule_mode") else "Categoría fija"}</div>
                    </div>
                    <div class="card">
                        <h3>🌤 Clima</h3>
                        <div class="value {"status-on" if bot_state.get("show_weather") else "status-off"}">{"ON" if bot_state.get("show_weather", True) else "OFF"}</div>
                        <div class="sub">{bot_state.get("weather_info", "N/A")}</div>
                    </div>
                    <div class="card">
                        <h3>📊 Progreso</h3>
                        <div class="value {"status-on" if bot_state.get("show_progress") else "status-off"}">{"ON" if bot_state.get("show_progress", True) else "OFF"}</div>
                        <div class="sub">Barra de progreso del día</div>
                    </div>
                    <div class="card">
                        <h3>📴 AFK</h3>
                        <div class="value {"status-on" if bot_state.get("afk_enabled") else "status-off"}">{"ON" if bot_state.get("afk_enabled", False) else "OFF"}</div>
                        <div class="sub">{bot_state.get("afk_message", "")[:30]}</div>
                    </div>
                </div>
                <div class="commands">
                    <h2 style="color:#00d4ff; margin-bottom:15px;">📋 Comandos de Telegram</h2>
                    <div class="cmd"><b>.style</b> [auto|neon|retro|minimal|gradient] — Cambiar estilo de imagen</div>
                    <div class="cmd"><b>.quote</b> [random|motivation|humor|philosophy|love|tech|life|schedule] — Categoría de frases</div>
                    <div class="cmd"><b>.weather</b> [on|off] — Mostrar clima en imagen</div>
                    <div class="cmd"><b>.progress</b> [on|off] — Barra de progreso del día</div>
                    <div class="cmd"><b>.countdown</b> [fecha|off] [label] — Cuenta regresiva</div>
                    <div class="cmd"><b>.afk</b> [on|off|mensaje] — Modo AFK</div>
                    <div class="cmd"><b>.status</b> — Estado del bot</div>
                    <div class="cmd"><b>.help</b> — Ayuda</div>
                </div>
                <div class="refresh">Auto-refresh cada 30s | 🤖 DateTime Userbot v2.0</div>
            </div>
        </body>
        </html>
        """
    
    @app.route("/api/status")
    def api_status():
        """API JSON del estado del bot."""
        return jsonify(bot_state)
    
    @app.route("/api/config", methods=["POST"])
    def api_config():
        """API para cambiar configuración vía POST."""
        data = request.get_json(force=True)
        changed = []
        
        for key in ["image_style", "bio_category", "show_weather", "show_progress", 
                     "afk_enabled", "afk_message", "countdown_date", "countdown_label",
                     "schedule_mode"]:
            if key in data:
                bot_state[key] = data[key]
                changed.append(key)
        
        return jsonify({"success": True, "changed": changed})
