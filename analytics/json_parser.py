import subprocess

from pyspark import SparkContext, SparkConf

from pyspark.sql.types import StructType, IntegerType, StringType, FloatType
from pyspark.sql import SparkSession, SQLContext, functions

from pyspark.sql.functions import lit
1

def parse_json(df, sc, spark, sqlContext):

    # Schemes for different sources
    twitter_schema = StructType().add(
    'created_at', StringType(), True).add(
    'text', StringType(), True).add(
    'favorite_count', IntegerType(), True).add(
    'retweet_count', IntegerType(), True).add(
    'hashtags', StringType(), True)

    memedroid_schema = StructType().add(
    'title', StringType(), True).add(
    'tags', StringType(), True).add(
    'date', StringType(), True).add(
    'popularity', StringType(), True)

    imgur_schema = StructType().add(
    'title', StringType(), True).add(
    'datetime', IntegerType(), True).add(
    'views', IntegerType(), True).add(
    'ups', IntegerType(), True).add(
    'downs', IntegerType(), True).add(
    'points', IntegerType(), True).add(
    'nsfw', StringType(), True)

    reddit_schema = StructType().add(
    'title', StringType(), True).add(
    'date', FloatType(), True).add(
    'upvotes', IntegerType(), True).add(
    'upvote_ratio', FloatType(), True)

    #final dataframe scheme
    final_schema = StructType().add(
        'id', StringType(), True).add(
        'image_path', StringType(), True).add(
        'extension', StringType(), True).add(
        'source', StringType(), True).add(
        'text', StringType(), True).add(
        'url', StringType(), True).add(
        # Twitter
        'twitter_created_at', StringType(), True).add(
        'twitter_tweet_text', StringType(), True).add(
        'twitter_favorite_count', IntegerType(), True).add(
        'twitter_retweet_count', IntegerType(), True).add(
        'twitter_hashtags', StringType(), True).add(
        # Memedroid
        'memedroid_title', StringType(), True).add(
        'memedroid_tags', StringType(), True).add(
        'memedroid_date', StringType(), True).add(
        'memedroid_popularity', StringType(), True).add(
        # imgur
        'imgur_title', StringType(), True).add(
        'imgur_datetime', StringType(), True).add(
        'imgur_views', IntegerType(), True).add(
        'imgur_ups', IntegerType(), True).add(
        'imgur_downs', IntegerType(), True).add(
        'imgur_points', IntegerType(), True).add(
        'imgur_nsfw', StringType(), True).add(
        # reddit
        'reddit_title', StringType(), True).add(
        'reddit_date', FloatType(), True).add(
        'reddit_upvotes', IntegerType(), True).add(
        'reddit_upvote_ratio', FloatType(), True)
    output = sqlContext.createDataFrame(sc.emptyRDD(), final_schema)

    schemes = {"twitter": twitter_schema,
               "memedroid": memedroid_schema,
               "imgur": imgur_schema,
               "reddit": reddit_schema}

    # all sources contain such columns 
    common_cols = ['id', 'image_path', 'extension', 'source', 'text', 'url']

    specific_cols = {"twitter": ['created_at', 'text', 'favorite_count', 'retweet_count', 'hashtags'],
    "memedroid": ['title', 'tags', 'date', 'popularity'],
    "imgur": ['title', 'datetime', 'views', 'ups', 'downs', 'points', 'nsfw'],
    "reddit": ['title', 'date', 'upvotes', 'upvote_ratio']}

    parsed_jsons = []

    for source in ["twitter", "memedroid", "imgur", "reddit"]:
        current_df = df.filter(df.source == source) 

        # check if specific data source was correctly collected 
        if current_df.count() > 0:

            current_data = current_df.select(
                functions.col('id'),
                functions.from_json(functions.col('additional_data'), schema=schemes[source]).alias('data')
                ).select('id', 'data.*')

            # twitter have 2 column with same name
            if source == "twitter": current_data = current_data.withColumnRenamed('text', 'tweet_text')

            df_alias = source + "_df"
            data_alias = source + "_data"

            current_df = current_df.alias(df_alias)
            current_data = current_data.alias(data_alias)

            # twitter col workaround
            current_join = current_df.join(current_data, current_df.id == current_data.id).select(
                *([(df_alias + "." + colname) for colname in common_cols] +
                 [(data_alias + "." + colname) if colname != 'text' else (data_alias + ".tweet_" + colname) for colname in specific_cols[source]]))

            # renaming cols
            for col in current_join.schema.names:
                if col not in common_cols:
                    current_join = current_join.withColumnRenamed(col, source + '_' + col)

            for field in output.schema.fields:
                if field.name not in current_join.schema.names:
                    current_join = current_join.withColumn(field.name, lit(None).cast(field.dataType))
            
            current_join = current_join.select(output.schema.names)
            parsed_jsons.append(current_join)

    output = parsed_jsons[0]
    for js in parsed_jsons[1:]:   
        output = output.union(js)

    return output

def main():

    #setup
    sc = SparkContext.getOrCreate()
    spark = SparkSession.builder.getOrCreate()
    sqlContext = SQLContext.getOrCreate(sc)

    spark.catalog.clearCache()
    sqlContext.clearCache()
    
    cmd = 'hdfs dfs -ls /jsons/'

    files = subprocess.check_output(cmd, shell=True)
    files = files.strip()
    files = files.decode().split('\n')

    out = []

    for path in files:
        f = path.split(" ")[-1]
        if 'memes_' in f:
            out.append(f)
            print(f)

    df = spark.read.json(out[-1])
    x = parse_json(df, sc, spark, sqlContext)
       
    x.limit(5).show()
    print("Count:")
    print(x.count())
    x.count()
    x.printSchema()

if __name__ == "__main__":
    main()