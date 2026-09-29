"""坐骑亲密度与驯养系统 - 含6个bug"""
from dataclasses import dataclass, field

@dataclass
class Mount:
    mid: str
    name: str
    intimacy: int = 0
    max_intimacy: int = 1000
    taming_bonus: dict = field(default_factory=dict)
    taming_count: int = 0

class IntimacySystem:
    def __init__(self):
        self.mounts: dict[str, Mount] = {}
        self.food_preferences: dict[str, list] = {}  # mount_id -> [liked foods]
        self.last_interaction: dict[str, float] = {}  # bug5: 只看离线

    def add_intimacy(self, mid: str, action: str, amount: int):
        # bug1: 挂机也加
        self.mounts[mid].intimacy += amount

    def get_taming_bonus(self, mid: str) -> dict:
        # bug2: 驯养效果固定
        return {"speed": 5}

    def get_intimacy_action(self, level: int) -> str:
        # bug3: 无专属互动
        return "pet"

    def get_food_bonus(self, mid: str, food: str) -> int:
        # bug4: 无喜好系统
        return 10

    def update_intimacy_decay(self, mid: str, online: bool, hours: float):
        # bug5: 在线也掉
        self.mounts[mid].intimacy -= int(hours * 5)

    def tame(self, mid: str) -> tuple[bool, str]:
        # bug6: 失败无保底
        if self.mounts[mid].taming_count < 10:
            self.mounts[mid].taming_count += 1
            return True, "success"
        return False, "failed"
