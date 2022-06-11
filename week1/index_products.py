# From https://github.com/dshvadskiy/search_with_machine_learning_course/blob/main/index_products.py
import requests
from lxml import etree

import click
import glob
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk
import logging
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(levelname)s:%(message)s')

# doc
# https://corise.com/course/search-fundamentals/module/opensearch-revisited-old

# NOTE: this is not a complete list of fields.  If you wish to add more, put in the appropriate XPath expression.
# TODO: is there a way to do this using XPath/XSL Functions so that we don't have to maintain a big list?
mappings = [
    "sku/text()", "sku", # SKU is the unique ID, productIds can have multiple skus
    "productId/text()", "productId",
    "name/text()", "name",
    "type/text()", "type",
    "regularPrice/text()", "regularPrice",
    "salePrice/text()", "salePrice",
    "onSale/text()", "onSale",
    "salesRankShortTerm/text()", "salesRankShortTerm",
    "salesRankMediumTerm/text()", "salesRankMediumTerm",
    "salesRankLongTerm/text()", "salesRankLongTerm",
    "bestSellingRank/text()", "bestSellingRank",
    "url/text()", "url",
    "categoryPath/*/name/text()", "categoryPath",  # Note the match all here to get the subfields
    "categoryPath/*/id/text()", "categoryPathIds",  # Note the match all here to get the subfields
    "categoryPath/category[last()]/id/text()", "categoryLeaf",
    "count(categoryPath/*/name)", "categoryPathCount",
    "customerReviewCount/text()", "customerReviewCount",
    "customerReviewAverage/text()", "customerReviewAverage",
    "inStoreAvailability/text()", "inStoreAvailability",
    "onlineAvailability/text()", "onlineAvailability",
    "releaseDate/text()", "releaseDate",
    "shortDescription/text()", "shortDescription",
    "class/text()", "class",
    "classId/text()", "classId",
    "department/text()", "department",
    "departmentId/text()", "departmentId",
    "bestBuyItemId/text()", "bestBuyItemId",
    "description/text()", "description",
    "manufacturer/text()", "manufacturer",
    "modelNumber/text()", "modelNumber",
    "image/text()", "image",
    "longDescription/text()", "longDescription",
    "longDescriptionHtml/text()", "longDescriptionHtml",
    "features/*/text()", "features"  # Note the match all here to get the subfields
]

# Open Search Helpers
def get_opensearch():
    host = 'localhost'
    port = 9200
    auth = ('admin', 'admin')

    #### Step 2.a: Create a connection to OpenSearch
    client = OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_compress=True,
        http_auth=auth,
        use_ssl=True,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
    )
    return client

def index_exists(client, index_name):
    return client.indices.exists(index_name)

def delete_index(client, index_name):
    response = client.indices.exists(index_name)

    client.indices.delete(index=index_name)
    logger.info(f'Index "{index_name}" has been deleted')

def create_index(client, index_name):
    index_body = {
        'settings': {
            'index': {
                'query': {
                    'default_field': "body"
                }
            }
        },
        "mappings": {
            "properties": {
                # Only text fields support the analyzer mapping parameter.
                "sku": {"type": "text", "analyzer": "standard",
                         "fields": {"keyword": {"type": "keyword", "ignore_above": 100}}},
                "productId": {"type": "keyword"},
                "name": {"type": "text", "analyzer": "standard",
                         "fields": {"keyword": {"type": "keyword", "ignore_above": 2000}}},
                "type": {"type": "keyword"},
                "regularPrice": {"type": "float"},
                "salePrice": {"type": "float"},
                "onSale": {"type": "boolean"},
                "salesRankShortTerm": {"type": "long"},
                "salesRankMediumTerm": {"type": "long"},
                "bestSellingRank": {"type": "long"},
                # https://stackoverflow.com/questions/417142/what-is-the-maximum-length-of-a-url-in-different-browsers
                "url": {"type": "text", "analyzer": "standard",
                        "fields": {"keyword": {"type": "keyword", "ignore_above": 2000}}},
                "categoryPath": {"type": "text", "analyzer": "standard",
                                 "fields": {"keyword": {"type": "keyword", "ignore_above": 2048}}},
                "categoryPathIds": {"type": "keyword"},
                "categoryLeaf": {"type": "keyword"},
                "categoryPathCount": {"type": "integer"},
                "customerReviewCount": {"type": "integer"},
                "customerReviewAverage": {"type": "integer"},
                "inStoreAvailability": {"type": "boolean"},
                "onlineAvailability": {"type": "boolean"},
                "releaseDate": {"type": "date"},
                "shortDescription": {"type": "text", "analyzer": "standard",
                                     "fields": {"keyword": {"type": "keyword", "ignore_above": 2048}}},
                "class": {"type": "text", "analyzer": "standard",
                          "fields": {"keyword": {"type": "keyword", "ignore_above": 500}}},
                "classId": {"type": "keyword"},
                "department": {"type": "text", "analyzer": "standard",
                               "fields": {"keyword": {"type": "keyword", "ignore_above": 1024}}},
                "departmentId": {"type": "integer"},
                "bestBuyItemId": {"type": "keyword"},
                "description": {"type": "text", "analyzer": "standard",
                                "fields": {"keyword": {"type": "keyword", "ignore_above": 2048}}},
                "manufacturer": {"type": "text", "analyzer": "standard",
                                 "fields": {"keyword": {"type": "keyword", "ignore_above": 1024}}},
                "modelNumber": {"type": "keyword"},
                "image": {"type": "keyword"},
                "longDescription": {"type": "text", "analyzer": "standard",
                                    "fields": {"keyword": {"type": "keyword", "ignore_above": 2048}}},
                # todo-later: use custom analyzer with "html_strip" filter. "standard" analyzer does not strip HTML tags
                "longDescriptionHtml": {"type": "text", "analyzer": "standard",
                                        "fields": {"keyword": {"type": "keyword", "ignore_above": 2048}}},
                "features": {"type": "text", "analyzer": "standard",
                             "fields": {"keyword": {"type": "keyword", "ignore_above": 2048}}},
            }
        }
    }
    client.indices.create(index_name, body=index_body)
    logger.info(f'Index "{index_name}" has been created')

