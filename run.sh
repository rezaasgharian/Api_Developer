#!/bin/bash

docker build -t bepro/api_developer .

echo --------------------------
echo Running Django test
echo --------------------------

docker run -it --rm bepro/api_developer python manage.py test

