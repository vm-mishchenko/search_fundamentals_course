# Queries from Open Search dev panel

```
# mapping
GET /bbuy_products

GET bbuy_products/_search

GET bbuy_products/_count


# sku
GET bbuy_products/_search
{
  "query": {
    "match": {
      "name": "films"
    }
  }
}


############################
##### EXAMPLES
############################

# text: short form
GET bbuy_products/_search
{
  "query": {
    "match": {
      "name": "test"
    }
  }
}


# text: long form
GET bbuy_products/_search
{
  "query": {
    "match": {
      "name": {
        "query": "test pilot",
        "operator": "and"
      }
    }
  }
}

# text multi_match example
GET bbuy_products/_search
{
  "query": {
    "multi_match": {
      "query": 47709,
      "fields": ["productId"]
    }
  }
}

# number: range query
GET bbuy_products/_search
{
  "query": {
    "range": {
      "regularPrice": {
        "gte": 15
      }
    }
  }
}

# boolean
GET bbuy_products/_search
{
  "query": {
    "term": {
      "onSale": false
    }
  }
}

```