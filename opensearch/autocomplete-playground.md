
## Query
```
POST autocomplete_example/_search?pretty
{
  "suggest": {
    "song-suggest": {
      "prefix": "fir",        
      "completion": {         
          "field": "suggest"  
      }
    }
  }
}
```

## Indexing
```
# mapping
PUT autocomplete_example
{
  "mappings": {
    "properties": {
      "suggest": {
        "type": "completion"
      },
      "title": {
        "type": "text"
      }
    }
  }
}

# index items
PUT autocomplete_example/_doc/1
{
  "suggest" : {
    "input": [ "First title" ],
    "weight" : 34
  },
  "title": "First title"
}

PUT autocomplete_example/_doc/2
{
  "suggest" : {
    "input": [ "Second title" ],
    "weight" : 34
  },
  "title": "Second title"
}
```