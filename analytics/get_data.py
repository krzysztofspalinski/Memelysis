from pyspark.sql.types import StructType, StringType, IntegerType, FloatType
from pyspark import SparkContext
from pyspark import SparkConf



import pyspark
import subprocess
from pyspark.ml.feature import Word2Vec
from pyspark.sql import functions, SparkSession
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator
from pyspark.sql.functions import regexp_extract


def get_all_memes(spark):
    cmd = 'hdfs dfs -ls /jsons/'

    files = subprocess.check_output(cmd, shell=True)
    files = files.strip()
    files = files.decode().split('\n')

    filenames = []

    for path in files:
        f = path.split(" ")[-1]
        if 'memes_' in f:
            filenames.append(f)
    memes_df = None

    for json_file in filenames:
        memes_tmp = spark.read.json(json_file)
        if memes_df is None:
            memes_df = memes_tmp
        else:
            memes_df = memes_df.union(memes_tmp)
    
    return memes_df

def get_reddit_data(memes_df):
    reddit_df = memes_df.filter(memes_df.source == 'reddit')
    
    reddit_schema = StructType().add(
        'date', StringType(),True).add(
        'title', StringType(), True).add(
        'upvotes', IntegerType(), True).add(
        'upvote_ratio', FloatType(), True)
    
    reddit_data =  reddit_df.select(
        functions.col('id'),
        functions.col('url'),
        functions.col('image_path'),
        functions.col('source'),
        functions.from_json(
            functions.col('additional_data'),
            schema=reddit_schema
        ).alias("data")
    ).select('id','data.*', 'url', 'image_path', 'source')

    reddit_data = reddit_data.filter(reddit_data.upvotes > 9)
    
    return reddit_data

def get_twitter_data(memes_df):
    twitter_df = memes_df.filter(memes_df.source == 'twitter')
    
    twitter_schema = StructType().add(
        'created_at', StringType(), True).add(
        'text', StringType(), True).add(
        'favorite_count', IntegerType(), True).add(
        'retweet_count', IntegerType(), True).add(
        'hashtags', StringType(), True)
    
    twitter_data =  twitter_df.select(
        functions.col('id'),
        functions.from_json(
            functions.col('additional_data'),
            schema=twitter_schema
        ).alias("data")
    ).select('id','data.*')

    twitter_data = twitter_data.filter(twitter_data.favorite_count > 1)
    
    return twitter_data

def get_memedroid_data(memes_df):
    memedroid_df = memes_df.filter(memes_df.source == 'memedroid')
    
    memedroid_schema = StructType().add(
        'title', StringType(), True).add(
        'tags', StringType(), True).add(
        'date', StringType(), True).add(
        'popularity', StringType(), True)
    
    memedroid_data =  memedroid_df.select(
        functions.col('id'),
        functions.from_json(
            functions.col('additional_data'),
            schema=memedroid_schema
        ).alias("data")
    ).select('id','data.*')
    
    upvote_percentage = pyspark.sql.functions.split(memedroid_data['popularity'], '%').getItem(0)
    number_of_votes = pyspark.sql.functions.split(memedroid_data['popularity'], '%').getItem(1)
    
    memedroid_data = memedroid_data.withColumn(
        'upvote_percentage', upvote_percentage.cast("Integer")).withColumn(
        'number_of_votes', regexp_extract(number_of_votes, '[0-9]+',0).cast("Integer"))

    upvotes = (memedroid_data.upvote_percentage * memedroid_data.number_of_votes * 0.01)
    memedroid_data = memedroid_data.withColumn('upvotes', upvotes.cast("Integer"))
    
    memedroid_data = memedroid_data.filter(memedroid_data.upvotes > 100)
    
    return memedroid_data

def get_imgur_data(memes_df):
    imgur_df = memes_df.filter(memes_df.source == 'imgur')
    
    imgur_schema = StructType().add(
        'title', StringType(), True).add(
        'datetime', IntegerType(), True).add(
        'views', IntegerType(), True).add(
        'ups', IntegerType(), True).add(
        'downs', IntegerType(), True).add(
        'points', IntegerType(), True).add(
        'nsfw', StringType(), True)
    
    imgur_data =  imgur_df.select(
        functions.col('id'),
        functions.from_json(
            functions.col('additional_data'),
            schema=imgur_schema
        ).alias("data")
    ).select('id','data.*')

    imgur_data = imgur_data.filter(imgur_data.points > 5)
    
    return imgur_data

def get_tags_data(memes_df):
    memedroid_data = get_memedroid_data(memes_df)
    twitter_data = get_twitter_data(memes_df)
    
    tags_memedroid = memedroid_data.select(
        functions.col('id'),
        functions.col('tags'))

    tags_twitter = twitter_data.select(
        functions.col('id'),
        functions.col('hashtags').alias('tags'))

    tags_df = tags_memedroid.union(tags_twitter)

    return tags_df

def get_text_data(memes_df):
    text_data = memes_df.select('id', 'text')
    return text_data