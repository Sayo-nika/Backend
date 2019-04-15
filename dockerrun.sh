#!/bin/sh

alembic upgrade head
hypercorn main:sayonika_instance -b 0.0.0.0:8000 -k uvloop
