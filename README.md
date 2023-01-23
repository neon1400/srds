``` sql
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
```

## Motywacja tabel:

* aircrafts - informacje zawierajace konkretny samolot i ilosc dostepnych miejsc
* flights - korelacja danego samolotu z dana trasa danego dnia - konkretny lot
* available_seats - tabela zawierajaca wolne miejsca dla wszystkich dostepnych lotow. Szybkie wyszukiwanie wolnych miejsc, bo tylko takie sa w tej tabeli. W przypadku zajecia jakiegos miejsca, jest ono stamtad po prostu usuwane
* taken_seats - reprezentuje zbior zajetych miejsc - sa dodawane przy usunieciu miejsca z available_seats. Ticket_id pozwala na skorelowanie miejsca z konkretnym klientem, ktory kupil bilet
* seat_reserv - zawiera klientow i bilety jakie kupili. W przypadku usuniecia rezerwacji, usuwany jest takze rekord z taken_seats i dodawany z powrotem do available_seats

## Testy:
* 5000 klientow probujacych kupic 1512 miejsc. Z czego kazdy klient losowal na ktory lot kupi bilet i ile kupi biletow (1-5)
* Test mial ograniczone mozliwosci, gdyz 5000 procesow niesposob bylo uruchomic jednoczesnie na 8 watkowym procesorze, wiec wyniki zalezaly mocno od tego jak system operacyjny zarzadzal dostepem do procesora
