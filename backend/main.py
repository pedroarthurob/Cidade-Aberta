from fastapi import FastAPI
import sqlite3

app = FastAPI()

def make_query(query):
    conn = sqlite3.connect("transparencia_cg.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(query)

    return cursor.fetchall()

@app.get("/enterprise/work/not_finish")
def read_root():
    
    return {"enterprise": "resultado"}

@app.get("/enterprise/bigger_spent")
def bigger_spend():
    return {"enterprise": make_query("SELECT * FROM empenhos ORDER BY amount_empenhado DESC;")}

@app.get("/enterprise/less_spent")
def bigger_spend():
    return {"enterprise": make_query("SELECT * FROM empenhos ORDER BY amount_empenhado ASC;")}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}