"""坐骑亲密度与驯养系统"""
import random
from dataclasses import dataclass, field

# 有效的互动行为：挂机(idle)不算互动
VALID_ACTIONS = {"feed", "pet", "ride", "battle"}

# 亲密度等级解锁的专属互动动作与语音
INTIMACY_ACTIONS = [
    (0, "pet"),
    (200, "nuzzle"),
    (400, "play_trick"),
    (600, "sing_duet"),
    (800, "soul_bond"),
    (1000, "legendary_bond"),  # 满级特殊互动
]

# 驯养次数上限，超过后增益不再增长
TAMING_CAP = 10

# 驯养保底：连续失败达到该次数后必定成功
TAMING_PITY = 5


@dataclass
class Mount:
    mid: str
    name: str
    intimacy: int = 0
    max_intimacy: int = 1000
    taming_bonus: dict = field(default_factory=dict)
    taming_count: int = 0
    taming_fail_streak: int = 0

class IntimacySystem:
    def __init__(self):
        self.mounts: dict[str, Mount] = {}
        self.food_preferences: dict[str, list] = {}  # mount_id -> [liked foods]
        self.last_interaction: dict[str, float] = {}
        self.rng = random.Random()

    def is_valid_action(self, action: str) -> bool:
        # fix1: 只有喂食/抚摸/骑乘/战斗等真实互动才有效，挂机不算
        return action in VALID_ACTIONS

    def add_intimacy(self, mid: str, action: str, amount: int):
        # fix1: 亲密度按互动行为综合计算，挂机不加
        if not self.is_valid_action(action):
            return
        mount = self.mounts[mid]
        mount.intimacy = min(mount.max_intimacy, mount.intimacy + amount)

    def get_taming_bonus(self, mid: str) -> dict:
        # fix2: 驯养效果按次数递增且有上限
        count = min(self.mounts[mid].taming_count, TAMING_CAP)
        return {
            "speed": 5 + count * 2,
            "stamina": count * 3,
            "strength": count,
        }

    def get_intimacy_action(self, level: int) -> str:
        # fix3: 亲密度等级解锁专属动作，满级有特殊互动
        action = INTIMACY_ACTIONS[0][1]
        for threshold, name in INTIMACY_ACTIONS:
            if level >= threshold:
                action = name
        return action

    def get_food_bonus(self, mid: str, food: str) -> int:
        # fix4: 食物有喜好度，喜欢的加更多，讨厌的加很少
        liked = self.food_preferences.get(mid, [])
        if food in liked:
            return 30
        return 2

    def update_intimacy_decay(self, mid: str, online: bool, hours: float):
        # fix5: 只在长期不互动(离线)时缓慢下降，在线不掉
        if online:
            return
        mount = self.mounts[mid]
        mount.intimacy = max(0, mount.intimacy - int(hours * 2))

    def tame_success_rate(self, mid: str) -> float:
        # fix6: 连续失败提升下次成功率，达到保底次数必定成功
        mount = self.mounts[mid]
        if mount.taming_fail_streak >= TAMING_PITY:
            return 1.0
        return min(1.0, 0.5 + mount.taming_fail_streak * 0.1)

    def tame(self, mid: str) -> tuple[bool, str]:
        # fix6: 失败保留部分材料并提升下次成功率，有保底机制
        mount = self.mounts[mid]
        if self.rng.random() < self.tame_success_rate(mid):
            mount.taming_count += 1
            mount.taming_fail_streak = 0
            return True, "success"
        mount.taming_fail_streak += 1
        return False, "failed: materials partially kept, success rate increased"
