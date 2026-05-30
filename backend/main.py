from fastapi import FastAPI
import duckdb
import numpy
import pandas

app = FastAPI()


@app.get("/enterprise/work/not_finish")
def read_root():
    resultado = duckdb.sql("""
    SELECT nome, salario
    FROM read_csv_auto('contratos.csv')
    WHERE salario > 5000
    """).df()
    return {"enterprise": resultado}

@app.get("/enterprise/bigger_spent")
def bigger_spend():
    resultado = duckdb.sql("""
    SELECT institucao, contrato, objetivo, dtInicial, covid
    FROM read_csv_auto('contratos.csv')
    WHERE valorContrato > 5000
    """).df()
    return {"enterprise": resultado}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}