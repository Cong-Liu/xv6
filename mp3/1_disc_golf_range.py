from threading import Thread, Semaphore, Lock
from time import sleep

from random import random

# initial variables

stash = 0
num_disc_per_bucket = 0  # N
num_frolfer = 0
dish_on_field = 0

# initial two threads

fThread = Semaphore(0)
cThread = Semaphore(0)

# locks
acquire_stash = Lock()
retrieve_discs_on_field = Lock()

def frolfer(num):
    global stash, dish_on_field, num_disc_per_bucket
    flg = True
    # helper to avoid infinite loop
    count = 0
    while flg:
        print "Frolfer ", num, "calling for bucket"

        # lock stash
        acquire_stash.acquire()

        # if stash doesn't have enough disc, release cart and acquire all frolfer
        if stash < num_disc_per_bucket:

            cThread.release()
            fThread.acquire()

        # update stash and print # discs in stash
        stash -= num_disc_per_bucket
        print "Frolfer num got ", num_disc_per_bucket, " discs; Stash = ", stash

        #release stash
        acquire_stash.release()

        for i in range(0, num_disc_per_bucket):
            retrieve_discs_on_field.acquire()
            print "Frolfer ", num, " threw disc ", i
            dish_on_field += 1
            retrieve_discs_on_field.release()
            sleep(random())
        count += 1
        if count>3:
            print "Frolfer ", num, " Game over!"
            flg = False


def cart():
    global stash, dish_on_field
    flg = True
    while flg:
        # this is run after frolfer release a sem to call cart run
        cThread.acquire()

        retrieve_discs_on_field.acquire()
        print "################################################################################"
        print "Stash = ", stash, " ; Cart entering field"
        stash += dish_on_field
        print "Cart done, gathered ", dish_on_field, " discs; Stash = ", stash
        dish_on_field = 0
        retrieve_discs_on_field.release()
        print "################################################################################"
        # cart done, so frolfer can run again
        fThread.release()

def run(s = 15, disc = 0, f = 3, N = 5):
    global stash, dish_on_field, num_frolfer, num_disc_per_bucket
    stash = s
    dish_on_field = disc
    num_frolfer = f
    num_disc_per_bucket = N
    # run the cart first
    acart = Thread(target=cart)
    acart.start()
    sleep(0)
    frolferlist = []

    for i in range(0, num_frolfer):
        frolferlist.append(Thread(target=frolfer, args=[i]))
        frolferlist[i].start()
        sleep(random())

# default set: stash = 15, disc_on_field = 0, num_frolfer = 3, num_disc_per_bucket = 5
run()

