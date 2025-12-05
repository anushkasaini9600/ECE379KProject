import matplotlib.pyplot as plt
normal_sessions = 100         
brute_force_alerts = 45        
scraping_alerts = 80          
admin_alerts = 20              

labels = [
    "Normal User Behavior",
    "Brute Force Attack",
    "Scraping Attack",
    "Direct Admin Access Attack",
]

values = [
    normal_sessions,
    brute_force_alerts,
    scraping_alerts,
    admin_alerts,
]

plt.figure(figsize=(8, 5))
plt.bar(labels, values)
plt.ylabel("Count (sessions / alerts)")
plt.title("Experiment 1: Detecting Abnormal API Sequences")
plt.xticks(rotation=15, ha="right")
plt.tight_layout()
plt.savefig("experiment1_bar_chart.png", dpi=300)
plt.show()
