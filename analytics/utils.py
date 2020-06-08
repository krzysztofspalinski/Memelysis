import subprocess

from pyspark.ml.feature import Tokenizer, StopWordsRemover, Word2Vec
from pyspark.ml.clustering import KMeans
from pyspark.ml import Pipeline
from pyspark.ml.feature import StandardScaler
from pyspark.sql import Window
from pyspark.sql import functions
from pyspark.sql.functions import row_number
from google.cloud import storage

def train_model(dataFrame, k_value, w2v_value, seed = 2137):
    """Train and save model"""
    
    tokenizer = Tokenizer(inputCol="text", outputCol="words_raw")
    remover = StopWordsRemover(inputCol="words_raw", outputCol="words")
    word2Vec = Word2Vec(vectorSize=w2v_value, seed=seed, inputCol="words", outputCol="features_unnormalized")
    scaler = StandardScaler(inputCol="features_unnormalized", outputCol="features",withStd=True, withMean=True)
    kmeans = KMeans(k = k_value, seed = seed)
    pipeline = Pipeline(stages=[tokenizer, remover, word2Vec, scaler, kmeans])
    pipeline = pipeline.fit(dataFrame)
    pipeline.write().overwrite().save("hdfs:///models/model")
    
    return pipeline


def get_popular_tag(list_of_tags, cluster_names):
    """From list_of_tags return the most popular, unique tag"""

    i = 0
    tags_to_omit = ['', 'memes', 'meme', 'funny','dump', 'memedump', 'dankmemes', 'reddit', 'description', 'twitter', 'lol', 'thumbnailhash']
    while True:
        if list_of_tags[i][0] not in tags_to_omit and list_of_tags[i][0] not in cluster_names:
            if list_of_tags[i][0] == 'randommemedump':
                list_of_tags[i] = list(list_of_tags[i])
                list_of_tags[i][0] = 'other'
                list_of_tags = tuple(list_of_tags)
            return list_of_tags[i][0]
        i += 1
        

def get_source_upvotes(memes_source, upvotes_column, source):
    """Get upvotes_centile and save upvotes to hdfs (for hour predictions)"""
    
    df = memes_source
    df.select(upvotes_column).write.format("com.databricks.spark.csv").mode("overwrite").save('hdfs:///upvotes/{0}'.format(source))
    n = df.count()
    w = Window.orderBy(upvotes_column)
    df = df.withColumn('upvotes_centile', functions.round(row_number().over(w) / n, 5))
    df = df.select('id', functions.col(upvotes_column).alias('upvotes'), 'upvotes_centile', 'timestamp')
    return df


def upload_blob(source_file_name, destination_blob_name, bucket_name = "images-and-logs"):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )
    

def upload_to_bucket(folderpath_hdfs, destination_blob_name = "tmp-data-for-website/daily/daily.json",
                     path_local = "/home/data_to_upload_on_bucket/tmp.json"):
    """Copies file from folder in hdfs to local host and then uploads it to bucket"""
    cmd = 'hdfs dfs -ls {0}'.format(folderpath_hdfs)

    files = subprocess.check_output(cmd, shell=True)
    files = files.strip()
    files = files.decode().split('\n')
    filename = files[-1].split(" ")[-1]
    
    cmd2 = "sudo hadoop fs -get -f {0} {1}".format(filename, path_local)
    
    subprocess.run(cmd2, shell = True)
    
    upload_blob(path_local, destination_blob_name) 