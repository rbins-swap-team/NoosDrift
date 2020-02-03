# NOOS-Drift

This is a README file commenting project NOOS-Drift.

## Backend part

The backend part of this project will be divided in two parts each programmed using

* python (>3.6.x)
* Django web-framework

### Backend sub-elements

The backend has two sub-elements

* A central server who collects all data
* Distributed workers who process simulation requests and make resulting data available

## Frontend part

The fronted part will be programmed in JavaScript using Angular2 (version ??)


## Basic django commands

### Run django

```bash
python ./manage.py runserver
```

### Create super user

```bash
python ./manage.py createsuperuser
```

### Run some simple scripts
```bash
python ./manage.py shell < ./anyscript.py
```

### Change Model objects
Execute this procedure

```bash
./manage.py makemigrations --name changed_my_model your_app_label
./manage.py sqlmigrate
./manage.py migrate
```

## Environment packages

See file ./requirements.txt

## Update packages with list in requirements

```bash
pip install --no-cache-dir --upgrade --force-reinstall -r requirements.txt
```

### List packages that are in use now

```bash
pip3 freeze > new-requirements.txt
```

## Manage allowed hosts
In 'settings.py' add your machine name or ip to ALLOWED_HOSTS as a string.

example :

```python
ALLOWED_HOSTS = ['127.0.0.1', 'www.example.com']
```


On test systems, this is also practical

```python
ALLOWED_HOSTS = ['*']
``` 

NOTE :

Mozilla has released a Python package called 'django-allow-cidr' which is designed to solve allowing IP ranges.
The announcement blog post explains that it's useful for things like health checks that don't have a Host header and just use an IP address.
You would have to write your IP address '172.17.*.*' to be a CIDR range like 172.17.0.0/16

## Static files
Some apps use static files which are better collected and placed in the '/static' folder.
'manage.py' does that

```bash
./manage.py collectstatic
```


## Deployment
After deployment, run these commands to generate static files.

```bash
source venv/bin/activate
yes yes 2>/dev/null | python ~/noosDrift/manage.py collectstatic --settings=deploy_settings
deactivate
```

If it does not exist, the static folder will be created.

This could be done with a git hook.

## Reloading after an update without reloading apache (in Daemon Mode)
```bash
touch ~/noosDrift/noosDrift/wsgi.py
```

## Testing jwt

### The basics.

Added jwt library to the project.

Did the following to test

#### Getting a token
```bash
curl -X POST -H "Content-Type: application/json" -d @auth.json http://127.0.0.1:8000/api-token-auth/ > token.json
```

Where auth.json is a file containing a valid usr/pwd combination in the form

```json
{"username":"usernamevalue","password":"passwordvalue"}
```

#### Checking a token
```bash
curl -X POST -H "Content-Type: application/json" -D headers.txt -d @token.json http://127.0.0.1:8000/api-token-verify/
```

Succession of curl commands worked

The django application sends back a json response containing the token. The file headers.txt contains the http header of the response with a 200 code
The structure of teh response is
```json
{"token":"header.payload.signature"}
```

Where "header.payload.signature" is a string created by the django app that follows JWT standards.

 * header, payload, signature are separate parts contcatenated using '.'
 * header, payload are base64 encoded strings
 * signature is : base64(sha256(base64(header)+'.'+base64(payload)))

A file of form
```json
{
  "token":"tokenOfDjangoApp",
  "message":"Just a message or anything else"
}
```

Will now be accepted
But if the value of tokenOfDjangoApp is altered it will not be accepted anymore

Altered the file token.json to produce a file badtoken.json

Used this bad token in the request

```bash
curl -X POST -H "Content-Type: application/json" -D headersbt.txt -d @badtoken.json http://127.0.0.1:8000/api-token-verify/
```

The result of the request was  :

The result of the request was a 400 message and a headersbt.txt file containing an http header with a 404 code


```http request
HTTP/1.1 400 Bad Request
Date: Fri, 05 Oct 2018 12:39:56 GMT
Server: WSGIServer/0.2 CPython/3.6.3
Content-Type: application/json
Vary: Accept
Allow: POST, OPTIONS
X-Frame-Options: SAMEORIGIN
Content-Length: 50
{"non_field_errors":["Error decoding signature."]}
```

## Fixing "Uncaught TypeError: a.indexOf is not a function" (a jQuery 3 incompatibility)

