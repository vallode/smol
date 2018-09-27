# Smol.link  

A tiny link shortener written in Python3 using Flask.  

## Running

Edit `config.py` to your suited production settings, make sure to adjust 
`DATABASE_NAME`, `DATABASE_USER`, and `DATABASE_PASS` to your database variables.

Create your user, the database and run the schema:
`psql "dbname=smol host=localhost user=smol password=smol" -a -f schema.sql`  
replacing the correct database details.

To run, simply set `FLASK_APP` to `smol.py` and execute: `flask run`

Note: Make sure to set `FLASK_ENV` to `development` if you are running it locally.