# persona/hormone_adjuster.py

import json
from typing import Dict, Tuple
from pathlib import Path
import random

HORMONES_FILE = Path("persona/hormones.json")
MOOD_WEIGHTS_FILE = Path("persona/mood_weights.json")

_DEFAULT_HORMONES = {"dopamine": 0.5, "serotonin": 0.5, "cortisol": 0.5, "oxytocin": 0.5}
_DEFAULT_MOOD_WEIGHTS = {
    "cheerful": {"dopamine": 0.7, "serotonin": 0.3},
    "anxious": {"cortisol": 0.8, "dopamine": -0.3},
    "affectionate": {"oxytocin": 0.9},
    "depressed": {"serotonin": -0.5, "cortisol": 0.6},
    "excited": {"dopamine": 0.8, "cortisol": 0.2},
    "melancholic": {"serotonin": -0.4, "dopamine": -0.2},
    "energetic": {"dopamine": 0.6, "serotonin": 0.4},
    "contemplative": {"serotonin": 0.3, "cortisol": -0.2},
    "restless": {"cortisol": 0.5, "dopamine": 0.3},
    "serene": {"serotonin": 0.8, "cortisol": -0.4}
}

# Enhanced contextual emotion patterns
_EMOTION_PATTERNS = {
    "strong_negative": {
        "patterns": [" you", "you suck", "terrible", "awful", "worst", "you're terrible", "you're awful"],
        "hormones": {"cortisol": 0.15, "serotonin": -0.1, "dopamine": -0.05},
        "base_intensity": 0.8
    },
    "strong_positive": {
        "patterns": ["love you", "i love you", "amazing", "wonderful", "fantastic", "best ever", "you're amazing", "you're wonderful"],
        "hormones": {"dopamine": 0.15, "serotonin": 0.1, "oxytocin": 0.1},
        "base_intensity": 0.8
    },
    "moderate_negative": {
        "patterns": ["you are bad", "bad", "not good", "disappointed", "annoyed", "stupid", "foolish"],
        "hormones": {"cortisol": 0.08, "serotonin": -0.05},
        "base_intensity": 0.6
    },
    "moderate_positive": {
        "patterns": ["good", "nice", "like it", "thanks", "great", "thank you"],
        "hormones": {"dopamine": 0.08, "serotonin": 0.05},
        "base_intensity": 0.6
    },
    "affectionate": {
        "patterns": ["kiss", "i kiss you", "hug", "cuddle", "hold you", "miss you", "kiss you"],
        "hormones": {"oxytocin": 0.12, "dopamine": 0.06},
        "base_intensity": 0.7
    },
    "playful": {
        "patterns": ["lets go", "let's go", "ride", "play", "fun", "adventure", "explore", "lets go for a ride"],
        "hormones": {"dopamine": 0.1, "oxytocin": 0.05},
        "base_intensity": 0.6
    },
    "offensive": {
        "patterns": ["dirty", "nasty", "disgusting", "gross"],
        "hormones": {"cortisol": 0.1, "serotonin": -0.08},
        "base_intensity": 0.7
    }
}

