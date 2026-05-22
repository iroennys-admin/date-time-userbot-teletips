#!/usr/bin/env python3
"""Generador de imágenes de perfil con múltiples estilos, temas día/noche, y más."""

import datetime
import logging
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger("DateTimeUserbot")

# Colores para tema día/noche
THEME_COLORS = {
    "day": {
        "bg_top": (70, 130, 220),      # Azul cielo
        "bg_bottom": (135, 200, 255),   # Azul claro
        "time_color": (255, 255, 255),  # Blanco
        "date_color": (255, 255, 255),
        "shadow_color": (0, 0, 0),
        "progress_bg": (255, 255, 255, 80),
        "progress_fg": (255, 200, 50, 200),
    },
    "night": {
        "bg_top": (15, 15, 60),        # Azul oscuro
        "bg_bottom": (40, 20, 80),     # Púrpura oscuro
        "time_color": (0, 255, 255),   # Cian neón
        "date_color": (200, 200, 255),
        "shadow_color": (0, 0, 0),
        "progress_bg": (255, 255, 255, 40),
        "progress_fg": (0, 255, 255, 200),
    },
}


def get_theme(hour: int) -> str:
    """Determina si es día o noche basado en la hora."""
    return "day" if 6 <= hour < 19 else "night"


def generate_profile_image(
    time_str: str,
    date_str: str,
    hour: int,
    style: str = "auto",
    base_image: str = "image.jpg",
    font_path: str = "ds-digit.ttf",
    weather: dict = None,
    show_progress: bool = True,
    countdown_days: int = None,
    countdown_label: str = "",
    extra_tz_times: list = None,
) -> str:
    """
    Genera una imagen de perfil de 512x512 con todas las mejoras.
    
    Retorna la ruta del archivo generado.
    """
    output_path = "profile_output.jpg"
    
    try:
        theme = get_theme(hour) if style == "auto" else None
        colors = THEME_COLORS.get(theme, THEME_COLORS["night"]) if theme else THEME_COLORS["night"]
        
        # Crear imagen base según estilo
        if style in ("auto", "gradient") or not Path(base_image).exists():
            img = _create_gradient(512, 512, colors["bg_top"], colors["bg_bottom"])
        elif style == "neon":
            img = _create_neon_background(512, 512, hour)
        elif style == "retro":
            img = _create_retro_background(512, 512)
        elif style == "minimal":
            img = _create_minimal_background(512, 512, colors)
        elif style == "emoji":
            img = _create_emoji_background(512, 512, hour)
        else:
            if Path(base_image).exists():
                img = Image.open(base_image).resize((512, 512), Image.Resampling.LANCZOS)
            else:
                img = _create_gradient(512, 512, colors["bg_top"], colors["bg_bottom"])
        
        draw = ImageDraw.Draw(img)
        
        # Cargar fuentes
        try:
            if Path(font_path).exists():
                font_xl = ImageFont.truetype(font_path, 68)
                font_large = ImageFont.truetype(font_path, 52)
                font_medium = ImageFont.truetype(font_path, 28)
                font_small = ImageFont.truetype(font_path, 20)
            else:
                font_xl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 68)
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
                font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except Exception:
            font_xl = ImageFont.load_default()
            font_large = font_xl
            font_medium = font_xl
            font_small = font_xl
        
        img_w = 512
        
        # ── Overlay oscuro para legibilidad ──
        overlay = Image.new("RGBA", (512, 512), (0, 0, 0, 80))
        img_rgba = img.convert("RGBA")
        img_rgba = Image.alpha_composite(img_rgba, overlay)
        img = img_rgba.convert("RGB")
        draw = ImageDraw.Draw(img)
        
        y_offset = 30
        
        # ── Clima (arriba) ──
        if weather:
            weather_text = f"{weather['emoji']} {weather['temp']} {weather['desc']}"
            w_bbox = draw.textbbox((0, 0), weather_text, font=font_small)
            w_w = w_bbox[2] - w_bbox[0]
            draw.text((2, y_offset + 2), weather_text, (0, 0, 0), font=font_small)
            draw.text((0, y_offset), weather_text, colors["time_color"], font=font_small)
            y_offset += 30
        
        # ── Hora principal (centrada, grande) ──
        time_bbox = draw.textbbox((0, 0), time_str, font=font_xl)
        time_w = time_bbox[2] - time_bbox[0]
        time_x = (img_w - time_w) // 2
        draw.text((time_x + 2, y_offset + 2), time_str, colors["shadow_color"], font=font_xl)
        draw.text((time_x, y_offset), time_str, colors["time_color"], font=font_xl)
        y_offset += 80
        
        # ── Fecha ──
        date_bbox = draw.textbbox((0, 0), date_str, font=font_medium)
        date_w = date_bbox[2] - date_bbox[0]
        date_x = (img_w - date_w) // 2
        draw.text((date_x + 1, y_offset + 1), date_str, colors["shadow_color"], font=font_medium)
        draw.text((date_x, y_offset), date_str, colors["date_color"], font=font_medium)
        y_offset += 40
        
        # ── Zonas horarias adicionales ──
        if extra_tz_times:
            for tz_name, tz_time in extra_tz_times:
                tz_text = f"{tz_name}: {tz_time}"
                tz_bbox = draw.textbbox((0, 0), tz_text, font=font_small)
                tz_w = tz_bbox[2] - tz_bbox[0]
                tz_x = (img_w - tz_w) // 2
                draw.text((tz_x, y_offset), tz_text, (200, 200, 200), font=font_small)
                y_offset += 24
        
        # ── Barra de progreso del día ──
        if show_progress:
            now = datetime.datetime.now()
            day_progress = (now.hour * 3600 + now.minute * 60 + now.second) / 86400
            bar_y = y_offset + 15
            bar_w = 400
            bar_h = 16
            bar_x = (512 - bar_w) // 2
            
            # Fondo de la barra
            draw.rounded_rectangle(
                [bar_x, bar_y, bar_x + bar_w, bar_y + bar_h],
                radius=8, fill=(255, 255, 255, 40)
            )
            # Progreso
            fill_w = int(bar_w * day_progress)
            if fill_w > 0:
                draw.rounded_rectangle(
                    [bar_x, bar_y, bar_x + fill_w, bar_y + bar_h],
                    radius=8, fill=colors["progress_fg"]
                )
            # Texto del porcentaje
            pct_text = f"{day_progress*100:.0f}% del día"
            pct_bbox = draw.textbbox((0, 0), pct_text, font=font_small)
            pct_w = pct_bbox[2] - pct_bbox[0]
            draw.text(((512 - pct_w) // 2, bar_y + bar_h + 4), pct_text, (200, 200, 200), font=font_small)
            y_offset = bar_y + bar_h + 28
        
        # ── Countdown ──
        if countdown_days is not None and countdown_days >= 0:
            cd_text = f"{countdown_days} días"
            if countdown_label:
                cd_text = f"{countdown_label}: {cd_text}"
            cd_bbox = draw.textbbox((0, 0), cd_text, font=font_medium)
            cd_w = cd_bbox[2] - cd_bbox[0]
            cd_x = (512 - cd_w) // 2
            y_cd = 512 - 60
            draw.text((cd_x + 1, y_cd + 1), cd_text, (0, 0, 0), font=font_medium)
            draw.text((cd_x, y_cd), cd_text, (255, 100, 100), font=font_medium)
        
        img.save(output_path, "JPEG", quality=95)
        return output_path
        
    except Exception as e:
        logger.error(f"Error generando imagen: {e}")
        return None


# ─── Estilos de fondo ──────────────────────────────────────────────

def _create_gradient(w, h, top_color, bottom_color):
    """Degradado vertical suave."""
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
    """Fondo estilo neón cyberpunk."""
    img = Image.new("RGB", (w, h), (10, 0, 20))
    draw = ImageDraw.Draw(img)
    # Líneas de neón
    for y in range(0, h, 8):
        intensity = int(30 + 20 * math.sin(y * 0.05 + hour))
        draw.line([(0, y), (w, y)], fill=(intensity, 0, intensity + 20))
    # Brillo central
    for r in range(150, 0, -3):
        alpha = int(15 * (1 - r / 150))
        draw.ellipse([256 - r, 256 - r, 256 + r, 256 + r], fill=(alpha, 0, alpha + 5))
    return img


def _create_retro_background(w, h):
    """Fondo estilo retro sunset."""
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        ratio = y / h
        if ratio < 0.5:
            # Cielo naranja-rosa
            r = int(255 - 60 * ratio)
            g = int(100 + 50 * ratio)
            b = int(80 + 100 * ratio)
        else:
            # Suelo oscuro
            r = int(30 + 20 * (1 - ratio))
            g = int(20 + 10 * (1 - ratio))
            b = int(40 + 20 * (1 - ratio))
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    # Líneas horizontales retro
    for y in range(int(h * 0.55), h, 4):
        draw.line([(0, y), (w, y)], fill=(40, 20, 60))
    return img


def _create_minimal_background(w, h, colors):
    """Fondo minimalista oscuro."""
    img = Image.new("RGB", (w, h), (25, 25, 35))
    draw = ImageDraw.Draw(img)
    # Línea sutil superior
    draw.line([(100, 180), (412, 180)], fill=(60, 60, 80), width=1)
    draw.line([(100, 340), (412, 340)], fill=(60, 60, 80), width=1)
    return img


def _create_emoji_background(w, h, hour):
    """Fondo con emoji grande semi-transparente."""
    # Usar degradado de noche por defecto
    img = _create_gradient(w, h, (15, 15, 60), (40, 20, 80))
    return img
