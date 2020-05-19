import re
import operator
import numpy as np 


from pyspark.ml.feature import Tokenizer, StopWordsRemover, HashingTF, IDF, Word2Vec, PCA
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator
from pyspark.sql.types import StringType, DoubleType
from pyspark.sql.functions import translate
from pyspark.sql import functions
from pyspark.ml.feature import StandardScaler


def text_clustering(dataFrame, k_value, w2v = False, w2v_value = None, seed = 2137, normalize = True, plot = True):
    """
    args:
        -dataFrame: spark Data Frame
        -k_value: number of clusters in k-means algorithm
        -w2v: if True word2Vec is used and w2v_value must be specified, otherwise tf-idf is used
        -w2v_value: number of parameters to be returned with Word2Vec
        -seed: seed
        -normalize: should normalization after Word2Vec be performed?
        -plot: if True, clusters are visualized with the use of PCA
        
    """
    
    #Data preprocessing
    tokenizer = Tokenizer(inputCol="text", outputCol="words_raw")
    dataFrame = tokenizer.transform(dataFrame)
    remover = StopWordsRemover(inputCol="words_raw", outputCol="words")
    dataFrame = remover.transform(dataFrame)
        

    if w2v and w2v_value is None:
        raise ValueError('You have to give w2v_values parameter')
        
    if not w2v: #tf-idf
        hashingTF = HashingTF(inputCol="words_raw", outputCol="rawFeatures", numFeatures=20)
        featurizedData = hashingTF.transform(dataFrame)
        idf = IDF(inputCol="rawFeatures", outputCol="features")
        idfModel = idf.fit(featurizedData)
        memes_df = idfModel.transform(featurizedData)

    else: #word2vec                
        word2Vec = Word2Vec(vectorSize=w2v_value, seed=seed, inputCol="words", outputCol="features_unnormalized")
        model_w2v = word2Vec.fit(dataFrame)       
        memes_df = model_w2v.transform(dataFrame)
        model_w2v.write().overwrite().save("hdfs:///models/model_w2v")
        
        
        if normalize:
            scaler = StandardScaler(inputCol="features_unnormalized", outputCol="features",
                            withStd=True, withMean=True)
            scalerModel = scaler.fit(memes_df)
            memes_df = scalerModel.transform(memes_df)


    #kmeans
    kmeans = KMeans(k = k_value, seed = seed)
    model_kmeans = kmeans.fit(memes_df)
    memes_df = model_kmeans.transform(memes_df)
    model_kmeans.write().overwrite().save("hdfs:///models/model_kmeans")

    
    #clustering evaluation
    evaluator = ClusteringEvaluator()
    silhouette = evaluator.evaluate(memes_df)

    centers = model_kmeans.clusterCenters()

    if plot:
        
        import matplotlib.pyplot as plt #virtual environment might have problems if imported "the classical" way
        
        #pca
        pca = PCA(k=2, inputCol="features", outputCol="pcaFeatures")
        model_pca = pca.fit(memes_df)
        memes_df = model_pca.transform(memes_df)
        #memes_df.show()

        centers_pca = [None]*len(centers)
        for i in range(len(centers)):
            centers_pca[i] = np.multiply(model_pca.pc.toArray().T, centers[i]).sum(axis = 1)
        centers_pca = np.array(centers_pca)



        #plot section
        split_col = functions.split(memes_df["pcaFeatures"].cast(StringType()), ',')
        memes_df = memes_df.withColumn('x', translate(split_col.getItem(0), "[", "").cast(DoubleType()))
        memes_df = memes_df.withColumn('y', translate(split_col.getItem(1), "]", "").cast(DoubleType()))
        #memes_df.show(truncate = False)

        df = memes_df.toPandas()
        groups = df.groupby('prediction')
        fig, ax = plt.subplots()
        ax.margins(0.05)
        for name, group in groups:
            ax.plot(group.x, group.y, marker='o', linestyle='', ms=5, label=name)
            ax.text(centers_pca[name,0], centers_pca[name,1], s = name, fontsize = 10)
        ax.legend()
        ax.title.set_text("k={0}, wn={1}, Silhouette={2}".format(k_value,w2v_value,silhouette))
        plt.show()
        print("PCA, explained variance= {0}".format(model_pca.explainedVariance))
            
    return memes_df


def tags(df, num_of_clusters):
    """
    Extracts and filters tags 
    args:
        -df- PySpark DataFrame after text_clustering (with prediction column) from which tags are extracted
        -num_of_clusters - number of classes in the prediction column
    returns:
        -a dictionary with all tags from each cluster
    """
    dict_clusters = {}
    for cluster in range(num_of_clusters): 
        dict_tags = {}
        for i in df.filter('prediction == {0}'.format(cluster)).select('tags_separated').collect():
            for j in i.tags_separated:          
                if 'indices' in j:
                    continue
                j = j.split(":")[-1]
                j = re.sub('[^A-Za-z0-9]+', '', j.lower())
                try:
                    int(j)
                    continue
                except:
                    if j == 'memes' or j == 'meme' or j == 'reddit' or j == '' or 'dong' in j:
                        continue

                    if j in dict_tags.keys():
                        dict_tags[j] += 1
                    else:
                        dict_tags[j] = 1
            
        dict_clusters[str(cluster)] = sorted(dict_tags.items(), key=operator.itemgetter(1), reverse = True)
            
    return dict_clusters


def train_model(memes_df, memes_tags, k = 7, wn = 50, plot = False):
    """
    Trains model with Word2Vec and KMeans
    args:
        -memes_df - PySpark DataFrame
        -memes_tags - PySpark DataFrame for tags extraction
        -k - number of clusters in KMeans
        -wn - number of parameters to be returned with Word2Vec
        -plot: if True, clusters are visualized with the use of PCA
    returns:
        -PySpark DataFrame with predictions
        -a dictionary with clusters names
        
    
    """
    df = text_clustering(memes_df, k, True, wn, plot = plot)
    memes_tags = df.join(memes_tags, on=['id'], how='left_outer')
    split_col = functions.split(memes_tags.tags, ',')
    dataFrame = memes_tags.withColumn("tags_separated", split_col)
    df2 = dataFrame.filter('tags_separated is not null').select('tags_separated', 'prediction')
    clust_names = tags(df2, k)
    for key in clust_names.keys():
        try:
            clust_names[key] = clust_names[key][0][0]
        except:
            clust_names[key] = ''
   
    return df, clust_names