import matplotlib.pyplot as plt


def plot_samples_per_sign(stats):
    data = stats["samples_per_sign"]
    if not data:
        print("No data to plot.")
        return

    words = list(data.keys())
    counts = list(data.values())

    plt.figure(figsize=(10, 5))
    plt.bar(words, counts)
    plt.xlabel("Sign")
    plt.ylabel("Samples")
    plt.title("Number of Samples per Sign")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


def plot_hand_distribution(stats):
    data = stats["signs_per_hand"]
    if not data:
        print("No data to plot.")
        return

    plt.figure(figsize=(6, 6))
    plt.pie(data.values(), labels=data.keys(), autopct="%1.0f%%")
    plt.title("Hand Distribution")
    plt.show()