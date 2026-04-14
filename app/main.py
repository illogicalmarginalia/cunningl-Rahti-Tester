from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.db import get_conn, create_schema
from pydantic import BaseModel
from datetime import date

app = FastAPI()

origins = [
    # "https://cunningl-rahti-tester-web-communication-and-databases.2.rahtiapp.fi",
    # "http://localhost",
    # "http://localhost:8080",
    # "http://localhost:5500",
    "*",  # change in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_schema()


# Create Pydantic Model
class Booking(BaseModel):
    guest_id: int
    room_id: int
    date_from: date
    date_to: date


@app.get("/")
def read_root():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT 'hello postgres'")
        result = cur.fetchone()

    return {"msg": "Now for something entirely different", "dbstatus": result}


@app.get("/api/ip")
def read_root(request: Request):
    return {"ip": request.client.host}


# @app.get("/api/ip", response_class=HTMLResponse)
# def read_root(request: Request):
#    client_host = request.client.host
#    return f"<h1> ip: {client_host} </h1>"
# if-statements
@app.get("/if/{term}")
def if_test(term: str):
    msg = "Default msg"
    if term == "hello" or term == "hi":
        msg = "Hello! How are you?"
    elif term == "hej":
        msg = "Hej! Hur mår du?"
    elif term == "moi":
        msg = "Moika!"
    else:
        msg = f"I don't understand {term}"
    return {"msg": msg}


@app.get("/items/{id}")
def read_item(item_id: int, q: str = None):
    return {"id": id, "q": q}


# View Rooms
@app.get("/api/rooms")
def read_root(request: Request):
    hotelRooms = [
        {"roomNumber": 14, "bedSize": "Queen", "TV": "Yes", "Bookable": "Yes"},
        {"roomNumber": 7, "bedSize": "Twin", "TV": "No", "Bookable": "Yes"},
        {"roomNumber": 17, "bedSize": "King", "TV": "Yes", "Bookable": "No"},
    ]
    return {"hotelRooms": hotelRooms}


@app.get("/rooms/{id}")
def get_one_room(id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT * 
            FROM rooms 
            WHERE id = %s
        """,
            (id,),
        )  # <- tuple, list is also fine: [id]
        room = cur.fetchone()
    return room


# Create Booking
@app.post("/api/bookings")
def create_booking(booking: Booking):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
                INSERT INTO bookings (
                    room_id, 
                    guest_id,
                    date_from,
                    date_to
                ) VALUES (
                    %s, %s, %s, %s
                ) RETURNING id
            """,
            [booking.room_id, booking.guest_id, booking.date_from, booking.date_to],
        )
        new_booking = cur.fetchone()

    return {"msg": "Booking created!", "id": new_booking["id"]}
