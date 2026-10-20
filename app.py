import streamlit as st
import random
import time
import json
import csv
import io
import os
import uuid
import html
import unicodedata
from collections import Counter
from datetime import datetime, timezone

# ✅ MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(page_title="🚩 卐 सर्वेश्वररत्न 卐 🚩", layout="centered",
                   initial_sidebar_state="collapsed")

# ============================================================
# CONFIG
# ============================================================
BANK_PATH = "ashtadhyayi_question_bank.json"
LOG_DIR = "logs"
LOG_PATH = os.path.join(LOG_DIR, "rl_log.jsonl")

POLICY_NAME = "thompson_target_difficulty"
POLICY_VERSION = "1.1"
TARGET_SUCCESS = 0.7        # aim for questions answered correctly ~70% of the time
MASTERY_MIN_ATTEMPTS = 3
MASTERY_THRESHOLD = 0.6     # posterior mean needed to unlock the next unit
MOVE_ON_ATTEMPTS = 8        # unlock the next unit anyway after this many tries
PROPENSITY_SAMPLES = 500    # Monte Carlo samples to estimate P(action | state)
MEMORIZE_SECONDS = 3
SPEED_SECONDS = 60

MODES = {
    "adaptive": "🧠 अनुकूली / Adaptive (AI chooses questions)",
    "practice": "🎯 अभ्यासः / Practice one unit",
    "speed":    "⚡ त्वरा-क्रीडा / Speed round (60 s)",
}
DIFFICULTIES = ["easy", "medium", "hard"]

# ============================================================
# TEXT
# ============================================================
MSG = {
    "title": "🪶 सर्वेश्वररत्न-महेश्वरसूत्र-स्मरणक्रीडा ⚔️",
    "welcome": "स्वागतम्! महेश्वरसूत्राणां पाणिनीयव्याकरणस्य च अभ्यासे प्रवर्तस्व!",
    "instructions": (
        "१. स्मरणप्रश्नेषु अक्षराणि ३ सेकण्डपर्यन्तं पश्यतु।<br>"
        "२. एमोजी-रूपेण गूढेषु कार्डेषु समीचीनम् अक्षरं/सूत्रं चिनोतु।<br>"
        "३. व्याकरणप्रश्नेषु समीचीनम् उत्तरं चिनोतु वा लिखतु।<br>"
        "४. प्रत्येकं विभागं साधयित्वा नूतनः स्तरः प्राप्यते।"
    ),
    "card_info": "एमोजी-रूपेण कार्डाः आवृताः सन्ति!",
    "memorize": "🧠 स्मरतु... ३ सेकण्डेषु कार्डाः गूढाः भविष्यन्ति",
    "correct": "साधु! उत्तमम्!",
    "wrong": "क्षम्यताम्! समीचीनम् उत्तरम्: {}",
    "level_up": "अभिनन्दनम्! नूतनः स्तरः प्राप्तः!",
    "start": "🎮 क्रीडां प्रारभताम्!",
    "reset": "🔁 पुनः प्रारभ्यताम्!",
    "next": "अग्रिमः प्रश्नः ➡️",
    "submit": "उत्तरं ददातु ✅",
    "tap_hint": "सर्वाणि समीचीनानि चिनोतु",
    "arrange_hint": "क्रमेण चिनोतु (प्रथमं प्रथमम्)",
    "fill_hint": "उत्तरं लिखतु",
    "consent": "I agree that my anonymous answers are recorded for research "
               "(अनुसन्धानाय मम उत्तराणि अनामतया अभिलिख्यन्ताम्)",
}

EMOJI_CARDS = ["🦊","🐱","🫎","🦇","🦉","🐥","🐢","🪼","🐙","🦑","🐡","🐠",
               "🐟","🐬","🐳","🐋","🦈","🐅","🐆","🦧","🐘","🐂","🐄","🐿️",
               "🐦‍🔥","🐚","☀️","🪁","🪂","🏹","🤹🏻‍♀️","🎮","🪈","🏎️","🏍️",
               "🚔","🚖","🚀","🛸","🚁","🚤","⛴️","🎡","🎠","🏰","🛕",
               "🔭","🔬","🙈","🙉","🙊"]
