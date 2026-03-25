from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
app = FastAPI()

@app.get("/")
def read_root():
    return { "msg": "Now for something entirely different", "v": "0.2" }

@app.get("/api/ip", response_class=HTMLResponse)
def read_root(request: Request):
    client_host = request.client.host
    return f"<h1> ip: {client_host} </h1>"

@app.get("/items/{id}")
def read_item(item_id: int, q: str = None):
    return {"id": id, "q": q}
