# Wingman
Wingman is the backend layer of the conversation stack.
It is a django server that uses OpenAI developer API to send prompts to a
conversation model.

# Environment variable that needs to be set
- OPENAI_API_KEY (no default): the OpenAI api key that is used for communicating
  witheir services.
- ALLOWED\_ORIGIN (default is "\*"): sets from what origin the server can be
  talked to (famously knows as CORS policy).
- SECRET\_KEY (default can be used in dev mode): the secret key to all encrypted django communication, one will be
  created and preciously stored when we will be deploying in production.
- DEBUG (default to "1"): use this environment variable when there is a need to
  get debug logs (NOT IN PRODUCTION).
- HOST: the host domain name, set this only if procedure says it is needed.
- DB\_NAME (default to "conversation"): the name of the postgreSQL database.
- DB\_USER (default to "wingman"): the user's name of the postgreSQL database.
- DB\_PASSWORD (default to "test123"): the user's password of the postgreSQL database.
- DB\_HOST (default to "127.0.0.1"): the hostname or address of the postgreSQL database.
- DB\_PORT (default to "6666"): the port of the postgreSQL database.

# How to run ?

## In development mode

### For Foundxtion and nixOS users
In a terminal, do the following commands:
```zsh
cd tools/;
nix-shell --run zsh;
cd ..;
poetry install;
EXPORT OPENAI_API_KEY="YOUR_KEY_HERE";
make run;
```

### For other distributions
You can launch the entire conversation stack in development mode using the
provided docker-compose file in the conversation repository. This usage
simplifies the setting of the environment variables needed.

## In production mode
For the moment, no method other than using the docker compose file in
conversation repository is available. You will need to deploy Wingman along with
the entire conversation stack.
