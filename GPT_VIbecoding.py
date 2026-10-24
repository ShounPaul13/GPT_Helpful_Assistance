import json
import os
import time
import uuid
from dotenv import find_dotenv, load_dotenv
import streamlit as st

# LangChain & Tavily Imports
from langchain_community.tools import TavilySearchResults
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

# Load local environment variables if available
load_dotenv(find_dotenv(), override=True)

# -----------------------------------------------------------------------------
# HARDCODED TAVILY API KEY (No user prompt required)
# -----------------------------------------------------------------------------
DEFAULT_TAVILY_KEY = "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"

# -----------------------------------------------------------------------------
# 1. PAGE & LIGHT GLASSMORPHISM STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="NEXUS AI // INTELLIGENT WORKSPACE",
    page_icon="✨",
    layout="wide"
)

LIGHT_GLASS_CSS = """
<style>
/* Continuous Animated Mesh Gradient Background */
@keyframes gradientAnimation {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.stApp {
    background: linear-gradient(-45deg, #38bdf8, #818cf8, #c084fc, #e0f2fe, #f472b6, #38bdf8);
    background-size: 400% 400%;
    animation: gradientAnimation 14s ease infinite;
    color: #0f172a;
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

/* Glassmorphism Cards */
.glass-card {
    background: rgba(255, 255, 255, 0.45) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(255, 255, 255, 0.75) !important;
    border-radius: 20px !important;
    padding: 2rem !important;
    box-shadow: 0 12px 40px rgba(31, 38, 135, 0.12) !important;
}

/* Hero Titles */
.hero-title {
    font-size: 3.5rem;
    font-weight: 900;
    text-align: center;
    color: #1e1b4b;
    letter-spacing: -1.5px;
    margin-bottom: 0.2rem;
    text-shadow: 0 4px 20px rgba(255, 255, 255, 0.6);
}

.hero-subtitle {
    text-align: center;
    color: #334155;
    font-size: 1.25rem;
    font-weight: 500;
    margin-bottom: 2rem;
}

/* Empty State Chat Greeting Hero */
.chat-welcome-title {
    font-size: 2.8rem;
    font-weight: 800;
    text-align: center;
    color: #1e1b4b;
    margin-top: 2rem;
    margin-bottom: 0.3rem;
    text-shadow: 0 2px 10px rgba(255, 255, 255, 0.5);
}

.chat-welcome-sub {
    font-size: 1.15rem;
    text-align: center;
    color: #475569;
    margin-bottom: 2.5rem;
}

/* Feature Grid Cards */
.feature-card {
    background: rgba(255, 255, 255, 0.5) !important;
    backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(255, 255, 255, 0.8) !important;
    border-radius: 18px !important;
    padding: 1.8rem 1.2rem !important;
    text-align: center !important;
    transition: transform 0.3s ease, box-shadow 0.3s ease !important;
    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.08) !important;
}

.feature-card:hover {
    transform: translateY(-6px);
    background: rgba(255, 255, 255, 0.7) !important;
    box-shadow: 0 12px 40px rgba(31, 38, 135, 0.18) !important;
}

.feature-icon { font-size: 2.4rem; margin-bottom: 0.6rem; }
.feature-title { color: #1e1b4b; font-weight: 800; font-size: 1.15rem; margin-bottom: 0.4rem; }
.feature-desc { color: #475569; font-size: 0.9rem; line-height: 1.4; }

/* Glass Sidebar */
[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.3) !important;
    backdrop-filter: blur(25px) !important;
    -webkit-backdrop-filter: blur(25px) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.6) !important;
}

/* Readability Font Colors */
h1, h2, h3, h4, h5, h6, p, span, label, div {
    color: #0f172a !important;
}

/* Custom Message Bubbles */
[data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.55) !important;
    backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(255, 255, 255, 0.8) !important;
    border-radius: 16px !important;
    padding: 1rem 1.2rem !important;
    margin-bottom: 1rem !important;
    box-shadow: 0 6px 20px rgba(31, 38, 135, 0.06) !important;
}

/* Input Fields */
div[data-baseweb="input"], div[data-baseweb="base-input"], textarea {
    background: rgba(255, 255, 255, 0.6) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255, 255, 255, 0.9) !important;
}

input, textarea {
    color: #0f172a !important;
    font-weight: 500 !important;
}

/* Hide Default Streamlit Headers/Footers */
footer, header, [data-testid="stHeader"], [data-testid="stFooter"] {
    display: none !important;
    visibility: hidden !important;
}

/* Seamless Floating Input Styling for Chat Workspace */
[data-testid="stBottom"], 
[data-testid="stBottom"] > div,
.stBottom, 
.stBottom > div,
[data-testid="stChatInput"],
.stChatInputContainer {
    background: transparent !important;
    background-color: transparent !important;
    box-shadow: none !important;
    border: none !important;
}

.main .block-container {
    padding-bottom: 100px !important;
}

[data-testid="stChatInput"] {
    padding-bottom: 20px !important;
}

[data-testid="stChatInput"] > div {
    background: rgba(255, 255, 255, 0.65) !important;
    backdrop-filter: blur(25px) !important;
    -webkit-backdrop-filter: blur(25px) !important;
    border: 1.5px solid rgba(255, 255, 255, 0.9) !important;
    border-radius: 28px !important;
    box-shadow: 0 10px 35px rgba(31, 38, 135, 0.15) !important;
}

[data-testid="stChatInput"] textarea {
    color: #0f172a !important;
    background: transparent !important;
}

/* Buttons */
.stButton > button {
    border-radius: 12px !important;
    border: 1px solid rgba(255, 255, 255, 0.8) !important;
    background: rgba(255, 255, 255, 0.5) !important;
    color: #1e1b4b !important;
    font-weight: 600 !important;
    backdrop-filter: blur(10px) !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    background: rgba(255, 255, 255, 0.8) !important;
    box-shadow: 0 4px 15px rgba(255, 255, 255, 0.5) !important;
}

/* Manual Instruction Card */
.instruction-card {
    background: rgba(255, 255, 255, 0.85);
    border-left: 5px solid #ef4444;
    padding: 1.2rem;
    border-radius: 10px;
    margin-top: 1rem;
}
</style>
"""
st.markdown(LIGHT_GLASS_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. LOCAL PERSISTENCE UTILITIES
# -----------------------------------------------------------------------------
STORAGE_FILE = "chat_history.json"

def load_chats_from_file():
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_chats_to_file(data):
    filtered_data = {
        tid: tdata for tid, tdata in data.items()
        if len(tdata.get("messages", [])) > 0
    }
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=2)

