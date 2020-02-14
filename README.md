# THIS PROJECT HAS BEEN ARCHIVED AND IS NO LONGER MAINTAINED.

![Sayonika](https://media.discordapp.net/attachments/373669252554686464/458045399563763775/sayonika.png?width=430&height=430)

# Sayonika Server

This repository contains the Sayonika server code.
Sayonika uses a Microservice layout for serving its mod listing. This means, each component has to be deployed individually but increases fault tolerance.
Sayonika server is built with Quart, Micro, and ❤️.

## Running

Sayonika requires Python and Node.js to run.

0. Get the latest version of Python from the [Python website](https://python.org) (Python 3.7.0 or higher) and the latest version of Node.js from the [Node.js website](https://nodejs.org) (Node 8.0.0 or higher).
1. Clone/download the repository and install dependencies by running `pip install -r requirements.txt` and `npm install` (in `services/`).
2. Set environment variables as described in [env-vars.md](./env-vars.md).
3. Run migrations with `alembic upgrade head`.
4. Run `python main.py`.

## Contributing

The main server is created with Python, with the microservices being done in Node.js. You are required to follow the coding style set on our repository.
The full contribution guide can be found [here](CONTRIBUTING.md)

## Disclaimer

Sayonika, Sayonika chibi, and the Sayonika Logo are copyrighted under Creative Commons 3.0 Non-Commercial.
Doki Doki Literature Club, The Doki Doki Literature Club Logo, and its characters are Copyright 2017-2018 (c) Team Salvato.
Sayonika is not associated with Team Salvato in any way, and the service complies with the Team Salvato Guidelines.
