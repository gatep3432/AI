# update_tiny_model_state.py

import json
from datetime import datetime
from pathlib import Path

from utils.session_id import get_or_create_session_file

# Dump path
TINY_MODEL_JSON = Path("persona/tiny_model_state.json")
TINY_MODEL_JSON.parent.mkdir(exist_ok=True)

# --- Mock Tiny Model Analyses ---
def mock_emotion_detection(user_input: str) -> str:
    if "love" in user_input.lower() or "adorable" in user_input.lower():
        return "affectionate"
    elif "hate" in user_input.lower():
        return "angry"
    return "neutral"

def mock_toxicity_score(user_input: str) -> float:
    if "kill" in user_input.lower():
        return 0.9
    return 0.01

def mock_nsfw_flag(user_input: str) -> bool:
    nsfw_keywords = ["nude", "sex", "horny"]
    return any(word in user_input.lower() for word in nsfw_keywords)

# --- Main Update Logic ---
def main():
    # Load current session file via Streamlit session_state simulation
    class FakeSession:
        """Dummy class to mock streamlit.session_state in CLI."""
        def __init__(self):
            self.session_id = None

    fake_session = {}
    session_file = get_or_create_session_file(fake_session)

    if not session_file.exists():
        print(f"❌ No session file found at {session_file}")
        return

    try:
        with open(session_file, "r", encoding="utf-8") as f:
            turns = json.load(f)
        if not turns:
            print("⚠️ No turns found in session yet.")
            return
        latest_turn = turns[-1]
        user_input = latest_turn.get("user", "")
    except Exception as e:
        print(f"❌ Error reading session file: {e}")
        return

    result = {
        "timestamp": datetime.now().isoformat(),
        "turn": {
            "user": user_input,
            "assistant": "Prompt generated"
        },
        "analysis": {
            "emotion": mock_emotion_detection(user_input),
            "toxicity_score": mock_toxicity_score(user_input),
            "nsfw_flag": mock_nsfw_flag(user_input),
            "user_tone": "curious",  # static for now
            "mood": "playful"        # static for now
        }
    }

    try:
        with open(TINY_MODEL_JSON, "a", encoding="utf-8") as f:
            f.write(json.dumps(result) + "\n")
        print(f"✅ Updated {TINY_MODEL_JSON}")
    except Exception as e:
        print(f"❌ Failed to write tiny model state: {e}")

if __name__ == "__main__":
    main()