def serialize_messages(messages):
    serialized = []
    for msg in messages:
        if isinstance(msg, SystemMessage):
            serialized.append({"type": "system", "content": msg.content})
        elif isinstance(msg, HumanMessage):
            serialized.append({"type": "human", "content": msg.content})
        elif isinstance(msg, AIMessage):
            serialized.append({"type": "ai", "content": msg.content})
    return serialized

def deserialize_messages(message_dicts):
    deserialized = []
    for msg in message_dicts:
        if msg["type"] == "system":
            deserialized.append(SystemMessage(content=msg["content"]))
        elif msg["type"] == "human":
            deserialized.append(HumanMessage(content=msg["content"]))
        elif msg["type"] == "ai":
            deserialized.append(AIMessage(content=msg["content"]))
    return deserialized

def create_new_thread():
    new_id = str(uuid.uuid4())[:8]
    st.session_state.saved_threads[new_id] = {
        "title": "New Chat",
        "custom_system_role": "",
        "last_updated": time.time(),
        "messages": []
    }
    st.session_state.current_thread_id = new_id
    return new_id

# -----------------------------------------------------------------------------
# 3. SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = ""

if "saved_threads" not in st.session_state:
    st.session_state.saved_threads = load_chats_from_file()

if "current_thread_id" not in st.session_state:
    st.session_state.current_thread_id = None

if "editing_idx" not in st.session_state:
    st.session_state.editing_idx = None

if not st.session_state.saved_threads or st.session_state.current_thread_id is None:
    create_new_thread()

