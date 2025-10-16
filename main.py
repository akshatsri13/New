from fastapi import FastAPI, HTTPException,Path
import sqlite3
from pydantic import BaseModel


app = FastAPI()

def get_db_conn():
    conn = sqlite3.connect("patients.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_Table():
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS patients(
    id INT PRIMARY KEY,
    name TEXT NOT NULL,
    age INT,
    disease TEXT 
    )
"""   )
    conn.commit()
    conn.close()
create_Table()

# pydantic model

class Patient(BaseModel):
    id: int
    name: str
    age: int
    disease: str

# making end points
@app.get("/")
def read_root():
    return {"message":"Test api for patient"}


@app.get("/test/{p_id}")
def read_route(p_id: int = Path(...,description="Enter the id of the patient", example='1')):
    conn = get_db_conn()
    cursor = conn.cursor()
    row = cursor.execute("SELECT * FROM patients WHERE id=?", (p_id,)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return dict(row)

@app.get("/patients")
def get_patient():
    conn = get_db_conn()
    cursor = conn.cursor()
    p1 = cursor.execute("SELECT * FROM patients").fetchall()
    conn.close()
    add = []
    for a in p1:
        add.append(dict(a))
    return add    
    
    # return [dict(p) for p in p1]
    

@app.post("/add")
def add_patient(patient:Patient):
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO patients (id,name,age,disease) VALUES (?,?,?,?)", (patient.id,patient.name, patient.age,patient.disease),)
    conn.commit()
    conn.close()
    return {"message" : "Patient added succesfully"}

@app.put("/patient/{p_id}")
def update_patient(p_id:int, patient: Patient):
    conn = get_db_conn()
    cursor = conn.cursor()
    existing = cursor.execute("SELECT * FROM patients WHERE id=?", (p_id,)).fetchone()
    if existing is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Patient not found")
    cursor.execute("UPDATE patients SET name=?, age=?, disease=? WHERE id=?",(patient.name, patient.age, patient.disease, p_id))
    conn.commit()
    conn.close()
    return {"message" : "Patient record updated successfully"}


@app.delete("/patient/{p_id}")
def delete_patient(p_id:int, patient: Patient):
    conn = get_db_conn()
    cursor = conn.cursor()
    existing = cursor.execute("SELECT * FROM patients WHERE id=?", (p_id,)).fetchone()
    if existing is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Patient not found")
    cursor.execute("DELETE FROM patients WHERE id=?", (p_id,))
    conn.commit()
    conn.close()
    return {"message" : "Patient deleted successfully"}
