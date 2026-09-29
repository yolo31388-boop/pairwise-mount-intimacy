"""坐骑亲密度与驯养系统 - 红态测试"""
import pytest, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mount.intimacy import IntimacySystem, Mount

class TestActionRequirement:
    def test_idle_does_not_increase_intimacy(self):
        insys = IntimacySystem()
        insys.mounts["m1"] = Mount("m1", "horse")
        before = insys.mounts["m1"].intimacy
        # 挂机不应该加亲密度
        assert hasattr(insys, "is_valid_action")
        assert insys.is_valid_action("idle") == False  # bug1: 可能有效

class TestTamingScaling:
    def test_more_taming_gives_better_bonus(self):
        insys = IntimacySystem()
        insys.mounts["m1"] = Mount("m1", "horse", taming_count=1)
        insys.mounts["m2"] = Mount("m2", "horse", taming_count=10)
        b1 = insys.get_taming_bonus("m1")
        b10 = insys.get_taming_bonus("m2")
        assert b10["speed"] > b1["speed"]  # bug2: 都是5

class TestUniqueActions:
    def test_high_intimacy_unlocks_unique_action(self):
        insys = IntimacySystem()
        a0 = insys.get_intimacy_action(0)
        a1000 = insys.get_intimacy_action(1000)
        assert a1000 != a0  # bug3: 都是"pet"

class TestFoodPreference:
    def test_liked_food_gives_more_intimacy(self):
        insys = IntimacySystem()
        insys.mounts["m1"] = Mount("m1", "horse")
        insys.food_preferences["m1"] = ["apple", "carrot"]
        bonus_liked = insys.get_food_bonus("m1", "apple")
        bonus_disliked = insys.get_food_bonus("m1", "rock")
        assert bonus_liked > bonus_disliked  # bug4: 都是10

class TestDecayOnlyOffline:
    def test_online_no_intimacy_decay(self):
        insys = IntimacySystem()
        insys.mounts["m1"] = Mount("m1", "horse", intimacy=500)
        before = insys.mounts["m1"].intimacy
        insys.update_intimacy_decay("m1", online=True, hours=10)
        assert insys.mounts["m1"].intimacy == before  # bug5: 在线也掉

class TestTamingPity:
    def test_failed_taming_has_pity(self):
        insys = IntimacySystem()
        insys.mounts["m1"] = Mount("m1", "horse")
        # 连续失败应该提升成功率
        assert hasattr(insys, "tame_success_rate")
        # 失败后应该有保底
        results = [insys.tame("m1") for _ in range(20)]
        success = sum(1 for r, _ in results if r)
        assert success > 0  # bug6: 可能全失败
