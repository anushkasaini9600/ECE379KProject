import sys
import re

if len(sys.argv) < 2:
    print("Usage: python falsepositives.py <logfile>")
    sys.exit(1)

logfile = sys.argv[1]

TOTAL_NORMAL_SESSIONS = 100

suspicious_sessions = set()

with open(logfile, "r") as f:
    for line in f:
        if "[SUSPICIOUS]" not in line:
            continue
        m = re.search(r"'session': '([^']+)'", line)
        if m:
            suspicious_sessions.add(m.group(1))

num_flagged_sessions = len(suspicious_sessions)
fpr = num_flagged_sessions / TOTAL_NORMAL_SESSIONS

print(f"Log file: {logfile}")
print(f"Normal sessions (total): {TOTAL_NORMAL_SESSIONS}")
print(f"Sessions flagged as suspicious: {num_flagged_sessions}")
print(f"False positive rate (per session): {fpr:.3f}")
