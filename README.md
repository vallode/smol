# Smol.link  

A tiny link shortener written in Python3 using Flask.  

## Running

Create a user `smol` with a database named `smol`
(or whatever you set in the configuration)

`source env/bin/activate`  
`env FLASK_APP=smol.py FLASK_DEBUG=True FLASK_ENV=development flask run`  