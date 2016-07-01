import random


from threading import Thread, Semaphore
from time import sleep
from timeit import Timer

rng = random.Random()
rng.seed(100)

# global variables
# it's a hard code, please change the number of philosophers and number of meals below to test this method
num_phi = 10
num_meal = 5

mutex = Semaphore(1)
forks = [Semaphore(1) for i in range(num_phi)]

#footman
footman = Semaphore(num_phi-1)

def solu_footman(left,phi,meal):
    while (meal>0):
        right = (left+1)%phi
        # every phi
        footman.acquire()
        #get forks
        forks[right].acquire()
        forks[left].acquire()
        #eat
        mutex.acquire()
        sleep(rng.random()/10)
        meal = meal-1
        mutex.release()
        # eat finished
        forks[right].release()
        forks[left].release()
        footman.release()
        #thinking
        sleep(rng.random()/10)


# left_hand
def solu_left_hand(left, phi, meal):
    while (meal>0):
        right = (left+1)%phi
        if (left == 1):
            # print "left :", left, "right: ", right
            forks[right].acquire()
            forks[left].acquire()
        else:
            # print "aaa left :", left, "right: ", right
            forks[left].acquire()
            forks[right].acquire()
        mutex.acquire()
        sleep(rng.random()/10)
        meal = meal-1
        mutex.release()
        forks[left].release()
        forks[right].release()
        sleep(rng.random()/10)


# Tanenbaum

state = ['thinking'] * num_phi
sem = [Semaphore(0) for i in range(num_phi)]
mutex2 = Semaphore(1)

def right(i):
    # global num_phi
    return (i+1)%num_phi

def left(i):
    return (i+num_phi-1) % num_phi

def get_fork(i):
    mutex.acquire()
    state[i] = 'hungry'
    test(i)
    mutex.release()
    sem[i].acquire()

def put_fork(i):
    mutex.acquire()
    state[i] = 'thinking'
    test(right(i))
    test(left(i))
    mutex.release()
def test(i):
    if state[i] == 'hungry' and state[left(i)] != 'eating' and state[right(i)] != 'eating':
        state[i] = 'eating'
        sem[i].release()

#
def solu_Tanenbaum(fid, phi, meal):

    while (meal>0):
       get_fork(fid)
       mutex2.acquire()
       meal = meal-1
       mutex2.release()
       sleep(rng.random()/10)
       put_fork(fid)
       sleep(rng.random()/10)


def run_footman():
    global num_phi, num_meal
    thread_array = []
    for i in range(num_phi):
        thrd = Thread(target=solu_footman,args=[i,num_phi,num_meal])
        thread_array.append(thrd)
    for th in thread_array:
        th.start()
    for th in thread_array:
        th.join()


def run_left_hand():
    global num_phi, num_meal
    thread_array = []
    for i in range(num_phi):
        thrd = Thread(target=solu_left_hand,args=[i,num_phi,num_meal])
        thread_array.append(thrd)
    for th in thread_array:
        th.start()
    for th in thread_array:
        th.join()


def run_Tane():
    global num_phi, num_meal
    thread_array = []
    for i in range(num_phi):
        # print "tmd", i,num_phi,num_meal
        thrd = Thread(target=solu_Tanenbaum,args=[i,num_phi,num_meal])
        thread_array.append(thrd)
    for th in thread_array:
        th.start()
    for th in thread_array:
        th.join()


# loop run

# def run(name):
#     global num_phi, num_meal
#     thread_array = []
#     for i in range(num_phi):
#         thrd = Thread(target=name,args=[i,num_phi,num_meal])
#         thread_array.append(thrd)
#     for th in thread_array:
#         th.start()
#     for th in thread_array:
#         th.join()
# #
# solution = [solu_footman, solu_left_hand, solu_Tanenbaum]
#
# time = []
# for name in solution:
#     timer1 = Timer(run(name))
#     print name, ": time elapsed: {:0.3f}s".format(Timer(timer1.timeit(1)))
#     time.append(Timer(run(name)))
#
# print("1. Footman solution, time elapsed: {:0.3f}s".format(time[0]))
# print("2. Left-handed solution, time elapsed: {:0.3f}s".format(time[1]))
# print("3. Tanenbaum's solution, time elapsed: {:0.3f}s".format(time[2]))


# it's a hard code, please change the number of philosophers and number of meals at line 13, 14
print "number of philosophers: ",num_phi, ", number of meals: ", num_meal
timer1 = Timer(run_footman)
print("1. Footman solution, time elapsed: {:0.3f}s".format(timer1.timeit(1)))
timer2 = Timer(run_left_hand)
print("2. Left-handed solution, time elapsed: {:0.3f}s".format(timer2.timeit(1)))
timer3 = Timer(run_Tane)
print("3. Tanenbaum's solution, time elapsed: {:0.3f}s".format(timer3.timeit(1)))