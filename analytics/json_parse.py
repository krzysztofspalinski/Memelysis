import pyspark
import subprocess
import os
import subprocess
from pyspark.sql import SQLContext
from pyspark import SparkContext
import pyspark
import ast
import pandas as pd 

def parse(df):
    """
    Parse json from all sources
    """

    memedroid_cols = ['id', 'extension', 'image_path', 'source', 'text', 'url', 'date', 'title', 'popularity', 'tags']
    twitter_cols = ['id', 'extension', 'source', 'text', 'url', 'created_at', 'title', 'hashtags', 'favorite_count', 'retweet_count']  
    reddit_cols = ['id', 'extension', 'source', 'title', 'url', 'date', 'title', 'upvotes' 'upvote_ratio'] 
    imgur_cols = ['id', 'extension', 'source', 'url', 'additional_data'] 

    json_cols = {"twitter": twitter_cols, "reddit": reddit_cols, "imgur": imgur_cols, "memedroid": memedroid_cols}

    df = sqlContext.read.option("multiline", True).option("mode", "PERMISSIVE").json(path)
    df = df.toPandas()
    d = ast.literal_eval(df.loc[0, 'additional_data'])

    json_source = df.loc[0, "source"]

    ans = []

    for col in json_cols[json_source]:
        try:
            ans.append(d[col])
        except KeyError:
            ans.append(df.loc[0, col])
        finally:
            ans.append(None)

    return pd.DataFrame(ans, columns=json_cols[json_source])

def main():
    print('Hello world')
    

    cmd = 'hdfs dfs -ls /jsons/'

    files = subprocess.check_output(cmd, shell=True)
    files = files.strip()
    files = files.decode().split('\n')

    out = []

    for path in files:
        f = path.split(" ")[-1]
        if '.json' in f and 'memes' not in f: out.append(f)

    for i in out:
        print(i)

    sc = SparkContext()
    sqlContext = SQLContext(sc)
    
    for json in out:
        print(parse(json))


if __name__ == "__main__":
    main()
