from toon_format import encode
import json
from time import perf_counter
with open(r"C:\Projects\pyspark_file\ready_metrics.json", "r") as file:
    data = json.load(file)

# data = [{"res": None},{"res": 1},{"res": 2}]
start = perf_counter()
res = encode(data)
print(res)
end = perf_counter()
print("__ " * 45, end="\n\n")
print(f"time: {end - start:.6f}")
