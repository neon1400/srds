from main import Session
from multiprocessing import Process
import random

class Customer:
    def __init__(self, customer_id, flight, amount) -> None:
        self.session = Session()
        self.customer_id = customer_id
        self.flight = flight
        self.amount = amount

    def start(self):
        print('started')
        s = []
        t = []
        for i in range(self.amount):
            seat, ticket = self.session.book_random_seat(self.flight, self.customer_id)
            s.append(seat)
            t.append(ticket)
            print('dupa')

        print(s)
        print(t)

def customer(customer_id, flight, amount):
    #print('started')
    session = Session()

    s = []
    t = []
    for i in range(amount):
        seat, ticket = session.book_random_seat(flight, customer_id)
        s.append(seat)
        t.append(ticket)

    #print(s)
    #print(t)

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