COLOR_OPTIONS = ["#d63384", "#6f42c1", "#0d6efd", "#198754", "#fd7e14", "#dc3545"]

# ============================================================
# MAHEŚVARA SŪTRAS
# ============================================================
SUTRAS = [
    ["अ", "इ", "उ", "ण्"], ["ऋ", "ऌ", "क्"], ["ए", "ओ", "ङ्"], ["ऐ", "औ", "च्"],
    ["ह", "य", "व", "र", "ट्"], ["ल", "ण्"], ["ञ", "म", "ङ", "ण", "न", "म्"],
    ["झ", "भ", "ञ्"], ["घ", "ढ", "ध", "ष्"], ["ज", "ब", "ग", "ड", "द", "श्"],
    ["ख", "फ", "छ", "ठ", "थ", "च", "ट", "त", "व्"], ["क", "प", "य्"],
    ["श", "ष", "स", "र्"], ["ह", "ल्"],
]
FLAT = [(letter, si) for si, sutra in enumerate(SUTRAS) for letter in sutra]
LETTER_COUNT = Counter(letter for letter, _ in FLAT)
UNIQUE_LETTERS = list(dict.fromkeys(letter for letter, _ in FLAT))
SUTRA_TEXT = [" ".join(s) for s in SUTRAS]

# Distractors for "tap" questions (the bank only lists correct answers).
# You can instead add a "distractors" list to any tap question in the JSON.
TAP_DISTRACTORS = {
    "VAR-007": ["श", "ष", "ह", "म", "ज"],
    "VAR-008": ["य", "व", "क", "ज", "न"],
    "PRA-002": ["अ", "आ", "ए", "ओ", "औ"],
    "PRA-003": ["ह", "म", "न", "श", "ज"],
    "KAR-007": ["सम्बन्ध", "सम्बोधन", "विशेषण", "अव्यय"],
}

ARM_LABELS = {
    "mahesvara_letter": "महेश्वरसूत्राणि – वर्णाः", "mahesvara_sutra": "महेश्वरसूत्राणि – सूत्राणि",
    "varnamala": "वर्णमाला", "pratyahara": "प्रत्याहाराः", "it_samjna": "इत्संज्ञा",
    "prakriti_pratyaya": "प्रकृतिः प्रत्ययश्च", "sandhi_ach": "अच्सन्धिः", "sandhi_hal": "हल्सन्धिः",
    "sandhi_visarga": "विसर्गसन्धिः", "asiddha": "असिद्धत्वम्", "karaka": "कारकाणि",
    "abhihita": "अभिहितानभिहितम्", "subartha_non_karaka": "विभक्त्यर्थाः", "subanta": "सुबन्ताः",
    "tinganta": "तिङन्ताः", "avyaya_upasarga": "अव्ययोपसर्गाः",
    "visheshana_visheshya": "विशेषणविशेष्यौ", "kridanta": "कृदन्ताः",
    "stree_pratyaya": "स्त्रीप्रत्ययाः", "taddhita": "तद्धिताः", "samasa_bonus": "समासाः",
    "sutra_memory": "सूत्रस्मरणम्",
}

