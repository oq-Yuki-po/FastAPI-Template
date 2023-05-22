# FastAPI-Template
FastApi Template

## Run Gunicorn

```
cd app
gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000 --log-config logging.conf --reload
```

access to https://localhost/v1.0/docs

## Run alembic migration

### Create migration
```
cd app
alembic revision --autogenerate -m "message"
```

### Upgrade
```
cd app
alembic upgrade head
```

### Downgrade
```
cd app
alembic downgrade base
```



## Make ER Diagram

```
docker exec -it schemaspy sh make.sh
```
