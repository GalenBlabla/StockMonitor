# Admin_monitoring Service
from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def read_root():
    return {'message': 'Admin_monitoring Service'}
