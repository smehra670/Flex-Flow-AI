import streamlit as st
import os
import base64
from dotenv import load_dotenv
import json
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools import tool

st.set_page_config(page_title="Flex Flow AI", layout="centered")
load_dotenv()
groq_key = os.getenv("GROQ_API_KEY")
if groq_key:
    os.environ["GROQ_API_KEY"] = groq_key

USER_FILE  = "users.json"
SCORE_FILE = "score.json"

def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    with open(filename, "w") as f:
        json.dump({}, f, indent=2)
    return {}

def save_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def load_users():
    return load_json(USER_FILE)

def save_user(username, password):
    users = load_users()
    users[username] = password
    save_json(users, USER_FILE)

def authenticate(username, password):
    users = load_users()
    return username in users and users[username] == password

def load_scores():
    return load_json(SCORE_FILE)

def save_scores(all_scores):
    save_json(all_scores, SCORE_FILE)

if "logged_in"       not in st.session_state: st.session_state.logged_in       = False
if "username"        not in st.session_state: st.session_state.username        = None
if "all_scores"      not in st.session_state: st.session_state.all_scores      = load_scores()
if "daily_score"     not in st.session_state: st.session_state.daily_score     = 0
if "task_given"      not in st.session_state: st.session_state.task_given      = False
if "task_completed"  not in st.session_state: st.session_state.task_completed  = False
if "fitness_plan"    not in st.session_state: st.session_state.fitness_plan    = None
if "plan_key"        not in st.session_state: st.session_state.plan_key        = 0
if "diet_plan"       not in st.session_state: st.session_state.diet_plan       = None
if "diet_key"        not in st.session_state: st.session_state.diet_key        = 0
if "messages"        not in st.session_state: st.session_state.messages        = []

import base64, mimetypes

def _img_to_data_uri(path):
    mime = mimetypes.guess_type(path)[0] or "image/jpeg"
    with open(path, "rb") as f:
        return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"

def section_bg_css(path, class_name, darkness=0.55, position="center"):
    try:
        uri = _img_to_data_uri(path)
    except FileNotFoundError:
        uri = ""
    overlay = f"linear-gradient(rgba(7,12,18,{darkness}), rgba(7,12,18,{darkness}))"
    image   = f"url('{uri}')" if uri else "linear-gradient(120deg,#0b1220,#111827)"
    return f"""
    <style>
      .{class_name}::before {{
        content:""; position:fixed; inset:0; z-index:-1;
        background: {overlay}, {image};
        background-size: cover; background-position: {position}; background-repeat: no-repeat; background-attachment: fixed;
        filter: saturate(1.05) contrast(1.05);
      }}
      .{class_name} .glass-card, .{class_name} .metric-card {{
        background: rgba(17,24,39,0.55); border:1px solid rgba(255,255,255,.18);
        backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
      }}
      .{class_name} h1, .{class_name} h2, .{class_name} .section-title,
      .{class_name} .section-sub, .{class_name} p, .{class_name} label,
      .{class_name} .metric-label {{ color:#f3f4f6 !important; }}
      .{class_name} .metric-value {{ color:#22c55e !important; }}
    </style>
    """

def load_background_image():
    try:
        with open("back.jpg", "rb") as f:
            data = f.read()
            encoded = base64.b64encode(data).decode()
            return f"data:image/jpg;base64,{encoded}"
    except FileNotFoundError:
        return None

import base64

def _img_to_data_uri(path, mime="image/avif"):
    with open(path, "rb") as f:
        return "data:%s;base64,%s" % (mime, base64.b64encode(f.read()).decode())

def daily_tasks_image_bg_css(path="task.avif", darkness=0.55):
    try:
        uri = _img_to_data_uri(path, "image/avif")
    except FileNotFoundError:
        uri = ""
    overlay = f"linear-gradient(rgba(7,12,18,{darkness}), rgba(7,12,18,{darkness}))"
    image   = f"url('{uri}')" if uri else "linear-gradient(120deg,#0b1220,#111827)"
    return f"""
    <style>
      .daily-hero::before {{
        content:""; position:fixed; inset:0; z-index:-1;
        background: {overlay}, {image};
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        filter: saturate(1.05) contrast(1.05);
      }}
      .daily-hero .glass-card, .daily-hero .metric-card {{
        background: rgba(17,24,39,0.55);
        border: 1px solid rgba(255,255,255,0.18);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        box-shadow: 0 18px 40px rgba(0,0,0,.35);
      }}
      .daily-hero .section-title, .daily-hero .section-sub,
      .daily-hero .metric-label {{ color: #f3f4f6 !important; }}
      .daily-hero .metric-value {{ color: #22c55e !important; }}
    </style>
    """

