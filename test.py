from main import Session
from multiprocessing import Process
import random


def customer(customer_id, flight, amount):
    #print('started')
    session = Session()

    s = []
    t = []
    for i in range(amount):
        seat, ticket = session.book_random_seat(flight, customer_id)
        s.append(seat)
        t.append(ticket)

if __name__ == "__main__":
    process_list = []
    for i in range(5000):
        flight_id = random.randint(1,8)
        seat_number = random.randint(1,5)
        p = Process(target=customer, args=(i, flight_id, seat_number))
        process_list.append(p)
    
    for p in process_list:
        p.start()

    for p in process_list:
        p.join()