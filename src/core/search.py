def idx_for_normal(hour: int, minute: int, start_hour: int = 9) -> int:
    """
    通常枠(9:00-24:00)の時刻→インデックス(0-29)
    24:00ちょうどは「終端」なので 30 を返す（スライスのend用）
    """
    # 通常枠の範囲チェック：ここで深夜が混ざるのを禁止する
    if hour < start_hour or hour > 24 or (hour == 24 and minute > 0):
        raise ValueError("通常枠は 9:00〜24:00 の範囲のみ")

    # 24:00ちょうどはマスではなく終点（end側で使う）
    if hour == 24 and minute == 0:
        return 30

    # start_hour(通常9:00)からの経過分
    minutes = (hour - start_hour) * 60 + minute

    # 30分刻みじゃない入力を弾く（仕様を守る）
    if minutes % 30 != 0:
        raise ValueError("30分刻みのみ対応")

    # 30分 = 1マスなので、30で割ればインデックスになる
    return minutes // 30  # 0..29


def is_free_normal(day_bits: str, start_h: int, start_m: int, end_h: int, end_m: int, start_hour: int = 9) -> bool:
    """
    通常枠(9-24)だけで空き判定。深夜枠(day_bits[30])は一切見ない。
    [start, end) の範囲が全部 '0' なら空き。
    """
    if len(day_bits) != 31:
        raise ValueError("day_bitsは31文字想定")

    s = idx_for_normal(start_h, start_m, start_hour)
    e = idx_for_normal(end_h, end_m, start_hour)

    # 指定区間のマスが全部0なら空き
    return all(ch == "0" for ch in day_bits[s:e])


def is_free_midnight(day_bits: str) -> bool:
    """
    深夜枠(24-30)が空きかどうか。最後の1文字だけを見る。
    """
    if len(day_bits) != 31:
        raise ValueError("day_bitsは31文字想定")
    return day_bits[30] == "0"