# ============================================================
# QUESTION BANK
# ============================================================
@st.cache_data
def load_bank(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

if not os.path.exists(BANK_PATH):
    st.error(f"Question bank not found: {BANK_PATH}")
    st.stop()

BANK = load_bank(BANK_PATH)
BANK_BY_UNIT = {}
for _q in BANK["questions"]:
    BANK_BY_UNIT.setdefault(_q["unit"], []).append(_q)

# Bandit arms, in teaching (unlock) order
ARMS = ["mahesvara_letter", "mahesvara_sutra"] + [u for u in BANK["units"] if u in BANK_BY_UNIT]

def label(arm):
    return ARM_LABELS.get(arm, arm)

# ============================================================
# HELPERS
# ============================================================
def to_text(x):
    if isinstance(x, list):
        return ", ".join(str(i) for i in x)
    if isinstance(x, dict):
        return "; ".join(f"{k} → {v}" for k, v in x.items())
    return str(x)

def norm(s):
    """Normalize typed Devanagari answers: Unicode NFC, no dandas, no spaces."""
    s = unicodedata.normalize("NFC", str(s or ""))
    s = s.replace("।", "").replace("॥", "")
    return "".join(s.split())

def num_options():
    return {"easy": 3, "medium": 4, "hard": 6}[st.session_state.difficulty]

# ============================================================
# SESSION STATE
# ============================================================
def init_state():
    defaults = {
        "stage": "start", "player_id": "", "consent": False,
        "session_id": str(uuid.uuid4()), "step": 0,
        "score": 0, "level": 1, "streak": 0, "max_streak": 0,
        "difficulty": "medium",
        "mode": "adaptive", "practice_unit": "mahesvara_letter",
        "round_end": None, "round_start_step": 0, "flash": None,
        "bandit": {arm: [1, 1] for arm in ARMS},   # Beta(alpha, beta) per arm
        "recent_ids": [], "recent_results": [],
        "q": None, "phase": None, "result": None, "question_start": None,
        "color": random.choice(COLOR_OPTIONS), "emojis": random.sample(EMOJI_CARDS, 6),
        "session_log": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def reset_game():
    keep = {k: st.session_state.get(k)
            for k in ("player_id", "consent", "difficulty", "mode", "practice_unit")}
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    init_state()
    for k, v in keep.items():
        st.session_state[k] = v
    st.rerun()

# ============================================================
# BANDIT POLICY
# ============================================================
def attempts(arm):
    a, b = st.session_state.bandit[arm]
    return a + b - 2

def posterior_mean(arm):
    a, b = st.session_state.bandit[arm]
    return a / (a + b)

def opens_next(arm):
    n = attempts(arm)
    mastered = n >= MASTERY_MIN_ATTEMPTS and posterior_mean(arm) >= MASTERY_THRESHOLD
    return mastered or n >= MOVE_ON_ATTEMPTS

def unlocked_arms():
    out = []
    for arm in ARMS:
        out.append(arm)
        if not opens_next(arm):
            break
    return out

def thompson_pick(bandit, arms):
    samples = {a: random.betavariate(*bandit[a]) for a in arms}
    return min(samples, key=lambda a: abs(samples[a] - TARGET_SUCCESS))

def choose_arm():
    ss = st.session_state
    arms = unlocked_arms()
    if ss.mode == "practice":
        return ss.practice_unit, 1.0, arms          # learner's choice, not the policy's
    chosen = thompson_pick(ss.bandit, arms)
    hits = sum(thompson_pick(ss.bandit, arms) == chosen for _ in range(PROPENSITY_SAMPLES))
    return chosen, max(hits, 1) / PROPENSITY_SAMPLES, arms

def snapshot_state(arms):
    ss = st.session_state
    recent = ss.recent_results[-5:]
    return {
        "posterior": {a: list(v) for a, v in ss.bandit.items()},
        "unlocked": arms,
        "streak": ss.streak,
        "level": ss.level,
        "recent_accuracy": round(sum(recent) / len(recent), 3) if recent else None,
        "step": ss.step,
    }

# ============================================================
# QUESTION BUILDERS
# ============================================================
def make_letter_question():
    direction = random.choice(["forward", "reverse"])
    if direction == "forward":
        idx = random.randint(0, len(FLAT) - 2)
        target, ti = FLAT[idx + 1]
        word = "अनन्तरं"
    else:
        idx = random.randint(1, len(FLAT) - 1)
        target, ti = FLAT[idx - 1]
        word = "पूर्वं"
    letter, si = FLAT[idx]
    # ह and ण् occur twice: show their sūtra so the question has one answer
    shown = f"{letter} ({SUTRA_TEXT[si].replace(' ', '')})" if LETTER_COUNT[letter] > 1 else letter
    options = random.sample([l for l in UNIQUE_LETTERS if l != target], num_options() - 1) + [target]
    random.shuffle(options)
    context = " | ".join(dict.fromkeys([SUTRA_TEXT[si], SUTRA_TEXT[ti]]))
    return dict(qid=f"MSL-{idx}-{direction}", qtype="memory_mc",
                prompt=f"{shown} इत्यस्य {word} किम् अक्षरम्?", highlight=shown,
                answer=target, options=options, explanation=f"सन्दर्भः: {context}",
                sutra_ref="", direction=direction)

def make_sutra_question():
    direction = random.choice(["forward", "reverse"])
    if direction == "forward":
        idx = random.randint(0, len(SUTRAS) - 2)
        ti, word = idx + 1, "अनन्तरं"
    else:
        idx = random.randint(1, len(SUTRAS) - 1)
        ti, word = idx - 1, "पूर्वं"
    current, target = SUTRA_TEXT[idx], SUTRA_TEXT[ti]
    others = [s for s in SUTRA_TEXT if s not in (current, target)]
    options = random.sample(others, num_options() - 1) + [target]
    random.shuffle(options)
    return dict(qid=f"MSS-{idx}-{direction}", qtype="memory_mc",
                prompt=f"{current} इत्यस्य {word} किं सूत्रम्?", highlight=current,
                answer=target, options=options, explanation="",
                sutra_ref="", direction=direction)

def make_bank_question(unit):
    ss = st.session_state
    pool = [q for q in BANK_BY_UNIT[unit] if q["id"] not in ss.recent_ids] or BANK_BY_UNIT[unit]
    q = random.choice(pool)
    ss.recent_ids = (ss.recent_ids + [q["id"]])[-20:]
    base = dict(qid=q["id"], prompt=q["prompt"], highlight=None,
                explanation=q.get("explanation", ""), sutra_ref=q.get("sutra", ""),
                direction=None)
    t = q["type"]
    if t == "multiple_choice":
        answer = to_text(q["answer"])
        distractors = [to_text(o) for o in q["options"] if to_text(o) != answer]
        if ss.difficulty == "easy":
            distractors = random.sample(distractors, min(2, len(distractors)))
        options = distractors + [answer]
        random.shuffle(options)
        base.update(qtype="mc", answer=answer, options=options)
    elif t == "tap":
        answer = list(q["answer"])
        extra = (q.get("distractors") or TAP_DISTRACTORS.get(q["id"])
                 or random.sample([l for l in UNIQUE_LETTERS if l not in answer], 4))
        options = answer + [e for e in extra if e not in answer]
        random.shuffle(options)
        base.update(qtype="tap", answer=answer, options=options)
    elif t == "arrange":
        answer = list(q["answer"])
        options = answer[:]
        while options == answer and len(options) > 1:
            random.shuffle(options)
        base.update(qtype="arrange", answer=answer, options=options)
    elif t == "match":
        answer = dict(q["answer"])
        choices = list(answer.values())
        random.shuffle(choices)
        base.update(qtype="match", answer=answer, options=choices)
    else:  # fill_blank
        base.update(qtype="fill", answer=q["answer"], options=[])
    return base

def next_question():
    ss = st.session_state
    arm, propensity, arms = choose_arm()
    state_before = snapshot_state(arms)
    if arm == "mahesvara_letter":
        q = make_letter_question()
    elif arm == "mahesvara_sutra":
        q = make_sutra_question()
    else:
        q = make_bank_question(arm)
    q.update(arm=arm, propensity=propensity, state_before=state_before)
    if ss.mode == "speed" and q["qtype"] == "memory_mc":
        q["qtype"] = "mc"        # no 3-second memorize phase in a speed round
    ss.q = q
    ss.step += 1
    ss.result = None
    ss.color = random.choice(COLOR_OPTIONS)
    ss.emojis = random.sample(EMOJI_CARDS, 6)
    if q["qtype"] == "memory_mc":
        ss.phase = "memorize"
        ss.question_start = None
    else:
        ss.phase = "answer"
        ss.question_start = time.time()

# ============================================================
# CHECKING & LOGGING
# ============================================================
def check(q, response):
    t = q["qtype"]
    if t in ("mc", "memory_mc"):
        return response == q["answer"]
    if t == "tap":
        return set(response or []) == set(q["answer"])
    if t == "arrange":
        return list(response or []) == q["answer"]
    if t == "match":
        return response == q["answer"]
    return norm(response) == norm(q["answer"])  # fill

def write_log(record):
    # On Streamlit Cloud this folder is wiped on restart: swap for a database insert in production.
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def submit(response):
    ss = st.session_state
    q = ss.q
    correct = check(q, response)
    rt = round(time.time() - ss.question_start, 2) if ss.question_start else None
    arm = q["arm"]

    # Bandit update (the policy's learning step)
    ss.bandit[arm][0 if correct else 1] += 1
    ss.recent_results.append(int(correct))

    if correct:
        ss.score += 1
        ss.streak += 1
        ss.max_streak = max(ss.max_streak, ss.streak)
    else:
        ss.streak = 0

    # Level = number of units unlocked through mastery
    new_level = len(unlocked_arms())
    level_up = new_level > ss.level
    ss.level = new_level

    record = {
        "schema_version": 2,
        "session_id": ss.session_id,
        "player_id": ss.player_id or "anon",
        "step": ss.step,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "mode": ss.mode,
        "policy": POLICY_NAME if ss.mode != "practice" else "user_choice",
        "policy_version": POLICY_VERSION,
        "target_success": TARGET_SUCCESS,
        "difficulty": ss.difficulty,
        "state": q["state_before"],                       # s
        "action": {                                        # a
            "arm": arm, "question_id": q["qid"], "question_type": q["qtype"],
            "propensity": q["propensity"],                 # π(a|s)
            "n_unlocked": len(q["state_before"]["unlocked"]),
        },
        "reward": int(correct),                            # r
        "next_state": {                                    # s'
            "posterior": {a: list(v) for a, v in ss.bandit.items()},
            "unlocked": unlocked_arms(),
            "streak": ss.streak,
        },
        "response_time_sec": rt,
        "response": response,
        "correct_answer": q["answer"],
        "direction": q.get("direction"),
        "level_up": level_up,
    }
    ss.session_log.append(record)
    if ss.consent:
        write_log(record)

    if ss.mode == "speed":
        ss.flash = (correct, "✅" if correct else f"❌ {to_text(q['answer'])}")
        next_question()
        st.rerun()

    ss.result = {"correct": correct, "level_up": level_up, "celebrated": False}
    ss.phase = "feedback"
    st.rerun()

CSV_FIELDS = ["session_id", "player_id", "step", "timestamp", "mode", "policy", "difficulty",
              "arm", "question_id", "question_type", "propensity", "n_unlocked",
              "arm_alpha_before", "arm_beta_before", "recent_accuracy", "streak_before",
              "reward", "response_time_sec", "response", "correct_answer", "direction"]

def flatten(r):
    arm = r["action"]["arm"]
    a, b = r["state"]["posterior"][arm]
    return {
        "session_id": r["session_id"], "player_id": r["player_id"], "step": r["step"],
        "timestamp": r["timestamp"], "mode": r.get("mode"), "policy": r["policy"],
        "difficulty": r["difficulty"], "arm": arm,
        "question_id": r["action"]["question_id"],
        "question_type": r["action"]["question_type"],
        "propensity": r["action"]["propensity"], "n_unlocked": r["action"]["n_unlocked"],
        "arm_alpha_before": a, "arm_beta_before": b,
        "recent_accuracy": r["state"]["recent_accuracy"],
        "streak_before": r["state"]["streak"], "reward": r["reward"],
        "response_time_sec": r["response_time_sec"],
        "response": to_text(r["response"]), "correct_answer": to_text(r["correct_answer"]),
        "direction": r["direction"],
    }

def to_csv_bytes(records):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=CSV_FIELDS)
    writer.writeheader()
    writer.writerows(flatten(r) for r in records)
    return buf.getvalue().encode("utf-8-sig")   # utf-8-sig: Devanagari opens correctly in Excel

def to_jsonl_bytes(records):
    return "\n".join(json.dumps(r, ensure_ascii=False) for r in records).encode("utf-8")

def get_admin_key():
    try:
        return st.secrets.get("ADMIN_KEY")
    except Exception:
        return None

# ============================================================
# UI
# ============================================================
def inject_css(color):
    st.markdown(f"""
<style>
.big-font {{ font-size: 30px; color: {color}; font-weight: bold; }}
.card {{ font-size: 48px; padding: 1rem; border-radius: 15px; margin: 0.4rem 0;
  border: 3px solid #6c757d; background-color: #f8f9fa; color: #212529; min-height: 110px;
  display: flex; align-items: center; justify-content: center; text-align: center; }}
.question-box {{ background-color: #fff3cd; color: #212529; padding: 20px; border-radius: 10px;
  border: 2px solid #ffeeba; margin: 20px 0; box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  display: flex; align-items: center; justify-content: center; text-align: center; }}
.progress-bar {{ height: 10px; background-color: #e9ecef; border-radius: 5px; margin-bottom: 12px; }}
.progress {{ height: 100%; background-color: #28a745; border-radius: 5px; }}
.badge {{ display: inline-block; padding: 0.25em 0.5em; font-size: 70%; font-weight: 700;
  border-radius: 0.25rem; color: white; margin-left: 6px; }}
@media (max-width: 768px) {{
  .card {{ font-size: 36px; min-height: 90px; }}
  .big-font {{ font-size: 24px; }}
}}
</style>""", unsafe_allow_html=True)

def render_header():
    ss = st.session_state
    badge = {"easy": "#28a745", "medium": "#fd7e14", "hard": "#dc3545"}[ss.difficulty]
    st.markdown(f"### 🌟 स्तरः {ss.level} / {len(ARMS)} <span class='badge' "
                f"style='background:{badge}'>{ss.difficulty.upper()}</span>",
                unsafe_allow_html=True)
    st.caption(MODES[ss.mode])

    unlocked = unlocked_arms()
    frontier = unlocked[-1]
    progress = 100 * min(attempts(frontier) / MASTERY_MIN_ATTEMPTS, 1) * \
               min(posterior_mean(frontier) / MASTERY_THRESHOLD, 1)
    st.markdown(
        f"<div class='progress-bar'><div class='progress' style='width:{progress:.0f}%'></div></div>"
        f"<div style='font-size:20px; color:#28a745; font-weight:bold; margin-bottom:8px;'>"
        f"अङ्काः: {ss.score} | अनुक्रमः: {ss.streak} (उच्चतमः: {ss.max_streak})</div>",
        unsafe_allow_html=True)
    if len(unlocked) < len(ARMS):
        st.caption(f"🔓 अग्रिमः विभागः: {label(ARMS[len(unlocked)])}")

def render_question_box(q):
    text = html.escape(q["prompt"])
    if q.get("highlight"):
        h = html.escape(q["highlight"])
        text = text.replace(h, f"<span style='color:#dc3545; font-size:1.2em;'>{h}</span>", 1)
    st.markdown(f"<div class='question-box'><div class='big-font'>🔍 {text}</div></div>",
                unsafe_allow_html=True)

def render_memorize(q):
    cols = st.columns(len(q["options"]))
    with st.spinner(MSG["memorize"]):
        for col, opt in zip(cols, q["options"]):
            size = "24px" if len(opt) > 3 else "48px"
            col.markdown(f"<div class='card' style='font-size:{size}'>{html.escape(opt)}</div>",
                         unsafe_allow_html=True)
        time.sleep(MEMORIZE_SECONDS)
    st.session_state.phase = "answer"
    st.session_state.question_start = time.time()
    st.rerun()

def render_answer(q):
    ss = st.session_state
    step = ss.step
    t = q["qtype"]
    if t == "memory_mc":
        st.caption(MSG["card_info"])
        cols = st.columns(len(q["options"]))
        for i, (col, opt) in enumerate(zip(cols, q["options"])):
            with col:
                st.markdown(f"<div class='card'>{ss.emojis[i % len(ss.emojis)]}</div>",
                            unsafe_allow_html=True)
                if st.button("✋", key=f"pick_{step}_{i}", use_container_width=True):
                    submit(opt)
    elif t == "mc":
        for i, opt in enumerate(q["options"]):
            if st.button(opt, key=f"mc_{step}_{i}", use_container_width=True):
                submit(opt)
    elif t == "tap":
        sel = st.pills(MSG["tap_hint"], q["options"], selection_mode="multi", key=f"tap_{step}")
        if st.button(MSG["submit"], key=f"sub_{step}", type="primary"):
            submit(list(sel or []))
    elif t == "arrange":
        sel = st.multiselect(MSG["arrange_hint"], q["options"], key=f"arr_{step}")
        if st.button(MSG["submit"], key=f"sub_{step}", type="primary"):
            submit(list(sel))
    elif t == "match":
        response = {}
        for k in q["answer"]:
            response[k] = st.selectbox(k, ["—"] + q["options"], key=f"match_{step}_{k}")
        if st.button(MSG["submit"], key=f"sub_{step}", type="primary"):
            submit(response)
    else:  # fill
        text = st.text_input(MSG["fill_hint"], key=f"fill_{step}")
        if st.button(MSG["submit"], key=f"sub_{step}", type="primary"):
            submit(text)

def render_feedback(q):
    ss = st.session_state
    res = ss.result
    if res["correct"]:
        st.success(f"🎉 {MSG['correct']}")
    else:
        st.error(MSG["wrong"].format(to_text(q["answer"])))
    note = q.get("explanation", "")
    if q.get("sutra_ref"):
        note += f"  \n📜 सूत्रम्: {q['sutra_ref']}"
    if note:
        st.info(note)
    if res["level_up"] and not res["celebrated"]:
        st.balloons()
        st.success(f"🏅 {MSG['level_up']} 🔓 {label(ARMS[ss.level - 1])}")
        res["celebrated"] = True
    if st.button(MSG["next"], type="primary", use_container_width=True):
        next_question()
        st.rerun()

def show_speed_results():
    ss = st.session_state
    rnd = [r for r in ss.session_log if r["step"] > ss.round_start_step]
    right = sum(r["reward"] for r in rnd)
    st.header("⚡ समयः समाप्तः!")
    c1, c2, c3 = st.columns(3)
    c1.metric("उत्तराणि / Answered", len(rnd))
    c2.metric("समीचीनानि / Correct", right)
    c3.metric("सटीकता / Accuracy", f"{100 * right / len(rnd):.0f}%" if rnd else "–")
    if st.button("⚡ पुनः / Play again", type="primary", use_container_width=True):
        ss.round_end = time.time() + SPEED_SECONDS
        ss.round_start_step = ss.step
        next_question()
        st.rerun()

def render_sidebar():
    ss = st.session_state
    with st.sidebar:
        st.markdown("### ⚙️ सेटिङ्ग्स्")
        ss.difficulty = st.selectbox("कठिनतास्तरः", DIFFICULTIES,
                                     index=DIFFICULTIES.index(ss.difficulty),
                                     help="Applies from the next question.")

        st.markdown("### 📈 प्रगतिः")
        for arm in unlocked_arms():
            st.progress(posterior_mean(arm), text=f"{label(arm)} ({attempts(arm)})")

        st.markdown("### 📜 महेश्वरसूत्राणि")
        for s in SUTRA_TEXT:
            st.markdown(f"**{s}**")

        if ss.session_log:
            st.markdown("### 📥 मम परिणामाः")
            name = f"{ss.player_id or 'anon'}_{ss.session_id[:8]}"
            st.download_button("CSV", to_csv_bytes(ss.session_log),
                               file_name=f"{name}.csv", mime="text/csv")
            st.download_button("JSONL (RL)", to_jsonl_bytes(ss.session_log),
                               file_name=f"{name}.jsonl", mime="application/json")

        admin_key = get_admin_key()
        if admin_key:
            with st.expander("🔬 Researcher"):
                k = st.text_input("Key", type="password", key="admin_input")
                if k == admin_key and os.path.exists(LOG_PATH):
                    with open(LOG_PATH, "rb") as f:
                        st.download_button("All logs (JSONL)", f.read(),
                                           file_name="rl_log_all.jsonl")

        if st.button(MSG["reset"]):
            reset_game()

def show_start_page():
    ss = st.session_state
    st.title(MSG["title"])
    st.markdown("""
<div style='text-align:center; font-size:100px; animation: bounce 2s infinite;'>🕉️</div>
<style>@keyframes bounce {0%,100% {transform: translateY(0);} 50% {transform: translateY(-20px);}}</style>
""", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center; margin:1.5rem 0;'><h3>{MSG['welcome']}</h3>"
                f"<p style='font-size:1.1rem;'>{MSG['instructions']}</p></div>",
                unsafe_allow_html=True)

    pid = st.text_input("Player ID (optional, e.g. P01)", value=ss.player_id)
    consent = st.checkbox(MSG["consent"], value=ss.consent)
    diff = st.selectbox("कठिनतास्तरः", DIFFICULTIES, index=DIFFICULTIES.index(ss.difficulty))
    mode = st.radio("क्रीडाप्रकारः / Mode", list(MODES), format_func=MODES.get,
                    index=list(MODES).index(ss.mode))
    unit = ss.practice_unit
    if mode == "practice":
        unit = st.selectbox("विभागः / Unit", ARMS, format_func=label,
                            index=ARMS.index(ss.practice_unit))

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(MSG["start"], use_container_width=True, type="primary"):
            ss.player_id = pid.strip()
            ss.consent = consent
            ss.difficulty = diff
            ss.mode = mode
            ss.practice_unit = unit
            if mode == "speed":
                ss.round_end = time.time() + SPEED_SECONDS
                ss.round_start_step = ss.step
            ss.stage = "game"
            next_question()
            st.rerun()

def show_game_page():
    ss = st.session_state
    if ss.q is None:
        next_question()
    render_sidebar()            # drawn first so it stays usable during the 3-second wait
    inject_css(ss.color)
    st.title(MSG["title"])
    render_header()

    if ss.mode == "speed":
        remaining = int(ss.round_end - time.time())
        if remaining <= 0:
            show_speed_results()
            return
        st.caption(f"⏱️ {remaining} s")
        if ss.flash:
            (st.success if ss.flash[0] else st.error)(ss.flash[1])
            ss.flash = None

    q = ss.q
    st.caption(f"📚 {label(q['arm'])}")
    render_question_box(q)
    if ss.phase == "memorize":
        render_memorize(q)
    elif ss.phase == "answer":
        render_answer(q)
    else:
        render_feedback(q)

# ============================================================
# MAIN
# ============================================================
init_state()
if st.session_state.stage == "start":
    show_start_page()
else:
    show_game_page()

st.markdown("---")
st.markdown("⭐ Made By Mishr_priya")
