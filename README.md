# Python wrapper for Ambar API, v0.1.0

Ambar stack: https://ambar.cloud/.

Constructor: `ambar = Ambar( email , password , host )`
with `host = "hostname:port"`.

Available methods:

- auth ( email , password ) --> /api/users/login
- put ( filename [, source] ) --> /api/files/:source/:filename
- get_meta ( id ) --> /api/files/direct/:id/meta
- get_text ( id ) --> /api/files/direct/:id/text
- get_source ( id ) --> /api/files/direct/:id/source
- check ( id )
- search ( query [, size , page] ) --> /api/search
- scan ( query [, size] )

