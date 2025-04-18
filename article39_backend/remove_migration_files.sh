#!/bin/bash

echo "Deleting all Django migration files..."

find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

echo "All migration files (except __init__.py) have been deleted."
