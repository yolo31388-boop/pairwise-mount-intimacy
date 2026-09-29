"""坐骑亲密度与驯养系统"""
import random
import time
from dataclasses import dataclass, field

VALID_ACTIONS = ("feed", "pet", "ride", "battle")
ACTION_INTIMACY = {"feed": 10, "pet": 5, "ride": 8, "battle": 15}

LIKED_FOOD_BONUS = 20
NORMAL_FOOD_BONUS = 10
DISLIKED_FOOD_BONUS = 2

DECAY_GRACE_HOURS = 24.0
DECAY_PER_HOUR = 2

BASE_SUCCESS_RATE = 0.6
PITY_BONUS_PER_FAIL = 0.15
PITY_GUARANTEE_FAILS = 4
MATERIAL_REFUND_RATE = 0.5
MAX_TAMING = 10

INTIMACY_LEVELS = (
    (0, "stranger"),
    (200, "familiar"),
    (500, "close"),
    (800, "intimate"),
    (1000, "soulbound"),
)
INTIMACY_ACTIONS = (
    "pet",
    "nuzzle",
    "fetch_play",
    "ride_trick",
    "soul_dance",
)
INTIMACY_VOICES = (
    "...",
    "neigh_softly",
    "happy_whinny",
    "excited_roar",
    "eternal_bond",
)


@dataclass
class Mount:
    mid: str
    name: str
    intimacy: int = 0
    max_intimacy: int = 1000
    taming_bonus: dict = field(default_factory=dict)
    taming_count: int = 0
    consecutive_failures: int = 0
    materials: dict = field(default_factory=dict)


class IntimacySystem:
    def __init__(self, rng=None):
        self.mounts: dict[str, Mount] = {}
        self.food_preferences: dict[str, list] = {}
        self.food_dislikes: dict[str, list] = {}
        self.last_interaction: dict[str, float] = {}
        self._rng = rng or random.Random()

    def is_valid_action(self, action: str) -> bool:
        return action in VALID_ACTIONS

    def add_intimacy(self, mid: str, action: str, amount: int | None = None):
        if not self.is_valid_action(action):
            return 0
        if amount is None:
            amount = ACTION_INTIMACY[action]
        mount = self.mounts[mid]
        mount.intimacy = min(mount.max_intimacy, mount.intimacy + amount)
        self.last_interaction[mid] = time.time()
        return amount

    def get_intimacy_level(self, intimacy: int) -> int:
        level = 0
        for idx, (threshold, _name) in enumerate(INTIMACY_LEVELS):
            if intimacy >= threshold:
                level = idx
        return level

    def get_intimacy_action(self, level: int) -> str:
        idx = self.get_intimacy_level(level)
        return INTIMACY_ACTIONS[idx]

    def get_intimacy_voice(self, level: int) -> str:
        idx = self.get_intimacy_level(level)
        return INTIMACY_VOICES[idx]

    def is_max_intimacy_interaction(self, intimacy: int) -> bool:
        return self.get_intimacy_level(intimacy) == len(INTIMACY_LEVELS) - 1

    def get_taming_bonus(self, mid: str) -> dict:
        count = self.mounts[mid].taming_count
        bonus: dict[str, int] = {"speed": min(count * 5, 50)}
        if count >= 3:
            bonus["stamina"] = min(count * 3, 30)
        if count >= 5:
            bonus["strength"] = min(count * 4, 40)
        if count >= 7:
            bonus["crit"] = min(count * 2, 20)
        if count >= MAX_TAMING:
            bonus["aura"] = 10
        return bonus

    def get_food_bonus(self, mid: str, food: str) -> int:
        if food in self.food_preferences.get(mid, []):
            return LIKED_FOOD_BONUS
        if food in self.food_dislikes.get(mid, []):
            return DISLIKED_FOOD_BONUS
        return NORMAL_FOOD_BONUS

    def feed(self, mid: str, food: str) -> int:
        gained = self.get_food_bonus(mid, food)
        self.add_intimacy(mid, "feed", gained)
        return gained

    def update_intimacy_decay(self, mid: str, online: bool, hours: float):
        if online or hours <= DECAY_GRACE_HOURS:
            return 0
        decay = int((hours - DECAY_GRACE_HOURS) * DECAY_PER_HOUR)
        mount = self.mounts[mid]
        mount.intimacy = max(0, mount.intimacy - decay)
        return decay

    def tame_success_rate(self, mid: str) -> float:
        mount = self.mounts[mid]
        if mount.consecutive_failures >= PITY_GUARANTEE_FAILS - 1:
            return 1.0
        return min(
            0.99,
            BASE_SUCCESS_RATE + mount.consecutive_failures * PITY_BONUS_PER_FAIL,
        )

    def tame(self, mid: str, materials: dict | None = None) -> tuple[bool, str]:
        mount = self.mounts[mid]
        if mount.taming_count >= MAX_TAMING:
            return False, "max_taming_level"

        if materials:
            for item, qty in materials.items():
                mount.materials[item] = mount.materials.get(item, 0) + qty

        if self._rng.random() <= self.tame_success_rate(mid):
            mount.taming_count += 1
            mount.consecutive_failures = 0
            mount.taming_bonus = self.get_taming_bonus(mid)
            return True, "success"

        mount.consecutive_failures += 1
        refunded = {}
        if materials:
            for item, qty in materials.items():
                kept = int(qty * MATERIAL_REFUND_RATE)
                if kept:
                    refunded[item] = kept
        if mount.consecutive_failures >= PITY_GUARANTEE_FAILS - 1:
            return False, f"failed_pity_guaranteed_next:{mount.consecutive_failures}"
        return False, f"failed_pity_bonus:{mount.consecutive_failures}:{refunded}"
