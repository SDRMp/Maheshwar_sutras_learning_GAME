import streamlit as st
import random
import time
from streamlit_extras.let_it_rain import rain

# ✅ MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="🚩 卐 सर्वेश्वररत्न 卐 🚩", 
    layout="centered", 
    initial_sidebar_state="collapsed",
    # Add mobile viewport meta tag
    meta_tags=[
        {'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0'}
    ]
)

# ========== CONSTANTS ==========
SANSKRIT_MESSAGES = {
    "welcome": "स्वागतम्! महेश्वरसूत्राणां स्मरणपरीक्षायां प्रवर्तस्व!",
    "card_info": "एमोजी-रूपेण कार्डाः आवृताः सन्ति!",
    "correct": "साधु! उत्तमम्!",
    "wrong": "क्षम्यताम्! सही उत्तरम्: {}",
    "level_up": "अभिनन्दनम्! नूतनं स्तरं प्राप्तम्!",
    "instructions": """
    १. अक्षराणि "३" सेकण्डपर्यन्त पश्यतु \n
    २. एमोजी-रूपेण गूढेषु कार्डेषु सही अक्षरं/सूत्रं चिनुतु  \n
    ३. सही उत्तरैः नूतनः स्तरः प्राप्यते \n
    """,
    "reset": "पुनः प्रारभ्यताम्!",
    "start_game": "क्रीडां प्रारभताम्!"
}

EMOJI_CARDS = ["🦊","🐱","🫎","🦇","🦉","🐥","🐢","🪼","🐙","🦑","🐡","🐠",
               "🐟","🐬","🐳","🐋","🦈","🐅","🐆","🦧","🐘","🐂","🐄","🐿️",
               "🐦‍🔥","🐚","☀️","🪁","🪂","🏹","🤹🏻‍♀️","🎮","🪈","🏎️","🏍️",
               "🚔","🚖","🚀","🛸","🚁","🚤","⛴️","🎡","🎠","🏰","🛕","🔫",
               "🔭","🔬","🙈","🙉","🙊"]

COLOR_OPTIONS = ["#d63384", "#6f42c1", "#0d6efd", "#198754", "#fd7e14", "#dc3545"]

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

flat_sutra_sequence = ["अ", "इ", "उ", "ण्", "ऋ", "ऌ", "क्", "ए", "ओ", "ङ्", 
                      "ऐ", "औ", "च्", "ह", "य", "व", "र", "ट्", "ल", "ण्", 
                      "ञ", "म", "ङ", "ण", "न", "म्", "झ", "भ", "ञ्", "घ", 
                      "ढ", "ध", "ष्", "ज", "ब", "ग", "ड", "द", "श्", "ख", 
                      "फ", "छ", "ठ", "थ", "च", "ट", "त", "व्", "क", "प", 
                      "य्", "श", "ष", "स", "र्", "ह", "ल्"]

