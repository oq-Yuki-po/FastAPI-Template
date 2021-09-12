# FastAPI-Template
FastApi Template

## Run Uvicorn

```
cd app
gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000 --log-config logging.conf --reload
```
