import streamlit as st
import random
import time
from streamlit_extras.let_it_rain import rain
from streamlit_lottie import st_lottie
import json
import requests

# ✅ MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(page_title="📚 महेश्वर सूत्र - Memory Flip", layout="centered")

# Load Lottie animations
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Animation URLs
celebration_anim = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_5tkzkblw.json")
thinking_anim = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_uqfbsoei.json")
welcome_anim = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_5tkzkblw.json")

# Sound effects (using HTML audio)
def play_sound(sound_type):
    audio_html = ""
    if sound_type == "correct":
        audio_html = """<audio autoplay><source src="https://www.soundjay.com/buttons/sounds/button-09.mp3"></audio>"""
    elif sound_type == "wrong":
        audio_html = """<audio autoplay><source src="https://www.soundjay.com/buttons/sounds/button-10.mp3"></audio>"""
    elif sound_type == "level_up":
        audio_html = """<audio autoplay><source src="https://www.soundjay.com/buttons/sounds/button-21.mp3"></audio>"""
    st.components.v1.html(audio_html, height=0)

# Maheshwar Sutra sequence
sutra_sequence = [ 
    ["अ", "इ", "उ", "ण्"],
    ["ऋ", "ऌ", "क्"],
    ["ए", "ओ", "ङ्"],
    ["ऐ", "औ", "च्"],
    ["ह", "य", "व", "र", "ट्"],
    ["ल", "ण्"],
    ["ञ", "म", "ङ", "ण", "न", "म्"],
    ["झ", "भ", "ञ्"],
    ["घ", "ढ", "ध", "ष्"],
    ["ज", "ब", "ग", "ड", "द", "श्"],
    ["ख", "फ", "छ", "ठ", "थ", "च", "ट", "त", "व्"],
    ["क", "प", "य्"],
    ["श", "ष", "स", "र्"],
    ["ह", "ल्"]
]

# Flatten the sequence
flat_sutra_sequence = [letter for sublist in sutra_sequence for letter in sublist]

