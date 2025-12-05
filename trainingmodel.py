import json
from collections import Counter

#tracks how often a user moves from one API state to another
class TransitionModel:
    #stores count
    def __init__(self):
        self.transitions = Counter()
        self.state_counts = Counter()

    #updates transition table when a new state is called
    def observe(self, prev_state: str, next_state: str):
        self.transitions[(prev_state, next_state)] += 1
        self.state_counts[prev_state] += 1

    #computes probability of transition
    def transition_probability(self, prev_state: str, next_state: str) -> float:
        total = self.state_counts[prev_state]
        if total == 0:
            return 0.0
        return self.transitions[(prev_state, next_state)] / total

    #checks if transition is suspicious based on threshold
    def is_suspicious(self, prev_state: str, next_state: str,
                      prob_threshold: float) -> bool:
        if self.state_counts[prev_state] == 0:
            return True
        p = self.transition_probability(prev_state, next_state)
        return p < prob_threshold

    #saves model to file
    def save(self, path: str):
        data = {
            "transitions": {
                f"{a}|||{b}": c for (a, b), c in self.transitions.items()
            },
            "state_counts": dict(self.state_counts),
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    #loads model from file
    @classmethod
    def load(cls, path: str):
        model = cls()
        with open(path, "r") as f:
            data = json.load(f)
        for key, c in data["transitions"].items():
            a, b = key.split("|||", 1)
            model.transitions[(a, b)] = c
        #state count
        model.state_counts.update(data["state_counts"])
        return model
