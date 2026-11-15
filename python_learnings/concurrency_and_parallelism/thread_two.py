import threading
import time


def prepare_chain(type_, wait_time):
    print(f"{type_} chai: brewing...")
    time.sleep(wait_time)
    print(f"{type_} chai: Ready.")


t1 = threading.Thread(target=prepare_chain, args=("Masala",2))
t2 = threading.Thread(target=prepare_chain, args=("Ginger",3))

t1.start()
t2.start()

t1.join()
t2.join()

