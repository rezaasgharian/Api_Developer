# API Developer (Python / Django)

## Requirements

- docker

## Environment in docker

- Ubuntu 20.04
- python 3.7
- SQLite

    
## How to Run
```
# with mac os or linux
bash run.sh

# manually build & run
docker build -t bepro/api_developer .
docker run -it --rm bepro/api_developer python manage.py test
```
