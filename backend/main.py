from fastapi import FastAPI
import sqlite3
from google import genai
import os

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
def bigger_spend(limit: int = 10, page: int = 1):
    offset = (page - 1) * limit

    query = f"""
        SELECT *
        FROM empenhos
        ORDER BY amount_empenhado DESC
        LIMIT {limit} OFFSET {offset}
    """

    return {"empenhos": make_query(query)}

@app.get("/enterprise/less_spent")
def less_spend(limit: int = 10, page: int = 1):
    offset = (page - 1) * limit

    query = f"""
        SELECT *
        FROM empenhos
        ORDER BY amount_empenhado ASC
        LIMIT {limit} OFFSET {offset}
    """

    return {"empenhos": make_query(query)}

@app.get("/enterprises")
def enterprises(limit: int = 10, page: int = 1):
    offset = (page - 1) * limit

    query = f"""
        SELECT *
        FROM empenhos
        ORDER BY id ASC
        LIMIT {limit} OFFSET {offset}
    """

    return {"empenhos": make_query(query)}

@app.get("/chat")
def chat(prompt: str=""):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    if len(prompt) == 0:
        return {"message" : "Nenhum prompt foi enviado."}

    def chat_with_gemini(prompt: str):
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    return {"result" : chat_with_gemini(prompt)}


