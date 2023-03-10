from main import Session
from multiprocessing import Process, Queue, Pool, get_context
import random
from datetime import datetime
from statistics import mean
import matplotlib.pyplot as plt
import time
import itertools


def customer(customer_id):
    times = []
    #print(customer_id)
    try:
        # print('started')
        session = Session()

        flight = random.randint(1,16)
        amount = random.randint(1,5)
        free = session._get_free(flight)
        #s = []
        #t = []
        if not free:
            print(customer_id, times)
            return times
        for i in range(amount):
            start = datetime.now()
            result = session.book_random_seat(flight, customer_id)
            if result:
                stop = datetime.now() - start
                times.append(stop.total_seconds()*1000.0)
            else:
                print('ODWOLANE')
            #print(times)
            #s.append(seat)
            #t.append(ticket)
        # print(customer_id)
    except:
        pass
    print(customer_id, times)
    return times

