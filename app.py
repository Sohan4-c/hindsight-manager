"""
╔═══════════════════════════════════════════════════════════╗
║   Hindsight-Powered AI Group Project Manager              ║
║   Stack: Streamlit · Groq (qwen3-32b) · Hindsight        ║
╚═══════════════════════════════════════════════════════════╝
"""

import asyncio
import concurrent.futures
import os
import time
import traceback
from datetime import datetime, timezone

import nest_asyncio
nest_asyncio.apply()  # patch Streamlit's running loop to allow nested asyncio calls

import streamlit as st
from dotenv import load_dotenv

# ── Load environment ──────────────────────────────────────
load_dotenv()

GROQ_API_KEY        = os.getenv("GROQ_API_KEY", "")
HINDSIGHT_API_KEY   = os.getenv("HINDSIGHT_API_KEY", "")
HINDSIGHT_BASE_URL  = os.getenv("HINDSIGHT_BASE_URL", "https://api.hindsight.io")
LLM_MODEL           = "qwen/qwen3-32b"
HINDSIGHT_BANK      = "project-manager-v1"

# ══════════════════════════════════════════════════════════
#  SECTION 1 — PREMIUM CSS OVERRIDE
# ══════════════════════════════════════════════════════════

def inject_css() -> None:
    """Inject full CSS override — Claude/Anthropic-inspired warm cream design."""
    st.markdown(
        """
        <style>
        /* ── Google Fonts ── */
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600&family=Inter:wght@300;400;500;600&display=swap');

        /* ── Root Tokens ── */
        :root {
            --bg:          #F7F5F2;
            --bg-alt:      #EFEDE8;
            --bg-deep:     #E8E5DE;
            --surface:     #FDFCFA;
            --user-bubble: #EAE7E0;
            --ai-bubble:   #F0EDE6;
            --border:      #DDD9D0;
            --accent:      #8B6F47;
            --accent-soft: #C9A87C;
            --text-primary: #2C2A26;
            --text-body:    #4A4540;
            --text-muted:   #8A847A;
            --sidebar-bg:   #F0EDE8;
            --radius:       12px;
            --shadow:       0 2px 12px rgba(0,0,0,0.06);
        }

        /* ── Global Reset ── */
        html, body,
        [data-testid="stApp"],
        [data-testid="stAppViewContainer"],
        [data-testid="stAppViewContainer"] > section,
        [data-testid="stMain"],
        .main, .css-18e3th9, .css-1d391kg {
            background: var(--bg) !important;
            background-color: var(--bg) !important;
            font-family: 'Inter', system-ui, sans-serif !important;
            color: #1E1E1E !important;
        }

        /* ── Kill Streamlit header/toolbar bar background seam ── */
        [data-testid="stHeader"],
        [data-testid="stToolbar"] {
            background: var(--bg) !important;
            background-color: var(--bg) !important;
            border-bottom: none !important;
            box-shadow: none !important;
        }

        /* ── Fix input focus ring ── */
        *:focus, *:focus-visible {
            outline-color: var(--accent-soft) !important;
            box-shadow: 0 0 0 2px rgba(139,111,71,0.25) !important;
        }

        /* ── Force dark text everywhere ── */
        .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span,
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4,
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li,
        [data-testid="stMarkdownContainer"] span,
        [data-testid="stMarkdownContainer"] h1,
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3 {
            color: #1E1E1E !important;
        }

        /* ── Suggestion buttons ── */
        .stButton > button {
            background: var(--bg-alt) !important;
            color: #1E1E1E !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px !important;
            font-size: 0.82rem !important;
        }
        .stButton > button:hover {
            background: var(--bg-deep) !important;
            border-color: var(--accent-soft) !important;
        }

        /* ── Hide Streamlit Chrome ── */
        #MainMenu, footer, header,
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        .stDeployButton { display: none !important; }

        /* ── Main content column — centered Claude-style layout ── */
        .block-container,
        [data-testid="block-container"] {
            max-width: 850px !important;
            margin: 0 auto !important;
            padding: 2rem 2rem 1rem !important;
        }
        [data-testid="stMainBlockContainer"] {
            max-width: 850px !important;
            margin: 0 auto !important;
            padding: 0 2rem !important;
        }

        /* ── Chat message bubbles — generous spacing ── */
        [data-testid="stChatMessage"] {
            padding: 1.5rem !important;
            border-radius: 0.75rem !important;
            margin-bottom: 1rem !important;
        }

        /* ── Bottom input bar — aligned with the 850px column ── */
        [data-testid="stBottomBlock"],
        [data-testid="stBottom"] {
            max-width: 850px !important;
            margin: 0 auto !important;
            left: 0 !important;
            right: 0 !important;
        }

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {
            background: var(--sidebar-bg) !important;
            border-right: 1px solid var(--border) !important;
            padding: 0 !important;
        }
        [data-testid="stSidebar"] > div:first-child {
            padding: 1.5rem 1.25rem !important;
        }

        /* ── Sidebar Header ── */
        .sidebar-header {
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 1.15rem;
            font-weight: 600;
            color: var(--text-primary);
            letter-spacing: -0.01em;
            margin-bottom: 0.25rem;
        }
        .sidebar-subtitle {
            font-size: 0.72rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 1.5rem;
        }
        .sidebar-section-label {
            font-size: 0.68rem;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin: 1.25rem 0 0.75rem;
        }

        /* ── Team Member Cards ── */
        .member-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 0.85rem 1rem;
            margin-bottom: 0.6rem;
            box-shadow: var(--shadow);
            transition: box-shadow 0.2s ease;
        }
        .member-card:hover { box-shadow: 0 4px 18px rgba(0,0,0,0.1); }
        .member-name {
            font-weight: 600;
            font-size: 0.88rem;
            color: var(--text-primary);
            margin-bottom: 0.15rem;
        }
        .member-role {
            font-size: 0.72rem;
            color: var(--text-muted);
            margin-bottom: 0.55rem;
        }
        .member-task {
            font-size: 0.78rem;
            color: var(--text-body);
            margin-bottom: 0.45rem;
        }

        /* ── Status Badges ── */
        .badge {
            display: inline-block;
            padding: 0.18rem 0.5rem;
            border-radius: 20px;
            font-size: 0.68rem;
            font-weight: 500;
            letter-spacing: 0.03em;
        }
        .badge-pending   { background: #FEF3C7; color: #92400E; border: 1px solid #FDE68A; }
        .badge-progress  { background: #DBEAFE; color: #1E40AF; border: 1px solid #BFDBFE; }
        .badge-done      { background: #D1FAE5; color: #065F46; border: 1px solid #A7F3D0; }

        /* ── Progress Bar ── */
        .progress-wrap {
            background: var(--bg-deep);
            border-radius: 20px;
            height: 4px;
            margin-top: 0.45rem;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            border-radius: 20px;
            background: linear-gradient(90deg, var(--accent-soft), var(--accent));
        }

        /* ── Memory Status Box ── */
        .memory-status {
            background: var(--bg-alt);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.6rem 0.8rem;
            font-size: 0.72rem;
            color: var(--text-muted);
            margin-top: 1.25rem;
        }
        .memory-dot {
            display: inline-block;
            width: 7px; height: 7px;
            border-radius: 50%;
            margin-right: 5px;
            vertical-align: middle;
        }
        .dot-on  { background: #10B981; box-shadow: 0 0 5px #10B981; }
        .dot-off { background: #F87171; }

        /* ── Main Chat Area ── */
        .chat-container {
            display: flex;
            flex-direction: column;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem 2.5rem;
            gap: 0;
            min-height: calc(100vh - 120px);
        }

        /* ── App Title Bar ── */
        .app-title-bar {
            max-width: 800px;
            margin: 0 auto;
            padding: 1.5rem 2.5rem 0.5rem;
            border-bottom: none !important;
            background: transparent !important;
            width: 100%;
        }
        .app-title {
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 1.4rem;
            font-weight: 500;
            color: var(--text-primary);
            letter-spacing: -0.02em;
        }
        .app-tagline {
            font-size: 0.78rem;
            color: var(--text-muted);
            margin-top: 0.2rem;
        }

        /* ── Chat Bubbles ── */
        .msg-wrapper {
            display: flex;
            flex-direction: column;
            margin: 0.6rem 0;
            animation: fadeSlideIn 0.25s ease forwards;
        }
        @keyframes fadeSlideIn {
            from { opacity: 0; transform: translateY(6px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        .msg-label {
            font-size: 0.68rem;
            font-weight: 600;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            margin-bottom: 0.25rem;
            color: var(--text-muted);
        }
        .msg-bubble {
            display: inline-block;
            max-width: 82%;
            padding: 0.85rem 1.1rem;
            border-radius: 14px;
            font-size: 0.9rem;
            line-height: 1.65;
            color: var(--text-primary);
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .msg-user { align-items: flex-end; }
        .msg-user .msg-bubble {
            background: var(--user-bubble);
            border: 1px solid var(--border);
            border-bottom-right-radius: 4px;
        }
        .msg-ai { align-items: flex-start; }
        .msg-ai .msg-bubble {
            background: var(--ai-bubble);
            border: 1px solid var(--border);
            border-bottom-left-radius: 4px;
        }

        /* ── Memory Recall Callout ── */
        .recall-callout {
            font-size: 0.74rem;
            color: #92400E;
            background: #FFFBEB;
            border: 1px solid #FDE68A;
            border-radius: 8px;
            padding: 0.4rem 0.7rem;
            margin-bottom: 0.4rem;
            max-width: 82%;
        }

        /* ── Timestamp ── */
        .msg-time {
            font-size: 0.65rem;
            color: var(--text-muted);
            margin-top: 0.2rem;
        }

        /* ── Divider ── */
        .chat-divider {
            border: none;
            border-top: 1px solid var(--border);
            margin: 2rem 0 1rem;
        }

        /* ── Welcome Banner ── */
        .welcome-banner {
            text-align: center;
            padding: 3rem 2rem 2rem;
            color: var(--text-muted);
        }
        .welcome-icon { font-size: 2.5rem; margin-bottom: 0.75rem; }
        .welcome-title {
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 1.25rem;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
        }
        .welcome-text { font-size: 0.85rem; line-height: 1.7; }

        /* ── Bottom container wrappers + input container — cream bg, no dark pill ── */
        [data-testid="stBottomBlock"],
        [data-testid="stBottom"],
        [data-testid="stBottom"] > div,
        [data-testid="stBottomBlock"] > div,
        [data-testid="stChatInputContainer"],
        [data-testid="stChatInputContainer"] > div {
            background-color: #F7F5F2 !important;
            background: #F7F5F2 !important;
            border: none !important;
            box-shadow: none !important;
            border-radius: 0 !important;
        }

        /* ── Chat input outer shell ── */
        [data-testid="stChatInput"] {
            background: #F7F5F2 !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0.5rem 0 1rem !important;
        }

        /* ── The actual textarea pill ── */
        [data-testid="stChatInput"] textarea,
        [data-testid="stChatInput"] textarea:focus,
        [data-testid="stChatInput"] textarea:active {
            background: #E8E5DE !important;
            color: #1E1E1E !important;
            border: 1px solid var(--border) !important;
            border-radius: 12px !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.88rem !important;
        }
        [data-testid="stChatInput"] textarea::placeholder {
            color: #5A5450 !important;
            opacity: 1 !important;
        }
        [data-testid="stChatInput"] textarea:focus {
            border-color: var(--accent-soft) !important;
            box-shadow: 0 0 0 2px rgba(139,111,71,0.2) !important;
            outline: none !important;
        }
        [data-testid="stChatInputContainer"]:focus-within {
            box-shadow: 0 0 0 2px var(--accent-soft) !important;
            outline: none !important;
        }
        }
        [data-testid="stChatInput"] button {
            background: var(--accent) !important;
            border-radius: 8px !important;
        }

        /* ── Spinner ── */
        .stSpinner > div { border-color: var(--accent) transparent transparent !important; }

        /* ── Error Box ── */
        .error-box {
            background: #FEE2E2;
            border: 1px solid #FECACA;
            border-radius: 8px;
            padding: 0.8rem 1rem;
            font-size: 0.82rem;
            color: #991B1B;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════
#  SECTION 2 — HINDSIGHT MEMORY ENGINE
# ══════════════════════════════════════════════════════════

@st.cache_resource(show_spinner=False)
def init_hindsight() -> bool:
    """
    Returns True if HINDSIGHT_API_KEY is configured.
    No client is created here — each call site creates its own
    local client inside asyncio.run() to avoid the asyncio.timeout()
    'must be inside a Task' error that occurs with cached/shared clients.
    """
    return bool(HINDSIGHT_API_KEY)


def _make_client():
    """Create a fresh Hindsight client. Called locally in each SDK call."""
    from hindsight_client import Hindsight  # type: ignore
    return Hindsight(base_url=HINDSIGHT_BASE_URL, api_key=HINDSIGHT_API_KEY)


def recall_team_memory(query: str) -> str:
    """
    Recall relevant memories from Hindsight.
    All exceptions (including RuntimeError for event-loop conflicts) are
    silently swallowed — memory is a best-effort enhancement, never a blocker.
    """
    if not HINDSIGHT_API_KEY:
        return ""
    try:
        async def _recall():
            client = _make_client()
            try:
                result = client.recall(bank_id=HINDSIGHT_BANK, query=query)
                if asyncio.iscoroutine(result):
                    result = await result
                return result
            finally:
                if hasattr(client, 'aclose'):
                    await client.aclose()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(_recall())
        finally:
            loop.close()

        if isinstance(result, list) and result:
            memories = []
            for item in result:
                if isinstance(item, dict):
                    content = item.get("content", "") or item.get("text", "")
                elif isinstance(item, str):
                    content = item
                else:
                    content = str(item)
                if content.strip():
                    memories.append(f"• {content.strip()}")
            return "\n".join(memories)

        if isinstance(result, str):
            return result.strip()

        return ""
    except Exception:        # silent fallback — never show a warning to the user
        return ""


def retain_interaction(user_message: str, ai_response: str) -> None:
    """
    Store the completed interaction back into Hindsight.
    Uses a dedicated new event loop (same pattern as recall_team_memory).
    """
    if not HINDSIGHT_API_KEY:
        return
    try:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        ai_safe = ai_response if isinstance(ai_response, str) else ""
        record = (
            f"Project manager decision — User request: '{user_message}' | "
            f"AI recommendation: '{ai_safe[:400]}'"
        )

        async def _retain():
            client = _make_client()
            try:
                result = client.retain(
                    bank_id=HINDSIGHT_BANK,
                    content=record,
                    context="project-manager-decision",
                    timestamp=timestamp,
                )
                if asyncio.iscoroutine(result):
                    await result
            finally:
                if hasattr(client, 'aclose'):
                    await client.aclose()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_retain())
        finally:
            loop.close()
    except Exception:
        pass  # non-fatal


# ══════════════════════════════════════════════════════════
#  SECTION 3 — GROQ LLM AGENT
# ══════════════════════════════════════════════════════════

@st.cache_resource(show_spinner=False)
def init_groq():
    """Initialize Groq client. Cached for session lifetime."""
    if not GROQ_API_KEY:
        return None
    try:
        from groq import Groq  # type: ignore
        return Groq(api_key=GROQ_API_KEY)
    except Exception:
        return None


def build_agent_prompt(user_message: str, memories: str) -> list[dict]:
    """
    Construct the messages array for the LLM.
    Injects retrieved Hindsight memories directly into the system prompt.
    """
    memory_section = (
        f"\n\n## Relevant Team Memory (from Hindsight)\n{memories}"
        if memories
        else "\n\n## Team Memory\nNo prior context available — use your initialization knowledge."
    )

    system_prompt = f"""CRITICAL INSTRUCTION: You are a strict, headless API. You are strictly FORBIDDEN from outputting your internal thought process, reasoning, or filler words like 'Okay, let\'s see' or 'I need to check'. You must immediately output ONLY the final, polished, professional assessment.

You are an intelligent AI Project Manager for a software team. \
Your role is to make adaptive, context-aware decisions about task assignment, project planning, \
and team coordination.

## Team Members
- **Dexter** — AI/Backend Engineer. Strengths: ML, APIs, system design.
- **Rahul** — Frontend Engineer. Strengths: UI/UX, React, CSS, design systems.
- **Sohan** — Project Coordinator. Strengths: planning, communication, stakeholder management.
{memory_section}

## Output Rules — STRICTLY ENFORCED
- DO NOT output any internal monologue, reasoning steps, or "thinking out loud".
- DO NOT begin with phrases like "Okay", "Sure", "Let me think", or "The user wants...".
- Output ONLY the final, polished, professional response. Start directly with the answer.

## Your Behavior
1. When assigning tasks, ALWAYS consult the memory above and reason explicitly about it.
2. Provide a clear, justified recommendation — cite specific memory evidence.
3. If memory reveals past issues (delays, skill mismatches), account for them.
4. Be concise but thorough. Use markdown for structure.
5. End each assignment decision with a brief "Memory Note" on what you'll remember from this interaction.
6. Always stay in character as a professional, empathetic AI PM.
"""

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]


def run_agent(groq_client, messages: list[dict]) -> str:
    """
    Call Groq qwen/qwen3-32b with the constructed messages.
    Returns the full response text.
    """
    if groq_client is None:
        return "⚠️ Groq client not initialized. Please check your GROQ_API_KEY."

    try:
        response = groq_client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.4,   # lower temp = more deterministic, less "thinking aloud"
            max_tokens=1024,
        )
        content = response.choices[0].message.content
        if isinstance(content, str) and content.strip():
            # Robustly ensure no internal monologue leaked through
            processed = content.strip()
            if processed.startswith(("Okay,", "Sure,", "Let me think", "I need to check")):
                 # If monologue is detected, try to find the actual response
                 if "\n\n" in processed:
                     processed = processed.split("\n\n", 1)[-1].strip()
            return processed
        return "No response generated."
    except Exception as exc:
        err = str(exc)
        if "model" in err.lower() and ("not found" in err.lower() or "404" in err.lower()):
            # Fallback to secondary model
            try:
                response = groq_client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=messages,
                    temperature=0.65,
                    max_tokens=1024,
                )
                return response.choices[0].message.content or "No response generated."
            except Exception:
                pass
        return f"⚠️ LLM error: {err}"


# ══════════════════════════════════════════════════════════
#  SECTION 4 — SIDEBAR TASK DASHBOARD
# ══════════════════════════════════════════════════════════

TEAM_DATA = [
    {
        "name": "Dexter",
        "role": "AI / Backend Engineer",
        "avatar": "🤖",
        "task": "Model fine-tuning pipeline",
        "status": "progress",
        "progress": 65,
    },
    {
        "name": "Rahul",
        "role": "Frontend Engineer",
        "avatar": "🎨",
        "task": "Dashboard redesign sprint",
        "status": "pending",
        "progress": 20,
    },
    {
        "name": "Sohan",
        "role": "Project Coordinator",
        "avatar": "📋",
        "task": "Sprint retrospective & planning",
        "status": "done",
        "progress": 100,
    },
]

STATUS_LABELS = {
    "pending":  ("Pending",     "badge-pending"),
    "progress": ("In Progress", "badge-progress"),
    "done":     ("Done",        "badge-done"),
}


def render_sidebar(hindsight_ready: bool) -> None:
    """Render the styled sidebar with team cards and memory status."""
    with st.sidebar:
        # Header
        st.markdown(
            """
            <div class="sidebar-header">⚡ Project Manager</div>
            <div class="sidebar-subtitle">Hindsight-Powered</div>
            """,
            unsafe_allow_html=True,
        )

        # Team Members
        st.markdown(
            '<div class="sidebar-section-label">👥 Team</div>',
            unsafe_allow_html=True,
        )

        for member in TEAM_DATA:
            # Type-safe status lookup
            raw_status = member.get("status", "Pending")
            status_key = str(raw_status) if isinstance(raw_status, (str, int)) else "Pending"
            label, badge_class = STATUS_LABELS.get(status_key, ("Pending", "badge-pending"))
            
            # Type-safe field retrieval
            raw_name = member.get("name", "Unknown")
            name = str(raw_name) if isinstance(raw_name, (str, int)) else "Unknown"
            
            raw_avatar = member.get("avatar")
            avatar = str(raw_avatar) if isinstance(raw_avatar, str) and raw_avatar else name[0]
            
            raw_role = member.get("role", "Team Member")
            role = str(raw_role) if isinstance(raw_role, (str, int)) else "Team Member"
            
            raw_task = member.get("task", "No active task")
            task = str(raw_task) if isinstance(raw_task, (str, int)) else "No active task"
            
            raw_progress = member.get("progress", 0)
            progress = int(raw_progress) if isinstance(raw_progress, (int, float, str)) and str(raw_progress).isdigit() else 0

            st.markdown(
                f"""
                <div class="member-card">
                    <div class="member-name">{avatar} {name}</div>
                    <div class="member-role">{role}</div>
                    <div class="member-task">📌 {task}</div>
                    <span class="badge {badge_class}">{label}</span>
                    <div class="progress-wrap">
                        <div class="progress-fill" style="width:{progress}%"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Sprint Stats
        st.markdown(
            '<div class="sidebar-section-label">📊 Sprint Stats</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="member-card" style="font-size:0.8rem; line-height:1.8;">
                <div>🗓️ <b>Sprint 7</b> — Week 2 of 2</div>
                <div>✅ Tasks completed: <b>4 / 7</b></div>
                <div>⏱️ Avg velocity: <b>91%</b></div>
                <div>🔥 Blockers: <b>1</b></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Hindsight Memory Status
        dot_class = "dot-on" if hindsight_ready else "dot-off"
        status_text = "Hindsight Memory: Active" if hindsight_ready else "Hindsight Memory: Offline"
        extra = "" if hindsight_ready else "<br>Set HINDSIGHT_API_KEY to enable."

        st.markdown(
            f"""
            <div class="memory-status">
                <span class="memory-dot {dot_class}"></span>
                {status_text}{extra}
                <br><span style="margin-left:12px">Bank: <code>{HINDSIGHT_BANK}</code></span>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════
#  SECTION 5 — CHAT UI
# ══════════════════════════════════════════════════════════

def render_welcome() -> None:
    """Display the welcome banner when no messages exist."""
    st.markdown(
        """
        <div class="welcome-banner">
            <div class="welcome-icon">🧠</div>
            <div class="welcome-title">What can I help you decide today?</div>
            <div class="welcome-text">
                I'm your AI Project Manager with persistent team memory.<br>
                Ask me to assign tasks, review progress, resolve blockers,<br>
                or reason about who should own what — and why.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    # Suggestion pills
    cols = st.columns(3)
    suggestions = [
        "Assign the login UI to the best person",
        "Who should own the API integration?",
        "Review Dexter's current workload",
    ]
    for col, text in zip(cols, suggestions):
        with col:
            if st.button(text, key=f"suggest_{text[:20]}", use_container_width=True):
                st.session_state.setdefault("pending_input", text)
                st.rerun()


def render_messages(messages: list[dict]) -> None:
    """Render the full chat history with styled bubbles."""
    for msg in messages:
        role    = msg["role"]
        content = msg["content"]
        ts      = msg.get("timestamp", "")
        recall  = msg.get("recall_snippet", "")

        if role == "user":
            st.markdown(
                f"""
                <div class="msg-wrapper msg-user">
                    <div class="msg-label">You</div>
                    <div class="msg-bubble">{content}</div>
                    <div class="msg-time">{ts}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            recall_html = ""
            if recall:
                recall_html = f'<div class="recall-callout">💡 Memory recalled: {recall}</div>'

            # Render AI markdown properly via st.markdown inside a container
            st.markdown(
                f"""
                <div class="msg-wrapper msg-ai">
                    <div class="msg-label">AI Project Manager</div>
                    {recall_html}
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div style="
                    background: var(--ai-bubble);
                    border: 1px solid var(--border);
                    border-radius: 14px;
                    border-bottom-left-radius: 4px;
                    padding: 0.85rem 1.1rem;
                    max-width: 82%;
                    font-size: 0.9rem;
                    line-height: 1.65;
                    color: var(--text-primary);
                    margin-bottom: 0.2rem;
                ">
                {content}
                </div>
                <div class="msg-time" style="margin-bottom:0.5rem">{ts}</div>
                """,
                unsafe_allow_html=True,
            )


# ══════════════════════════════════════════════════════════
#  SECTION 6 — HINDSIGHT LEARNING LOOP
# ══════════════════════════════════════════════════════════

def run_hindsight_loop(
    user_message: str,
    groq_client,
) -> tuple[str, str]:
    """
    The core Hindsight Learning Loop:

    1. Recall  — Query Hindsight for relevant team history
    2. Inject  — Embed memories into the LLM system prompt
    3. Decide  — Run Groq LLM with memory-enriched context
    4. Respond — Return AI response + memory snippet
    5. Retain  — Store this interaction back into Hindsight

    Returns (ai_response, recall_snippet)
    """

    # ── Step 1: Recall ────────────────────────────────────
    recall_query = f"team member performance and task history relevant to: {user_message}"
    memories     = recall_team_memory(recall_query)   # creates its own local client

    # Create a short snippet for the UI callout
    if memories:
        lines   = [ln for ln in memories.split("\n") if ln.strip()]
        snippet = lines[0].lstrip("• ").strip() if lines else ""
        snippet = snippet[:90] + "…" if len(snippet) > 90 else snippet
    else:
        snippet = ""

    # ── Step 2 & 3: Inject + Decide ──────────────────────
    messages     = build_agent_prompt(user_message, memories)
    ai_response  = run_agent(groq_client, messages)

    # ── Step 4: Retain ────────────────────────────────────
    retain_interaction(user_message, ai_response)    # creates its own local client

    return ai_response, snippet


# ══════════════════════════════════════════════════════════
#  SECTION 7 — MAIN APPLICATION
# ══════════════════════════════════════════════════════════

def main() -> None:
    # ── Page Config ───────────────────────────────────────
    st.set_page_config(
        page_title="AI Project Manager · Hindsight",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    inject_css()

    # ── Initialise clients ────────────────────────────────
    groq_client     = init_groq()
    hindsight_ready = init_hindsight()   # True if API key present; no client cached

    # ── Initialise session state ──────────────────────────
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # ── Sidebar ───────────────────────────────────────────
    render_sidebar(hindsight_ready)

    # ── Title Bar ─────────────────────────────────────────
    st.markdown(
        """
        <div class="app-title-bar">
            <div class="app-title">AI Group Project Manager</div>
            <div class="app-tagline">
                Memory-powered decisions · Groq qwen3-32b · Hindsight memory engine
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── API Key Warnings ──────────────────────────────────
    if not GROQ_API_KEY:
        st.markdown(
            """
            <div class="error-box">
                ⚠️ <b>GROQ_API_KEY not set.</b> Copy <code>.env.example</code> to <code>.env</code>
                and fill in your Groq API key from <a href="https://console.groq.com" target="_blank">console.groq.com</a>.
            </div>
            """,
            unsafe_allow_html=True,
        )

    if "hindsight_error" in st.session_state:
        st.markdown(
            f"""
            <div class="error-box" style="background:#FFF7ED; border-color:#FED7AA; color:#92400E; margin-top:0.5rem">
                ℹ️ <b>Hindsight memory offline.</b> {st.session_state['hindsight_error']}
                The app runs normally — responses will use only the built-in team context.
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Chat Area ─────────────────────────────────────────
    chat_placeholder = st.container()
    with chat_placeholder:
        if not st.session_state.messages:
            render_welcome()
        else:
            render_messages(st.session_state.messages)

    # ── Handle suggestion button presses ─────────────────
    if "pending_input" in st.session_state:
        pending = st.session_state.pop("pending_input")
        _process_user_message(pending, groq_client)
        st.rerun()

    # ── Chat Input ────────────────────────────────────────
    user_input = st.chat_input(
        "Ask me to assign a task, review progress, or make a decision…",
        key="chat_input",
    )

    if user_input and user_input.strip():
        _process_user_message(user_input.strip(), groq_client)
        st.rerun()


def _process_user_message(
    user_message: str,
    groq_client,
) -> None:
    """
    Process a new user message:
    1. Append user message to history
    2. Run the Hindsight Learning Loop
    3. Append AI response to history
    """
    timestamp = datetime.now().strftime("%H:%M")

    # Append user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_message,
        "timestamp": timestamp,
    })

    # Run with animated status indicator
    with st.status("🧠 Consulting team memory…", expanded=True) as status:
        st.write("Recalling relevant history from Hindsight...")
        ai_response, recall_snippet = run_hindsight_loop(
            user_message,
            groq_client,
        )
        status.update(label="✅ Response ready", state="complete", expanded=False)

    # Append AI response
    st.session_state.messages.append({
        "role": "assistant",
        "content": ai_response,
        "timestamp": timestamp,
        "recall_snippet": recall_snippet,
    })


# ── Entry Point ───────────────────────────────────────────
if __name__ == "__main__":
    main()
