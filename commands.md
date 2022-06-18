```shell
# check products logs
tail -f /workspace/logs/index_products.log

# check queries logs
tail -f /workspace/logs/index_queries.log
```

```shell
# start week1 app | Can set up "Run configuration" as well
pyenv activate search_fundamentals
export FLASK_ENV=development
export FLASK_APP=week1
flask run --port 3000
```


## week 2 project
```shell
# index data
./index-data.sh -y ./week2 -p ./week2/conf/bbuy_products.json -q ./week2/conf/bbuy_queries.json
```

## install jupiter server
```shell
# for some reason has to install "jupyter_server" first. Without it `pip install jupyter` did not work.
pip install jupyter_server

pip install jupyter
```