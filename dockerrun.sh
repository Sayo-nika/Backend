#!/bin/sh

alembic upgrade head
# hypercorn main:sayonika_instance -b 0.0.0.0:8000
daphne -b 0.0.0.0 -p 8000 main:sayonika_instance
