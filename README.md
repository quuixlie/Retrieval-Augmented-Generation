## Running the app

>![important]
> Make sure to clone the repository with ```--recursive``` flag or manually initialize the submodules.

### Running with docker compose (Preferred)

1. Make sure you have ```docker-compose``` installed.
2. Make sure docker service is running.
3. Create a copy of ```.env.docker.template``` called ```.env```
4. Fill all the environment variables in newly created ```.env``` file
5. In the root directory run ```docker-compose up --build``` (on linux it may require sudo)

### Without docker-compose


1. Install pymilvus
    1. Local installation  
       - ```pip install pymilvus``` (Linux and MacOS)
    2. Docker installation 
       - with Milvus' [automatic configuration script](https://milvus.io/docs/install_standalone-docker-compose.md)
2. Download and install Postgres
    1. Local installation  
       - [Postgres](https://www.postgresql.org/download/)
       - and create a database for the application
    2. Docker installation
       - ```docker pull postgres```
       - Run the image ```docker run --name my_postgres -e POSTGRES_USER=<YOUR_USERNAME> -e POSTGRES_PASSWORD=<YOUR_USER_PASSWORD> -e POSTGRES_DB=<YOUR_DB_NAME> -p 5432:5432 -d postgres```
3. Install all the required packages using: 
    ```
    # If you are using a virtual environment, make sure to activate it first

    pip install -r requirements.txt
    ```
4. Export these environment variables:
    ```
    MILVUS_URL=<RUNNING_MILVUS_URL_HERE> (or a path in case of local milvus installation)
    
    API_BASE_URL=http://localhost:<PORT_OF_FLASK_APP>
    
    # Postgres is the preferred database
    DB_CONNECTION_STRING=postgresql://<YOUR_USERNAME>:<YOUR_USER_PASSWORD>@localhost:5432/<YOUR_DB_NAME>
    
    OPENAI_API_KEY=<YOUR_KEY>
    ```
5. Run the app using:
    ```
   flask run --port <PORT_OF_FLASK_APP>
    ```
