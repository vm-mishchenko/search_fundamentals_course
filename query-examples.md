## Spelling

### Phrase suggestor (spelling correction)
```shell
GET bbuy_products/_search
{
  "suggest": {
    "text": "some query",
    "phrase_suggest": {
      "phrase": {
        "field": "suggest.trigrams",
        "direct_generator": [
          {
            "field": "title.trigrams",
            "min_word_length": 2,
            "suggest_mode": "popular"
          }
        ]
      }
    }
  }
}
```


### Term suggestion (spelling correction)
Spelling correction is looking directly in the existing index. Other options might be: logs and dictionary. More in my course notess
```shell
GET /suggesters_index/_search
{
  "suggest": {
    "text": "huonds",
    "my-custom-name":{
      "term":{
        "field":"title",
        "min_word_length": 2,
        "suggest_mode": "popular"
      }
    }
  }
}
```

## Custom "word_delimiter_graph" filter
```shell
GET /_analyze
{
  "tokenizer": "whitespace",
  "filter": [
    {
      "type": "word_delimiter_graph",
      "catenate_all": true,
      "catenate_words": true
    }
  ],
  "text": "Neil's-Super-Duper-XL500--42+AutoCoder"
}
```

## Custom "shingle" filter
```shell
GET /_analyze
{
  "tokenizer": "whitespace",
  "filter": [
    {
      "type": "shingle",
      "min_shingle_size": 2,
      "max_shingle_size": 3
    }
  ],
  "text": "Some text or another"
}
```


## Queries from week 1
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

# rescore structure
{
  "query": {
    // Query DSL
    // https://www.elastic.co/guide/en/elasticsearch/reference/7.10/query-dsl.html
  },
  "rescore": [
    {
        "window_size": 1,
        "query": {
            "rescore_query": {
                // Query DSL
            }
        }
    }
  ]
}
```