# ========== HELPER FUNCTIONS ==========
def initialize_session_state():
    defaults = {
        'game_started': False,
        'show_settings': False,
        'score': 0,
        'level': 1,
        'streak': 0,
        'max_streak': 0,
        'question_count': 0,
        'current_letter_index': random.randint(0, len(flat_sutra_sequence)-1),
        'current_sutra_index': random.randint(0, len(sutra_sequence)-1),
        'options': [],
        'selected': None,
        'show_letters': False,
        'current_mode': "letter",
        'direction': "forward",
        'difficulty': "medium",
        'current_color': random.choice(COLOR_OPTIONS),
        'current_emojis': random.sample(EMOJI_CARDS, 4)
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def reset_game():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    initialize_session_state()
    st.rerun()

def get_next_question():
    st.session_state.current_color = random.choice(COLOR_OPTIONS)
    st.session_state.current_emojis = random.sample(EMOJI_CARDS, 4)
    
    if st.session_state.current_mode == "letter":
        current_idx = random.randint(0, len(flat_sutra_sequence)-1)
        current_letter = flat_sutra_sequence[current_idx]
        
        if st.session_state.direction == "forward":
            next_idx = current_idx + 1 if current_idx + 1 < len(flat_sutra_sequence) else 0
            correct_answer = flat_sutra_sequence[next_idx]
            question_text = f"{current_letter} इत्यस्य अनन्तरं किम् अक्षरम् आगच्छति?"
        else:
            next_idx = current_idx - 1 if current_idx > 0 else len(flat_sutra_sequence)-1
            correct_answer = flat_sutra_sequence[next_idx]
            question_text = f"{current_letter} इत्यस्य पूर्वं किम् अक्षरम् आसीत्?"
        
        return current_letter, correct_answer, question_text, "letter"
    else:
        current_idx = random.randint(0, len(sutra_sequence)-1)
        current_sutra = sutra_sequence[current_idx]
        
        if st.session_state.direction == "forward":
            next_idx = current_idx + 1 if current_idx + 1 < len(sutra_sequence) else 0
            correct_answer = sutra_sequence[next_idx]
            question_text = f"{' '.join(current_sutra)} इत्यस्य अनन्तरं किम् सूत्रम् आगच्छति?"
        else:
            next_idx = current_idx - 1 if current_idx > 0 else len(sutra_sequence)-1
            correct_answer = sutra_sequence[next_idx]
            question_text = f"{' '.join(current_sutra)} इत्यस्य पूर्वं किम् सूत्रम् आसीत्?"
        
        return current_sutra, correct_answer, question_text, "sutra"

def generate_options(correct_answer, mode):
    options = [correct_answer]
    
    if mode == "letter":
        pool = flat_sutra_sequence.copy()
    else:
        pool = sutra_sequence.copy()
        if correct_answer in pool:
            pool.remove(correct_answer)
    
    num_options = 4
    if st.session_state.difficulty == "easy":
        num_options = 3
    elif st.session_state.difficulty == "hard":
        num_options = 6
    
    while len(options) < num_options and pool:
        if mode == "letter":
            rand = random.choice(pool)
            if rand not in options:
                options.append(rand)
            pool.remove(rand)
        else:
            rand = random.choice(pool)
            if rand not in options:
                options.append(rand)
            pool.remove(rand)
    
    random.shuffle(options)
    return options

# ========== PAGE LAYOUTS ==========
def show_start_page():
    st.title("🪶 सर्वेश्वररत्न-महेश्वर सूत्र-स्मरण क्रीड़ा ⚔️ ")
    
    # Emoji animation replacement
    st.markdown("""
    <style>
    @keyframes bounce {
        0%, 100% {transform: translateY(0);}
        50% {transform: translateY(-20px);}
    }
    .om-symbol {
        text-align: center; 
        font-size: 80px; 
        animation: bounce 2s infinite;
        margin: 20px 0;
    }
    @media (max-width: 768px) {
        .om-symbol {
            font-size: 60px;
        }
    }
    </style>
    <div class='om-symbol'>
        🕉️ 
    </div>
    """, unsafe_allow_html=True)
        
    st.markdown(f"""
        <div style="text-align: center; margin: 1rem 0;">
            <h3 style="font-size: 1.2rem;">{SANSKRIT_MESSAGES['welcome']}</h3>
            <p style="font-size: 1rem; line-height: 1.5;">{SANSKRIT_MESSAGES['instructions']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button(f"🎮 {SANSKRIT_MESSAGES['start_game']}", use_container_width=True, type="primary"):
        st.session_state.game_started = True
        st.rerun()
    
    with st.expander("⚙️ सेटिङ्ग्स्", expanded=False):
        st.session_state.difficulty = st.selectbox(
            "कठिनतास्तरः",
            ["easy", "medium", "hard"],
            index=["easy", "medium", "hard"].index(st.session_state.difficulty)
        )
        st.session_state.show_settings = st.checkbox("सेटिङ्ग्स् सदैव दृश्यताम्", value=False)

def show_game_page():
    # CSS Styles with mobile optimizations
    st.markdown(f"""
        <style>
        /* Base styles */
        .big-font {{
            font-size: 24px !important;
            color: {st.session_state.current_color};
            font-weight: bold;
        }}
        .card {{
            font-size: 32px;
            padding: 1rem;
            border-radius: 10px;
            margin: 0.25rem;
            border: 2px solid #6c757d;
            background-color: #f8f9fa;
            transition: all 0.3s ease;
            min-width: 60px;
            height: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
        }}
        .card-container {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 0.5rem;
            margin: 1rem 0;
        }}
        .question-box {{
            background-color: #fff3cd;
            padding: 15px;
            border-radius: 8px;
            border: 2px solid #ffeeba;
            margin: 15px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            min-height: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
        }}
        .progress-bar {{
            height: 8px;
            background-color: #e9ecef;
            border-radius: 4px;
            margin-bottom: 15px;
        }}
        .progress {{
            height: 100%;
            background-color: #28a745;
            border-radius: 4px;
            transition: width 0.5s ease;
        }}
        .difficulty-badge {{
            display: inline-block;
            padding: 0.2em 0.4em;
            font-size: 70%;
            font-weight: 700;
            line-height: 1;
            text-align: center;
            white-space: nowrap;
            vertical-align: baseline;
            border-radius: 0.25rem;
            margin-left: 5px;
        }}
        
        /* Mobile-specific styles */
        @media (max-width: 768px) {{
            /* Adjust font sizes */
            h1 {{
                font-size: 1.5rem !important;
            }}
            h3 {{
                font-size: 1.2rem !important;
            }}
            .big-font {{
                font-size: 20px !important;
            }}
            
            /* Make cards smaller */
            .card {{
                font-size: 24px;
                padding: 0.5rem;
                min-width: 50px;
                height: 70px;
            }}
            
            /* Adjust question box */
            .question-box {{
                padding: 10px;
                min-height: 70px;
            }}
            
            /* Score display */
            .score-display {{
                font-size: 18px !important;
            }}
            
            /* Reduce margins */
            .container {{
                padding: 0.5rem !important;
            }}
        }}
        
        /* Make buttons more touch-friendly */
        .stButton>button {{
            min-height: 3rem;
            padding: 0.5rem 1rem;
        }}
        
        /* Highlight for mobile tap feedback */
        .card:active {{
            transform: scale(0.95);
            background-color: #ffc107;
        }}
        </style>
    """, unsafe_allow_html=True)

    # Header with responsive title
    st.markdown("""
    <style>
    @media (max-width: 768px) {
        .game-title {
            font-size: 1.3rem !important;
            text-align: center;
        }
    }
    </style>
    <h1 class="game-title">🧠 महेश्वर सूत्र - स्मरण क्रीड़ा ⚔️</h1>
    """, unsafe_allow_html=True)
    
    st.markdown(f"### 🌟 स्तरः {st.session_state.level} <span class='difficulty-badge' style='background-color: {'#dc3545' if st.session_state.difficulty == 'hard' else ('#fd7e14' if st.session_state.difficulty == 'medium' else '#28a745')}; color: white;'>{st.session_state.difficulty.upper()}</span>", unsafe_allow_html=True)

    # Progress bar
    progress = min((st.session_state.score % 3) / 3 * 100, 100)
    st.markdown(f"""
        <div class="progress-bar">
            <div class="progress" style="width: {progress}%"></div>
        </div>
        <div class="score-display" style="font-size: 20px; color: #28a745; font-weight: bold; margin-bottom: 15px;">
            अङ्काः: {st.session_state.score} | अनुक्रमः: {st.session_state.streak} (उच्चतमः: {st.session_state.max_streak})
        </div>
        <div style="font-size: 16px; color: #6c757d; margin-bottom: 10px; font-style: italic;">
            {SANSKRIT_MESSAGES['card_info']}
        </div>
    """, unsafe_allow_html=True)

    # Determine question mode
    st.session_state.current_mode = "letter" if st.session_state.question_count % 10 != 0 else "sutra"
    if st.session_state.question_count % 3 == 0:
        st.session_state.direction = random.choice(["forward", "reverse"])

    # Get question if none exists
    if not st.session_state.options:
        current, correct, question_text, mode = get_next_question()
        st.session_state.current_item = current
        st.session_state.correct_answer = correct
        st.session_state.question_text = question_text
        st.session_state.options = generate_options(correct, mode)
        st.session_state.show_letters = True

    # Question display with responsive sizing
    highlight_color = "#dc3545"
    question_parts = st.session_state.question_text

    if st.session_state.current_mode == "letter":
        target_letter = st.session_state.current_item
        if st.session_state.direction == "forward":
            question_parts = question_parts.replace(
                f"{target_letter} इत्यस्य", 
                f"<span style='color:{highlight_color}; font-size: 28px; font-weight:bold;'>{target_letter}</span> इत्यस्य"
            )
        else:
            question_parts = question_parts.replace(
                f"{target_letter} इत्यस्य", 
                f"<span style='color:{highlight_color}; font-size: 28px; font-weight:bold;'>{target_letter}</span> इत्यस्य"
            )
    elif st.session_state.current_mode == "sutra":
        current_sutra = st.session_state.current_item
        if isinstance(current_sutra, list):
            joined_sutra = ' '.join(current_sutra)
            question_parts = question_parts.replace(
                joined_sutra, 
                f"<span style='color:{highlight_color}; font-size: 28px; font-weight:bold;'>{joined_sutra}</span>"
            )

    st.markdown(f"""
        <div class="question-box">
            <div class="big-font">🔍 {question_parts}</div>
        </div>
    """, unsafe_allow_html=True)

    # Cards display - Flexbox layout for better mobile handling
    if st.session_state.show_letters:
        with st.spinner("🧠 स्मरतु... ३ सेकण्डेषु कार्डाः अदृश्याः भविष्यन्ति"):
            st.markdown("<div class='card-container'>", unsafe_allow_html=True)
            for option in st.session_state.options:
                display_text = ' '.join(option) if isinstance(option, list) else option
                font_size = "20px" if isinstance(option, list) else "32px"
                st.markdown(f"""
                    <div class="card" style="font-size: {font_size};">
                        {display_text}
                    </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            time.sleep(3)
            st.session_state.show_letters = False
            st.rerun()
    else:
        st.markdown("<div class='card-container'>", unsafe_allow_html=True)
        for i, option in enumerate(st.session_state.options):
            emoji = st.session_state.current_emojis[i % len(st.session_state.current_emojis)]
            st.markdown(f"""
                <div class="card">
                    {emoji}
                </div>
            """, unsafe_allow_html=True)
            # Invisible button overlay with larger tap target
            if st.button("Select", key=f"option_{i}"):
                st.session_state.selected = st.session_state.options[i]
                st.session_state.question_count += 1
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Answer handling
    if st.session_state.selected:
        if st.session_state.selected == st.session_state.correct_answer:
            st.session_state.streak += 1
            if st.session_state.streak > st.session_state.max_streak:
                st.session_state.max_streak = st.session_state.streak
            
            st.success(f"🎉 {SANSKRIT_MESSAGES['correct']}")
            st.balloons()
            
            st.session_state.score += 1
            if st.session_state.score % 3 == 0:
                rain(emoji="🏅", font_size=40, falling_speed=5, animation_length="infinite")
                st.session_state.level += 1
            
            time.sleep(2)
            st.session_state.options = []
            st.session_state.selected = None
            st.session_state.show_letters = False
            st.rerun()
        else:
            st.session_state.streak = 0
            correct_display = ' '.join(st.session_state.correct_answer) if isinstance(st.session_state.correct_answer, list) else st.session_state.correct_answer
            st.error(SANSKRIT_MESSAGES['wrong'].format(correct_display))
            st.session_state.options = []
            st.session_state.selected = None
            st.session_state.show_letters = False
            time.sleep(2)
            st.rerun()

    # Sidebar - simplified for mobile
    if st.session_state.show_settings:
        with st.sidebar:
            st.markdown("### ⚙️ सेटिङ्ग्स्")
            new_difficulty = st.selectbox(
                "कठिनतास्तरः",
                ["easy", "medium", "hard"],
                index=["easy", "medium", "hard"].index(st.session_state.difficulty)
            )
            if new_difficulty != st.session_state.difficulty:
                st.session_state.difficulty = new_difficulty
                st.session_state.options = []
                st.rerun()
            
            if st.button(f"🔁 {SANSKRIT_MESSAGES['reset']}", use_container_width=True):
                reset_game()

# ========== MAIN APP FLOW ==========
initialize_session_state()

if not st.session_state.game_started:
    show_start_page()
else:
    show_game_page()


     
st.markdown("---")
st.markdown("⭐ अस्य अनुप्रयोगस्य [GitHub](https://github.com/SDRMp/Maheshwar_sutras_learning_GAME) स्थाने तारां ददातु")
# Footer
st.markdown("---") 
st.markdown("⭐ इस game को [GitHub पर स्टार करें](https://github.com/SDRMp/Maheshwar_sutras_learning_GAME)")
