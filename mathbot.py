"""Dhruv's MathBot: a mental math simulator for trading and quant interviews.

Questions are read aloud (and optionally shown on screen), you type the answer,
and your score goes up by one for a correct answer and down by one for a wrong one.
"""

import io
import random

import streamlit as st
from gtts import gTTS

st.set_page_config(
    page_title="Dhruv's MathBot",
    page_icon="🧮",
    layout="centered",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------- #
# Styling
# --------------------------------------------------------------------------- #
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

:root {
  --bg: #0b0d17;
  --panel: rgba(255,255,255,0.04);
  --panel-border: rgba(255,255,255,0.09);
  --text: #e8eaf6;
  --muted: #8b90b0;
  --accent: #7c5cff;
  --accent-2: #22d3ee;
  --good: #34d399;
  --bad: #f87171;
}

html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif; }

.stApp {
  background:
    radial-gradient(900px 500px at 10% -10%, rgba(124,92,255,0.22), transparent 60%),
    radial-gradient(700px 500px at 110% 10%, rgba(34,211,238,0.14), transparent 60%),
    var(--bg);
  color: var(--text);
}

#MainMenu, footer, header [data-testid="stToolbar"] { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
[data-testid="InputInstructions"] { display: none; }
.block-container { padding-top: 2.5rem; max-width: 760px; }

