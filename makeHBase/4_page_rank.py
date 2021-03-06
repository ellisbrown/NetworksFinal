simport sys

from pyspark import SparkConf, SparkContext

from variables import MACHINE, BUCKET, PAGE_TABLE, INDEX_TABLE, COLUMN_FAMILY, COLUMN

link_file = BUCKET + 'link_index'
rank_file = BUCKET + 'ranks'


'''
Implement page rank.

Mimic the pyspark code: https://github.com/apache/spark/blob/master/examples/src/main/python/pagerank.py

Use the iterations input to control the number of times to loop.

The results should be written to the rank_file.

You will want to use sortBy to order pages by rank.

'''
def page_rank(spark, iterations):
    links = spark.textFile(link_file)
    links = links.map(lambda line: eval(line)) \
        .map(lambda line: (line[0], line[1])) \
        .distinct().groupByKey().cache()

    # Loads all URLs with other URL(s) link to from input file and initialize ranks of them to one.
    ranks = links.map(lambda url_neighbors: (url_neighbors[0], 1.0))

    # Calculates and updates URL ranks continuously using PageRank algorithm.
    for iteration in range(iterations):
        # Calculates URL contributions to the rank of other URLs.
        contribs = links.join(ranks).flatMap(
            lambda uur: computeContribs(uur[1][0], uur[1][1]))

        # Re-calculates URL ranks based on neighbor contributions.
        ranks = contribs.reduceByKey(lambda x, y: x + y) \
            .mapValues(lambda rank: rank * 0.85 + 0.15)

    ranks.sortBy(lambda (x,y): y) \
        .saveAsTextFile(rank_file)

def computeContribs(urls, rank):
    """Calculates URL contributions to the rank of other URLs."""
    num_urls = len(urls)
    for url in urls:
        yield (url, rank / num_urls)

if __name__ == '__main__':
    spark = SparkContext(appName='pagerank')
    page_rank(spark, 10)
    spark.stop()