# -----------------------------------------------------------------------------
# 4. STAGE 1: WELCOME LANDING PAGE & KEY VALIDATION
# -----------------------------------------------------------------------------
if not st.session_state.authenticated:
    st.markdown("""
        <style>
            [data-testid="stBottom"], .stBottom, [data-testid="stChatInput"] {
                display: none !important;
                visibility: hidden !important;
                height: 0px !important;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="hero-title">NEXUS AI // WORKSPACE</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Next-Generation Intelligent Assistant with Real-Time Web Cognition</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🌐</div>
            <div class="feature-title">Live Web Intelligence</div>
            <div class="feature-desc">Fetches real-world data and online research dynamically via Tavily API.</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <div class="feature-title">Real-Time Streaming</div>
            <div class="feature-desc">Instant token generation with low-latency streaming output.</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔒</div>
            <div class="feature-title">Private Execution</div>
            <div class="feature-desc">Client-side API authentication ensures zero data sharing or tracking.</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Adaptive Context</div>
            <div class="feature-desc">Configure specialized system personas per conversation workspace.</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🔑 Activate Workspace Access")
        
        with st.form(key="key_form", clear_on_submit=False):
            input_key = st.text_input(
                "Enter OpenAI API Key:",
                type="password",
                placeholder="sk-...",
                help="Press Enter or click Launch to authenticate."
            )
            submit_btn = st.form_submit_button("Launch Assistant Workspace ✨", use_container_width=True)

        if submit_btn:
            if input_key.startswith("sk-") and len(input_key.strip()) > 20:
                try:
                    with st.spinner("Validating API Key credentials..."):
                        test_llm = ChatOpenAI(model_name="gpt-4o-mini", api_key=input_key.strip(), max_tokens=5)
                        test_llm.invoke("test")
                    
                    st.session_state.openai_api_key = input_key.strip()
                    st.session_state.authenticated = True
                    create_new_thread()
                    
                    st.toast("🎉 API Key Authenticated Successfully!")
                    st.success("✨ Welcome to Nexus AI workspace!\n\n> *\"AI is not about replacing human intelligence, but amplifying human potential.\"*")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.markdown("""
                    <div class="instruction-card">
                        <h4 style="color: #dc2626 !important; margin-top:0;">❌ Invalid API Key Provided</h4>
                        <p style="color: #475569 !important;">The API key you entered was rejected by OpenAI. Please verify and provide a valid key.</p>
                        <hr style="border-top: 1px solid rgba(0,0,0,0.1);">
                        <h5 style="color: #1e1b4b !important;">📖 How to get an OpenAI API Key:</h5>
                        <ol style="color: #334155 !important; padding-left: 1.2rem;">
                            <li>Go to the official <a href="https://platform.openai.com/api-keys" target="_blank" style="color:#2563eb; font-weight:bold;">OpenAI API Keys Portal</a>.</li>
                            <li>Sign in or create an OpenAI account.</li>
                            <li>Click on <b>"Create new secret key"</b>.</li>
                            <li>Copy the generated key and paste it above.</li>
                        </ol>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Invalid Format: API Key must start with 'sk-' and be at least 20 characters long.")
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. STAGE 2: CHAT WORKSPACE
# -----------------------------------------------------------------------------
else:
    current_thread = st.session_state.saved_threads.get(
        st.session_state.current_thread_id, 
        st.session_state.saved_threads[list(st.session_state.saved_threads.keys())[0]]
    )

    # Glass Sidebar
    with st.sidebar:
        st.title("✨ Control Center")

        st.caption("ASSISTANT CONFIGURATION")
        enable_search = st.toggle("🌐 Enable Web Search", value=False)

        user_system_input = st.text_input(
            "System Role:",
            value=current_thread.get("custom_system_role", ""),
            placeholder="Enter custom prompt (Optional)...",
            help="If left empty, defaults to 'You are a helpful assistant.' automatically."
        )
        current_thread["custom_system_role"] = user_system_input

        st.divider()

        st.subheader("💬 Active Threads")

        search_query = st.text_input("🔍 Search Chats", placeholder="Type keyword...").lower()

        if st.button("+ New Chat", use_container_width=True):
            create_new_thread()
            st.rerun()

        non_empty_threads = {
            tid: tdata for tid, tdata in st.session_state.saved_threads.items()
            if len(tdata.get("messages", [])) > 0 or tid == st.session_state.current_thread_id
        }

        sorted_threads = sorted(
            non_empty_threads.items(),
            key=lambda item: item[1].get("last_updated", 0),
            reverse=True
        )

        filtered_threads = [
            (tid, tdata) for tid, tdata in sorted_threads
            if search_query in tdata["title"].lower() or any(
                search_query in msg.get("content", "").lower() for msg in tdata.get("messages", [])
            )
        ]

        for thread_id, thread_data in filtered_threads:
            if len(thread_data.get("messages", [])) == 0 and thread_id != st.session_state.current_thread_id:
                continue

            col_select, col_del = st.columns([4, 1])
            with col_select:
                label = f"{'▶ ' if thread_id == st.session_state.current_thread_id else ''}{thread_data['title']}"
                if st.button(label, key=f"btn_{thread_id}", use_container_width=True):
                    st.session_state.current_thread_id = thread_id
                    st.rerun()
            with col_del:
                if st.button("🗑️", key=f"del_{thread_id}"):
                    if len(st.session_state.saved_threads) > 1:
                        del st.session_state.saved_threads[thread_id]
                        if st.session_state.current_thread_id == thread_id:
                            st.session_state.current_thread_id = list(st.session_state.saved_threads.keys())[0]
                        save_chats_to_file(st.session_state.saved_threads)
                        st.rerun()

        st.divider()

        if st.button("🔴 Logout / Reset Key", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.openai_api_key = ""
            st.rerun()

    raw_messages = current_thread.get("messages", [])
    active_messages = deserialize_messages(raw_messages)

    prompt_to_send = None

    # EMPTY CHAT STATE: Hero Landing Screen
    if len(active_messages) == 0:
        st.markdown('<div class="chat-welcome-title">What can I help with today?</div>', unsafe_allow_html=True)
        st.markdown('<div class="chat-welcome-sub">Ask a question, research live data, or brainstorm ideas below.</div>', unsafe_allow_html=True)

        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            if st.button("💡 Brainstorm creative project ideas", use_container_width=True):
                prompt_to_send = "Brainstorm 5 innovative tech project ideas."
        with sc2:
            if st.button("🌐 Research latest global developments", use_container_width=True):
                prompt_to_send = "What are the latest breakthroughs in AI technology?"
        with sc3:
            if st.button("📝 Help draft a professional summary", use_container_width=True):
                prompt_to_send = "Help me draft a concise professional bio for LinkedIn."

    # ACTIVE CHAT TRANSCRIPT WITH GEMINI-STYLE MODIFY OPTION
    else:
        st.subheader(f"Workspace // {current_thread['title']}")
        for idx, msg in enumerate(active_messages):
            if isinstance(msg, HumanMessage):
                col_msg, col_edit = st.columns([10, 1])
                with col_msg:
                    with st.chat_message("human"):
                        if st.session_state.editing_idx == idx:
                            edited_text = st.text_area("Modify your prompt:", value=msg.content, key=f"edit_field_{idx}")
                            c_save, c_cancel = st.columns([1, 1])
                            with c_save:
                                if st.button("Submit Modification ✨", key=f"save_edit_{idx}"):
                                    prompt_to_send = edited_text
                                    active_messages = active_messages[:idx]
                                    st.session_state.editing_idx = None
                            with c_cancel:
                                if st.button("Cancel", key=f"cancel_edit_{idx}"):
                                    st.session_state.editing_idx = None
                                    st.rerun()
                        else:
                            st.write(msg.content)
                with col_edit:
                    if st.session_state.editing_idx != idx:
                        if st.button("✏️ Modify", key=f"modify_{idx}", help="Modify this prompt"):
                            st.session_state.editing_idx = idx
                            st.rerun()

            elif isinstance(msg, AIMessage):
                with st.chat_message("ai"):
                    st.write(msg.content)

    user_input = st.chat_input("Ask anything...")
    if user_input:
        prompt_to_send = user_input

    # Execute LLM Generation with Feedback Spinner
    if prompt_to_send:
        with st.chat_message("human"):
            st.write(prompt_to_send)

        effective_system_role = (
            user_system_input.strip() 
            if user_system_input and user_system_input.strip() 
            else "You are a helpful assistant."
        )

        messages_to_send = [SystemMessage(content=effective_system_role)]
        messages_to_send.extend(active_messages)
        messages_to_send.append(HumanMessage(content=prompt_to_send))

        with st.chat_message("ai"):
            try:
                with st.spinner("⚡ Processing your request with Nexus Engine..."):
                    if enable_search:
                        try:
                            # Using predefined Tavily API Key directly
                            tavily_tool = TavilySearchResults(
                                max_results=3, 
                                tavily_api_key=DEFAULT_TAVILY_KEY
                            )
                            search_results = tavily_tool.run(prompt_to_send)
                            search_context = f"\n\n[Real-Time Internet Search Results]:\n{search_results}"
                            messages_to_send[0] = SystemMessage(
                                content=effective_system_role + search_context
                            )
                        except Exception as search_err:
                            st.warning(f"Web Search Notice: Could not retrieve web results ({search_err}). Proceeding with direct knowledge.")

                    llm = ChatOpenAI(
                        model_name="gpt-4o",
                        temperature=0.5,
                        api_key=st.session_state.openai_api_key,
                        streaming=True
                    )

                def stream_response():
                    for chunk in llm.stream(messages_to_send):
                        yield chunk.content

                full_response = st.write_stream(stream_response())

                active_messages.append(HumanMessage(content=prompt_to_send))
                active_messages.append(AIMessage(content=full_response))

                current_thread["title"] = prompt_to_send[:22] + "..." if len(prompt_to_send) > 22 else prompt_to_send
                current_thread["messages"] = serialize_messages(active_messages)
                current_thread["last_updated"] = time.time()
                
                save_chats_to_file(st.session_state.saved_threads)

                st.rerun()

            except Exception as e:
                st.error(f"Execution Error: {e}")