Edit the bottom of file `static/rest_framework/js/default.js`
```javascript
$(window).load(function(){});
```
becomes:
```javascript
$(window).on('load', function(){});
```

## Alternative way of specifying the token

This is an alternative way of specifying the token once you have a valid one

```bash
curl -X GET -H "Authorization: "+"JWT "+insertTokenValue http://127.0.0.1:8000/ -o output.html
```

I suppose this will work too

```bash
curl -X POST -H "Content-Type: application/json" -H "Authorization: "+"JWT "+insertTokenValue http://127.0.0.1:8000/ -d @postdata.json -o output.html
```

In JavaScript, this means that the request will have to be manipulated with

```javascript
theTokenValue="Whatever";
req.setRequestHeader("Authorization", "JWT "+theTokenValue);
```

before being sent

## Some new things about token expiration

Added this in the settings.py. Was tired of having to aske for a new token all the time.

```python
import datetime
 
# Configure the JWTs to expire after 1 hour, and allow users to refresh near-expiration tokens
JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(hours=1),
    'JWT_ALLOW_REFRESH': True,
}

# Enables django-rest-auth to use JWT tokens instead of regular tokens.
REST_USE_JWT = True

```

## Updating data in the Django app


Discovered that updating data in the Django app can (should?) be done using HTTP method PATCH

I got a token using the previously mentionned method
then I used

```bash
curl -X PATCH -H "Content-Type: application/json" -H "Authorization: JWT "+theToken http://127.0.0.1:8000/modelElement/Id/ -d @updateData.json -o outputupdate.html
```

And it worked.

## Created User with HTTP and API

 * First, get a token as above
 * Then create an http request

```bash
curl -X POST -H "Content-Type: application/json" -H "Authorization: JWT "+theToken -D createuser-01-responseheaders.txt http://127.0.0.1:8000/users/ -d @createuser-01.json -o createuser-01.html
```

file **createuser-01.json** only contains

 * username
 * email
 * is_active:"true"

Hmmm, strange : added 

 * password
 * first_name
 * last_name

to the json cration file and none of these fields were stored in the DB

Even stranger, at DB level, these fields are declare not nullable :-)

## Before creating a request by sending a JSON via POST request
Look at the validation process in noos_services/serializers.py

The JSON MUST contain :
- "lat": a valid number
- "long": a valid number

This field is automatically created:
- "filedir": "/home/sorsi/Documents/PycharmProjects/noosDrift/netcdf" or THE valid dir described as "NETCDF_DIR" on the server

```json
{"filedir": "/home/sorsi/Documents/PycharmProjects/noosDrift/netcdf", "lat":50, "long": 3}
```

## Local pip repository
```bash
pip2pi ~/pip_repository/ -r requirements.txt pip==19.2.3 setuptools==41.4.0 wheel==0.33.6
pip install --index-url=file:///var/.../pip_repository/simple -r requirements.txt
```
Files to edit

|From | To|
|-----|---|
|django-jsonfield-1.3.1-py2.py3-none-any.whl | django_jsonfield-1.3.1-py2.py3-none-any.whl|
|django-widget-tweaks-1.4.5-py2.py3-none-any.whl | django_widget_tweaks-1.4.5-py2.py3-none-any.whl|
|djangorestframework-jwt-1.11.0-py2.py3-none-any.whl | djangorestframework_jwt-1.11.0-py2.py3-none-any.whl|
|importlib-metadata-0.23-py2.py3-none-any.whl | importlib_metadata-0.23-py2.py3-none-any.whl|
|more-itertools-7.2.0-py3-none-any.whl | more_itertools-7.2.0-py3-none-any.whl|

## Reset the database

```sqlite
DELETE FROM noos_services_simulationdemand;
DELETE FROM noos_services_loggingmessage;
DELETE FROM noos_services_uploadedfile;
UPDATE noos_services_node set is_active = 0 WHERE id = 5; -- Machine MK
UPDATE noos_services_node set is_active = 1 WHERE id = 6; -- Machine SO
UPDATE sqlite_sequence set seq = 0 WHERE name = 'noos_services_simulationdemand';
UPDATE sqlite_sequence set seq = 0 WHERE name = 'noos_services_loggingmessage';
UPDATE sqlite_sequence set seq = 0 WHERE name = 'noos_services_uploadedfile';
```
