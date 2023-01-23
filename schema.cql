CREATE KEYSPACE srds WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 3};

CREATE TABLE srds.aircrafts(
    aircraft_id    int PRIMARY KEY,
    model text,
    no_seats int
)

CREATE TABLE srds.flights(
    aircraft_id int,
    flight_date date,
    flight_id int,
    route_id int, 
    PRIMARY KEY ((flight_date), route_id)
);

CREATE TABLE srds.available_seats(
    flight_id int,
    seat_id int,
    PRIMARY KEY ((flight_id), seat_id)
);

CREATE TABLE srds.taken_seats(
    flight_id int,
    seat_id int,
    ticket_id uuid PRIMARY KEY 
);

CREATE TABLE srds.seat_reserv(
    seat_id int,
    flight_id int,
    customer_id int,
    ticket_id uuid,
    PRIMARY KEY ((customer_id) , ticket_id)
);