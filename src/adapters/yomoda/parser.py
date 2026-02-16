def parse_all(raw_all):

    parsed = []

    for studio_name, raw in raw_all.items():

        week = raw["week_time_array"]

        for date, date_data in week.items():

            slots = date_data["data"]

            for key, arr in slots.items():

                for slot in arr:

                    if slot["work_disable_flg"] == 1:
                        continue

                    time = slot["sttime_view"]

                    hour = int(time[:2])

                    period = "night" if hour >= 23 or hour < 7 else "day"

                    parsed.append({

                        "studio": studio_name,
                        "date": date,
                        "time": time,
                        "period": period,

                    })

    return parsed
