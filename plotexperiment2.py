import matplotlib.pyplot as plt

thresholds = [0.01, 0.03, 0.05, 0.10, 0.20]
false_positive_rates = [0.0, 0.0, 0.0, 0.0, 0.47]

plt.figure(figsize=(8, 5))
plt.plot(thresholds, false_positive_rates, marker="o")
plt.xlabel("Transition probability threshold")
plt.ylabel("False positive rate (per normal session)")
plt.title("Experiment 2: False Positive Rate vs Threshold")
plt.grid(True)
plt.tight_layout()
plt.savefig("experiment2_fpr.png", dpi=300)
plt.show()
