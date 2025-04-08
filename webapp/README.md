## Running the app

### New way (in webapp directory)
```
# Intall and run milvus
curl -sfL https://raw.githubusercontent.com/milvus-io/milvus/master/scripts/standalone_embed.sh -o standalone_embed.sh
bash standalone_embed.sh start

# Install and run postgres
sudo docker pull postgres-alpine3.20
sudo docker run --name my_postgres -e POSTGRES_PASSWORD=12345 -e POSTGRES_DB=flaskragdb -p 6921:5432 -d postgres:alpine3.20

# Install dependencies
pip install -r requirements.txt

# Run the app
flask run
```

```
# Deprecated way (in webapp directory)
sudo docker build -t rag-service .
sudo docker run --rm rag-service
```

---
## Running the app
### Old way

First install all the required packages using:

```
pip install -r requirements.txt
```

And then the application should be ready.
You can run the following command inside the directory with ```app.py```:

```
flask run
```

### Running database migrations

Using flask-migrate package

```
flask db init
flask db migrate -m "<message>"
flask db upgrade
```