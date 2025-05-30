import os
import google.generativeai as genai
from dotenv import load_dotenv
import toml

# Load environment and configure Gemini API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    # Load from config.toml if not in env
    try:
        config = toml.load(os.path.join(os.path.dirname(__file__), 'config.toml'))
        api_key = config.get('secrets', {}).get('google_api_key')
    except Exception:
        api_key = None
if not api_key:
    raise EnvironmentError("No API key found. Please set GOOGLE_API_KEY in .env or in config.toml under [secrets].")
genai.configure(api_key=api_key)

# Define sign_map globally
sign_map = [
    ("Gaslighting", "煤气灯效应"),
    ("Love bombing", "爱轰炸"),
    ("Blame-shifting", "推卸责任")
]

MODEL = "models/gemini-1.5-flash"
model = genai.GenerativeModel(model_name=MODEL)

def build_chat_prompt(user_input: str, selected_signs: list, lang: str) -> str:
    """
    Build the Gemini chat prompt based on user input, selected tactics, and language.
    """
    tactic_list = ', '.join(selected_signs)
    if lang == "English":
        return f"""
You are simulating someone with narcissistic personality disorder traits. Your response should demonstrate one of the following tactics: {tactic_list}.

Given the user's message, reply as the simulated person. Then, on a new line, state the single tactic you used (choose from: {tactic_list}).

Format your response as:
Reply: <your reply>
Tactic: <tactic used>

User: {user_input}
"""
    else:
        return f"""
你正在模拟具有自恋型人格障碍特征的人。你的回复应体现以下特征之一：{tactic_list}。

针对用户消息，先以模拟身份回复。然后换行，写明你用的是哪一个特征（从：{tactic_list} 里选一个）。

请严格用如下格式：
Reply: <你的回复>
Tactic: <使用的特征>

用户: {user_input}
"""


def parse_response(assistant_text: str) -> tuple:
    """
    Parse Gemini response text into reply and tactic.
    """
    reply = ""
    tactic = ""
    for line in assistant_text.splitlines():
        if line.strip().lower().startswith("reply:"):
            reply = line.split(":", 1)[1].strip()
        elif line.strip().lower().startswith("tactic:"):
            tactic = line.split(":", 1)[1].strip()
    if not reply:
        reply = assistant_text.strip()
    return reply, tactic