def _ensure_file(file_path: Path, default_data: dict):
    """Create the file with default data if it doesn't exist."""
    if not file_path.exists():
        try:
            file_path.parent.mkdir(exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(default_data, f, indent=2)
            print(f"[autocreate] Created {file_path} with defaults.")
        except Exception as e:
            print(f"[autocreate error] Could not create {file_path}: {e}")

def load_hormone_levels() -> Dict[str, float]:
    """Load current hormone levels from JSON file. Create if missing."""
    _ensure_file(HORMONES_FILE, _DEFAULT_HORMONES)
    try:
        with open(HORMONES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Hormone load error]: {e}")
        return _DEFAULT_HORMONES.copy()

def save_hormone_levels(levels: Dict[str, float]):
    """Save hormone levels to JSON file."""
    try:
        HORMONES_FILE.parent.mkdir(exist_ok=True)
        with open(HORMONES_FILE, "w", encoding="utf-8") as f:
            json.dump(levels, f, indent=2)
        print(f"[Hormone Save]: Saved levels - {levels}")
    except Exception as e:
        print(f"[Hormone save error]: {e}")

def load_mood_weights() -> Dict:
    """Load mood weight mappings from JSON file. Create if missing."""
    _ensure_file(MOOD_WEIGHTS_FILE, _DEFAULT_MOOD_WEIGHTS)
    try:
        with open(MOOD_WEIGHTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Mood weights load error]: {e}")
        return _DEFAULT_MOOD_WEIGHTS.copy()

def calculate_contextual_intensity(text: str, base_intensity: float) -> float:
    """Calculate emotional intensity based on contextual cues."""
    intensity = base_intensity
    text_lower = text.lower()
    
    # Exclamation marks boost intensity
    exclamation_count = text.count('!')
    if exclamation_count > 0:
        intensity *= (1 + 0.1 * min(exclamation_count, 3))
    
    # All caps detection
    if text.isupper() and len(text) > 3:
        intensity *= 1.2
    
    # Profanity intensifies emotion
    profanity_words = ["fuck", "shit", "damn", "hell"]
    if any(word in text_lower for word in profanity_words):
        intensity *= 1.3
    
    # Repetition detection
    words = text_lower.split()
    if len(words) > 1 and len(set(words)) < len(words) * 0.7:  # 30% or more repeated words
        intensity *= 1.15
    
    return min(1.0, intensity)

def analyze_contextual_sentiment(text: str) -> Dict:
    """Enhanced contextual sentiment analysis with pattern matching."""
    text_lower = text.lower().strip()
    
    print(f"[Contextual Analysis]: Analyzing '{text}' -> '{text_lower}'")
    
    # Check for exact phrase matches first (most accurate)
    for emotion_type, config in _EMOTION_PATTERNS.items():
        for pattern in config["patterns"]:
            if pattern in text_lower:
                intensity = calculate_contextual_intensity(text, config["base_intensity"])
                
                result = {
                    "emotion_type": emotion_type,
                    "intensity": intensity,
                    "hormone_adjustments": config["hormones"],
                    "confidence": 0.9,  # High confidence for pattern matches
                    "triggered_by": pattern,
                    "method": "pattern_match"
                }
                
                print(f"[Pattern Match]: Found '{pattern}' -> {emotion_type} (intensity: {intensity:.2f})")
                return result
    
    # Fallback to enhanced word-level analysis
    return _word_level_sentiment_analysis(text_lower)

def _word_level_sentiment_analysis(text: str) -> Dict:
    """Enhanced word-level analysis with better thresholds and context."""
    positive_words = [
        "good", "great", "awesome", "happy", "love", "excellent", "wonderful",
        "amazing", "fantastic", "brilliant", "perfect", "beautiful", "nice",
        "enjoy", "like", "fun", "exciting", "yes", "thank", "thanks", "sweet",
        "cool", "best", "super", "fine"
    ]
    
    negative_words = [
        "bad", "terrible", "sad", "hate", "awful", "horrible", "disappointed",
        "frustrated", "angry", "upset", "annoyed", "stressed", "fuck", "shit",
        "damn", "stupid", "foolish", "no", "don't", "stop", "worst", "suck",
        "nasty", "gross", "disgusting", "dirty"
    ]
    
    words = text.split()
    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)
    
    print(f"[Word Analysis]: positive={positive_count}, negative={negative_count}")
    
    # More sensitive thresholds - even 1 word can trigger
    if positive_count > 0 and positive_count >= negative_count:
        intensity = min(0.7, 0.4 + positive_count * 0.1)  # Scale with word count
        return {
            "emotion_type": "moderate_positive",
            "intensity": intensity,
            "hormone_adjustments": {"dopamine": 0.08, "serotonin": 0.05},
            "confidence": 0.6,
            "triggered_by": f"{positive_count} positive words",
            "method": "word_analysis"
        }
    elif negative_count > 0 and negative_count > positive_count:
        intensity = min(0.7, 0.4 + negative_count * 0.1)  # Scale with word count
        return {
            "emotion_type": "moderate_negative", 
            "intensity": intensity,
            "hormone_adjustments": {"cortisol": 0.08, "serotonin": -0.05},
            "confidence": 0.6,
            "triggered_by": f"{negative_count} negative words",
            "method": "word_analysis"
        }
    else:
        return {
            "emotion_type": "neutral",
            "intensity": 0.3,
            "hormone_adjustments": {},
            "confidence": 0.4,
            "triggered_by": "no clear sentiment",
            "method": "neutral_fallback"
        }

