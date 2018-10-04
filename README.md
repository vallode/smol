# Smol.link  

A tiny link shortener written in Python3 using Flask.  

## API

`/api/v1`  
Base endpoint for all future v1 API calls  
  
###`/api/v1/shorten`   
**Args:**  
> `link` (str) : Form body data that you want shortened 

**Returns:**  
> `success` (Bool) : Dependant on success of operation  
`original` (str) : Original link given to API  
`link` (str) : Shortened link for your use  


## To-do

- [x] Initial launch
- [x] Redesign and refactor
- [ ] API endpoint
- [ ] Duplicate link detection
- [ ] Link usage statistics 

## Running

Edit `config.py` to your suited production settings, make sure to adjust 
`DATABASE_NAME`, `DATABASE_USER`, and `DATABASE_PASS` to your database variables.

Create your user, the database and run the schema:
`psql "dbname=smol host=localhost user=smol password=smol" -a -f schema.sql`  
replacing the correct database details.

To run, simply set `FLASK_APP` to `smol.py` and execute: `flask run`

Note: Make sure to set `FLASK_ENV` to `development` if you are running it locally.