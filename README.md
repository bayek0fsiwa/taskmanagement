### To run the application first initialize the database. Before that rename the .env.example file to just .env and put your DATABASE URL if you are using you own otherwise all good. For example here I am using Docker to setup PostgreSQL. Run below command:

```
docker compose up -d
```

### After successfully creating the db container run the app using (I am using Windows; adjust accordingly as per your OS):

```
fastapi dev .\src\main.py
```

### Go to this URL to access the routes (check the port mapping as well):

```
http://127.0.0.1:8000/docs
```

#### This is for the second task to create a diagram for architecture Design 
```
https://excalidraw.com/#json=aRA1gKwW45wAeofig-PmL,ELjr0e60fPrkLHPs4zTDAQ
```