/* Hero */
.hero { text-align: center; margin-bottom: 1.8rem; }
.hero .badge {
  display: inline-block; padding: 4px 12px; border-radius: 999px;
  font-size: 0.75rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase;
  color: var(--accent-2); background: rgba(34,211,238,0.08);
  border: 1px solid rgba(34,211,238,0.25);
}
.hero h1 {
  font-size: clamp(2.2rem, 6vw, 3.4rem); font-weight: 800; letter-spacing: -0.03em;
  margin: 0.6rem 0 0.4rem; padding: 0; line-height: 1.05;
  background: linear-gradient(120deg, #ffffff 0%, #c4b5fd 45%, #67e8f9 100%);
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
.hero p { color: var(--muted); font-size: 1.02rem; max-width: 540px; margin: 0 auto; }

/* Stat cards */
.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 18px; }
.stat {
  background: var(--panel); border: 1px solid var(--panel-border); border-radius: 16px;
  padding: 14px 12px; text-align: center; backdrop-filter: blur(8px);
}
.stat .label { color: var(--muted); font-size: 0.72rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.08em; }
.stat .value { font-family: 'JetBrains Mono', monospace; font-size: 1.7rem; font-weight: 700;
  margin-top: 2px; color: var(--text); }
.stat .value.pos { color: var(--good); }
.stat .value.neg { color: var(--bad); }
@media (max-width: 560px) { .stats { grid-template-columns: repeat(2, 1fr); } }

/* Question card */
.qcard {
  position: relative; overflow: hidden;
  background: linear-gradient(160deg, rgba(124,92,255,0.14), rgba(34,211,238,0.06));
  border: 1px solid rgba(124,92,255,0.35); border-radius: 22px;
  padding: 28px 24px 22px; text-align: center; margin-bottom: 14px;
  box-shadow: 0 20px 60px -20px rgba(124,92,255,0.45);
}
.qcard .qnum { color: var(--muted); font-size: 0.8rem; font-weight: 600;
  letter-spacing: 0.1em; text-transform: uppercase; }
.qcard .expr {
  font-family: 'JetBrains Mono', monospace; font-weight: 700;
  font-size: clamp(2.2rem, 9vw, 3.6rem); letter-spacing: -0.02em;
  color: #fff; margin: 8px 0 2px; line-height: 1.15; word-break: break-word;
}
.qcard .hidden-expr { font-size: clamp(1.4rem, 5vw, 1.9rem); color: #c4b5fd; margin: 12px 0 4px;
  font-weight: 600; }
.qcard .hint { color: var(--muted); font-size: 0.9rem; }

/* Feedback */
.feedback {
  border-radius: 14px; padding: 12px 16px; margin: 6px 0 14px; font-weight: 500;
  animation: pop .25s ease-out;
}
.feedback.good { background: rgba(52,211,153,0.10); border: 1px solid rgba(52,211,153,0.35); color: #a7f3d0; }
.feedback.bad  { background: rgba(248,113,113,0.10); border: 1px solid rgba(248,113,113,0.35); color: #fecaca; }
.feedback code { background: rgba(255,255,255,0.08); color: #fff; padding: 1px 6px; border-radius: 6px;
  font-family: 'JetBrains Mono', monospace; }
@keyframes pop { from { transform: translateY(4px); opacity: 0; } to { transform: none; opacity: 1; } }

/* Inputs & buttons */
.stTextInput input {
  font-family: 'JetBrains Mono', monospace !important; font-size: 1.5rem !important;
  text-align: center; height: 3.4rem; border-radius: 14px !important;
  background: rgba(255,255,255,0.05) !important; color: #fff !important;
  border: 1px solid var(--panel-border) !important;
}
.stTextInput input:focus { border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(124,92,255,0.25) !important; }
.stButton button, .stFormSubmitButton button {
  border-radius: 12px; font-weight: 600; height: 2.9rem; transition: all .15s ease;
}
.stFormSubmitButton button[kind="primaryFormSubmit"], .stButton button[kind="primary"] {
  background: linear-gradient(120deg, var(--accent), #5b8cff); border: none; color: white;
}
.stFormSubmitButton button[kind="primaryFormSubmit"]:hover { filter: brightness(1.12); transform: translateY(-1px); }
[data-testid="stForm"] { border: none; padding: 0; }
audio { width: 100%; border-radius: 12px; }

/* Sidebar */
section[data-testid="stSidebar"] {
  background: rgba(13,15,28,0.96); border-right: 1px solid var(--panel-border);
}
section[data-testid="stSidebar"] h2 { font-size: 1.05rem; font-weight: 700; letter-spacing: -0.01em; }
.side-note { color: var(--muted); font-size: 0.82rem; line-height: 1.45; }

/* History chips */
.history { display: flex; flex-wrap: wrap; gap: 6px; justify-content: center; margin-top: 6px; }
.chip { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; padding: 4px 10px;
  border-radius: 999px; border: 1px solid var(--panel-border); background: var(--panel); }
.chip.good { color: #6ee7b7; border-color: rgba(52,211,153,0.3); }
.chip.bad  { color: #fca5a5; border-color: rgba(248,113,113,0.3); }

.footer { text-align: center; color: var(--muted); font-size: 0.8rem; margin-top: 2.5rem; }
</style>
""",
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------- #
# Session state
# --------------------------------------------------------------------------- #
DEFAULTS = {
    "score": 0,
    "attempted": 0,
    "correct": 0,
    "streak": 0,
    "best_streak": 0,
    "question": None,       # dict with text, spoken, answer
    "audio_bytes": None,
    "feedback": None,       # (is_correct, user_answer, question_text, correct_answer)
    "history": [],          # list of (question_text, is_correct)
    "q_number": 0,
    "settings_sig": None,
}
for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --------------------------------------------------------------------------- #
# Sidebar: drill settings (same options and ranges as the original app)
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.markdown("## ⚙️ Drill settings")

    st.markdown("**Operations**")
    add = st.checkbox("➕ Addition", value=True)
    sub = st.checkbox("➖ Subtraction", value=True)
    mult = st.checkbox("✖️ Multiplication", value=True)

    st.markdown("**Mode**")
    mode = st.radio(
        "Mode",
        ["🎧 Audio", "👀 Visual"],
        index=0,
        horizontal=True,
        label_visibility="collapsed",
        help="Audio reads the question aloud, like a real interview. Visual shows it on screen.",
    )
    audio_mode = mode.startswith("🎧")
    autoplay = st.toggle("Autoplay each question", value=True, disabled=not audio_mode)

    st.markdown("**Difficulty**")
    add_sub_range = st.slider(
        "Addition / subtraction: upper range",
        min_value=100, max_value=10000, step=50, value=100,
    )
    multiply_range1 = st.slider(
        "Multiplication number 1: upper range",
        min_value=12, max_value=1000, step=2, value=12,
    )
    multiply_range2 = st.slider(
        "Multiplication number 2: upper range",
        min_value=100, max_value=1000, step=2, value=100,
    )
    st.markdown(
        f"<div class='side-note'>Current: (2–{add_sub_range:,}) ± (2–{add_sub_range:,}) and "
        f"(2–{multiply_range1:,}) × (2–{multiply_range2:,}).</div>",
        unsafe_allow_html=True,
    )

    st.divider()
    if st.button("↺ Reset session", use_container_width=True):
        for key, val in DEFAULTS.items():
            st.session_state[key] = val if not isinstance(val, list) else []
        st.rerun()

# --------------------------------------------------------------------------- #
# Question generation (same logic as the original app)
# --------------------------------------------------------------------------- #
def make_question():
    operations = []
    if add:
        operations.append("Plus")
    if sub:
        operations.append("Minus")
    if mult:
        operations.append("Multiplied By")
    if not operations:
        return None

    op = random.choice(operations)
    if op == "Plus":
        a = random.randint(2, add_sub_range)
        b = random.randint(2, add_sub_range)
        return {"text": f"{a} + {b}", "spoken": f"{a} Plus {b}", "answer": a + b}
    if op == "Minus":
        a, b = sorted((random.randint(2, add_sub_range), random.randint(2, add_sub_range)), reverse=True)
        return {"text": f"{a} − {b}", "spoken": f"{a} Minus {b}", "answer": a - b}
    a = random.randint(2, multiply_range1)
    b = random.randint(2, multiply_range2)
    a, b = random.sample([a, b], 2)
    return {"text": f"{a} × {b}", "spoken": f"{a} Multiplied By {b}", "answer": a * b}


@st.cache_data(show_spinner=False, max_entries=256)
def speak(text):
    """Return MP3 bytes for the given text using Google Text-to-Speech."""
    buf = io.BytesIO()
    gTTS(text=text, lang="en", slow=False).write_to_fp(buf)
    return buf.getvalue()


def new_question():
    q = make_question()
    st.session_state.question = q
    st.session_state.q_number += 1
    st.session_state.audio_bytes = None
    if q is not None:
        try:
            st.session_state.audio_bytes = speak(q["spoken"])
        except Exception:
            st.session_state.audio_bytes = None


# Regenerate the question if there isn't one yet or the settings changed.
settings_sig = (add, sub, mult, add_sub_range, multiply_range1, multiply_range2)
if st.session_state.question is None or st.session_state.settings_sig != settings_sig:
    st.session_state.settings_sig = settings_sig
    new_question()


def check_answer():
    q = st.session_state.question
    if q is None:
        return
    raw = st.session_state.answer_input.strip().replace(",", "")
    if not raw:
        return
    is_correct = raw.lstrip("+") == str(q["answer"])
    st.session_state.attempted += 1
    if is_correct:
        st.session_state.score += 1
        st.session_state.correct += 1
        st.session_state.streak += 1
        st.session_state.best_streak = max(st.session_state.best_streak, st.session_state.streak)
    else:
        st.session_state.score -= 1
        st.session_state.streak = 0
    st.session_state.feedback = (is_correct, raw, q["text"], q["answer"])
    st.session_state.history = ([(q["text"], is_correct)] + st.session_state.history)[:12]
    new_question()


# --------------------------------------------------------------------------- #
# Main layout
# --------------------------------------------------------------------------- #
st.markdown(
    """
<div class="hero">
  <span class="badge">Trader & quant interview prep</span>
  <h1>Dhruv's MathBot</h1>
  <p>Mental math drills you <b>hear</b>, not just read — the way questions come at you in a real interview.</p>
</div>
""",
    unsafe_allow_html=True,
)

score = st.session_state.score
accuracy = (
    f"{round(100 * st.session_state.correct / st.session_state.attempted)}%"
    if st.session_state.attempted
    else "—"
)
score_cls = "pos" if score > 0 else "neg" if score < 0 else ""
st.markdown(
    f"""
<div class="stats">
  <div class="stat"><div class="label">Score</div><div class="value {score_cls}">{score if score <= 0 else f"+{score}"}</div></div>
  <div class="stat"><div class="label">Accuracy</div><div class="value">{accuracy}</div></div>
  <div class="stat"><div class="label">Streak</div><div class="value">🔥 {st.session_state.streak}</div></div>
  <div class="stat"><div class="label">Best</div><div class="value">{st.session_state.best_streak}</div></div>
</div>
""",
    unsafe_allow_html=True,
)

q = st.session_state.question
if q is None:
    st.warning("Pick at least one operation in the sidebar to start practising.")
    st.stop()

audio_ok = st.session_state.audio_bytes is not None
show_text = (not audio_mode) or (not audio_ok)

if show_text:
    body = f"<div class='expr'>{q['text']}</div>"
    hint = "Type your answer below and press Enter."
else:
    body = "<div class='hidden-expr'>🎧 Listen carefully…</div>"
    hint = "Press play, then type your answer and press Enter."

st.markdown(
    f"""
<div class="qcard">
  <div class="qnum">Question {st.session_state.q_number}</div>
  {body}
  <div class="hint">{hint}</div>
</div>
""",
    unsafe_allow_html=True,
)

if audio_mode:
    if audio_ok:
        st.audio(st.session_state.audio_bytes, format="audio/mp3", autoplay=autoplay)
    else:
        st.info("Couldn't reach the text-to-speech service, so the question is shown on screen instead.")

fb = st.session_state.feedback
if fb is not None:
    ok, given, qtext, correct = fb
    if ok:
        msg = f"✅ Correct! <code>{qtext} = {correct:,}</code>"
    else:
        msg = f"❌ Not quite. You said <code>{given}</code>, but <code>{qtext} = {correct:,}</code>"
    st.markdown(f"<div class='feedback {'good' if ok else 'bad'}'>{msg}</div>", unsafe_allow_html=True)

with st.form("answer_form", clear_on_submit=True, border=False):
    st.text_input(
        "Your answer",
        key="answer_input",
        placeholder="Your answer",
        label_visibility="collapsed",
    )
    c1, c2 = st.columns([3, 1])
    c1.form_submit_button("Submit answer", type="primary", use_container_width=True, on_click=check_answer)
    skip = c2.form_submit_button("Skip ↷", use_container_width=True)

if skip:
    st.session_state.feedback = None
    new_question()
    st.rerun()

if st.session_state.history:
    chips = "".join(
        f"<span class='chip {'good' if ok else 'bad'}'>{t}</span>" for t, ok in st.session_state.history
    )
    st.markdown(f"<div class='history'>{chips}</div>", unsafe_allow_html=True)

with st.expander("About this app"):
    st.markdown(
        """
This app was built by **Dhruv Suresh** to help people practise mental math through both the visual
**and** the auditory medium. It's aimed at aspiring traders and quants preparing for interviews.
Most online platforms only show questions on screen, which doesn't match a real interview where
questions are spoken to you. MathBot combines speech and text to simulate that more closely.

**Defaults:** addition and subtraction use (2 to 100) ± (2 to 100); multiplication uses
(2 to 12) × (2 to 100). Use the sliders in the sidebar to raise the difficulty. Addition and
subtraction go up to 5 digits and multiplication up to 4 *(if you can do 4×4s mentally, you can
legally call yourself a human calculator)*.

**Scoring:** +1 for a correct answer, −1 for a wrong one. Pick any combination of operations
with the checkboxes. Enjoy!
"""
    )

st.markdown("<div class='footer'>Built by Dhruv Suresh · 2022, refreshed 2026</div>", unsafe_allow_html=True)
