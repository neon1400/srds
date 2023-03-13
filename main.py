from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT
from cassandra.util import Date
from cassandra.cqlengine.query import BatchStatement
from cassandra import ConsistencyLevel
from datetime import date
from random import choice
import uuid
from functools import reduce

class Session:
    def __init__(self) -> None:
        ep = ExecutionProfile(consistency_level=ConsistencyLevel.ONE, request_timeout=60)

        # self.cluster = Cluster(['127.0.0.1'], port=9042, execution_profiles={EXEC_PROFILE_DEFAULT: ep})
        self.cluster = Cluster(['10.0.0.3', '10.0.0.4', '10.0.0.2'], port=9042, execution_profiles={EXEC_PROFILE_DEFAULT: ep})

        try:
            self.session = self.cluster.connect('srds', wait_for_all_pools=False)
        except:
            raise RuntimeError
        #self.session.default_timeout=10
        self.session.execute('USE srds')

        self.insert_reserv = self.session.prepare("INSERT INTO seat_reserv(seat_id, flight_id, customer_id, ticket_id) \
            VALUES(?, ?, ?, ?)")
        self.insert_taken = self.session.prepare("INSERT INTO taken_seats(flight_id, seat_id, ticket_id) VALUES(?, ?, ?)")
        self.del_avail = self.session.prepare("DELETE FROM available_seats WHERE flight_id=? AND seat_id=?")

        self.del_taken = self.session.prepare("DELETE FROM taken_seats WHERE ticket_id=?")
        self.insert_avail = self.session.prepare("INSERT INTO available_seats(flight_id, seat_id) VALUES (?, ?)")
        self.del_reserv = self.session.prepare("DELETE FROM seat_reserv WHERE customer_id=? AND ticket_id=?")

        self.aircraft_info = self.session.prepare("SELECT * FROM aircrafts WHERE aircraft_id=?")
        self.flight_info = self.session.prepare("SELECT flight_id, aircraft_id FROM flights WHERE route_id=? AND flight_date=?")

        self.free = self.session.prepare("SELECT seat_id FROM available_seats WHERE flight_id=?")
        self.seat_free = self.session.prepare("SELECT seat_id FROM available_seats WHERE flight_id=? AND seat_id=?")
        self.seat_succ = self.session.prepare("SELECT ticket_id FROM taken_seats WHERE ticket_id=?")
        self.rem_res = self.session.prepare("SELECT flight_id, seat_id FROM seat_reserv WHERE customer_id=? and ticket_id=?")

    def get_aircraft_info(self, aircraft_id: int):
        row = self.session.execute(self.aircraft_info, [aircraft_id]).one()
        #print(row)
        if row:
            return row.no_of_stops, row.no_seats, row.path
        raise Exception('No such train')

    def get_flight_info(self, route_id, date):
        row = self.session.execute(self.flight_info, [route_id, date])
        row = row.one()
        if row:
            return row.flight_id, row.aircraft_id
        raise Exception('No such flight')

    def _get_free(self, flight_id):
        rows = self.session.execute(self.free, [flight_id])
        
        free_seats = []
        for row in rows:
            free_seats.append(row.seat_id)

        return free_seats

    def __is_seat_free(self, flight_id, seat_id):
        rows = self.session.execute(self.seat_free, [flight_id, seat_id])
        rows = rows.one()

        if rows:
            return True
        return False

    def _is_seat_succes(self, ticket_id):
        rows = self.session.execute(self.seat_succ, [ticket_id])
        rows = rows.one()

        if rows:
            return True
        return False

    def _set_flight_seats(self, flight_id):
        self.set_seats = self.session.prepare("INSERT INTO available_seats(flight_id, seat_id) VALUES (?, ?)")
        for i in range(189):
            self.session.execute(self.set_seats, [flight_id, i])

    def _reserve_seat(self, flight_id, seat_id, ticket_id, customer_id) -> bool:
        batch = BatchStatement(consistency_level=ConsistencyLevel.ONE)     

        batch.add(self.del_avail, (flight_id, seat_id))
        batch.add(self.insert_taken, (flight_id, seat_id, ticket_id))
        batch.add(self.insert_reserv, (seat_id, flight_id, customer_id, ticket_id))
        self.session.execute(batch)

        reserved = self._is_seat_succes(ticket_id)
        if not reserved:
            self.remove_reserv(customer_id=customer_id, ticket_id=ticket_id)
            return False
        return True
        
    def book_random_seat(self, flight_id, customer_id):
        free_seats = self._get_free(flight_id)
        if free_seats:
            seat_id = choice(free_seats)
            #print(seat_id)
            ticket_id = uuid.uuid4()
            return  self._reserve_seat(flight_id, seat_id, ticket_id, customer_id)
        return False

    def book_seat(self, flight_id, seat_id, customer_id):
        if self.__is_seat_free(flight_id, seat_id):
            ticket_id = uuid.uuid4()
            return self._reserve_seat(flight_id, seat_id, ticket_id, 2137), ticket_id
        return False, 0

    def remove_reserv(self, customer_id, ticket_id):
        row = self.session.execute(self.rem_res, [customer_id, ticket_id]).one()
        if row:
            batch = BatchStatement(consistency_level=ConsistencyLevel.ONE)     
            
            batch.add(self.del_taken, (ticket_id,))
            batch.add(self.insert_avail, (row.flight_id, row.seat_id))
            batch.add(self.del_reserv, (customer_id, ticket_id))

            self.session.execute(batch)

    def book_many_seats(self, num_of_seats, flight_id, customer_id):
        free_seats = self._get_free(flight_id)

        if free_seats:
            if len(free_seats) < num_of_seats:
                return False

            chosen_seats = []
            for _ in range(num_of_seats):
                seat_id = choice(free_seats)
                chosen_seats.append(seat_id)
                free_seats.remove(seat_id)

            did_it_work = []
            ticket_list = []
            for seat in chosen_seats:
                result, ticket_id = self.book_seat(flight_id=flight_id, seat_id=seat, customer_id=customer_id)
                did_it_work.append(result)
                ticket_list.append(ticket_id)
            result = reduce(lambda a, b: a and b, did_it_work)

            if not result:
                for ticket in ticket_list:
                    self.remove_reserv(customer_id=customer_id, ticket_id=ticket)
                return False
            return True



