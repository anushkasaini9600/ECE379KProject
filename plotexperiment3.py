import matplotlib.pyplot as plt

backend_mean = 1.03
proxy_mean   = 2.27

backend_p95  = 1.10
proxy_p95    = 2.48

labels = ["Direct Backend", "Through Monitor Proxy"]
means  = [backend_mean, proxy_mean]
p95    = [backend_p95, proxy_p95]

plt.figure(figsize=(10,6))
bars = plt.bar(labels, means, color=["steelblue", "coral"])

plt.title("Experiment 3:Mean Latency", fontsize=16)
plt.ylabel("Latency (ms)")
plt.ylim(0, max(means) + 1)

for i, val in enumerate(means):
    plt.text(i, val + 0.05, f"{val:.2f} ms", ha='center', fontsize=12)

plt.show()


plt.figure(figsize=(10,6))
bars = plt.bar(labels, p95, color=["steelblue", "coral"])

plt.title("Experiment 3: 95th Percentile", fontsize=16)
plt.ylabel("Latency (ms)")
plt.ylim(0, max(p95) + 1)

for i, val in enumerate(p95):
    plt.text(i, val + 0.05, f"{val:.2f} ms", ha='center', fontsize=12)

plt.show()
