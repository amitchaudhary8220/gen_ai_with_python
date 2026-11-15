import threading

counter = 0
lock = threading.Lock()


def increament():
    global counter
    for _ in range(10000):
        f


threads = [threading.Thread(target=increament) for _ in range(10)]
[t.start() for t in threads]
[t.join() for t in threads]

print(f"Final counter : {counter}")
