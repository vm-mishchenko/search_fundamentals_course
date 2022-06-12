```shell
# check products logs
tail -f /workspace/logs/index_products.log

# check queries logs
tail -f /workspace/logs/index_queries.log
```

```shell
# start week1 app

pyenv activate search_fundamentals
export FLASK_ENV=development
export FLASK_APP=week1
flask run --port 3000
```