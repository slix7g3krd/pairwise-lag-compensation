import pytest
from gameplay import lag_compensation as mod

CASES = [
    ("window", 'm.tick_window(100, 30) == 3'),
    ("rewind", 'm.rewind_tick(10, 100, 30) == 7'),
    ("offset", 'm.clock_offset(5, 4) == 1'),
    ("dedupe", 'm.dedupe_shot(1, [2]) is True'),
    ("platform", 'm.platform_rewind((1.0, 2.0), (3.0, 4.0)) == approx((4.0, 6.0))'),
    ("melee", 'm.melee_authority(1, 2) == 2'),
    ("fair", 'm.fairness_delay(50, 100) == 50'),
    ("alpha", 'm.sub_tick_alpha(1.5, 1) == approx(0.5)'),
    ("projectile", 'm.projectile_clock("hitscan", "hitscan") == "shared"'),
    ("origin", 'm.origin_shift((10.0, 10.0), (2.0, 3.0)) == approx((8.0, 7.0))'),
    ("ring", 'm.ring_slot(5, 3) == 2'),
    ("interp", 'm.interpolate(0, 10, 0.5) == approx(5.0)'),
    ("anticheat", 'm.anticheat_allow(False, True) is True'),
    ("window_cap", 'm.rewind_window_size(20, 10) == 10'),
    ("history", 'm.history_valid(5, 3, 8) is True')
]

@pytest.mark.parametrize("name,expr", CASES, ids=[c[0] for c in CASES])
def test_contract(name, expr):
    assert eval(expr, {"m": mod, "approx": pytest.approx})
