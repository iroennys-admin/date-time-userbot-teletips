#!/usr/bin/env python3
"""Generador de imagenes de perfil con multiples estilos, temas, y funciones avanzadas."""

import datetime
import logging
import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger("DateTimeUserbot")

# ─── Colores para tema dia/noche ──────────────────────────────────
THEME_COLORS = {
    "day": {
        "bg_top": (70, 130, 220),
        "bg_bottom": (135, 200, 255),
        "time_color": (255, 255, 255),
        "date_color": (255, 255, 255),
        "shadow_color": (0, 0, 0),
        "progress_bg": (255, 255, 255, 80),
        "progress_fg": (255, 200, 50, 200),
        "accent": (255, 200, 50),
    },
    "night": {
        "bg_top": (15, 15, 60),
        "bg_bottom": (40, 20, 80),
        "time_color": (0, 255, 255),
        "date_color": (200, 200, 255),
        "shadow_color": (0, 0, 0),
        "progress_bg": (255, 255, 255, 40),
        "progress_fg": (0, 255, 255, 200),
        "accent": (0, 255, 255),
    },
}

# ─── Temas de fondo predefinidos ──────────────────────────────────
BACKGROUND_THEMES = {
    "anime": {
        "name": "Anime",
        "bg_top": (255, 105, 135),
        "bg_bottom": (255, 182, 193),
        "time_color": (255, 255, 255),
        "date_color": (255, 240, 245),
        "shadow_color": (100, 0, 30),
        "accent": (255, 50, 80),
        "emoji": "🌸",
        "pattern": "sakura",
    },
    "code": {
        "name": "Programacion",
        "bg_top": (20, 25, 35),
        "bg_bottom": (30, 40, 55),
        "time_color": (0, 255, 128),
        "date_color": (120, 200, 255),
        "shadow_color": (0, 0, 0),
        "accent": (0, 255, 128),
        "emoji": "💻",
        "pattern": "matrix",
    },
    "gaming": {
        "name": "Gaming",
        "bg_top": (25, 0, 50),
        "bg_bottom": (50, 0, 80),
        "time_color": (200, 50, 255),
        "date_color": (150, 150, 255),
        "shadow_color": (0, 0, 0),
        "accent": (200, 50, 255),
        "emoji": "🎮",
        "pattern": "grid",
    },
    "nature": {
        "name": "Naturaleza",
        "bg_top": (34, 85, 34),
        "bg_bottom": (85, 170, 85),
        "time_color": (255, 255, 255),
        "date_color": (220, 255, 220),
        "shadow_color": (0, 30, 0),
        "accent": (100, 255, 100),
        "emoji": "🌿",
        "pattern": "leaves",
    },
    "cyberpunk": {
        "name": "Cyberpunk",
        "bg_top": (10, 0, 30),
        "bg_bottom": (40, 0, 60),
        "time_color": (255, 0, 128),
        "date_color": (0, 200, 255),
        "shadow_color": (0, 0, 0),
        "accent": (255, 0, 128),
        "emoji": "🌆",
        "pattern": "lines",
    },
    "ocean": {
        "name": "Oceano",
        "bg_top": (0, 50, 100),
        "bg_bottom": (0, 120, 180),
        "time_color": (255, 255, 255),
        "date_color": (180, 230, 255),
        "shadow_color": (0, 20, 50),
        "accent": (0, 200, 255),
        "emoji": "🌊",
        "pattern": "waves",
    },
    "sunset": {
        "name": "Atardecer",
        "bg_top": (255, 80, 50),
        "bg_bottom": (255, 165, 0),
        "time_color": (255, 255, 255),
        "date_color": (255, 230, 200),
        "shadow_color": (80, 20, 0),
        "accent": (255, 200, 50),
        "emoji": "🌅",
        "pattern": "glow",
    },
    "galaxy": {
        "name": "Galaxia",
        "bg_top": (5, 0, 20),
        "bg_bottom": (15, 5, 40),
        "time_color": (200, 180, 255),
        "date_color": (150, 130, 200),
        "shadow_color": (0, 0, 0),
        "accent": (180, 100, 255),
        "emoji": "🌌",
        "pattern": "stars",
    },
    "retro": {
        "name": "Retro 80s",
        "bg_top": (40, 0, 60),
        "bg_bottom": (120, 40, 80),
        "time_color": (255, 105, 180),
        "date_color": (255, 215, 0),
        "shadow_color": (20, 0, 30),
        "accent": (255, 105, 180),
        "emoji": "📼",
        "pattern": "scanlines",
    },
    "minimal": {
        "name": "Minimalista",
        "bg_top": (25, 25, 35),
        "bg_bottom": (35, 35, 45),
        "time_color": (255, 255, 255),
        "date_color": (180, 180, 180),
        "shadow_color": (0, 0, 0),
        "accent": (100, 100, 120),
        "emoji": "◻️",
        "pattern": "none",
    },
}


