from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT
from cassandra.util import Date
from cassandra.cqlengine.query import BatchStatement
from cassandra import ConsistencyLevel
from datetime import date
from random import choice
import uuid

class Session:
    def __init__(self) -> None:
        self.cluster = Cluster(['127.0.0.1'], port=9042)
        self.session = self.cluster.connect('srds', wait_for_all_pools=False)
        self.session.execute('USE srds')

        self.insert_reserv = self.session.prepare("INSERT INTO seat_reserv(seat_id, flight_id, customer_id, ticket_id) \
            VALUES(?, ?, ?, ?)")
        self.insert_taken = self.session.prepare("INSERT INTO taken_seats(flight_id, seat_id, ticket_id) VALUES(?, ?, ?)")
        self.del_avail = self.session.prepare("DELETE FROM available_seats WHERE flight_id=? AND seat_id=?")

        self.del_taken = self.session.prepare("DELETE FROM taken_seats WHERE ticket_id=?")
        self.insert_avail = self.session.prepare("INSERT INTO available_seats(flight_id, seat_id) VALUES (?, ?)")
        self.del_reserv = self.session.prepare("DELETE FROM seat_reserv WHERE customer_id=? AND ticket_id=?")


    def get_aircraft_info(self, aircraft_id: int):
        row = self.session.execute(f'SELECT * FROM aircrafts WHERE aircraft_id={aircraft_id}').one()
        #print(row)
        if row:
            return row.no_of_stops, row.no_seats, row.path
        raise Exception('No such train')

    def get_flight_info(self, route_id, date):

        row = self.session.execute(f"SELECT flight_id, aircraft_id FROM flights WHERE route_id={route_id} AND flight_date='{date}'")
        row = row.one()
        if row:
            return row.flight_id, row.aircraft_id
        raise Exception('No such flight')

    def _get_free(self, flight_id):

        rows = self.session.execute(f"SELECT seat_id FROM available_seats WHERE flight_id={flight_id}")
        
        free_seats = []
        for row in rows:
            free_seats.append(row.seat_id)

        return free_seats

    def __is_seat_free(self, flight_id, seat_id):
        rows = self.session.execute(f"SELECT seat_id FROM available_seats WHERE flight_id={flight_id} AND seat_id={seat_id}")
        rows = rows.one()

        if rows:
            return True
        return False

    def _set_flight_seats(self, flight_id):
        for i in range(189):
            self.session.execute(f"INSERT INTO available_seats(flight_id, seat_id) VALUES ({flight_id}, {i})")

    def _reserve_seat(self, flight_id, seat_id, ticket_id, customer_id):
        batch = BatchStatement(consistency_level=ConsistencyLevel.ONE)     

        batch.add(self.del_avail, (flight_id, seat_id))
        batch.add(self.insert_taken, (flight_id, seat_id, ticket_id))
        batch.add(self.insert_reserv, (seat_id, flight_id, customer_id, ticket_id))
        self.session.execute(batch)
        
    def book_random_seat(self, flight_id, customer_id):
        free_seats = self._get_free(flight_id)
        if free_seats:
            seat_id = choice(free_seats)
            #print(seat_id)
            ticket_id = uuid.uuid4()
            self._reserve_seat(flight_id, seat_id, ticket_id, customer_id)
            return seat_id, ticket_id
        return None, None

    def book_seat(self, flight_id, seat_id):
        if self.__is_seat_free(flight_id, seat_id):
            ticket_id = uuid.uuid4()
            self._reserve_seat(flight_id, seat_id, ticket_id, 2137)

    def remove_reserv(self, customer_id, ticket_id):
        row = self.session.execute(f"SELECT flight_id, seat_id FROM seat_reserv").one()
        if row:
            batch = BatchStatement(consistency_level=ConsistencyLevel.ONE)     
            
            batch.add(self.del_taken, (ticket_id,))
            batch.add(self.insert_avail, (row.flight_id, row.seat_id))
            batch.add(self.del_reserv, (customer_id, ticket_id))

            self.session.execute(batch)



if __name__ == "__main__":
    session = Session()
    for i in range(8):
        session._set_flight_seats(i+1)



"""
INSERT INTO aircrafts(aircraft_id, model, no_seats) VALUES (101, 'Boeing 737-800', 189);
INSERT INTO aircrafts(aircraft_id, model, no_seats) VALUES (102, 'Boeing 737-800', 189);


INSERT INTO flights(aircraft_id, flight_date, flight_id, route_id) VALUES (101, '2023-01-18', 1, 1);
INSERT INTO flights(aircraft_id, flight_date, flight_id, route_id) VALUES (101, '2023-01-19', 2, 1);
INSERT INTO flights(aircraft_id, flight_date, flight_id, route_id) VALUES (101, '2023-01-18', 3, 2);
INSERT INTO flights(aircraft_id, flight_date, flight_id, route_id) VALUES (101, '2023-01-19', 4, 2);

INSERT INTO flights(aircraft_id, flight_date, flight_id, route_id) VALUES (102, '2023-01-18', 5, 3);
INSERT INTO flights(aircraft_id, flight_date, flight_id, route_id) VALUES (102, '2023-01-19', 6, 3);
INSERT INTO flights(aircraft_id, flight_date, flight_id, route_id) VALUES (102, '2023-01-18', 7, 4);
INSERT INTO flights(aircraft_id, flight_date, flight_id, route_id) VALUES (102, '2023-01-19', 8, 4);





"""