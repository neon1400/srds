CREATE KEYSPACE srds WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 3};

CREATE TABLE srds.aircrafts(
    aircraft_id    int PRIMARY KEY,
    model text,
    no_seats int
) WITH comment = 'Q: Find information about trains';

// warszawa - poznan -szczecin 

CREATE TABLE srds.flights(
    aircraft_id int,
    flight_date date,
    flight_id int,
    route_id int, 
    PRIMARY KEY ((flight_date), route_id)
) WITH comment = 'Q: find voyage_id for train and date';

CREATE TABLE srds.available_seats(
    flight_id int,
    seat_id int,
    -- is_taken boolean,
    -- ticket_id uuid,
    PRIMARY KEY ((flight_id), seat_id)
) WITH comment = 'Q: find taken seats in a given voyage';

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
) WITH comment = 'Q: find/store seat reservations';