def index_docs(client, docs):
    bulk(client, docs)

def remove_all_docs_from_index(client, index_name):
    logger.info(f'Start removing docs "{index_name}" index')
    query_body = {
        "query": {
            "match_all": {}
        }
    }
    client.delete_by_query(index_name, body=query_body)
    logger.info(f'All docs were removed from "{index_name}" index')

def print_index_mapping(client, index_name):
    print(client.indices.get_mapping(index_name))

def print_number_of_docs_in_os(client, index_name):
    response = client.cat.count(index_name, params={"format": "json"})
    logger.info(f'Number of docs in OS: {response[0]["count"]}')

@click.command()
@click.option('--source_dir', '-s', default="/workspace/datasets/product_data/products", help='XML files source directsory')
@click.option('--index_name', '-i', default="bbuy_products", help="The name of the index to write to")
@click.option('--called_from_index_data', '-c', default="false", help="The name of the index to write to")
@click.option('--workers', '-w', default=8, help="The name of the index to write to")
def main(source_dir: str, index_name: str, called_from_index_data: str, workers: int):
    client = get_opensearch()

    # To test on a smaller set of documents, change this glob to be more restrictive than *.xml
    glob_example_product = '/workspace/search_fundamentals_course/document-examples/product.xml'
    glob_example_products = source_dir + "/products_0120_11768321_to_11821246.xml"
    glob_all_products = source_dir + "/*.xml"
    active_glob = glob_all_products

    # re-create index from scratch
    if is_debug_mode(called_from_index_data):
        logger.info(f'DEBUG MODE.')
        if index_exists(client, index_name):
            delete_index(client, index_name)
        create_index(client, index_name)
    else:
        logger.info(f'index_data.sh MODE.')
        if active_glob != glob_all_products:
            raise Exception('Double check active_globe')

    files = glob.glob(active_glob)
    docs_indexed = 0
    tic = time.perf_counter()
    docs = []

    for index, file in enumerate(files):
        logger.info(f'Processing file {index} out of {len(files)} : {file}')
        tree = etree.parse(file)
        root = tree.getroot()
        children = root.findall("./product")
        for child in children:
            doc = {}
            for idx in range(0, len(mappings), 2):
                xpath_expr = mappings[idx]
                key = mappings[idx + 1]
                # more about xpath: https://lxml.de/xpathxslt.html#the-xpath-method
                value = child.xpath(xpath_expr)
                doc[key] = value
            if not 'productId' in doc or len(doc['productId']) == 0:
                continue

            #### Step 2.b: Create a valid OpenSearch Doc and bulk index 2000 docs at a time
            the_doc = doc.copy()
            the_doc['id'] = the_doc['sku'][0]
            the_doc['_index'] = index_name

            assert the_doc['id'] is not None, "document 'id' is required"

            docs.append(the_doc)

            if len(docs) == 2000:
                logger.info(f'Index in bulk {len(docs)} docs.')
                index_docs(client, docs)
                docs_indexed += 2000
                docs = []

    if len(docs) > 0:
        logger.info(f'Final Index in bulk {len(docs)} docs.')
        index_docs(client, docs)
        docs_indexed += len(docs)

    toc = time.perf_counter()
    logger.info(f'Done. Total docs: {docs_indexed}.  Total time: {((toc - tic) / 60):0.3f} mins.')

# Helpers not related to Open Search
def print_value_for_field(doc, field_name):
    values = doc[field_name]
    if len(values) > 0:
        logger.info(f'{field_name}: {values}')

def is_debug_mode(called_from_index_data):
    return called_from_index_data == 'false'

if __name__ == "__main__":
    main()
