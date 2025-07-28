# emotion_nsfw_checker.py

from transformers import pipeline

# 1. Load GoEmotions (multi-label emotion classifier)
goemotions = pipeline(
    "text-classification",
    model="bhadresh-savani/distilbert-base-uncased-emotion",
    top_k=None  # Avoid deprecation warning, get all emotions
)

# 2. Load Toxicity detector (Unitary multi-label model)
toxicity_detector = pipeline(
    "text-classification",
    model="unitary/unbiased-toxic-roberta",
    top_k=None  # Get all relevant labels with scores
)

def detect_emotion(text):
    results = goemotions(text)[0]
    # Filter out low-confidence labels
    emotions = [r for r in results if r["score"] > 0.2]
    return sorted(emotions, key=lambda x: -x["score"])

def detect_toxicity(text):
    results = toxicity_detector(text)[0]
    # Filter out low confidence toxic labels
    toxic_labels = [r for r in results if r["score"] > 0.5]
    return sorted(toxic_labels, key=lambda x: -x["score"])

def main():
    print("🤖 Emotion + Toxicity Classifier")
    while True:
        user_input = input("\n👤 You: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        # Emotion detection
        emotions = detect_emotion(user_input)
        print("\n💬 Detected Emotions:")
        for e in emotions:
            print(f" - {e['label'].capitalize()} ({e['score']:.2f})")

        # Toxicity detection
        toxic = detect_toxicity(user_input)

        if toxic:
            print("\n🚨 Toxicity Detected:")
            for t in toxic:
                print(f" - {t['label'].capitalize()} ({t['score']:.2f})")
        else:
            print("\n✅ No significant toxicity detected (score < 0.5).")

if __name__ == "__main__":
    main()
