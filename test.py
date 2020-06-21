import time
import threading

def print_clock(name):
  start = 1
  while True:
    print("{}:{}".format(name,start))
    start += 1
    time.sleep(1)

t = threading.Thread(target=print_clock,args=("test",))
t.start()

print("program end")