def get_theme(hour: int) -> str:
    return "day" if 6 <= hour < 19 else "night"


def generate_profile_image(
    time_str: str,
    date_str: str,
    hour: int,
    style: str = "auto",
    bg_theme: str = "",
    base_image: str = "image.jpg",
    font_path: str = "ds-digit.ttf",
    weather: dict = None,
    show_progress: bool = True,
    countdown_days: int = None,
    countdown_label: str = "",
    extra_tz_times: list = None,
    mood_emoji: str = "",
    uptime_str: str = "",
) -> str:
    output_path = "profile_output.jpg"
    
    try:
        # Determinar colores
        if bg_theme and bg_theme in BACKGROUND_THEMES:
            theme_data = BACKGROUND_THEMES[bg_theme]
            colors = {
                "time_color": theme_data["time_color"],
                "date_color": theme_data["date_color"],
                "shadow_color": theme_data["shadow_color"],
                "progress_fg": theme_data["accent"],
            }
            theme_name = theme_data["name"]
        else:
            theme = get_theme(hour) if style == "auto" else "night"
            base_colors = THEME_COLORS.get(theme, THEME_COLORS["night"])
            colors = base_colors
            theme_name = theme.capitalize()

        # Crear fondo segun estilo o tema
        if bg_theme and bg_theme in BACKGROUND_THEMES:
            td = BACKGROUND_THEMES[bg_theme]
            img = _create_gradient(512, 512, td["bg_top"], td["bg_bottom"])
            img = _apply_pattern(img, td.get("pattern", "none"), hour)
        elif style in ("auto", "gradient") or not Path(base_image).exists():
            tc = THEME_COLORS.get(get_theme(hour) if style == "auto" else "night", THEME_COLORS["night"])
            img = _create_gradient(512, 512, tc["bg_top"], tc["bg_bottom"])
        elif style == "neon":
            img = _create_neon_background(512, 512, hour)
        elif style == "retro":
            img = _create_retro_background(512, 512)
        elif style == "minimal":
            img = _create_minimal_background(512, 512, colors)
        else:
            if Path(base_image).exists():
                img = Image.open(base_image).resize((512, 512), Image.Resampling.LANCZOS)
            else:
                tc = THEME_COLORS["night"]
                img = _create_gradient(512, 512, tc["bg_top"], tc["bg_bottom"])

        draw = ImageDraw.Draw(img)

        # Cargar fuentes
        try:
            if Path(font_path).exists():
                font_xl = ImageFont.truetype(font_path, 68)
                font_large = ImageFont.truetype(font_path, 52)
                font_medium = ImageFont.truetype(font_path, 28)
                font_small = ImageFont.truetype(font_path, 20)
                font_tiny = ImageFont.truetype(font_path, 16)
            else:
                font_xl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 68)
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
                font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
                font_tiny = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except Exception:
            font_xl = ImageFont.load_default()
            font_large = font_xl
            font_medium = font_xl
            font_small = font_xl
            font_tiny = font_xl
        
        # Overlay oscuro para legibilidad
        overlay = Image.new("RGBA", (512, 512), (0, 0, 0, 60))
        img_rgba = img.convert("RGBA")
        img_rgba = Image.alpha_composite(img_rgba, overlay)
        img = img_rgba.convert("RGB")
        draw = ImageDraw.Draw(img)
        
        y_offset = 25
        img_w = 512

        # Clima (arriba)
        if weather:
            weather_text = f"{weather['emoji']} {weather['temp']} {weather['desc']}"
            w_bbox = draw.textbbox((0, 0), weather_text, font=font_small)
            draw.text((2, y_offset + 2), weather_text, (0, 0, 0), font=font_small)
            draw.text((0, y_offset), weather_text, colors.get("time_color", (255, 255, 255)), font=font_small)
            y_offset += 28

        # Mood emoji grande (si hay)
        if mood_emoji:
            try:
                mood_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
            except:
                mood_font = font_large
            mood_bbox = draw.textbbox((0, 0), mood_emoji, font=mood_font)
            mood_w = mood_bbox[2] - mood_bbox[0]
            draw.text(((img_w - mood_w) // 2, y_offset), mood_emoji, font=mood_font)
            y_offset += 42

        # Hora principal
        time_color = colors.get("time_color", (0, 255, 255))
        date_color = colors.get("date_color", (200, 200, 255))
        shadow = colors.get("shadow_color", (0, 0, 0))

        time_bbox = draw.textbbox((0, 0), time_str, font=font_xl)
        time_w = time_bbox[2] - time_bbox[0]
        time_x = (img_w - time_w) // 2
        draw.text((time_x + 2, y_offset + 2), time_str, shadow, font=font_xl)
        draw.text((time_x, y_offset), time_str, time_color, font=font_xl)
        y_offset += 78

        # Fecha
        date_bbox = draw.textbbox((0, 0), date_str, font=font_medium)
        date_w = date_bbox[2] - date_bbox[0]
        date_x = (img_w - date_w) // 2
        draw.text((date_x + 1, y_offset + 1), date_str, shadow, font=font_medium)
        draw.text((date_x, y_offset), date_str, date_color, font=font_medium)
        y_offset += 36

        # Zonas horarias adicionales
        if extra_tz_times:
            for tz_name, tz_time in extra_tz_times:
                tz_text = f"{tz_name}: {tz_time}"
                tz_bbox = draw.textbbox((0, 0), tz_text, font=font_tiny)
                tz_w = tz_bbox[2] - tz_bbox[0]
                tz_x = (img_w - tz_w) // 2
                draw.text((tz_x, y_offset), tz_text, (180, 180, 200), font=font_tiny)
                y_offset += 20

        # Barra de progreso del dia
        if show_progress:
            now = datetime.datetime.now()
            day_progress = (now.hour * 3600 + now.minute * 60 + now.second) / 86400
            bar_y = y_offset + 10
            bar_w = 380
            bar_h = 14
            bar_x = (512 - bar_w) // 2
            
            draw.rounded_rectangle(
                [bar_x, bar_y, bar_x + bar_w, bar_y + bar_h],
                radius=7, fill=(255, 255, 255, 30)
            )
            fill_w = int(bar_w * day_progress)
            if fill_w > 0:
                prog_color = colors.get("progress_fg", (0, 255, 255))
                draw.rounded_rectangle(
                    [bar_x, bar_y, bar_x + fill_w, bar_y + bar_h],
                    radius=7, fill=prog_color
                )
            pct_text = f"{day_progress*100:.0f}% del dia"
            pct_bbox = draw.textbbox((0, 0), pct_text, font=font_tiny)
            pct_w = pct_bbox[2] - pct_bbox[0]
            draw.text(((512 - pct_w) // 2, bar_y + bar_h + 3), pct_text, (180, 180, 200), font=font_tiny)
            y_offset = bar_y + bar_h + 22

        # Countdown
        if countdown_days is not None and countdown_days >= 0:
            cd_text = f"{countdown_days} dias"
            if countdown_label:
                cd_text = f"{countdown_label}: {cd_text}"
            cd_bbox = draw.textbbox((0, 0), cd_text, font=font_medium)
            cd_w = cd_bbox[2] - cd_bbox[0]
            cd_x = (512 - cd_w) // 2
            y_cd = 512 - 55
            draw.text((cd_x + 1, y_cd + 1), cd_text, (0, 0, 0), font=font_medium)
            draw.text((cd_x, y_cd), cd_text, (255, 100, 100), font=font_medium)

        # Uptime (esquina inferior derecha)
        if uptime_str:
            draw.text((512 - 120, 512 - 20), uptime_str, (120, 120, 140), font=font_tiny)

        # Nombre del tema (esquina inferior izquierda)
        if bg_theme and bg_theme in BACKGROUND_THEMES:
            td = BACKGROUND_THEMES[bg_theme]
            theme_label = f"{td['emoji']} {td['name']}"
            draw.text((8, 512 - 20), theme_label, (140, 140, 160), font=font_tiny)

        img.save(output_path, "JPEG", quality=95)
        return output_path
        
    except Exception as e:
        logger.error(f"Error generando imagen: {e}")
        return None


# ─── Patrones de fondo ────────────────────────────────────────────

def _apply_pattern(img, pattern: str, hour: int = 12):
    """Aplica un patron decorativo sobre la imagen."""
    draw = ImageDraw.Draw(img)
    w, h = img.size

    if pattern == "stars":
        for _ in range(60):
            x = random.randint(0, w)
            y = random.randint(0, h)
            size = random.randint(1, 3)
            brightness = random.randint(150, 255)
            draw.ellipse([x, y, x + size, y + size], fill=(brightness, brightness, brightness + 20))

    elif pattern == "matrix":
        chars = "01"
        for y in range(0, h, 18):
            line = "".join(random.choice(chars) for _ in range(w // 10))
            draw.text((10, y), line, fill=(0, random.randint(80, 150), 0), font=ImageFont.load_default())

    elif pattern == "sakura":
        for _ in range(25):
            x = random.randint(0, w)
            y = random.randint(0, h)
            size = random.randint(3, 10)
            alpha = random.randint(60, 150)
            draw.ellipse([x, y, x + size, y + size], fill=(255, 180, 200, alpha))

    elif pattern == "grid":
        for x in range(0, w, 30):
            draw.line([(x, 0), (x, h)], fill=(80, 0, 120, 40), width=1)
        for y in range(0, h, 30):
            draw.line([(0, y), (w, y)], fill=(80, 0, 120, 40), width=1)

    elif pattern == "lines":
        for y in range(0, h, 6):
            intensity = int(20 + 15 * math.sin(y * 0.04 + hour))
            draw.line([(0, y), (w, y)], fill=(intensity, 0, intensity + 15))

    elif pattern == "scanlines":
        for y in range(0, h, 3):
            draw.line([(0, y), (w, y)], fill=(0, 0, 0, 30))

    elif pattern == "waves":
        for y in range(0, h, 20):
            points = [(x, y + int(8 * math.sin(x * 0.03 + y * 0.05))) for x in range(0, w, 4)]
            if len(points) > 1:
                draw.line(points, fill=(0, 100, 180, 30), width=1)

    elif pattern == "glow":
        for r in range(120, 0, -4):
            alpha = int(8 * (1 - r / 120))
            draw.ellipse([256 - r, 350 - r, 256 + r, 350 + r], fill=(255, alpha * 2, 0, alpha))

    return img


def _create_gradient(w, h, top_color, bottom_color):
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        ratio = y / h
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return img


def _create_neon_background(w, h, hour):
    img = Image.new("RGB", (w, h), (10, 0, 20))
    draw = ImageDraw.Draw(img)
    for y in range(0, h, 8):
        intensity = int(30 + 20 * math.sin(y * 0.05 + hour))
        draw.line([(0, y), (w, y)], fill=(intensity, 0, intensity + 20))
    for r in range(150, 0, -3):
        alpha = int(15 * (1 - r / 150))
        draw.ellipse([256 - r, 256 - r, 256 + r, 256 + r], fill=(alpha, 0, alpha + 5))
    return img


def _create_retro_background(w, h):
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        ratio = y / h
        if ratio < 0.5:
            r = int(255 - 60 * ratio)
            g = int(100 + 50 * ratio)
            b = int(80 + 100 * ratio)
        else:
            r = int(30 + 20 * (1 - ratio))
            g = int(20 + 10 * (1 - ratio))
            b = int(40 + 20 * (1 - ratio))
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    for y in range(int(h * 0.55), h, 4):
        draw.line([(0, y), (w, y)], fill=(40, 20, 60))
    return img


def _create_minimal_background(w, h, colors):
    img = Image.new("RGB", (w, h), (25, 25, 35))
    draw = ImageDraw.Draw(img)
    draw.line([(100, 180), (412, 180)], fill=(60, 60, 80), width=1)
    draw.line([(100, 340), (412, 340)], fill=(60, 60, 80), width=1)
    return img
