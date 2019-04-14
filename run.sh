#!/bin/sh

# First run the Alembic Migration
alembic upgrade head

# Now run the server
hypercorn main:sayonika_instance
