import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv  # keep for legacy .env support
import toml
import os
import random
from utils import sign_map, model, build_chat_prompt, parse_response

# Load api key config at startup
try:
    config = toml.load('config.toml')
    os.environ['GOOGLE_API_KEY'] = config.get('secrets', {}).get('google_api_key', '')
except Exception:
    pass

load_dotenv()

# Define sign_map globally so it's available everywhere
# sign_map = [
#     ("Gaslighting", "煤气灯效应"),
#     ("Love bombing", "爱轰炸"),
#     ("Blame-shifting", "推卸责任")
# ]

# Set Streamlit page config FIRST (before any other Streamlit commands)
st.set_page_config(
    page_title="MirrorShield - NPD Interaction Simulator",
    page_icon="🛡️",
    layout="centered"
)

# Global language selector in sidebar (always available)
st.sidebar.radio(
    "🌐 Language / 语言",
    ["English", "中文"],
    key="language_select"
)

# 3. Choose your Gemini model
MODEL = "models/gemini-1.5-flash"   # free Flash model

# Initial settings page
if "settings_done" not in st.session_state or not st.session_state["settings_done"]:
    with st.sidebar:
        st.markdown("## 🛠️ " + ("Initial Settings" if st.session_state.get("language_select", "English") == "English" else "初始设置"))
        lang = st.session_state["language_select"]
        # --- Randomize settings button (fixes Streamlit assignment error) ---
        if st.button("🎲 Randomize Settings" if lang == "English" else "🎲 随机设置", key="randomize_settings_btn"):
            intensity_labels = [x[0] if lang == "English" else x[1] for x in [
                ("Low", "低"),
                ("Medium", "中"),
                ("High", "高"),
                ("Random", "随机")
            ]]
            sign_labels = [x[0] if lang == "English" else x[1] for x in [
                ("Gaslighting", "煤气灯效应"),
                ("Love bombing", "爱轰炸"),
                ("Blame-shifting", "推卸责任")
            ]]
            st.session_state["intensity_select"] = random.choice(intensity_labels[:-1])
            st.session_state["signs_select"] = random.sample(sign_labels, random.randint(1, len(sign_labels)))
            st.session_state["random_mode"] = True
            st.rerun()
        # Intensity dropdown
        intensity_options = [
            ("Low", "低"),
            ("Medium", "中"),
            ("High", "高"),
            ("Random", "随机")
        ]
        intensity_labels = [x[0] if lang == "English" else x[1] for x in intensity_options]
        st.selectbox(
            "Intensity of NPD traits" if lang == "English" else "NPD特征强度",
            intensity_labels,
            key="intensity_select"
        )
        # Signs to include
        sign_labels = [x[0] if lang == "English" else x[1] for x in sign_map]
        if "signs_select" in st.session_state:
            st.multiselect(
                "Signs to include" if lang == "English" else "包含的特征",
                sign_labels,
                key="signs_select"
            )
        else:
            st.multiselect(
                "Signs to include" if lang == "English" else "包含的特征",
                sign_labels,
                default=sign_labels,
                key="signs_select"
            )
        random_mode = st.checkbox(
            "Randomize all settings" if lang == "English" else "随机所有设置",
            key="random_mode"
        )
        st.divider()
        st.subheader("Upload or Paste a Conversation for Analysis" if lang == "English" else "上传或粘贴对话进行分析")
        uploaded_file = st.file_uploader(
            "Upload a .txt file" if lang == "English" else "上传.txt文件",
            type=["txt"],
            key="settings_upload"
        )
        analyze_text = ""
        if uploaded_file is not None:
            analyze_text = uploaded_file.read().decode("utf-8")
        analyze_text = st.text_area(
            "Or paste conversation text here:" if lang == "English" else "或在此粘贴对话内容：",
            value=analyze_text,
            height=200,
            key="settings_analyze_input"
        )
        analyze_result = ""
        if st.button("Get Analysis" if lang == "English" else "获取分析", key="settings_run_analysis"):
            if analyze_text.strip():
                try:
                    if lang == "English":
                        analysis_prompt = f"""
Analyze the following conversation for signs of narcissistic personality disorder (NPD) traits.\nFocus on identifying instances of:\n1. Gaslighting\n2. Love bombing\n3. Blame-shifting\n4. Other NPD characteristics\n\nBased on these factors, provide a percentage indicating how strongly the conversation shows NPD traits.\nFormat your response as: \"NPD Traits Analysis: X%\"\nThen provide a brief explanation of why.\n\nConversation to analyze:\n{analyze_text}
"""
                    else:
                        analysis_prompt = f"""
请分析以下对话是否具有自恋型人格障碍（NPD）的特征。\n重点识别：\n1. 煤气灯效应\n2. 爱轰炸\n3. 推卸责任\n4. 其他NPD特征\n\n请根据这些因素，给出该对话表现出NPD特征的百分比。\n请用如下格式回答：\"NPD特征分析：X%\"\n并简要说明原因。\n\n待分析对话：\n{analyze_text}
"""
                    response = model.generate_content(analysis_prompt)
                    analyze_result = response.text
                    st.markdown(analyze_result)
                except Exception as e:
                    st.error(("Analysis failed: " if lang == "English" else "分析失败：") + str(e))
            else:
                st.warning("Please upload or paste conversation text to analyze." if lang == "English" else "请上传或粘贴要分析的对话内容。")
    # Main area landing page
    landing_title = "🛡️ MirrorShield" if st.session_state.get("language_select", "English") == "English" else "🛡️ 镜盾"
    landing_desc = (
        """
        MirrorShield is an interactive simulation that helps you recognize and understand manipulative behaviors associated with narcissistic personality disorder (NPD).\n\nConfigure your simulation settings in the sidebar, then click Continue to begin.\n\nYou can also upload or paste a real conversation to analyze for NPD traits before starting the simulation.
        """
        if st.session_state.get("language_select", "English") == "English" else
        """
        镜盾是一个互动模拟工具，帮助你识别和理解与自恋型人格障碍（NPD）相关的操控行为。\n\n请在左侧栏配置模拟设置，然后点击继续开始。\n\n你也可以在开始前上传或粘贴真实对话，分析其NPD特征。
        """
    )
    st.markdown(f"<div style='display:flex;flex-direction:column;align-items:center;margin-top:10vh;'>"
                f"<h1 style='font-size:3em;margin-bottom:0.5em;text-align:center;'>{landing_title}</h1>"
                f"<div style='font-size:1.3em;max-width:600px;text-align:center;margin-bottom:2em;'>{landing_desc}</div>"
                f"</div>", unsafe_allow_html=True)
    # Prominent Continue button (Streamlit-native)
    st.markdown("""
        <style>
        div[data-testid="stButton"] button.center-continue {
            font-size: 1.5em;
            font-weight: bold;
            background: #1a73e8;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.7em 2.5em;
            margin-top: 1em;
            margin-bottom: 2em;
            display: flex;
            justify-content: center;
            align-items: center;
            margin-left: auto;
            margin-right: auto;
        }
        div[data-testid="stButton"] { display: flex; justify-content: center; }
        </style>
    """, unsafe_allow_html=True)
    if st.button("Continue" if st.session_state.get("language_select", "English") == "English" else "继续", key="center_continue", help=None, type="secondary"):
        lang = st.session_state["language_select"]
        intensity_labels = [x[0] if lang == "English" else x[1] for x in [
            ("Low", "低"),
            ("Medium", "中"),
            ("High", "高"),
            ("Random", "随机")
        ]]
        sign_labels = [x[0] if lang == "English" else x[1] for x in [
            ("Gaslighting", "煤气灯效应"),
            ("Love bombing", "爱轰炸"),
            ("Blame-shifting", "推卸责任")
        ]]
        st.session_state["settings_done"] = True
        st.rerun()
    st.stop()

