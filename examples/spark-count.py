import pyspark 
print(pyspark.SparkContext().parallelize(range(0, 10)).count())
