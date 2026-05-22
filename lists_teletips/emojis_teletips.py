# Emojis por hora del día y emojis generales
# Usado cuando DYNAMIC_HOUR_EMOJI está activado

hour_emojis = {
    # Madrugada (00:00 - 05:59)
    0: "🌙", 1: "🌑", 2: "🌠", 3: "💫", 4: "✨", 5: "🌅",
    # Mañana (06:00 - 11:59)
    6: "☀️", 7: "🌻", 8: "🐝", 9: "☕", 10: "🌤", 11: "🌈",
    # Tarde (12:00 - 17:59)
    12: "🔥", 13: "⚡", 14: "🎯", 15: "🚀", 16: "💪", 17: "🌆",
    # Noche (18:00 - 23:59)
    18: "🌇", 19: "🌃", 20: "🎸", 21: "🎵", 22: "📖", 23: "🛋",
}

# Emojis generales (para cuando DYNAMIC_HOUR_EMOJI está desactivado)
general_emojis = [
    "💯", "🔅", "🔆", "〽️", "💬", "💭", "🗯", "🌻", "⚡️", "💫",
    "🌟", "🍃", "🔥", "💎", "🚀", "🎯", "🌈", "🦋", "🌸", "✨",
    "🎵", "🌙", "☀️", "🍀", "🎨", "💡", "🌊", "🎸", "🏆", "🪐",
    "🎪", "🎭", "🎬", "📚", "🔮", "⚡", "🌍", "🦅", "💫", "⭐",
    "🪷", "🫧", "🪩", "🫶", "🤍", "🖤", "🌸", "💫",
]

def get_emoji(hour: int, dynamic: bool = True) -> str:
    """Obtiene un emoji según la hora o aleatorio."""
    if dynamic:
        return hour_emojis.get(hour, "✨")
    import random
    return random.choice(general_emojis)
