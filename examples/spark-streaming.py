
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("HOST")
parser.add_argument("PORT")

args = parser.parse_args()

HOST = args.HOST
PORT = int(args.PORT)


if __name__ == "__main__":
    sc   = SparkContext()
    ssc  = StreamingContext(sc, 5)

    lines = ssc.socketTextStream(HOST, PORT)

    # Split each line into words
    words = lines.flatMap(lambda line: line.split(" "))
    # Count each word in each batch
    pairs = words.map(lambda word: (word, 1))
    wordCounts = pairs.reduceByKey(lambda x, y: x + y)

    # Print the first ten elements of each RDD generated in this DStream to the console
    wordCounts.pprint()


    ssc.start()             # Start the computation
    ssc.awaitTermination()  # Wait for the computation to terminate