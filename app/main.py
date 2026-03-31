from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

origins = [
   # "https://cunningl-rahti-tester-web-communication-and-databases.2.rahtiapp.fi",
   # "http://localhost",
   # "http://localhost:8080",
   # "http://localhost:5500",
   "*", #change in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return { "msg": "Now for something entirely different", "v": "0.2" }

@app.get("/api/ip")
def read_root(request: Request):
    return {"ip": request.client.host}

#@app.get("/api/ip", response_class=HTMLResponse)
#def read_root(request: Request):
#    client_host = request.client.host
#    return f"<h1> ip: {client_host} </h1>"

@app.get("/items/{id}")
def read_item(item_id: int, q: str = None):
    return {"id": id, "q": q}