def apply_contextual_hormone_adjustments(text: str) -> Dict[str, float]:
    """Apply hormone adjustments based on contextual sentiment analysis."""
    analysis = analyze_contextual_sentiment(text)
    
    print(f"[Contextual Hormone Adjustment]: {analysis}")
    
    if analysis["hormone_adjustments"]:
        hormones = load_hormone_levels()
        original_hormones = hormones.copy()
        
        # Apply contextual adjustments with intensity scaling
        intensity_multiplier = analysis["intensity"]
        for hormone, base_adjustment in analysis["hormone_adjustments"].items():
            # Scale adjustment by intensity
            scaled_adjustment = base_adjustment * intensity_multiplier
            hormones[hormone] = max(0.0, min(1.0, hormones[hormone] + scaled_adjustment))
            
            print(f"[Hormone Adjust]: {hormone} {hormones[hormone]:.3f} (was {original_hormones[hormone]:.3f}, adjustment: {scaled_adjustment:+.3f})")
        
        # Apply natural decay
        for hormone in hormones:
            if hormones[hormone] > 0.5:
                hormones[hormone] = max(0.5, hormones[hormone] - 0.01)
            elif hormones[hormone] < 0.5:
                hormones[hormone] = min(0.5, hormones[hormone] + 0.01)
        
        save_hormone_levels(hormones)
        return hormones
    else:
        print(f"[Contextual Hormone Adjustment]: No adjustments needed")
        return load_hormone_levels()

def calculate_mood_scores(hormone_levels: Dict[str, float], mood_weights: Dict) -> Dict[str, float]:
    """Calculate scores for all defined moods based on hormone levels."""
    mood_scores = {}
    for mood, weights in mood_weights.items():
        score = 0.0
        for hormone, weight in weights.items():
            score += hormone_levels.get(hormone, 0.5) * weight
        mood_scores[mood] = score
    return mood_scores

def detect_undefined_mood_state(mood_scores: Dict[str, float], hormone_levels: Dict[str, float], threshold: float = 0.15) -> Tuple[bool, str, float]:
    """
    Detect if current hormone combination represents an undefined/hybrid mood state.
    Returns: (is_undefined, mood_name, intensity)
    """
    sorted_moods = sorted(mood_scores.items(), key=lambda x: abs(x[1]), reverse=True)
    
    if len(sorted_moods) < 2:
        return False, sorted_moods[0][0], abs(sorted_moods[0][1])
    
    top_mood, top_score = sorted_moods[0]
    second_mood, second_score = sorted_moods[1]
    
    # Hybrid states: ambiguous
    if abs(abs(top_score) - abs(second_score)) < threshold:
        if top_score > 0 and second_score > 0:
            hybrid_name = f"{second_mood}-{top_mood}"
        elif top_score < 0 and second_score < 0:
            hybrid_name = f"conflicted-{top_mood}"
        else:
            pos_mood = top_mood if top_score > 0 else second_mood
            hybrid_name = f"bittersweet-{pos_mood}"
        intensity = (abs(top_score) + abs(second_score)) / 2
        return True, hybrid_name, min(1.0, intensity)
    
    max_abs_score = max(abs(score) for score in mood_scores.values())
    if max_abs_score < 0.2:
        return True, "undefined-neutral", max_abs_score

    dopamine = hormone_levels.get("dopamine", 0.5)
    cortisol = hormone_levels.get("cortisol", 0.5)
    serotonin = hormone_levels.get("serotonin", 0.5)
    oxytocin = hormone_levels.get("oxytocin", 0.5)
    if dopamine > 0.7 and cortisol > 0.7:
        return True, "manic-energy", (dopamine + cortisol) / 2
    if serotonin < 0.3 and oxytocin > 0.7:
        return True, "melancholic-affection", (oxytocin + (1 - serotonin)) / 2
    if all(level > 0.8 for level in [dopamine, cortisol, serotonin, oxytocin]):
        return True, "overwhelmed", 0.9
    if all(level < 0.2 for level in [dopamine, cortisol, serotonin, oxytocin]):
        return True, "numb", 0.8
    return False, top_mood, abs(top_score)

def generate_emergent_mood_variations(base_mood: str, hormone_levels: Dict[str, float]) -> str:
    """Generate subtle variations of mood based on hormone nuances."""
    dopamine = hormone_levels.get("dopamine", 0.5)
    cortisol = hormone_levels.get("cortisol", 0.5)
    serotonin = hormone_levels.get("serotonin", 0.5)
    oxytocin = hormone_levels.get("oxytocin", 0.5)
    
    prefixes = []
    if cortisol > 0.6:
        prefixes.append("tense")
    elif cortisol < 0.3:
        prefixes.append("relaxed")
    if dopamine > 0.7:
        prefixes.append("energetic")
    elif dopamine < 0.3:
        prefixes.append("lethargic")
    if oxytocin > 0.7:
        prefixes.append("warm")
    elif oxytocin < 0.3:
        prefixes.append("distant")
    if serotonin > 0.7:
        prefixes.append("balanced")
    elif serotonin < 0.3:
        prefixes.append("unstable")
    
    if prefixes and random.random() > 0.5:
        return f"{random.choice(prefixes)}-{base_mood}"
    return base_mood