def food_bg_css(class_name, darkness=0.55, position="center"):
    try:
        uri = _img_to_data_uri("food.jpg", "image/jpeg")
    except FileNotFoundError:
        uri = ""
    overlay = f"linear-gradient(rgba(7,12,18,{darkness}), rgba(7,12,18,{darkness}))"
    image   = f"url('{uri}')" if uri else "linear-gradient(120deg,#0b1220,#111827)"
    return f"""
    <style>
      .{class_name}::before {{
        content:""; position:fixed; inset:0; z-index:-1;
        background: {overlay}, {image};
        background-size: cover; background-position: {position}; background-repeat: no-repeat; background-attachment: fixed;
        filter: saturate(1.05) contrast(1.05);
      }}
      .{class_name} .glass-card, .{class_name} .metric-card {{
        background: rgba(17,24,39,0.55); border:1px solid rgba(255,255,255,.18);
        backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
        box-shadow: 0 18px 40px rgba(0,0,0,.35);
      }}
      .{class_name} h1, .{class_name} h2, .{class_name} .section-title,
      .{class_name} .section-sub, .{class_name} p, .{class_name} label,
      .{class_name} .metric-label {{ color:#f3f4f6 !important; }}
      .{class_name} .metric-value {{ color:#22c55e !important; }}
    </style>
    """

def quiz_bg_css(class_name, darkness=0.55, position="center"):
    try:
        uri = _img_to_data_uri("quiz.avif", "image/avif")
    except FileNotFoundError:
        uri = ""
    overlay = f"linear-gradient(rgba(7,12,18,{darkness}), rgba(7,12,18,{darkness}))"
    image   = f"url('{uri}')" if uri else "linear-gradient(120deg,#0b1220,#111827)"
    return f"""
    <style>
      .{class_name}::before {{
        content:""; position:fixed; inset:0; z-index:-1;
        background: {overlay}, {image};
        background-size: cover; background-position: {position}; background-repeat: no-repeat; background-attachment: fixed;
        filter: saturate(1.05) contrast(1.05);
      }}
      .{class_name} .glass-card, .{class_name} .metric-card {{
        background: rgba(17,24,39,0.55); border:1px solid rgba(255,255,255,.18);
        backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
        box-shadow: 0 18px 40px rgba(0,0,0,.35);
      }}
      .{class_name} h1, .{class_name} h2, .{class_name} .section-title,
      .{class_name} .section-sub, .{class_name} p, .{class_name} label,
      .{class_name} .metric-label {{ color:#f3f4f6 !important; }}
      .{class_name} .metric-value {{ color:#22c55e !important; }}
    </style>
    """

def chat_bg_css(class_name, darkness=0.55, position="center"):
    try:
        uri = _img_to_data_uri("chat.jpg", "image/jpeg")
    except FileNotFoundError:
        uri = ""
    overlay = f"linear-gradient(rgba(7,12,18,{darkness}), rgba(7,12,18,{darkness}))"
    image   = f"url('{uri}')" if uri else "linear-gradient(120deg,#0b1220,#111827)"
    return f"""
    <style>
      .{class_name}::before {{
        content:""; position:fixed; inset:0; z-index:-1;
        background: {overlay}, {image};
        background-size: cover; background-position: {position}; background-repeat: no-repeat; background-attachment: fixed;
        filter: saturate(1.05) contrast(1.05);
      }}
      .{class_name} h1, .{class_name} h2, .{class_name} h3,
      .{class_name} .section-title, .{class_name} .section-sub,
      .{class_name} p, .{class_name} label {{ color:#f3f4f6 !important; }}
      .{class_name} [data-testid="stChatMessage"] {{
        background: rgba(17,24,39,0.7) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        backdrop-filter: blur(8px) !important;
        border-radius: 12px !important;
      }}
      .{class_name} [data-testid="stChatInput"] > div {{
        background: rgba(17,24,39,0.7) !important;
        border: 1px solid rgba(255,255,255,0.25) !important;
        backdrop-filter: blur(8px) !important;
        border-radius: 12px !important;
      }}
    </style>
    """

