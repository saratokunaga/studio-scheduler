from src.adapters.worcle import fetch_mydata
from src.core.search import is_free_normal, is_free_midnight  # ← ここ重要

URL = "https://www.studioworcle.com/ichigaya/"
data = fetch_mydata(URL)

start_hour = data["StartHour"]
reserve_data = data["ReserveData"]

room_101 = reserve_data["D_103"]
day14 = room_101.split(",")[13]

print("2/14 day_bits:", day14)
print("Length:", len(day14))

print("normal 14:00-16:00 free?", is_free_normal(day14, 14, 0, 16, 0, start_hour))
print("normal 22:00-23:00 free?", is_free_normal(day14, 22, 0, 23, 0, start_hour))
print("midnight 24:00-30:00 free?", is_free_midnight(day14))