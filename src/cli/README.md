This is a sample command line script to print all listings

1. Start the database

```
docker-compose -f docker-compose.dev.yml
```

2. Apply all migrations

```
cd src
alembic upgrade head
```

3. Run the script (from src directory):

```
python -m cli
```


