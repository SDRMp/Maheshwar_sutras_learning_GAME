import streamlit as st
import time
from animations import animate_damaru, animate_sanskrit_text

# Page config
st.set_page_config(page_title="Māheśvara Sūtras", layout="wide")

# CSS for Sanskrit fonts
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sanskrit+Text&display=swap');
.sanskrit {
    font-family: 'Sanskrit Text', serif;
    font-size: 24px;
}
</style>
""", unsafe_allow_html=True)

# Header
st.title("Māheśvara Sūtras Learning Tool")
st.subheader("The Cosmic Sounds of Sanskrit")

# 1. Introduction Section
with st.expander("Introduction", expanded=True):
    st.markdown("""
    <div class="sanskrit">अइउण् ऋऌक् एओङ् ऐऔच्</div>
    """, unsafe_allow_html=True)
    
    animate_damaru()  # Animation of Shiva's drum
    
    cols = st.columns(2)
    with cols[0]:
        st.write("**Origin**: From Lord Shiva's cosmic dance (Tandava)")
        st.write("**Structure**: 14 sūtras (4 vowel + 10 consonant)")
    with cols[1]:
        st.image("shiva_tandava.jpg", caption="Shiva's Tandava")

# 2. Interactive Sūtra Explorer
selected_sutra = st.selectbox("Select a Sūtra:", [
    "अइउण् - Vowels 1", "ऋऌक् - Vowels 2", 
    "हयवरट् - Consonants 1", "शषसर् - Guṇas"
])

if selected_sutra.startswith("अइउण्"):
    animate_sanskrit_text("अइउण्", color="gold")
    st.write("""
    **Vowels**: अ, इ, उ
    **Philosophy**:
    - अ = Formless Brahman
    - इ = Pure consciousness
    - उ = Creative manifestation
    """)

# 3. Element Visualization
if st.checkbox("Show Element Mapping"):
    elements = {
        "ह": "Ākāśa (Space)", "य": "Vāyu (Air)", 
        "व": "Jala (Water)", "र": "Agni (Fire)", "ट": "Pṛthvī (Earth)"
    }
    
    for char, meaning in elements.items():
        col1, col2 = st.columns([1,4])
        with col1:
            st.markdown(f'<div class="sanskrit" style="font-size:48px">{char}</div>', 
                       unsafe_allow_html=True)
        with col2:
            st.progress(70)
            st.write(f"**{meaning}**")
            time.sleep(0.3)  # Animation effect

# 4. Quiz Section
if st.button("Take a Quick Quiz"):
    quiz_question = st.radio(
        "What does 'हयवरट्' represent?",
        ["Five senses", "Five elements", "Three guṇas"]
    )
    if quiz_question == "Five elements":
        st.success("Correct! हयवरट् = Ākāśa, Vāyu, Jala, Agni, Pṛthvī")
    else:
        st.error("Try again!")