# 6. Sidebar with your Red Flag Guide
with st.sidebar:
    # Exit session button
    lang = st.session_state.get("language_select", "English")
    # --- Show selected settings in chat page sidebar ---
    if "settings_done" in st.session_state and st.session_state["settings_done"]:
        st.markdown("---")
        st.markdown("### " + ("Simulation Settings" if lang == "English" else "模拟设置"))
        st.markdown((f"**Intensity:** {st.session_state.get('intensity_select', 'Medium')}" if lang == "English" else f"**强度：** {st.session_state.get('intensity_select', '中')}") )
        selected_signs = st.session_state.get('signs_select', [])
        if selected_signs:
            if lang == "English":
                st.markdown("**Signs Included:** " + ", ".join(selected_signs))
            else:
                st.markdown("**包含的特征：** " + ", ".join(selected_signs))
        if st.session_state.get('random_mode'):
            st.markdown("**Randomized Settings: Enabled**" if lang == "English" else "**随机设置：已启用**")
        st.markdown("---")
        if st.button("Exit Session" if lang == "English" else "退出会话", key="exit_session"):
            for k in ["settings_done", "chat", "messages", "intensity_select", "signs_select", "random_mode", "settings_upload", "settings_analyze_input"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()
    st.header("🚩 Red Flag Guide" if lang == "English" else "🚩 红旗指南")
    st.markdown(
        """
        ### Common Manipulation Tactics:

        1. **Gaslighting**  
           - Making you question your reality  
           - Denying things that happened  
           - "You're too sensitive"

        2. **Love Bombing**  
           - Excessive affection  
           - Over-the-top compliments  
           - Moving too fast

        3. **Blame-Shifting**  
           - Never taking responsibility  
           - Always the victim  
           - Turning situations around

        Pay attention to these patterns in the conversation!
        """ if lang == "English" else
        """
        ### 常见操控手法：

        1. **煤气灯效应**  
           - 让你怀疑自己的现实  
           - 否认发生过的事情  
           - “你太敏感了”

        2. **爱轰炸**  
           - 过度的关爱  
           - 夸张的赞美  
           - 进展太快

        3. **推卸责任**  
           - 从不承担责任  
           - 总是受害者  
           - 反过来指责别人

        聊天时请注意这些模式！
        """
    )

# 7. Initialize or retrieve a single chat session
if "chat" not in st.session_state:
    lang = st.session_state.get("language_select", "English")
    intensity = st.session_state.get("intensity_select", "Medium")
    signs = st.session_state.get("signs_select", ["Gaslighting", "Love bombing", "Blame-shifting"])
    # Compose the system prompt based on settings
    if lang == "English":
        signs_text = ", ".join(signs)
        system_prompt = (
            f"You are simulating someone with narcissistic personality disorder traits. "
            f"Your responses should demonstrate the following: {signs_text}. "
            f"Intensity: {intensity.lower()}. "
            f"Remain realistic and conversational."
        )
    else:
        sign_map_dict = dict(sign_map)
        signs_text = "，".join([sign_map_dict.get(s, s) for s in signs])
        system_prompt = (
            f"你正在模拟具有自恋型人格障碍特征的人。你的回复应体现以下特征：{signs_text}。"
            f"强度：{intensity}。"
            f"同时保持真实和对话性。"
        )
    st.session_state.chat = model.start_chat()
    st.session_state.chat.send_message(system_prompt)

# 8. Initialize chat history storage
if "messages" not in st.session_state:
    st.session_state.messages = []

# 9. Page header and instructions
st.title("🛡️ MirrorShield" if st.session_state.get("language_select", "English") == "English" else "🛡️ 镜盾")
st.markdown(
    """
This interactive simulation helps you recognize and understand manipulative behaviors 
associated with narcissistic personality disorder (NPD).

Type a message below to start the conversation.
""" if st.session_state.get("language_select", "English") == "English" else
    """
本互动模拟帮助你识别和理解与自恋型人格障碍（NPD）相关的操控行为。

在下方输入消息，开始对话。
"""
)

# 10. Render existing messages
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("tactic"):
            # Guessing logic
            guess_key = f"guess_tactic_{idx}"
            show_key = f"show_tactic_{idx}"
            if "guesses" not in st.session_state:
                st.session_state["guesses"] = {}
            if "show_tactics" not in st.session_state:
                st.session_state["show_tactics"] = {}
            lang = st.session_state.get("language_select", "English")
            selected_signs = st.session_state.get("signs_select", ["Gaslighting", "Love bombing", "Blame-shifting"])
            options = selected_signs + ["None"]
            # If not guessed yet, show radio and button
            if guess_key not in st.session_state["guesses"]:
                guess = st.radio(
                    "Guess the tactic used:" if lang == "English" else "请猜测使用的特征：",
                    options,
                    key=f"radio_{guess_key}"
                )
                if st.button("Submit Guess" if lang == "English" else "提交猜测", key=f"submit_{guess_key}"):
                    st.session_state["guesses"][guess_key] = guess
                    st.rerun()
            else:
                # After guess, show toggle to reveal
                col1, col2 = st.columns([2,1])
                with col1:
                    st.markdown((f"**Your guess:** {st.session_state['guesses'][guess_key]}" if lang == "English" else f"**你的猜测：** {st.session_state['guesses'][guess_key]}"))
                with col2:
                    show = st.toggle("Show tactic" if lang == "English" else "显示特征", key=show_key)
                    st.session_state["show_tactics"][show_key] = show
                if st.session_state["show_tactics"].get(show_key, False):
                    st.info((f"Tactic: {msg['tactic']}" if lang == "English" else f"特征：{msg['tactic']}"))
                    # Optionally, show if guess was correct
                    if st.session_state['guesses'][guess_key] == msg['tactic']:
                        st.success("Correct!" if lang == "English" else "猜对了！")
                    else:
                        st.error("Incorrect." if lang == "English" else "不正确。")

# 11. Handle new user input
user_input = st.chat_input("Type your message here..." if st.session_state.get("language_select", "English") == "English" else "在此输入你的消息……")
if user_input:
    # a) Display & save the user's message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # b) Send the user message to Gemini (structured tool call)
    try:
        selected_signs = st.session_state.get("signs_select", ["Gaslighting", "Love bombing", "Blame-shifting"])
        lang = st.session_state.get("language_select", "English")
        prompt = build_chat_prompt(user_input, selected_signs, lang)
        response = model.generate_content(prompt)
        assistant_text = response.text
        reply, tactic = parse_response(assistant_text)
        st.session_state.messages.append({"role": "assistant", "content": reply, "tactic": tactic})
        with st.chat_message("assistant"):
            st.markdown(reply)
            # Tactic reveal button
            tactic_key = f"show_tactic_{len(st.session_state.messages) - 1}"
            if "revealed_tactics" not in st.session_state:
                st.session_state["revealed_tactics"] = set()
            if tactic_key not in st.session_state["revealed_tactics"]:
                if st.button("Show tactic" if lang == "English" else "显示特征", key=tactic_key):
                    st.session_state["revealed_tactics"].add(tactic_key)
                    st.rerun()
            if tactic_key in st.session_state["revealed_tactics"]:
                st.info((f"Tactic: {tactic}" if lang == "English" else f"特征：{tactic}"))
    except Exception as e:
        st.error(("An error occurred: " if st.session_state.get("language_select", "English") == "English" else "发生错误：") + str(e))
        if "quota" in str(e).lower():
            st.error("API quota exceeded. Please check your API key limits." if st.session_state.get("language_select", "English") == "English" else "API额度已用尽。请检查你的API密钥限制。")
