# persona/mood_tracker.py
# Track and update mood based on interactions and hormones

import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from .hormone_adjuster import (
    load_hormone_levels,
    load_mood_weights,
    infer_mood_from_hormones,
    adjust_hormones,
    get_mood_context,
    apply_contextual_hormone_adjustments  # New enhanced function
)

MOOD_HISTORY_FILE = Path("persona/mood_history.json")

def load_mood_history() -> list:
    """Load mood history and create file if not present."""
    if not MOOD_HISTORY_FILE.exists():
        # Save empty list as initial history file
        try:
            MOOD_HISTORY_FILE.parent.mkdir(exist_ok=True)
            with open(MOOD_HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)
            print("[Mood History]: Created default mood history file")
        except Exception as e:
            print(f"[Mood history init error]: {e}")
        return []
    try:
        with open(MOOD_HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Mood history load error]: {e}")
        return []

def save_mood_history(history: list):
    """Save mood history."""
    try:
        MOOD_HISTORY_FILE.parent.mkdir(exist_ok=True)
        with open(MOOD_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"[Mood history save error]: {e}")

def update_mood(new_mood: str, intensity: float, reason: str = "", hormone_context: Dict = None):
    """Update current mood and log to history with enhanced context."""
    # Get mood context if not provided
    if hormone_context is None:
        hormone_context = get_mood_context(new_mood, intensity)
    
    # Update mood_adjustments.json with enhanced data
    mood_data = {
        "current_mood": new_mood,
        "intensity": intensity,
        "context": hormone_context,
        "last_updated": datetime.utcnow().isoformat()
    }

    try:
        with open("persona/mood_adjustments.json", "w", encoding="utf-8") as f:
            json.dump(mood_data, f, indent=2)
    except Exception as e:
        print(f"[Mood update error]: {e}")
        return

    # Log to history with enhanced information
    history = load_mood_history()
    history_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "mood": new_mood,
        "intensity": intensity,
        "reason": reason,
        "is_hybrid": hormone_context.get("is_hybrid", False),
        "is_emergent": hormone_context.get("is_emergent", False),
        "stability": hormone_context.get("stability", "medium")
    }
    
    # Add hormone levels snapshot for debugging contextual changes
    if reason and ("contextual" in reason or "hormone_event" in reason):
        history_entry["hormone_snapshot"] = load_hormone_levels()
    
    history.append(history_entry)

    # Keep only last 100 mood changes
    if len(history) > 100:
        history = history[-100:]

    save_mood_history(history)
    
    # Print mood change for debugging
    mood_type = ""
    if hormone_context.get("is_hybrid"):
        mood_type = " [HYBRID]"
    elif hormone_context.get("is_emergent"):
        mood_type = " [EMERGENT]"
    
    print(f"[Mood Update]: {new_mood}{mood_type} (intensity: {intensity:.2f}) - {reason}")

def get_current_mood() -> Dict[str, Any]:
    """Get current mood settings with enhanced context."""
    try:
        with open("persona/mood_adjustments.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Current mood load error]: {e}")
        return {
            "current_mood": "neutral", 
            "intensity": 0.5,
            "context": {"is_hybrid": False, "is_emergent": False, "stability": "medium"},
            "last_updated": datetime.utcnow().isoformat()
        }

def update_mood_from_hormones(reason="hormonal_shift"):
    """
    Calculate mood from current hormone levels and update mood accordingly.
    This is the primary function for hormone-driven mood updates.
    """
    hormone_levels = load_hormone_levels()
    mood_weights = load_mood_weights()
    mood, intensity = infer_mood_from_hormones(hormone_levels, mood_weights)
    
    # Get enhanced context
    context = get_mood_context(mood, intensity)
    
    # Update mood with context
    update_mood(mood, intensity, reason, context)
    
    return mood, intensity, context

