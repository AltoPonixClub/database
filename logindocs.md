# Login Details

1. User enters in username and password.
2. Username and password get sent to backend server via HTTPS
3. Password is verified with the hash stored in the database
4. Authentication token is generated and sent to client
5. Authentication token must be used for future requests.

Authentication tokens expire after 4 hours. This may be changed by editing ``TOKENS_MAX_AGE`` in database.py.

Argon2 hashing settings: (settings: Memory Cost=65536,Iterations=3,Parallelism Factor=4,Hash Length=32)
Generator: https://argon2.online.