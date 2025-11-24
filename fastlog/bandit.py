import random
import time

# ==========================================================
# Base Policy Class
# ==========================================================

class BanditPolicy:
    """
    Base class for all bandit strategies.
    """

    def choose_block_size(self, candidates, history):
        raise NotImplementedError

    def update_reward(self, block_size, compress_time, ratio):
        pass


# ==========================================================
# OFF MODE (Static block size)
# ==========================================================

class OffBandit(BanditPolicy):
    """
    Bandit disabled. Always returns a fixed block size.
    """

    def __init__(self, default=1024 * 1024):
        self.default = default

    def choose_block_size(self, candidates, history):
        return self.default


# ==========================================================
# ONE-SHOT BANDIT (Safe, fixed after first N samples)
# ==========================================================

class OneShotBandit(BanditPolicy):
    """
    Runs each candidate ONCE on the first few blocks.
    Then selects the winner for the rest of the stream.
    """

    def __init__(self, ratio_weight=0.7, speed_weight=0.3):
        self.ratio_weight = ratio_weight
        self.speed_weight = speed_weight
        self.selected = None

    def score(self, ratio, speed):
        return (ratio * self.ratio_weight) + (speed * self.speed_weight)

    def choose_block_size(self, candidates, history):
        # Winner already chosen → reuse
        if self.selected is not None:
            return self.selected

        # No history yet → return middle candidate (usually 1MB)
        if len(history) == 0:
            return candidates[len(candidates) // 2]

        # Still testing each candidate
        if len(history) < len(candidates):
            return candidates[len(history)]

        # All candidates evaluated → choose best
        scored = []
        for entry in history:
            bs = entry["block_size"]
            ratio = entry["ratio"]
            speed = entry["speed"]
            scored.append((self.score(ratio, speed), bs))

        scored.sort(reverse=True)

        self.selected = scored[0][1]
        return self.selected


# ==========================================================
# FULL BANDIT (Adaptive epsilon-greedy)
# ==========================================================

class FullBandit(BanditPolicy):
    """
    Adaptive bandit; learns best block size continuously.
    """

    def __init__(self, epsilon=0.1, ratio_weight=0.7, speed_weight=0.3):
        self.epsilon = epsilon
        self.ratio_weight = ratio_weight
        self.speed_weight = speed_weight

        self.values = {}
        self.counts = {}

    def score(self, ratio, speed):
        return (ratio * self.ratio_weight) + (speed * self.speed_weight)

    def update_reward(self, block_size, compress_time, ratio):
        speed = 1.0 / compress_time
        reward = self.score(ratio, speed)

        if block_size not in self.values:
            self.values[block_size] = reward
            self.counts[block_size] = 1
        else:
            n = self.counts[block_size]
            self.values[block_size] = (self.values[block_size] * n + reward) / (n + 1)
            self.counts[block_size] = n + 1

    def choose_block_size(self, candidates, history):
        # Random exploration
        if random.random() < self.epsilon:
            return random.choice(candidates)

        # Exploit best known
        best, best_val = None, float("-inf")
        for bs in candidates:
            val = self.values.get(bs, 0)
            if val > best_val:
                best_val = val
                best = bs

        # No data yet → choose middle
        if best is None:
            return candidates[len(candidates) // 2]

        return best

