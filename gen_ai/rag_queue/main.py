from tkinter import NO

from client.rq_client import queue
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from queues.worker import process_query

load_dotenv()
app = FastAPI()


@app.get("/")
def root():
    return {"status": "Server is up and running"}


@app.post("/chat")
def chat(query: str = Query(..., description="The chat query of the user")):
    job = queue.enqueue(process_query, query)
    return {"status": "queued", "job_id": job.id}

@app.get('/job-status')
def get_result(job_id: str = Query(..., description="Job ID")):
    job = queue.fetch_job(job_id=job_id)
    if job is None:
                raise HTTPException(status_code=404, detail="Job not found")
    result = job.return_value()

    return {"result": result}
