from threading import Thread, Semaphore, Lock
from time import sleep
from itertools import cycle
from random import random
from collections import deque

# while music
# # l and f entering one by one and pairing up
#
# l = leader_queue.popleft()
#
# lArrived.release()
# # l.enter_floor()
# print l.id, " is entering floor"
# fArrived.acquire()
#
# f = follower_queue.popleft()
#
# fArrived.release()
# # f.enter_floor()
# print f.id, "is entering floor"
# lArrived.acquire()
#
# print l.id, " and ", f.id, " are dancing."
# change music



# use for pair l & f after they entering the room (Ren)
lArrived = Semaphore(0)
fArrived = Semaphore(0)

# # used for l & f getting paired (mutex)
# self.pairs = Semaphore(2)
# end_dance = Semaphore(0) # barrier

# globle variables
num_of_leaders = 4
num_of_followers = 6

# data structure
leader_queue = deque([], maxlen=num_of_leaders)
follower_queue = deque([], maxlen=num_of_followers)

leader_dance_queue = deque([], maxlen=num_of_leaders)
follower_dance_queue = deque([], maxlen=num_of_followers)

#locks
leader_queue_lock = Lock()
leader_dance_queue_lock = Lock()
follower_queue_lock = Lock()
follower_dance_queue_lock = Lock()

# # semaphores
room_sem = Semaphore(0)


class Leader(Thread):
    def __init__(self, lid):
        self.lid = lid
        self.pairs = Semaphore(0)
        Thread.__init__(self)

    def getId(self):
        return self.lid

    def enter_floor(self):
        # leader should wait until bank start or switch music
        self.pairs.acquire()
        leader_dance_queue_lock.acquire()
        leader_dance_queue.append(self)
        # room_sem.acquire()
        print "Leader ", self.lid, " is entering floor."
        # room_sem.release()
        leader_dance_queue_lock.release()

    def dance(self):

        # print "dance"
        # follower_dance_queue_lock.acquire()
        # while len(follower_dance_queue) == 0:
        #     pass
        # follower = follower_queue.popleft()
        # # fArrived.acquire()
        # print "Leader ", self.lid, " and follower ", follower.fid, " are dancing."
        # self.pairs.release()
        # follower.pairs.release()
        # sleep(random())
        # follower_dance_queue_lock.release()

        dancing = False
        while not dancing:

            leader_dance_queue_lock.acquire()
            # check self match the next to dance
            if self.lid == leader_dance_queue[0].getId():
                #try to find a follower in dancing room
                follower_dance_queue_lock.acquire()
                if len(follower_dance_queue)>0:
                    follower = follower_dance_queue.popleft()
                    print "Leader ", self.lid, " and follower ", follower.getId(), " are dancing."
                    dancing = True
                follower_dance_queue_lock.release()

            leader_dance_queue_lock.release()
        # dance time randomly
        sleep(random())

    def line_up(self):
        leader_queue_lock.acquire()
        leader_queue.append(self)
        print "Leader ", self.lid, " getting back in line"
        leader_queue_lock.release()
        sleep(random())

    #override run() in Thread
    # lock the leader queue, push self into the queue
    def run(self):
        leader_queue_lock.acquire()
        leader_queue.append(self)
        leader_queue_lock.release()
        while True:
            lArrived.release()
            self.enter_floor()
            fArrived.acquire()
            self.dance()
            self.line_up()

class Follower(Thread):
    def __init__(self, fid):
        self.fid = fid
        self.pairs = Semaphore(0)

        Thread.__init__(self)

    def getId(self):
        return self.fid

    def run(self):
        follower_queue_lock.acquire()
        follower_queue.append(self)
        follower_queue_lock.release()

        while True:
            fArrived.release()
            self.enter_floor()
            lArrived.acquire()
            self.dance()
            self.line_up()

    def enter_floor(self):
        #waiting to be called to dance
        self.pairs.acquire()
        follower_dance_queue_lock.acquire()
        follower_dance_queue.append(self)
        # room_sem.acquire()
        print "Follower ", self.fid, " is entering floor."
        # room_sem.release()
        follower_dance_queue_lock.release()

    def dance(self):
        dancing = True
        while dancing:
            # check if this follower is paired
            follower_dance_queue_lock.acquire()
            if self not in follower_dance_queue:
                dancing = False
            follower_dance_queue_lock.release()

        sleep(random())

    def line_up(self):
        follower_queue_lock.acquire()
        follower_queue.append(self)
        print "Follower ", self.fid, " getting back in line"
        follower_queue_lock.release()



def play_music():
    global leader_dance_queue, follower_dance_queue,leader_queue,follower_queue
    while True:
        for music in cycle(['waltz', 'tango', 'foxtrot']):
            room_sem.release()
            start_music(music)
            sleep(random())
            if (len(leader_dance_queue) == 0 or len(follower_dance_queue) == 0):
                end_music(music)
            room_sem.acquire()


def start_music(music):
    print "** Band leader start playing ", music, " **"

    leader_queue_lock.acquire()
    if len(leader_queue) > 0:
        currl = leader_queue.popleft()
        currl.pairs.release()
    leader_queue_lock.release()

    follower_queue_lock.acquire()
    if len(follower_queue) > 0:
        currf = follower_queue.popleft()
        currf.pairs.release()
    follower_queue_lock.release()


def end_music(music):

    # leader_dance_queue.clear()
    follower_dance_queue.clear()
    print "** Band leader stopped playing,", music, "**"

for i in range(0, num_of_leaders):
    leader = Leader(i)
    leader.start()

for i in range(0, num_of_followers):
    follower = Follower(i)
    follower.start()


# num_of_followers and num_of_leaders can be changed at the begaining of this file
# default #leaders = 4, #followers=6
play_music()