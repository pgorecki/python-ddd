pipenv install
pipenv shell

code .


To run the app as Falcon server
```
FRAMEWORK=falcon gunicorn --reload main
```

To run the app as Flask server
```
FRAMEWORK=flask gunicorn --reload main
```