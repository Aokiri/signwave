from client.client import SignLanguageClient
from client.plots import plot_samples_per_sign, plot_hand_distribution

api = SignLanguageClient()

# Query existing data (loaded by seed.py)
all_signs = api.get_signs()
print(f"Total signs in DB: {len(all_signs)}")

# Filter by hand
right_hand = api.get_signs(hand="right")
print(f"Right-hand signs: {len(right_hand)}")
for s in right_hand[:5]:
    print(f"  - {s['word']}: {s['description']}")

# Check samples for a specific sign
if all_signs:
    first = all_signs[0]
    samples = api.get_samples(first["id"])
    print(f"\nSamples for '{first['word']}': {len(samples)}")

# Complete CRUD example: create, read, delete
new_sign = api.create_sign("demo_test", "both", description="Test sign for demo purposes")
print(f"\nCreated sign: {new_sign}")
api.delete_sign(new_sign["id"])
print("Deleted demo sign.")

# Plots and statistics
stats = api.get_stats()
print(f"\nStats: {stats['total_signs']} signs, {stats['total_samples']} samples")

plot_samples_per_sign(stats)
plot_hand_distribution(stats)

if __name__ == "__main__":
    instructions: str = """
How to run: 
You need to use two terminals:

# 1st Terminal:
uvicorn server.app:app --reload

# 2nd Terminal:
python demo.py
"""
    print(instructions)