# CSS Styles
st.markdown("""
    <style>
    .big-font {
        font-size:30px !important;
        color: #d63384;
        font-weight: bold;
    }
    .card-button {
        font-size: 26px;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem;
        border: 2px solid #6c757d;
        background-color: #f8f9fa;
        transition: all 0.3s ease;
    }
    .card-button:hover {
        background-color: #ffc107;
        transform: scale(1.05);
        cursor: pointer;
    }
    .question-box {
        background-color: #fff3cd;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #ffeeba;
        margin: 20px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .score-display {
        font-size: 24px;
        color: #28a745;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .progress-bar {
        height: 10px;
        background-color: #e9ecef;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .progress {
        height: 100%;
        background-color: #28a745;
        border-radius: 5px;
        transition: width 0.5s ease;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_index' not in st.session_state:
    st.session_state.current_index = random.randint(0, len(sutra_sequence) - 2)
if 'options' not in st.session_state:
    st.session_state.options = []
if 'selected' not in st.session_state:
    st.session_state.selected = None
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'level' not in st.session_state:
    st.session_state.level = 1
if 'usage_count' not in st.session_state:
    st.session_state.usage_count = 0
if 'streak' not in st.session_state:
    st.session_state.streak = 0
if 'max_streak' not in st.session_state:
    st.session_state.max_streak = 0

# Welcome animation
if st.session_state.level == 1 and st.session_state.score == 0:
    st_lottie(welcome_anim, speed=1, height=200, key="welcome")

# 🎯 Game title
st.title("🧠 महेश्वर सूत्र - Memory Flip Challenge")
st.markdown(f"### 🌟 स्तर {st.session_state.level}")

# Progress bar
progress = min((st.session_state.score % 3) / 3 * 100, 100)
st.markdown(f"""
    <div class="progress-bar">
        <div class="progress" style="width: {progress}%"></div>
    </div>
    <div class="score-display">
        स्कोर: {st.session_state.score} | स्ट्रीक: {st.session_state.streak} (उच्चतम: {st.session_state.max_streak})
    </div>
""", unsafe_allow_html=True)

# Determine which sequence to use
if st.session_state.usage_count < 10:
    current_sequence = flat_sutra_sequence
else:
    current_sequence = sutra_sequence

# Increment usage count and reset after 20 uses
st.session_state.usage_count += 1
if st.session_state.usage_count >= 20:
    st.session_state.usage_count = 0

# Update current and next letters
try:
    if isinstance(current_sequence[0], list):  # Original sequence
        current_letter = current_sequence[st.session_state.current_index][0]
        next_letter = current_sequence[st.session_state.current_index + 1][0]
    else:  # Flat sequence
        current_letter = current_sequence[st.session_state.current_index]
        next_letter = current_sequence[st.session_state.current_index + 1]
except IndexError:
    st.error("❌ अक्षर अनुक्रम समाप्त हो गया है।")
    st.stop()

# Generate options
def generate_options():
    if isinstance(current_sequence[0], list):  # Nested sequence
        future_letters = [
            letter for group in current_sequence[st.session_state.current_index + 1:]
            for letter in group if letter != next_letter
        ]
    else:  # Flat sequence
        future_letters = [
            letter for letter in current_sequence[st.session_state.current_index + 1:]
            if letter != next_letter
        ]

    options = [next_letter]
    while len(options) < 4 and future_letters:
        rand = random.choice(future_letters)
        if rand not in options:
            options.append(rand)

    while len(options) < 4:
        rand = random.choice(flat_sutra_sequence if not isinstance(current_sequence[0], list) 
                        else [l for group in current_sequence for l in group])
        if rand not in options:
            options.append(rand)

    random.shuffle(options)
    return options, current_letter, next_letter

# Question box
st.markdown(f"""
<div class="question-box">
    <div class="big-font">🔍 <span style='color:green;'>{current_letter}</span> के बाद के 1 अक्षर चुनें:</div>
</div>
""", unsafe_allow_html=True)

# Display cards
if not st.session_state.options:
    st.session_state.options, current_letter, next_letter = generate_options()
    st.session_state.current_letter = current_letter
    st.session_state.next_letter = next_letter
    show_letters = True
else:
    current_letter = st.session_state.get("current_letter", "")
    next_letter = st.session_state.get("next_letter", "")
    show_letters = False

if show_letters:
    with st.spinner("🧠 याद करें... 5 सेकंड में कार्ड छुप जाएंगे"):
        st_lottie(thinking_anim, speed=1, height=150, key="thinking")
        cols = st.columns(4)
        for i, col in enumerate(cols):
            with col:
                st.markdown(f"<button class='card-button'>{st.session_state.options[i]}</button>", 
                           unsafe_allow_html=True)
        time.sleep(5)
        st.rerun()
else:
    cols = st.columns(4)
    for i, col in enumerate(cols):
        with col:
            if st.button(f"कार्ड {i+1}"):
                st.session_state.selected = st.session_state.options[i]

# Handle answer selection
if st.session_state.selected:
    if st.session_state.selected == st.session_state.next_letter:
        st.session_state.streak += 1
        if st.session_state.streak > st.session_state.max_streak:
            st.session_state.max_streak = st.session_state.streak
            
        st.success("🎉 सही उत्तर!")
        play_sound("correct")
        st_lottie(celebration_anim, speed=1, height=200, key="celebrate")
        st.balloons()
        
        st.session_state.score += 1
        if st.session_state.score % 3 == 0:
            play_sound("level_up")
            rain(emoji="🏅", font_size=54, falling_speed=5, animation_length="infinite")
            st.session_state.level += 1
        
        time.sleep(2)
        # Reset for next round
        st.session_state.current_index = random.randint(0, len(sutra_sequence) - 2)
        st.session_state.options = []
        st.session_state.selected = None
        st.rerun()
    else:
        st.session_state.streak = 0
        st.error("❌ गलत उत्तर! फिर कोशिश करें।")
        play_sound("wrong")
        st.session_state.options = []
        st.session_state.selected = None
        time.sleep(2)
        st.rerun()

# Sidebar with additional info
with st.sidebar:
    st.markdown("### 📜 महेश्वर सूत्र")
    for sutra in sutra_sequence:
        st.markdown(f"**{' '.join(sutra)}**")
    
    st.markdown("---")
    st.markdown("### 🎮 गेम निर्देश")
    st.markdown("""
    1. अक्षरों को 5 सेकंड के लिए देखें
    2. कार्ड छुपने के बाद सही अक्षर चुनें
    3. 3 सही उत्तरों पर नया स्तर प्राप्त करें
    """)
    
    if st.button("🔁 गेम रीसेट करें"):
        st.session_state.current_index = random.randint(0, len(sutra_sequence) - 2)
        st.session_state.options = []
        st.session_state.selected = None
        st.session_state.score = 0
        st.session_state.level = 1
        st.session_state.streak = 0
        st.rerun()

# Footer
st.markdown("---")
st.markdown("⭐ इस ऐप को [GitHub पर स्टार करें](https://github.com/SDRMp)")