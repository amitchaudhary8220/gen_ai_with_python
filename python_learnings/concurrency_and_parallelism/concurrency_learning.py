import threading
import time


def take_order():
    for i in range(1, 4):
        print(f"Taking order from {i}")
        time.sleep(2)


def brew_chai():
    for i in range(1, 4):
        print(f"Brew chai for {i}")
        time.sleep(5)


order_thread = threading.Thread(target=take_order)
chai_thread = threading.Thread(target=brew_chai)

order_thread.start()
chai_thread.start()

order_thread.join()
chai_thread.join()


print(f"All order has been taken and chai has been brewed")