def get_login_styles():
    bg_image = load_background_image()
    if bg_image:
        bg_style = f"""
        background:
          linear-gradient(135deg, rgba(0,0,0,0.40), rgba(0,50,100,0.60)),
          url('{bg_image}');
        """
    else:
        bg_style = """
        background: linear-gradient(135deg, rgba(0,0,0,0.6), rgba(0,50,100,0.8));
        """

    return f"""
    <style>
      :root {{
        --glass: rgba(0,0,0,0.40);
        --border: rgba(255,255,255,0.30);
        --text:#ffffff; --muted: rgba(255,255,255,0.85);
        --accent:#6EE7F9;
      }}
      .stApp {{
        {bg_style}
        background-size: cover;
        background-position: 89% center;
        background-attachment: fixed;
        background-repeat: no-repeat;
      }}
      .block-container {{ padding-top: 0 !important; padding-bottom: 0 !important; }}
      .login-wrap-left {{
        max-width: 380px;
        margin: 10vh auto 6vh;
        margin-left: 5vw;
      }}
      @media (max-width: 900px) {{
        .login-wrap-left {{ margin-left:auto; margin-right:auto; max-width: 420px; }}
      }}
      .login-glass-card {{
        background: var(--glass);
        border: 2px solid var(--border);
        border-radius: 18px;
        padding: 28px;
        box-shadow: 0 24px 60px rgba(0,0,0,0.45);
        backdrop-filter: blur(16px);
      }}
      .login-title {{ color: var(--text); margin: 0 0 8px; font-size: 1.75rem; font-weight: 800; }}
      .login-subtitle {{ color: var(--muted); margin: 0 0 18px; }}
      .stTextInput > div > div > input {{
        background: rgba(255,255,255,0.16) !important;
        color:#fff !important; border:1px solid rgba(255,255,255,0.35) !important;
        border-radius:12px !important; padding:12px 14px !important;
      }}
      .stTextInput > div > div > input:focus {{
        border-color:#6EE7F9 !important; box-shadow:0 0 0 2px rgba(110,231,249,.35) !important;
      }}
      .stButton > button {{
        background: linear-gradient(135deg,#8bd3ff,#7aa8ff) !important;
        color:#061523 !important; border:0 !important; border-radius:12px !important;
        padding:12px 16px !important; font-weight:800 !important; width:100% !important;
        box-shadow:0 10px 24px rgba(34,211,238,.35) !important;
      }}
      .stButton > button:hover {{ transform: translateY(-1px); }}
      [data-testid="stHeader"]{{background:transparent}}
    </style>
    """

import base64

def _daily_bg_data_uri():
    svg = '''
<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%"  stop-color="#00d4ff"/>
      <stop offset="50%" stop-color="#7c3aed"/>
      <stop offset="100%" stop-color="#00ffa3"/>
    </linearGradient>
    <radialGradient id="r1" cx="0.15" cy="0.10" r="0.65">
      <stop offset="0%" stop-color="#34d399" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#34d399" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="r2" cx="0.90" cy="0.20" r="0.70">
      <stop offset="0%" stop-color="#a78bfa" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#a78bfa" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="100%" height="100%" fill="#0b1220"/>
  <rect width="100%" height="100%" fill="url(#g)" opacity="0.28"/>
  <rect width="100%" height="100%" fill="url(#r1)" opacity="0.85"/>
  <rect width="100%" height="100%" fill="url(#r2)" opacity="0.85"/>

  <g opacity="0.06">
    <text x="92%" y="50%" text-anchor="middle"
          font-size="220" font-weight="900" fill="#ffffff"
          transform="rotate(-90, 92, 540)">SHOW UP</text>
  </g>
</svg>'''.strip()
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()

def daily_tasks_bg_css():
    uri = _daily_bg_data_uri()
    return f"""
    <style>
      .daily-hero::before {{
        content: "";
        position: fixed; inset: 0; z-index: -1;
        background:
          linear-gradient(rgba(8,12,20,.72), rgba(10,14,22,.72)),
          url("{uri}") center/cover no-repeat fixed;
        filter: saturate(1.08) contrast(1.05);
      }}
      .daily-hero .glass-card, .daily-hero .metric-card {{
        box-shadow: 0 18px 40px rgba(0,0,0,.35);
        border-color: rgba(255,255,255,.28);
        background: rgba(255,255,255,.10);
        backdrop-filter: blur(12px);
      }}
    </style>
    """