def handle_event_and_update_mood(event: str):
    """
    Adjust hormones based on an event, then update mood from new hormone state.
    """
    print(f"[Event Trigger]: Processing event '{event}'")
    
    # First adjust hormones based on the event
    new_hormones = adjust_hormones(event)
    print(f"[Hormone Update]: New levels - {new_hormones}")
    
    # Then update mood based on new hormone levels
    mood, intensity, context = update_mood_from_hormones(reason=f"hormone_event:{event}")
    
    print(f"[Event Processed]: {event} -> Mood: {mood} ({intensity:.2f})")
    
    return mood, intensity, context, new_hormones

def apply_sentiment_to_mood(conversation_text: str):
    """
    Enhanced sentiment analysis using contextual hormone adjustments.
    This replaces the old simple word-counting approach.
    """
    print(f"[Enhanced Sentiment]: Processing input '{conversation_text}'")
    
    # Use the enhanced contextual hormone adjustment system
    new_hormones = apply_contextual_hormone_adjustments(conversation_text)
    
    # Update mood based on the new hormone levels
    mood, intensity, context = update_mood_from_hormones(reason="contextual_analysis")
    
    print(f"[Enhanced Sentiment Complete]: {mood} ({intensity:.2f}) from '{conversation_text}'")
    
    return mood, intensity, context

# Legacy functions kept for compatibility but now enhanced

def analyze_conversation_sentiment(conversation_text: str) -> str:
    """
    Legacy function kept for compatibility.
    Now uses contextual analysis internally.
    """
    from .hormone_adjuster import analyze_contextual_sentiment
    
    analysis = analyze_contextual_sentiment(conversation_text)
    
    # Map contextual analysis to legacy event types
    emotion_to_event = {
        "strong_negative": "stress",
        "moderate_negative": "stress", 
        "offensive": "stress",
        "strong_positive": "positive_feedback",
        "moderate_positive": "positive_feedback",
        "affectionate": "social_connection",
        "playful": "positive_feedback",
        "neutral": "neutral_interaction"
    }
    
    event = emotion_to_event.get(analysis["emotion_type"], "neutral_interaction")
    print(f"[Legacy Sentiment]: '{conversation_text}' -> {analysis['emotion_type']} -> {event}")
    
    return event

def get_mood_summary() -> Dict[str, Any]:
    """
    Get comprehensive summary of current mood state including hormone levels.
    """
    current_mood_data = get_current_mood()
    hormone_levels = load_hormone_levels()
    history = load_mood_history()
    recent_moods = [entry["mood"] for entry in history[-10:]] if history else []
    hybrid_count = sum(1 for entry in history[-20:] if entry.get("is_hybrid", False)) if history else 0
    emergent_count = sum(1 for entry in history[-20:] if entry.get("is_emergent", False)) if history else 0
    
    summary = {
        "current_state": current_mood_data,
        "hormone_levels": hormone_levels,
        "recent_patterns": {
            "recent_moods": recent_moods,
            "hybrid_states_count": hybrid_count,
            "emergent_states_count": emergent_count,
            "total_mood_changes": len(history)
        },
        "complexity_indicators": {
            "has_undefined_states": hybrid_count > 0 or emergent_count > 0,
            "mood_volatility": "high" if len(set(recent_moods)) > 6 else "medium" if len(set(recent_moods)) > 3 else "low"
        }
    }
    return summary

def force_mood_recalculation():
    """
    Force a complete recalculation of mood from current hormone levels.
    Useful for debugging or manual mood updates.
    """
    print("[Debug]: Forcing mood recalculation from hormones...")
    return update_mood_from_hormones(reason="manual_recalculation")

def simulate_hormone_fluctuation():
    """
    Simulate natural hormone fluctuation over time.
    Call this periodically for organic mood drift.
    """
    import random
    hormones = load_hormone_levels()
    print(f"[Hormone Fluctuation]: Before - {hormones}")
    for hormone in hormones:
        drift = random.uniform(-0.02, 0.02)
        baseline_pull = (0.5 - hormones[hormone]) * 0.01
        hormones[hormone] += drift + baseline_pull
        hormones[hormone] = max(0.0, min(1.0, hormones[hormone]))
    print(f"[Hormone Fluctuation]: After - {hormones}")
    from .hormone_adjuster import save_hormone_levels
    save_hormone_levels(hormones)
    return update_mood_from_hormones(reason="natural_fluctuation")
