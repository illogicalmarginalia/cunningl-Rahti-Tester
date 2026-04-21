from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import date
from app.db import get_conn, create_schema


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

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def validate_key(api_key: str = Depends(api_key_header)):
    if not api_key:
        raise HTTPException(status_code=401, detail={"error": "API Key missing!"})
    
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT * FROM guests WHERE api_key = %s
        """, [api_key] )
        guest = cur.fetchone()
        if not guest:
            raise HTTPException(status_code=401, detail={"error": "Bad API Key!"})
        return guest

# Create Pydantic Model
class Booking(BaseModel):
    guest_id: int
    room_id: int
    date_from: date
    date_to: date
    addinfo: str


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
def get_rooms():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM rooms")
        rooms = cur.fetchall()
    return rooms


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


# Get Guests
@app.get("/api/guests")
def get_guests(): 
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT 
                g.*,
                (SELECT count(*) 
                    FROM bookings
                    WHERE guest_id = g.id
                    ) as total_visits
            FROM guests g    
            ORDER BY g.lastname
        """)
        guests = cur.fetchall()
    return guests


# Get Booking
@app.get("/api/bookings")
def get_bookings(guest: dict = Depends(validate_key)):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT
                b.id, b.date_from, b.date_to, g.firstname, g.lastname, r.room_number,
                b.date_to - b.date_from AS nights,
                r.price * (b.date_to - b.date_from) AS total_price,
                (SELECT count(*) FROM bookings WHERE guest_id = g.id) AS previous_visits
            FROM bookings b
            INNER JOIN guests g
                ON b.guest_id = g.id
            INNER JOIN rooms r
                ON b.room_id = r.id"""
        )
        bookings = cur.fetchall()
        return bookings


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
                    date_to,
                    addinfo
                ) VALUES (
                    %s, %s, %s, %s, %s
                ) RETURNING id
            """,
            [
                booking.room_id,
                booking.guest_id,
                booking.date_from,
                booking.date_to,
                booking.addinfo,
            ],
        )
        new_booking = cur.fetchone()

    return {"msg": "Booking created!", "id": new_booking["id"]}