def get_app_styles():
    return """
    <style>
      :root {
        --bg1:#00c6ff; --bg2:#0072ff;
        --glass: rgba(255,255,255,0.10);
        --glass-strong: rgba(255,255,255,0.16);
        --border: rgba(255,255,255,0.25);
        --text:#ffffff;
        --muted: rgba(255,255,255,0.75);
        --success:#22c55e;
      }
      .stApp{
        background: linear-gradient(135deg,var(--bg1),var(--bg2)) !important;
        background-image: none !important;
      }
      .glass-card{
        background: var(--glass);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 28px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
        backdrop-filter: blur(10px);
      }
      .section-title { color: var(--text); margin: 0 0 8px 0; }
      .section-sub { color: var(--muted); margin: 0 0 18px 0; }
      .metric-card {
        background: var(--glass-strong);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 18px; text-align: center;
      }
      .metric-value { font-size: 2.2rem; font-weight: 800; color: var(--success); margin: 2px 0 0; }
      .metric-label { color: var(--muted); font-size: 0.85rem; margin-top: -4px; }
      .stButton > button {
        background: linear-gradient(135deg,#7dd3fc,#38bdf8);
        color: #00131a; border: 0; border-radius: 12px; padding: 10px 16px; font-weight: 700;
        box-shadow: 0 6px 18px rgba(56,189,248,.35);
      }
      .stButton > button:hover { transform: translateY(-1px); }
      .stTextInput > div > div > input { background: #ffffff1a !important; color: #fff !important; }
    </style>
    """

