import re
import subprocess

from pyspark import SparkContext
from pyspark.sql import SparkSession
from get_data import get_all_memes, save_meme_tags, get_memedroid_data, get_twitter_data, get_imgur_data, get_reddit_data
from utils import train_model, get_popular_tag, get_source_upvotes, upload_blob, upload_to_bucket
from pyspark.ml import PipelineModel
from google.cloud import storage

sc = SparkContext.getOrCreate()
spark = SparkSession.builder.getOrCreate()

number_of_clusters = 7

memes_df = get_all_memes(spark)
memes_df = memes_df.cache()
memes_df_train = memes_df.drop_duplicates(subset=['text'])
model = train_model(memes_df_train, number_of_clusters, 50)

# model = PipelineModel.load("hdfs:///models/model")
X = model.transform(memes_df)
X = X.select('id', 'prediction','additional_data', 'source')
X = X.cache()

save_meme_tags(X, number_of_clusters)

cluster_names = []
for cluster_id in range(number_of_clusters):
    words = sc.textFile("hdfs:///tags/all_tags_{0}".format(cluster_id)).flatMap(lambda line: line.split(" "))
    wordCounts = words.map(lambda word: (re.sub('[^A-Za-z0-9]+', '', word.lower()), 1)).reduceByKey(lambda a,b:a +b)
    tags = wordCounts.sortBy(lambda atuple: atuple[1], ascending = False).collect()
    cluster_names.append(get_popular_tag(tags, cluster_names))

tmp = spark.createDataFrame([(i, cluster_names[i]) for i in range(number_of_clusters)], ["prediction", "cluster"])

memedroid = get_memedroid_data(memes_df)
memedroid = get_source_upvotes(memedroid, 'upvotes', 'memedroid')
memedroid.cache()
twitter = get_twitter_data(memes_df)
twitter = get_source_upvotes(twitter, 'favorite_count', 'twitter')
twitter.cache()
reddit = get_reddit_data(memes_df)
reddit = get_source_upvotes(reddit, 'upvotes', 'reddit')
reddit.cache()
imgur = get_imgur_data(memes_df)
imgur = get_source_upvotes(imgur, 'ups', 'imgur')
imgur.cache()

all_upvotes = memedroid.union(twitter).union(reddit).union(imgur)

X = X.join(all_upvotes, on = ['id'], how="left_outer")

X = X.join(tmp, on = ['prediction'], how="left_outer")

X = X.na.drop()

X = X.select('id', 'upvotes', 'timestamp', 'upvotes_centile', 'cluster')

X.coalesce(1).write.format('json').mode("overwrite").save('hdfs:///json_bucket')


upload_to_bucket('/json_bucket')