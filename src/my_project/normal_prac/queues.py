""" import heapq
from time import perf_counter
data = [23, 33, 24, 65, 23, 76, 90, 34]
start = perf_counter()
heapq.heapify(data)
end = perf_counter()
print(f"First time is {end - start:.6f}")
print(data)
start2 = perf_counter()
er = sorted(data)
end2 = perf_counter()
print(f"Second time is {end2 - start2:.6f}")
if (end - start) <= (end2 - start2):
    print("First time is faster than second time")
else:
    print("Second time is faster than first time")
print(er)
 """

import heapq
from time import perf_counter
data = [23, 33, 24, 65, 23, 76, 90, 34]
start2 = perf_counter()
print(sorted(data, reverse=True))
end2 = perf_counter()
print(f"{end2 - start2:.6f}")
start = perf_counter()
data = [-i for i in data]
heapq.heapify(data)
data = [-i for i in data]
end = perf_counter()
print(f"{end - start:.6f}")
print(data)