if not st.session_state.logged_in:
    st.markdown(get_login_styles(), unsafe_allow_html=True)
    st.markdown('<div class="login-wrap-left"><div class="login-glass-card">', unsafe_allow_html=True)
    st.markdown('<h1 class="login-title">Flex Flow AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="login-subtitle">Transform your fitness journey with AI-powered planning</p>', unsafe_allow_html=True)
    mode = st.radio("", ["Sign In", "Create Account"], horizontal=True, label_visibility="collapsed")
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    if st.button("Sign In" if mode=="Sign In" else "Create Account"):
        if not username or not password:
            st.error("Please enter both username and password.")
        elif mode=="Sign In":
            if authenticate(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                loaded_scores = load_scores()
                st.session_state.all_scores = loaded_scores if isinstance(loaded_scores, dict) else {}
                st.session_state.daily_score = st.session_state.all_scores.get(username, 0)
                st.success("Welcome back! Redirecting...")
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")
        else:
            save_user(username, password)
            st.success("Account created successfully! Please sign in.")
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.stop()

st.markdown(get_app_styles(), unsafe_allow_html=True)

st.sidebar.title("🔗 Navigation")
nav_option = st.sidebar.radio("Go to", ["📋 Fitness Plan", "🗓️ Daily Tasks", "💬 Chat bot", "🥗 Diet planner", "❓ Quiz"])
st.sidebar.button("🔓 Logout", on_click=lambda: st.session_state.update({
    "logged_in": False,
    "username": None,
    "task_given": False,
    "task_completed": False
}))

@tool
def fitness(type):
    """You are a fitness trainer and return a 14-day fitness plan based on selected activities"""

@tool
def quest(topic):
    """Give 10 multiple choice questions based on the fitness topic requested by the user"""
    return "1. Question one?\n2. Question two?\n3. Question three? etc"

@tool
def diet(food):
    """You are a diet trainer and you will return a 14 day diet plan based on the type of diet requested such as bulking or cutting"""

gym = Agent(
    name="Gym Agent",
    role="Fitness planner",
    model=Groq(id="deepseek-r1-distill-llama-70b"),
    tools=[fitness],
    instructions="Create a 14-day fitness plan based ONLY on the selected activities. Each day must be under 2 hours.",
    show_tool_calls=True,
    markdown=True,
)
daily = Agent(
    name="Daily",
    role="Daily task generator",
    model=Groq(id="deepseek-r1-distill-llama-70b"),
    tools=[fitness],
    instructions="Give one challenging exercise task such as 25 pushups or 30 sit ups etc. It can be from a range of exercises and something they can do on the spot.",
    show_tool_calls=True,
    markdown=True,
)
chat = Agent(
    name="Fitness Chatbot",
    role=("You are a friendly, concise fitness coach. "
          "Provide ONLY the final answer—no chain-of-thought or preamble."),
    model=Groq(id="deepseek-r1-distill-llama-70b"),
    tools=[],
    instructions="Answer user questions directly and succinctly about fitness.",
    show_tool_calls=False,
    markdown=True,
)
food = Agent(
    role="Diet planner",
    model=Groq(id="deepseek-r1-distill-llama-70b"),
    tools=[diet],
    instructions="Create a 14-day diet plan based ONLY on the type selected.",
    show_tool_calls=True,
    markdown=True,
)
next_agent = Agent(
    role="You are a test generator.",
    model=Groq(id="deepseek-r1-distill-llama-70b"),
    tools=[quest],
    instructions=("When prompted, return 10 multiple choice questions based on the fitness topic inputted. "
                  "Do not return the answers unless explicitly asked for them separately."),
    show_tool_calls=True,
    markdown=True,
)

if nav_option == "📋 Fitness Plan":
    st.markdown(food_bg_css("fit-hero", darkness=0.55, position="center"), unsafe_allow_html=True)
    st.markdown('<div class="fit-hero">', unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>💪 AI Fitness Planner</h1>", unsafe_allow_html=True)
    st.markdown("### Select the activities you'd like to include:")
    cols = st.columns(4)
    options = {"Weight Lifting":"🏋️‍♂️","Cardio":"🏃‍♀️","Meditation":"🧘","Calisthenics":"🤸"}
    selected = []
    for i, (label, emoji) in enumerate(options.items()):
        with cols[i]:
            if st.toggle(f"{emoji} {label}", key=label):
                selected.append(label)
    if not selected:
        st.warning("Please select at least one activity.")
    else:
        st.success(f"You selected: {', '.join(selected)}")
        if st.session_state.fitness_plan:
            st.markdown(st.session_state.fitness_plan, unsafe_allow_html=True)
            if st.button("🔄 Refresh Plan", key=f"refresh_{st.session_state.plan_key}"):
                st.session_state.fitness_plan = None
                st.session_state.plan_key += 1
                st.rerun()
        else:
            if st.button("Generate My Plan"):
                with st.spinner("Generating..."):
                    all_acts = list(options.keys())
                    excluded = [a for a in all_acts if a not in selected]
                    prompt = (
                        f"You are a professional fitness trainer. Generate a 14-day fitness plan "
                        f"using ONLY these activities: {', '.join(selected)}.\n\n"
                        f"Do NOT include these types: {', '.join(excluded)}.\n"
                        f"For Weight Lifting, include bench press, deadlifts, curls, rows.\n"
                        f"Each day's workout must stay under 2 hours.\n"
                        f"Provide a clear day-by-day breakdown."
                    )
                    plan = gym.run(prompt).content
                    st.session_state.fitness_plan = plan
                    st.markdown(plan, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif nav_option == "🗓️ Daily Tasks":
    st.markdown(daily_tasks_image_bg_css("task.avif", darkness=0.55), unsafe_allow_html=True)
    st.markdown('<div class="daily-hero">', unsafe_allow_html=True)
    left, right = st.columns([3,1], gap="large")
    with left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-title">🗓️ Daily Task</h2>', unsafe_allow_html=True)
        st.markdown('<p class="section-sub">Challenge yourself with quick, on-the-spot workouts.</p>', unsafe_allow_html=True)
        if st.button("🎯 Get New Task", key="task_btn", help="Generate a new exercise challenge", use_container_width=True):
            prompt = ("Give an exercise task such as 25 sit-ups or 30 push-ups. "
                      "It must be doable on the spot, slightly challenging.")
            with st.spinner("Generating task..."):
                task = daily.run(prompt).content
            st.session_state.task_given = True
            st.session_state.task_completed = False
            st.session_state["last_task"] = task
        if st.session_state.get("last_task"):
            st.markdown(f"""
                <div style="
                    background: rgba(255,255,255,0.12);
                    border-left: 4px solid #22c55e;
                    border-radius: 12px; padding: 16px; margin-top: 16px;
                ">
                    <div style="color:#eaf6ff;font-weight:700;margin-bottom:6px;">Your Challenge</div>
                    <div style="color:#ffffffc9;">{st.session_state['last_task']}</div>
                </div>
            """, unsafe_allow_html=True)
        if st.session_state.task_given:
            def complete_task():
                st.session_state.daily_score   += 1
                st.session_state.task_given     = False
                st.session_state.task_completed = True
                user = st.session_state.username
                st.session_state.all_scores[user] = st.session_state.daily_score
                save_scores(st.session_state.all_scores)
            st.button("✅ Mark Complete", on_click=complete_task, key="complete_task_btn", use_container_width=True)
        if st.session_state.task_completed:
            st.success("✅ Task completed! Great job!")
        st.markdown('</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-sub" style="text-align:center;margin-bottom:6px;">Your Score</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{st.session_state.daily_score}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">completed tasks</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif nav_option == "💬 Chat bot":
    st.markdown(chat_bg_css("chat-hero", darkness=0.55, position="center"), unsafe_allow_html=True)
    st.markdown('<div class="chat-hero">', unsafe_allow_html=True)
    st.title("💬 Fitness Chat")
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])
    user_input = st.chat_input("Ask me anything about fitness…")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("assistant"):
            response = chat.run(user_input).content.strip()
            st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
    st.markdown('</div>', unsafe_allow_html=True)

elif nav_option == "🥗 Diet planner":
    st.markdown(food_bg_css("diet-hero", darkness=0.58, position="center"), unsafe_allow_html=True)
    st.markdown('<div class="diet-hero">', unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>🥗 AI Diet Planner</h1>", unsafe_allow_html=True)
    st.markdown("### Select your diet goal:")
    options = {"Bulking": "🍚", "Cutting": "🥗"}
    choice = st.radio(
        "Goal",
        [f"{emoji} {label}" for label, emoji in options.items()],
        horizontal=True,
        label_visibility="collapsed",
    )
    selected_goal = choice.split(" ", 1)[1]
    st.success(f"You selected: {selected_goal}")
    if st.session_state.diet_plan:
        st.markdown(st.session_state.diet_plan, unsafe_allow_html=True)
        if st.button("🔄 Refresh Plan", key=f"drefresh_{st.session_state.diet_key}"):
            st.session_state.diet_plan = None
            st.session_state.diet_key += 1
            st.rerun()
    else:
        if st.button("Generate My Diet Plan"):
            with st.spinner("Generating..."):
                prompt = (
                    f"You are a professional diet planner. Create a detailed 14-day diet plan for the goal: {selected_goal}.\n"
                    f"Include each day's breakfast, lunch, dinner, and 1–2 snacks. Add rough calories and macro focus.\n"
                    f"Keep it practical, affordable, and varied. Output a clear day-by-day breakdown."
                )
                plan = food.run(prompt).content
                st.session_state.diet_plan = plan
                st.markdown(plan, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif nav_option == "❓ Quiz":
    st.markdown(quiz_bg_css("quiz-hero", darkness=0.55, position="center"), unsafe_allow_html=True)
    st.markdown('<div class="quiz-hero">', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">📝 Quiz Generator</h2>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Create a quick 10-question MCQ quiz on any fitness topic.</p>', unsafe_allow_html=True)
    topic = st.text_input("Topic", placeholder="e.g., Hypertrophy basics")
    if st.button("⚙️ Generate Questions", key="generate_questions", use_container_width=True):
        if not topic.strip():
            st.warning("Please enter a topic.")
        else:
            with st.spinner("Generating questions..."):
                try:
                    response = next_agent.run(f"Generate 10 multiple choice questions on: {topic}")
                    st.session_state.questions = response.content.strip()
                    st.session_state.current_topic = topic
                    st.success("Questions generated!")
                except Exception as e:
                    st.error("❌ Failed to generate questions. Try a different topic.")
                    st.exception(e)
    if "questions" in st.session_state:
        st.markdown('<div class="section-sub" style="margin-top:20px;">Questions</div>', unsafe_allow_html=True)
        st.code(st.session_state.questions, language="text")
        if st.button("🔍 Show Answers", key="show_answers", use_container_width=True):
            prompt = (
                f"{st.session_state.questions}\n\n"
                "Now list only the correct answers to the 10 questions above.\n"
                "Do NOT include the questions again. Format exactly:\n"
                "1. ...\n2. ...\n3. ...\n4. ...\n5. ...\n6. ...\n7. ...\n8. ...\n9. ...\n10. ..."
            )
            with st.spinner("Getting answers..."):
                try:
                    ans = next_agent.run(prompt).content.strip()
                    st.session_state.answers = ans
                except Exception as e:
                    st.error("❌ Failed to get answers.")
                    st.exception(e)
        if "answers" in st.session_state:
            st.markdown('<div class="section-sub" style="margin-top:20px;">Answers</div>', unsafe_allow_html=True)
            st.code(st.session_state.answers, language="text")
    else:
        st.info("Enter a topic and generate questions to get started.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