if __name__ == "__main__":
    session = Session()
    for i in range(16):
        session._set_flight_seats(i+1)


# WSTAWIC PRZED URUCHOMIENIEM TESTU:

"""
INSERT INTO aircrafts(aircraft_id, model, no_seats) VALUES (101, 'Boeing 737-800', 189);
INSERT INTO aircrafts(aircraft_id, model, no_seats) VALUES (102, 'Boeing 737-800', 189);
INSERT INTO aircrafts(aircraft_id, model, no_seats) VALUES (103, 'Boeing 737-800', 189);
INSERT INTO aircrafts(aircraft_id, model, no_seats) VALUES (104, 'Boeing 737-800', 189);

INSERT INTO flights(aircraft_id, flight_date, flight_id, route_id) VALUES (101, '2023-01-18', 1, 1);
INSERT INTO flights(aircraft_id, flight_date, flight_id, route_id) VALUES (101, '2023-01-19', 2, 1);
INSERT INTO flights(aircraft_id, flight_date, flight_id, route_id) VALUES (101, '2023-01-18', 3, 2);
INSERT INTO flights(aircraft_id, flight_date, flight_id, route_id) VALUES (101, '2023-01-19', 4, 2);

INSERT INTO flights(aircraft_id, flight_date, flight_id, route_id) VALUES (102, '2023-01-18', 5, 3);
INSERT INTO flights(aircraft_id, flight_date, flight_id, route_id) VALUES (102, '2023-01-19', 6, 3);
INSERT INTO flights(aircraft_id, flight_date, flight_id, route_id) VALUES (102, '2023-01-18', 7, 4);
INSERT INTO flights(aircraft_id, flight_date, flight_id, route_id) VALUES (102, '2023-01-19', 8, 4);

INSERT INTO flights(aircraft_id, flight_date, flight_id, route_id) VALUES (103, '2023-01-18', 9, 5);
INSERT INTO flights(aircraft_id, flight_date, flight_id, route_id) VALUES (103, '2023-01-19', 10, 5);
INSERT INTO flights(aircraft_id, flight_date, flight_id, route_id) VALUES (103, '2023-01-18', 11, 6);
INSERT INTO flights(aircraft_id, flight_date, flight_id, route_id) VALUES (103, '2023-01-19', 12, 6);

INSERT INTO flights(aircraft_id, flight_date, flight_id, route_id) VALUES (104, '2023-01-18', 13, 7);
INSERT INTO flights(aircraft_id, flight_date, flight_id, route_id) VALUES (104, '2023-01-19', 14, 7);
INSERT INTO flights(aircraft_id, flight_date, flight_id, route_id) VALUES (104, '2023-01-18', 15, 8);
INSERT INTO flights(aircraft_id, flight_date, flight_id, route_id) VALUES (104, '2023-01-19', 16, 8);
"""
