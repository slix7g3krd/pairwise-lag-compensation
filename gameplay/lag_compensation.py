"""第 62 批：高延迟玩家打移动靶，命中判定落在靶子身后半米，低延迟玩家却打不中...

本模块给出延迟补偿所需的最小纯函数契约：
按实际 ping 与 tick 率（含子 tick 插值）回溯、环形历史窗口、
时钟同步、重传去重、移动平台换算、服务器权威近战、公平回退、
蒙皮命中盒/原点换算，以及 hitscan 与投射物共用的时钟。
"""


def tick_window(ping_ms, tick_rate):
    """回溯 tick 窗口：把单程 ping 换算成 tick 数（四舍五入）。"""
    if tick_rate <= 0:
        raise ValueError("tick_rate must be positive")
    return int(round(ping_ms * tick_rate / 1000.0))


def rewind_tick(current, ping_ms, tick_rate):
    """回溯目标 tick：当前 tick 减去按实际 ping 得到的窗口。"""
    return current - tick_window(ping_ms, tick_rate)


def clock_offset(client, server):
    """时钟同步：客户端时钟相对服务器时钟的偏移。"""
    return client - server


def dedupe_shot(sequence, seen):
    """重传去重：序列号已处理过则丢弃，返回是否为新射击。"""
    return sequence not in seen


def platform_rewind(position, delta):
    """移动平台回退：把平台位移叠加到历史位置上，保持相对关系。"""
    return (position[0] + delta[0], position[1] + delta[1])


def melee_authority(client, server):
    """近战服务器判定：伤害只认服务器结果，客户端结果仅作参考。"""
    return server


def fairness_delay(ping_a, ping_b):
    """公平回退：双方取较小 ping，避免高延迟玩家被过度优待。"""
    return min(ping_a, ping_b)


def sub_tick_alpha(time, tick_seconds):
    """子 tick 采样：返回当前时间落在两个 tick 之间的插值系数 [0, 1)。"""
    if tick_seconds <= 0:
        raise ValueError("tick_seconds must be positive")
    return (time % tick_seconds) / tick_seconds


def projectile_clock(hitscan_clock, projectile_clock):
    """投射物时钟：两套时钟一致时才可共享时间基准。"""
    return "shared" if hitscan_clock == projectile_clock else "mismatch"


def origin_shift(position, origin):
    """原点换算：把历史坐标从世界原点转换到重置后的局部原点。"""
    return (position[0] - origin[0], position[1] - origin[1])


def ring_slot(tick, size):
    """环形槽位：tick 在大小为 size 的环形缓冲中的下标。"""
    if size <= 0:
        raise ValueError("size must be positive")
    return tick % size


def interpolate(start, end, alpha):
    """插值：按 alpha 在 start 与 end 之间线性取值（alpha 需在 [0, 1]）。"""
    if not 0.0 <= alpha <= 1.0:
        raise ValueError("alpha must be within [0, 1]")
    return start + (end - start) * alpha


def anticheat_allow(flagged, legitimate):
    """反作弊白名单：回溯命中本身不是异常，合法高延迟玩家应放行。"""
    return legitimate or not flagged


def rewind_window_size(ticks, ring):
    """窗口上限：历史窗口不能超过环形缓冲容量。"""
    return min(ticks, ring)


def history_valid(tick, oldest, newest):
    """历史有效性：目标 tick 必须落在已记录的 [oldest, newest] 区间内。"""
    return oldest <= tick <= newest
