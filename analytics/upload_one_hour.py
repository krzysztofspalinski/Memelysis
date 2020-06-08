import re

from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession
from pyspark.ml.feature import Tokenizer, StopWordsRemover, Word2Vec
from get_data import get_all_memes, save_meme_tags, get_memedroid_data, get_twitter_data, get_imgur_data, get_text_data, get_reddit_data
from pyspark.ml.clustering import KMeans
from pyspark.ml import Pipeline
from pyspark.ml.feature import StandardScaler
from pyspark.sql import functions
from utils import upload_blob

import numpy as np

sc = SparkContext.getOrCreate()
spark = SparkSession.builder.getOrCreate()

memes_df = get_all_memes(spark, False)

number_of_clusters = 7

def load_upvote_data(source):
    upvotes = sc.textFile("hdfs:///upvotes/{}".format(str(source))).flatMap(lambda line: line.split('\n'))
    upvotes = upvotes.collect()
    upvotes = np.array([int(i) for i in upvotes])
    upvotes.sort()
    return upvotes

up_reddit = load_upvote_data('reddit')
up_twitter = load_upvote_data('twitter')
up_imgur = load_upvote_data('imgur')
up_memedroid = load_upvote_data('memedroid')


def get_percentile_reddit(value):
    import numpy as np
    return np.sum(value > up_reddit) / len(up_reddit)

def get_percentile_twitter(value):
    return np.sum(value > up_twitter) / len(up_twitter)

def get_percentile_imgur(value):
    return np.sum(value > up_imgur) / len(up_imgur)

def get_percentile_memedroid(value):
    return np.sum(value > up_memedroid) / len(up_memedroid)


from pyspark.ml import PipelineModel

memes_df = get_all_memes(spark, False)

model = PipelineModel.load("hdfs:///models/model")
X = model.transform(memes_df)

X = X.select('additional_data', 'source', 'id', 'prediction', 'url', 'image_path')
X = X.cache()

def get_popular_tag(list_of_tags, cluster_names):
    i = 0
    tags_to_omit = ['', 'randommemedump', 'memes', 'meme', 'funny','dump', 'memedump', 'dankmemes', 'reddit', 'description', 'twitter', 'lol', 'thumbnailhash']
    while True:
        if list_of_tags[i][0] not in tags_to_omit and list_of_tags[i][0] not in cluster_names:
            return list_of_tags[i][0]
        i += 1

cluster_names = []
for cluster_id in range(number_of_clusters):
    words = sc.textFile("hdfs:///tags/all_tags_{0}".format(cluster_id)).flatMap(lambda line: line.split(" "))
    wordCounts = words.map(lambda word: (re.sub('[^A-Za-z0-9]+', '', word.lower()), 1)).reduceByKey(lambda a,b:a +b)
    tags = wordCounts.sortBy(lambda atuple: atuple[1], ascending = False).collect()
    cluster_names.append(get_popular_tag(tags, cluster_names))


tmp = spark.createDataFrame([(i, cluster_names[i]) for i in range(number_of_clusters)], ["prediction", "cluster"])
X = X.join(tmp, on=['prediction'], how='left_outer')
X.cache()

memedroid = get_memedroid_data(memes_df)
memedroid = memedroid.select('id', "upvotes", "timestamp")

twitter = get_twitter_data(memes_df)
twitter = twitter.select('id', functions.col('favorite_count').alias('upvotes'), "timestamp")

reddit = get_reddit_data(memes_df)
reddit = reddit.select('id', 'upvotes', "timestamp")

imgur = get_imgur_data(memes_df)
imgur = imgur.select('id', functions.col('ups').alias('upvotes'), "timestamp")

all_upvotes = memedroid.union(twitter).union(reddit).union(imgur)

X = X.join(all_upvotes, on = ['id'], how="left_outer")

X = X.na.drop()
X.cache()

X_df = X.toPandas()

X_df.loc[X_df['source']=='reddit', 'percentile'] = X_df[X_df['source']=='reddit']['upvotes'].apply(
    get_percentile_reddit)
X_df.loc[X_df['source']=='twitter', 'percentile'] = X_df[X_df['source']=='twitter']['upvotes'].apply(
    get_percentile_twitter)
X_df.loc[X_df['source']=='imgur', 'percentile'] = X_df[X_df['source']=='imgur']['upvotes'].apply(
    get_percentile_imgur)
X_df.loc[X_df['source']=='memedroid', 'percentile'] = X_df[X_df['source']=='memedroid']['upvotes'].apply(
    get_percentile_memedroid)

X_df = X_df.loc[:, ['id', 'url', 'image_path', 'source', 'timestamp', 'upvotes', 'percentile', 'cluster']]

X_df.columns = ['meme_id', 'url', 'image_path', 'source', 'meme_datetime', 'upvotes', 'upvotes_centile', 'cluster']

X_df.to_json('/home/data_to_upload_on_bucket/one_hour_data.json')
upload_blob('/home/data_to_upload_on_bucket/one_hour_data.json', 'one_hour_data.json')