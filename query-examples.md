# Queries from Open Search dev panel

```
# mapping
GET /bbuy_products

GET /bbuy_products/_search

GET /bbuy_products/_count

# check whether index exists
HEAD /bbuy_products

# delete index
DELETE /bbuy_products

# query tunning
GET bbuy_products/_search
{
  "query": {
    "function_score": {
      "query": {
        "query_string": {
          "query": "\"ipad 2\"",
          "fields": [
            "name^1000",
            "shortDescription^50",
            "longDescription^10",
            "department"
          ]
        }
      },
      "boost_mode": "replace",
      "score_mode": "avg",
      "functions": [
        {
          "field_value_factor": {
            "field": "salesRankLongTerm",
            "modifier": "reciprocal",
            "missing": 100000000
          }
        },
        {
          "field_value_factor": {
            "field": "salesRankMediumTerm",
            "modifier": "reciprocal",
            "missing": 100000000
          }
        },
        {
          "field_value_factor": {
            "field": "salesRankShortTerm",
            "modifier": "reciprocal",
            "missing": 100000000
          }
        }
      ]
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