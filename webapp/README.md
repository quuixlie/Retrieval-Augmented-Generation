## Running the app

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