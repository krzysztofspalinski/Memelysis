import pyspark
import subprocess
import os
import subprocess
from pyspark.sql import SQLContext
from pyspark import SparkContext
import pyspark
import ast
import pandas as pd 
import json

def parse(path, sqlContext, json_cols):
    """
    Parse json from all sources
    """

    df = sqlContext.read.option("multiline", True).option("mode", "PERMISSIVE").json(path)
    df = df.toPandas()

    d = json.loads(df.loc[0, 'additional_data'])

    json_source = df.loc[0, "source"]

    ans = []

    for col in json_cols[json_source]:
        try:
            ans.append(d[col])
        except KeyError:
            ans.append(df.loc[0, col])

    return ans

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


    memedroid_cols = ['source', 'id', 'extension', 'image_path', 'text', 'url', 'date', 'title', 'popularity', 'tags']
    twitter_cols = ['source', 'id', 'extension', 'text', 'url', 'created_at', 'hashtags', 'favorite_count', 'retweet_count']  
    reddit_cols = ['source', 'id', 'extension', 'title', 'url', 'date', 'title', 'upvotes', 'upvote_ratio'] 
    imgur_cols = ['source', 'id', 'extension', 'url', 'additional_data'] 

    json_cols = {"twitter": twitter_cols, "reddit": reddit_cols, "imgur": imgur_cols, "memedroid": memedroid_cols}


    sc = SparkContext()
    sqlContext = SQLContext(sc)
    
    parsed_jsons = []

    for json in out:
        parsed_jsons.append(parse(json, sqlContext, json_cols))

    json_cols = {"twitter": [], "reddit": [], "imgur": [], "memedroid": []}

    for row in parsed_jsons:
        json_cols[row[0]].append(row)

    for source_name, data in json_cols.items():
        #df = pd.DataFrame(data, columns=json_cols[source_name])
        #print(df.head())

if __name__ == "__main__":
    main()
