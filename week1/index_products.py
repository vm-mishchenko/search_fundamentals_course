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
    # "name/text()", "name",
    # "type/text()", "type",
    # "regularPrice/text()", "regularPrice",
    # "salePrice/text()", "salePrice",
    # "onSale/text()", "onSale",
    # "salesRankShortTerm/text()", "salesRankShortTerm",
    # "salesRankMediumTerm/text()", "salesRankMediumTerm",
    # "salesRankLongTerm/text()", "salesRankLongTerm",
    # "bestSellingRank/text()", "bestSellingRank",
    # "url/text()", "url",
    # "categoryPath/*/name/text()", "categoryPath",  # Note the match all here to get the subfields
    # "categoryPath/*/id/text()", "categoryPathIds",  # Note the match all here to get the subfields
    # "categoryPath/category[last()]/id/text()", "categoryLeaf",
    # "count(categoryPath/*/name)", "categoryPathCount",
    # "customerReviewCount/text()", "customerReviewCount",
    # "customerReviewAverage/text()", "customerReviewAverage",
    # "inStoreAvailability/text()", "inStoreAvailability",
    # "onlineAvailability/text()", "onlineAvailability",
    # "releaseDate/text()", "releaseDate",
    # "shortDescription/text()", "shortDescription",
    # "class/text()", "class",
    # "classId/text()", "classId",
    # "department/text()", "department",
    # "departmentId/text()", "departmentId",
    # "bestBuyItemId/text()", "bestBuyItemId",
    # "description/text()", "description",
    # "manufacturer/text()", "manufacturer",
    # "modelNumber/text()", "modelNumber",
    # "image/text()", "image",
    # "longDescription/text()", "longDescription",
    # "longDescriptionHtml/text()", "longDescriptionHtml",
    # "features/*/text()", "features"  # Note the match all here to get the subfields
]


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

def index_docs(client, docs):
    bulk(client, docs)

def remove_all_docs_from_index(client, index_name):
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
def main(source_dir: str, index_name: str):

    glob_example_product = '/workspace/search_fundamentals_course/document-examples/product.xml'
    glob_example_products = source_dir + "/products_0120_11768321_to_11821246.xml"
    glob_all_products = source_dir + "/*.xml"

    client = get_opensearch()
    # print_index_mapping(client, index_name)
    # print_number_of_docs(client, index_name)
    remove_all_docs_from_index(client, index_name)

    # To test on a smaller set of documents, change this g]lob to be more restrictive than *.xml
    files = glob.glob(glob_all_products)
    docs_indexed = 0
    tic = time.perf_counter()
    docs = []

    for index, file in enumerate(files):
        logger.info(f'Processing file {index} : {file}')
        tree = etree.parse(file)
        root = tree.getroot()
        children = root.findall("./product")
        for child in children:
            doc = {}
            for idx in range(0, len(mappings), 2):
                xpath_expr = mappings[idx]
                key = mappings[idx + 1]
                # more about xpath: https://lxml.de/xpathxslt.html#the-xpath-method
                values = child.xpath(xpath_expr)

                # todo: remove afterwards
                assert len(values) == 1

                value = values[0]

                doc[key] = value
            if not 'productId' in doc or len(doc['productId']) == 0:
                continue

            #### Step 2.b: Create a valid OpenSearch Doc and bulk index 2000 docs at a time
            the_doc = doc.copy()
            the_doc['_id'] = the_doc['sku']
            the_doc['_index'] = index_name

            assert the_doc['_id'] is not None, "doc_id is required"

            docs.append(the_doc)

            if len(docs) == 2000:
                index_docs(client, docs)
                docs_indexed += 2000

    if len(docs) > 0:
        index_docs(client, docs)
        docs_indexed += len(docs)

    toc = time.perf_counter()
    logger.info(f'Done. Total docs: {docs_indexed}.  Total time: {((toc - tic) / 60):0.3f} mins.')
    print_number_of_docs_in_os(client, index_name)


if __name__ == "__main__":
    main()
