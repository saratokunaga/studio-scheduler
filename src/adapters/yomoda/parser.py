# src/adapters/yomoda/parser.py

from __future__ import annotations
from typing import Dict, Any, Tuple


def _iso_from_slash(date_slash: str) -> str:
    # '2026/02/17' -> '2026-02-17'
    y, m, d = date_slash.split("/")
    return f"{y}-{m}-{d}"


def parse_to_worcle_like(
    ajax_json: Dict[str, Any],
    target_date_slash: str,
    start_hour: int = 9,
) -> Dict[str, Any]:
    """
    worcle互換:
      {
        "StartHour": 9,
        "ReserveData": { "<studio_id>": "<31文字 day_bits>" , ... },
        "StudioMeta": { "<studio_id>": "<studio_name>" , ... },  # おまけ（表示用）
      }

    day_bits(31文字)の意味（worcleのsearch.py互換）:
      index 0..29 = 9:00〜24:00 の30分刻み
      index 30     = 深夜枠フラグ（ここは当面 '1' 固定）
    """

    date_iso = _iso_from_slash(target_date_slash)
    wta = ajax_json.get("week_time_array", {})
    if date_iso not in wta:
        raise ValueError(f"week_time_arrayに日付がありません: {date_iso}")

    day_obj = wta[date_iso]
    data = day_obj.get("data", {})  # { "0900_1": [..], ... }

    # まず「その日の各スタジオの 1時間枠 availability」を作る
    # hour_map[studio_id][st_hour(9..22)] = True/False
    hour_map: Dict[str, Dict[int, bool]] = {}
    studio_name: Dict[str, str] = {}

    for time_key, items in data.items():
        # "0900_1" -> "0900"
        sttime = time_key.split("_")[0]
        if len(sttime) != 4:
            continue

        st_h = int(sttime[:2])
        st_m = int(sttime[2:])
        if st_m != 0:
            # よもだは基本 :00 単位っぽいので、念のため
            continue

        # worcle互換のため 9時未満は捨てる（start_hourで制御）
        if st_h < start_hour:
            continue

        for it in items:
            # 予約可/在庫あり を空きとみなす
            # work_disable_flg_free=1 が「選択可能」っぽい挙動、stock_num>=1 が空き
            free = (int(it.get("work_disable_flg_free", 0)) == 1) and (int(it.get("stock_num", 0)) >= 1)

            # スタジオID（ページによってキー名が違う可能性があるので候補列挙）
            sid = (
                it.get("ist_no")
                or it.get("reserve_ist_no")
                or it.get("institution_no")
                or it.get("menu_ist_no")
            )
            if sid is None:
                continue
            sid = str(sid)

            # 名前（あるなら）
            nm = it.get("menu_name") or it.get("institution_name") or ""
            if nm and sid not in studio_name:
                studio_name[sid] = str(nm)

            hour_map.setdefault(sid, {})
            # 1時間枠の開始時刻をキーにする（09:00なら 9）
            hour_map[sid][st_h] = free

    # 次に、worcle互換の 31bit を組み立てる
    # 9:00〜24:00 の30分×30コマ + 深夜1コマ
    reserve_data: Dict[str, str] = {}

    for sid, hm in hour_map.items():
        bits = []

        # 9:00〜23:00 は hour_map を参照（各1時間を30分×2で複製）
        # 23:00〜24:00 はデータが無いことが多いので '1'（埋まってる扱い）で安全側
        for h in range(start_hour, 24):
            if h == 23:
                # 23:00〜24:00（2コマ） -> 安全側に埋める
                bits.extend(["1", "1"])
                continue

            free1h = hm.get(h, False)
            # 空きなら '0'、埋まりなら '1'
            bits.extend(["0" if free1h else "1", "0" if free1h else "1"])

        # ここまでで 30コマのはず
        if len(bits) != 30:
            # 想定外のstart_hour等
            raise RuntimeError(f"bits length mismatch: {len(bits)}")

        # 深夜bit（よもだは別メニューなので当面は '1' 固定＝空き判定で誤検知しない）
        bits.append("1")

        reserve_data[sid] = "".join(bits)

    return {
        "StartHour": start_hour,
        "ReserveData": reserve_data,
        "StudioMeta": studio_name,
        "TargetDateISO": date_iso,
    }
