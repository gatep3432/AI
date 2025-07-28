# update_faiss_memory_state.py

import json
from datetime import datetime
from pathlib import Path

PERSONA_DIR = Path("persona")
PERSONA_DIR.mkdir(exist_ok=True)

FAISS_MEMORY_JSON = PERSONA_DIR / "faiss_memory_state.json"

def determine_convo_phase(text: str) -> str:
    if any(w in text.lower() for w in ["start", "hello", "hi"]):
        return "onboarding"
    elif any(w in text.lower() for w in ["why", "how", "what"]):
        return "engagement"
    return "closure"

def extract_topics(text: str) -> list:
    if "adorable" in text.lower():
        return ["compliments", "emotional bonding"]
    return ["general conversation"]

def get_latest_session_file():
    session_files = sorted(
        [f for f in Path("data").glob("session_*.json") if f.is_file()],
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )
    return session_files[0] if session_files else None

def get_last_user_input(session_file: Path) -> str:
    try:
        session_data = json.loads(session_file.read_text(encoding="utf-8"))
        if not session_data or "user" not in session_data[-1]:
            raise ValueError("Invalid session structure.")
        return session_data[-1]["user"]
    except Exception as e:
        print(f"❌ Error reading session file: {e}")
        return None

def main():
    latest_session = get_latest_session_file()
    if not latest_session:
        print("⚠️ No session file found.")
        return

    user_input = get_last_user_input(latest_session)
    if not user_input:
        print("⚠️ No user input found in latest session.")
        return

    result = {
        "timestamp": datetime.now().isoformat(),
        "turn": {
            "user": user_input,
            "assistant": "Prompt generated"
        },
        "memory_context": {
            "conversation_phase": determine_convo_phase(user_input),
            "topic_stack": extract_topics(user_input),
            "preferences": ["empathy", "quick wit"],
            "intent_trend": "emotional exploration",
            "rapport_level": 0.88,
            "attachment_style": "secure"
        }
    }

    with open(FAISS_MEMORY_JSON.resolve(), "a", encoding="utf-8") as f:
        f.write(json.dumps(result) + "\n")

    print(f"✅ FAISS memory updated with input from {latest_session.name}")
    print(f"📁 Dumped to: {FAISS_MEMORY_JSON.resolve()}")

if __name__ == "__main__":
    main()