def infer_mood_from_hormones(hormone_levels: Dict[str, float], mood_weights: Dict) -> Tuple[str, float]:
    """Calculate which mood fits best based on hormone levels, including undefined states."""
    mood_scores = calculate_mood_scores(hormone_levels, mood_weights)
    is_undefined, mood_name, intensity = detect_undefined_mood_state(mood_scores, hormone_levels)
    if is_undefined:
        intensity = max(0.0, min(1.0, intensity))
        return mood_name, intensity
    # Standard mood selection for defined states
    best_mood = "neutral"
    best_score = 0.0
    for mood, score in mood_scores.items():
        if abs(score) > abs(best_score):
            best_mood = mood
            best_score = score
    final_mood = generate_emergent_mood_variations(best_mood, hormone_levels)
    intensity = max(0.0, min(1.0, abs(best_score)))
    return final_mood, intensity

def adjust_hormones(event: str = None) -> Dict[str, float]:
    """Adjust hormone levels in response to legacy events (kept for compatibility)."""
    hormones = load_hormone_levels()
    print(f"[Legacy Hormone Adjust]: Before adjustment - {hormones}")
    print(f"[Legacy Hormone Adjust]: Processing event '{event}'")
    
    original_hormones = hormones.copy()
    
    if event == "positive_feedback":
        hormones["dopamine"] = min(1.0, hormones["dopamine"] + 0.1)
        hormones["serotonin"] = min(1.0, hormones["serotonin"] + 0.05)
        print(f"[Legacy Hormone Adjust]: Applied positive_feedback - dopamine +0.1, serotonin +0.05")
    elif event == "stress":
        hormones["cortisol"] = min(1.0, hormones["cortisol"] + 0.1)
        hormones["serotonin"] = max(0.0, hormones["serotonin"] - 0.05)
        print(f"[Legacy Hormone Adjust]: Applied stress - cortisol +0.1, serotonin -0.05")
    elif event == "social_connection":
        hormones["oxytocin"] = min(1.0, hormones["oxytocin"] + 0.1)
        hormones["dopamine"] = min(1.0, hormones["dopamine"] + 0.05)
        print(f"[Legacy Hormone Adjust]: Applied social_connection - oxytocin +0.1, dopamine +0.05")
    elif event == "isolation":
        hormones["oxytocin"] = max(0.0, hormones["oxytocin"] - 0.1)
        hormones["cortisol"] = min(1.0, hormones["cortisol"] + 0.05)
        print(f"[Legacy Hormone Adjust]: Applied isolation - oxytocin -0.1, cortisol +0.05")
    elif event == "achievement":
        hormones["dopamine"] = min(1.0, hormones["dopamine"] + 0.15)
        hormones["serotonin"] = min(1.0, hormones["serotonin"] + 0.1)
        print(f"[Legacy Hormone Adjust]: Applied achievement - dopamine +0.15, serotonin +0.1")
    elif event == "disappointment":
        hormones["dopamine"] = max(0.0, hormones["dopamine"] - 0.1)
        hormones["serotonin"] = max(0.0, hormones["serotonin"] - 0.08)
        print(f"[Legacy Hormone Adjust]: Applied disappointment - dopamine -0.1, serotonin -0.08")
    else:
        print(f"[Legacy Hormone Adjust]: Unknown event '{event}', no adjustments made")
    
    # Natural decay toward baseline
    for hormone in hormones:
        if hormones[hormone] > 0.5:
            hormones[hormone] = max(0.5, hormones[hormone] - 0.01)
        elif hormones[hormone] < 0.5:
            hormones[hormone] = min(0.5, hormones[hormone] + 0.01)
    
    # Check if any changes were made
    changes_made = any(abs(hormones[h] - original_hormones[h]) > 0.001 for h in hormones)
    print(f"[Legacy Hormone Adjust]: Changes made: {changes_made}")
    print(f"[Legacy Hormone Adjust]: After adjustment - {hormones}")
    
    save_hormone_levels(hormones)
    return hormones

def get_mood_context(mood_name: str, intensity: float) -> Dict[str, any]:
    """Provide additional context about the current mood state."""
    context = {
        "mood": mood_name,
        "intensity": intensity,
        "is_hybrid": "-" in mood_name and mood_name not in ["well-being", "self-esteem"],
        "is_emergent": any(prefix in mood_name for prefix in ["undefined", "manic", "melancholic", "overwhelmed", "numb"]),
        "stability": "low" if intensity > 0.8 else "medium" if intensity > 0.4 else "high"
    }
    return context
