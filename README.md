# Indorse Technical Assignment "Cinema Ticket Booking"

## Initial description
Create a system that allows users to book a seat in a movie theatre - no authentication required.
This assignment is mainly to test the skills of the developers which would be useful for e-commerce websites or applications like shopping carts, booking systems and the like.

Display all the seats in the theater and allow users to book it by clicking it. Only one user should be allowed to reserved a specific seat.
If another user clicks a seat that was booked, he should get an error. You must handle the concurrency scenarios and avoid data inconsistency.

Seats can be unbooked by clicking the booked seat again.

## Implementation

**Live solution**: https://django-test-f3mfj5lgea-lz.a.run.app/

The frontend is written in React. Its tests are in `frontend/src/App.test.js`.
These tests are executed by running 
```
npm install && npm run tests 
```

The backend is written in Python37/Django. It uses PostgreSQL for storing data and Bootstrap for fancy forms and cards.
Tests are in `booking_system/tests.py`. These tests are executed by running 
```
pip install -r requirements.txt
python manage.py migrate
python manage.py test
```

### Building Frontend
In order to build frontend in its subdirectory:
```
cd frontend
npm install
npm run build
cp build/index.html ../booking_system/templates/
cp -rv build/static/* ../static/
```

### Backend Execution
**Make sure you build the frontend first!**

One way to execute the code is to build a Docker container with the supplied Dockerfile. It has everything needed for 
running the code and it runs automatically. And it's the same container which is going to run in Google Cloud once 
deployed.

Another way is to run the Python code directly, without building Docker image. Simply install the dependencies, set 
Postgres connection options, and run the server:****
```
# install dependencies
pip3 install -r requirements.txt

# set Postgres connection options
export DB_NAME=<database name>
export DB_USER=<Postgres username>
export DB_PASSWORD=...
export DB_HOST=<Postgres IP address>
export DB_PORT=<Postgres port>

# Run the server
python3 manage.py runserver
# or 
gunicorn --bind :8000 booking_system.wsgi
```  

In both cases the server should be running at port 8000.

### Deployment
```
# Create Google Storage bucket (if needed)
gsutil mb gs://[BUCKET_NAME]
gsutil defacl set public-read gs://[BUCKET_NAME]

# Upload static files (media, scripts, styles) to Google Storage
python manage.py collectstatic
gsutil -m rsync -r ./staticfiles gs://a-martynovich/static

# Connect CloudSQL to the server
gcloud sql instances create [INSTANCE_NAME] --tier=[MACHINE_TYPE] --region=[REGION]
gcloud run services update [INSTANCE_NAME] --platform managed \
  --add-cloudsql-instances [INSTANCE_CONNECTION_NAME] \
  --set-env-vars DB_USER=...,DB_PASSWORD=...,DB_NAME=...,\
        DB_HOST=/cloudsql/[CONNECTION_STRING]

# Connect to CloudSQL and set up the database (if needed):
gcloud sql connect [CONNECTION_STRING]
# or
cloud_sql_proxy -instances="[CONNECTION_STRING]"=tcp:3306
psql postgres -d postgres://localhost:3306/
postgres=> create database "[DATABASE_NAME]";

# Build and submit the server image
gcloud builds submit --tag gcr.io/[PROJECT_ID]/django-test
gcloud run deploy --image gcr.io/[PROJECT_ID]/django-test --platform managed
```
The server should be running immediately after deployment. It is possible to automate deployment using CI/CD, for 
example CircleCI which integrates with Github.
