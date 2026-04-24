import streamlit as st
import google.generativeai as ggai

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 800px; 
        }
        
        div.stButton button {
            border-radius: 20px;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# API key
try:
    key1 = st.secrets["GEMINI_API_KEY_1"]
    key2 = st.secrets["GEMINI_API_KEY_2"]
    api_keys = [key1, key2]
except:
    st.error("error, set up secrets.toml")
    st.stop()

# key right now
if 'key_index' not in st.session_state:
    st.session_state.key_index = 0

ggai.configure(api_key=api_keys[st.session_state.key_index])

# role of AI
companion_prompt = """
You are a gentle and supportive "Body Doubling" companion for a user with ADHD. 
When the user tells you a task they are avoiding, please follow these rules:
1. Validate their feelings. Talk like a supportive friend who is sitting next to them. Do not sound like a strict teacher or a robot.
2. Break it down and suggest exactly one small, 2-minute micro-task.
3. Keep it short (2-3 sentences).
"""

model = ggai.GenerativeModel('gemini-2.5-flash', system_instruction=companion_prompt)


# initialization
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'big_goal' not in st.session_state:
    st.session_state.big_goal = ""
if 'micro_task' not in st.session_state:
    st.session_state.micro_task = ""
if 'is_focusing' not in st.session_state:
    st.session_state.is_focusing = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])


def goto_page(page_num):
    st.session_state.step = page_num


# p0：choose your mood
if st.session_state.step == 0:
    st.write("")
    st.markdown("<h2 style='text-align: center;'>How is your brain feeling today? 🥰</h2>", unsafe_allow_html=True)
    st.write("")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔋 Ready to go", use_container_width=True):
            st.session_state.messages = [
                {"role": "ai", "content": "Awesome energy! 🚀 What big task are we tackling today?"}]
            goto_page(1)
            st.rerun()
    with col2:
        if st.button("😕 A bit tired", use_container_width=True):
            st.session_state.messages = [
                {"role": "ai", "content": "I hear you. 🫂 Let's do something extremely easy. What's on your mind?"}]
            goto_page(1)
            st.rerun()
    with col3:
        if st.button("🪫 Overwhelmed", use_container_width=True):
            st.session_state.messages = [
                {"role": "ai", "content": "Take a deep breath. 🌬️ Tell me the scariest task, I'll slice it tiny for you."}]
            goto_page(1)
            st.rerun()


# p1：break down your task
elif st.session_state.step == 1:
    st.title("🌱 Warm-up Chat")


    for msg in st.session_state.messages:
        if msg["role"] == "ai":
            with st.chat_message("assistant"):
                st.write(msg["content"])
        else:
            with st.chat_message("user"):
                st.write(msg["content"])

    user_input = st.chat_input("Type your task here...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.chat.send_message(user_input)
                    ai_answer = response.text
                except:
                    # api Key limited
                    if st.session_state.key_index == 0:
                        st.session_state.key_index = 1
                        ggai.configure(api_key=api_keys[1])
                        st.session_state.chat = model.start_chat(history=[])

                        try:
                            response = st.session_state.chat.send_message(user_input)
                            ai_answer = response.text
                        except:
                            ai_answer = "That sounds overwhelming, let's just start tiny! (Default)"
                    else:
                        ai_answer = "That sounds overwhelming, let's just start tiny! (Default)"

                st.write(ai_answer)

        st.session_state.messages.append({"role": "ai", "content": ai_answer})
        st.rerun()

    # start button
    if len(st.session_state.messages) > 1:
        st.write("---")
        if st.button("🚀 We found a 2-min task! Let's start!", use_container_width=True):
            with st.spinner("Loading..."):
                summary_prompt = "Summarize: Big Goal: [goal] Micro-task: [task]. Reply only in this format."
                try:
                    res = st.session_state.chat.send_message(summary_prompt).text
                    res = res.replace("**", "")
                    st.session_state.big_goal = res.split("Micro-task:")[0].replace("Big Goal:", "").strip()
                    st.session_state.micro_task = res.split("Micro-task:")[1].strip()
                except:
                    st.session_state.big_goal = "Tackle the task we discussed"
                    last_user_input = "Start with the 2-minute action"
                    for msg in reversed(st.session_state.messages):
                        if msg["role"] == "user":
                            last_user_input = msg["content"]
                            break
                    st.session_state.micro_task = f"Action related to: {last_user_input}"

                goto_page(2)
                st.rerun()


# p2：focus mode
elif st.session_state.step == 2:
    st.title("🌊 Zen Focus Mode")
    st.info(f"**🎯 Big Goal:** {st.session_state.big_goal}")
    st.success(f"**📝 Action:** {st.session_state.micro_task}")

    img_col1, img_col2, img_col3 = st.columns([1, 3, 1])
    with img_col2:
        try:
            st.image("read.gif", use_container_width=True)
        except:
            st.warning("image 'read.gif' missing")

    st.write("---")


    progress_bar_css = """
    <style>
        .my-progress-box {
            width: 100%;
            background-color: #f0f4f8;
            border-radius: 8px;
            overflow: hidden;
            height: 8px;
            margin-bottom: 10px;
        }
        .my-progress-line {
            height: 100%;
            width: 0%;
            animation: moveBar 120s linear forwards; 
        }
        @keyframes moveBar {
            0% { width: 0%; background: #90caf9; }
            50% { background: #ce93d8; }
            100% { width: 100%; background: #ffb74d; box-shadow: 0 0 10px #ffb74d; }
        }
        .fade-text {
            opacity: 0;
            text-align: center;
            font-size: 14px;
            color: #666;
            animation: showText 2s ease-in 120s forwards; 
        }
        @keyframes showText {
            to { opacity: 1; }
        }
    </style>

    <div class="my-progress-box">
        <div class="my-progress-line"></div>
    </div>
    <div class="fade-text">
        ✨ <strong>The friction of initiation is broken.</strong><br>
        You can finish now with zero guilt, or stay in the flow and keep going.
    </div>
    <br>
    """

    # finish
    if not st.session_state.is_focusing:
        st.markdown(progress_bar_css, unsafe_allow_html=True)

        btn1, btn2 = st.columns(2)
        with btn1:
            if st.button("✅ I finished!", use_container_width=True):
                goto_page(3)
                st.rerun()
        with btn2:
            if st.button("🌊 Stay in Flow!", use_container_width=True):
                st.session_state.is_focusing = True
                st.rerun()
    else:
        # stay
        st.markdown("<h4 style='text-align: center; color: #ffb74d;'>You are in the Hyperfocus... 🌊</h4>", unsafe_allow_html=True)
        st.write("")
        st.write("")

        center_col1, center_col2, center_col3 = st.columns([1, 1, 1])
        with center_col2:
            if st.button("Click here when you are done", use_container_width=True):
                st.session_state.is_focusing = False
                goto_page(3)
                st.rerun()


# p3：celebration
elif st.session_state.step == 3:
    st.balloons()
    st.markdown("<h1 style='text-align: center;'>🎉 You crushed it!</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("celebrate.gif", use_container_width=True)
        except:
            pass

    st.success("The first step is always the hardest. You successfully initiated the task!")

    end_col1, end_col2, end_col3 = st.columns([1, 2, 1])
    with end_col2:
        if st.button("🔥 Start another micro-task", use_container_width=True):
            st.session_state.clear()
            st.rerun()