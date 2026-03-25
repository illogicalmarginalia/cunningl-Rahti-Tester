from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/")
def read_root():
    return { "msg": "Now for something entirely different", "v": "0.2" }

@app.get("/api/ip")
def read_root(request: Request):
    client_host = request.client.host
    return {"ip": client_host}

@app.get("/items/{id}")
def read_item(item_id: int, q: str = None):
    return {"id": id, "q": q}
