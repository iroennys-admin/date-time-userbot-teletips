# Frases motivacionales organizadas por categoría

quotes_by_category = {
    "motivation": [
        "Love For All, Hatred For None.",
        "Change the world by being yourself.",
        "Every moment is a fresh beginning.",
        "Never regret anything that made you smile.",
        "Aspire to inspire before we expire.",
        "Be so good they can't ignore you.",
        "Yesterday you said tomorrow. Just do it.",
        "Strive for greatness.",
        "And still, I rise.",
        "The time is always right to do what is right.",
        "Progress, not perfection.",
        "Dream big, work hard, stay focused.",
        "Make each day your masterpiece.",
        "I have nothing to lose but something to gain.",
        "Be fearless in the pursuit of what sets your soul on fire.",
        "Do what is right, not what is easy.",
        "Fall seven times, stand up eight.",
        "The only impossible journey is the one you never begin.",
        "Inhale courage, exhale fear.",
        "Your potential is endless.",
    ],
    "humor": [
        "I could agree with you but then we'd both be wrong.",
        "I'm not lazy, I'm on energy saving mode.",
        "My bed and I love each other, but my alarm clock doesn't approve.",
        "I'm on a seafood diet. I see food and I eat it.",
        "Why don't scientists trust atoms? Because they make up everything.",
        "Life is short. Smile while you still have teeth.",
        "I'm not arguing. I'm just explaining why I'm right.",
        "Common sense is like deodorant. The people who need it most never use it.",
        "I told my computer I needed a break, and now it won't stop sending me travel ads.",
        "My life feels like a test I didn't study for.",
        "I'm not procrastinating. I'm doing side quests.",
        "If you can't convince them, confuse them.",
        "Behind every great person is a rolls eyes emoji.",
        "I came, I saw, I forgot what I came for.",
        "My phone battery lasts longer than my motivation.",
    ],
    "philosophy": [
        "Everything you can imagine is real.",
        "Simplicity is the ultimate sophistication.",
        "What we think, we become.",
        "All limitations are self-imposed.",
        "Reality is wrong, dreams are for real.",
        "Happiness depends upon ourselves.",
        "What consumes your mind controls your life.",
        "The meaning of life is to give life meaning.",
        "Turn your wounds into wisdom.",
        "White is not always light and black is not always dark.",
        "Let the beauty of what you love be what you do.",
        "When words fail, music speaks.",
        "To live will be an awfully big adventure.",
        "It hurt because it mattered.",
        "What lies behind us and what lies before us are tiny matters compared to what lies within us.",
    ],
    "love": [
        "Die with memories, not dreams.",
        "Nothing lasts forever but at least we got these memories.",
        "Try to be a rainbow in someone's cloud.",
        "A happy soul is the best shield for a cruel world.",
        "Stay close to people who feel like sunshine.",
        "You are allowed to be both a masterpiece and a work in progress.",
        "Embrace the glorious mess that you are.",
        "Be the energy you want to attract.",
        "May your choices reflect your hopes, not your fears.",
        "Don't you know your imperfections is a blessing?",
        "Collect moments, not things.",
        "Choose kindness and laugh often.",
        "I will remember and recover, not forgive and forget.",
        "She believed she could, so she did.",
        "Be patient with yourself. Growth takes time.",
    ],
    "tech": [
        "Code is poetry written in logic.",
        "In a world of algorithms, be the exception.",
        "Innovation distinguishes between a leader and a follower.",
        "The best error message is the one that never shows up.",
        "Talk is cheap. Show me the code.",
        "First, solve the problem. Then, write the code.",
        "The cloud is just someone else's computer.",
        "There are only 10 types of people: those who understand binary and those who don't.",
        "Artificial intelligence is the new electricity.",
        "The future is already here, it's just not evenly distributed.",
        "Any sufficiently advanced technology is indistinguishable from magic.",
        "Stay curious. Stay coding.",
        "Automate everything. Even your existence.",
        "Data is the new oil. AI is the new refinery.",
        "404: Motivation not found. Retrying...",
    ],
    "life": [
        "Tough times never last but tough people do.",
        "Problems are not stop signs, they are guidelines.",
        "Have enough courage to start and enough heart to finish.",
        "Whatever you do, do it well.",
        "Oh, the things you can find, if you don't stay behind.",
        "Determine your priorities and focus on them.",
        "I don't need it to be easy, I need it to be worth it.",
        "Never let your emotions overpower your intelligence.",
        "Change the game, don't let the game change you.",
        "Small steps every day lead to big changes.",
        "Breathe. It's just a bad day, not a bad life.",
        "A smooth sea never made a skilled sailor.",
        "Life begins at the end of your comfort zone.",
        "Don't compare your beginning to someone else's middle.",
        "Everything will be okay in the end. If it's not okay, it's not the end.",
    ],
}

# Frases según horario
schedule_quotes = {
    "morning": [  # 6-12
        "Good morning! Make today count.",
        "Rise and shine! New day, new opportunities.",
        "Every sunrise is an invitation to brighten someone's day.",
        "Morning coffee and positive vibes only.",
        "Start each day with a grateful heart.",
        "Today is a new chance to be amazing.",
        "Wake up with determination, go to bed with satisfaction.",
        "The early morning has gold in its mouth.",
    ],
    "afternoon": [  # 12-18
        "Keep going! The afternoon is yours.",
        "Halfway through the day, halfway to greatness.",
        "Afternoon energy: refuel and refocus.",
        "The best part of your day is still ahead.",
        "Don't watch the clock; do what it does. Keep going.",
        "Afternoon vibes: stay productive, stay positive.",
        "Make the second half better than the first.",
        "Consistency is the key to achievement.",
    ],
    "night": [  # 18-24
        "Rest is not idleness. Recharge for tomorrow.",
        "Night thoughts, quiet mind, grateful heart.",
        "End the day with a smile. You did great.",
        "Stars can't shine without darkness.",
        "Peaceful night, peaceful mind.",
        "Tomorrow is a new page. Rest well.",
        "The night is darkest just before the dawn.",
        "Close the day with gratitude, open tomorrow with hope.",
    ],
    "late_night": [  # 0-6
        "Still awake? Remember to rest.",
        "Late nights build future successes.",
        "The world is quiet. Time to reflect.",
        "Sleep is a beautiful thing. Don't skip it.",
        "Night owls see what early birds miss.",
        "Burning the midnight oil? Take care of yourself.",
        "Dream big, even with your eyes open.",
        "Rest now, conquer tomorrow.",
    ],
}

# Lista combinada para compatibilidad con el código anterior
quotes_teletips = []
for category_quotes in quotes_by_category.values():
    quotes_teletips.extend(category_quotes)

def get_quote(category: str = "random", hour: int = None, schedule_mode: bool = True) -> str:
    """Obtiene una frase según categoría u horario."""
    import random
    
    if schedule_mode and hour is not None:
        if 6 <= hour < 12:
            return random.choice(schedule_quotes["morning"])
        elif 12 <= hour < 18:
            return random.choice(schedule_quotes["afternoon"])
        elif 18 <= hour < 24:
            return random.choice(schedule_quotes["night"])
        else:
            return random.choice(schedule_quotes["late_night"])
    
    if category == "random":
        all_categories = list(quotes_by_category.keys())
        chosen = random.choice(all_categories)
        return random.choice(quotes_by_category[chosen])
    
    cat_quotes = quotes_by_category.get(category, quotes_by_category["motivation"])
    return random.choice(cat_quotes)
