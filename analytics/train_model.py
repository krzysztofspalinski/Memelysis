from text_clustering import text_clustering, tags, train_model
from get_data import get_all_memes, get_tags_data
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.ml.feature import Word2Vec
from pyspark.ml.clustering import KMeans

sc = SparkContext.getOrCreate()
spark = SparkSession.builder.getOrCreate()

memes_df = get_all_memes(spark)
memes_tags = get_tags_data(memes_df)

k = 7
data_with_prediciton, clust_names = train_model(memes_df, memes_tags, k = k) #funkcja zapisuje modele, zwraca data_frama z predykcjami oraz slownik z cluster name

tmp = spark.createDataFrame([(str(i), clust_names[str(i)]) for i in range(int(k))], ["Cluster_id", "Cluster_name"])
tmp \
   .repartition(1) \
   .write.format("com.databricks.spark.csv") \
   .option("header", "true") \
   .save("/models/clusters_names", mode='overwrite') # zapisanie słownika cluster_names jako .csv na hadoop
