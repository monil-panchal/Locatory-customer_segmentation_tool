import os
import pickle

from sklearn import metrics
from sklearn.cluster import KMeans, MiniBatchKMeans

from .configs import cfg


class Clustering:
    __instance__ = None

    def __init__(self):
        """ Constructor.
        """
        if Clustering.__instance__ is None:
            Clustering.__instance__ = self
        else:
            raise Exception("You cannot create another Clustering Log class")

    @staticmethod
    def get_instance():
        """ Static method to fetch the current instance.
        """
        if not Clustering.__instance__:
            Clustering()
        return Clustering.__instance__

    def get_models_path(self):
        return cfg.MODELS_PATH

    def create_path_if_not_exists(self, dir_path):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    def save_kmeans_model(self, model, model_path):
        # Create directory if not exists
        model_dir_path = self.get_models_path()
        self.create_path_if_not_exists(model_dir_path)

        # Saving model to directory
        pickle.dump(model, open(model_path, 'wb'))

    def load_predict_kmeans_model(self, model_path, rfmd_df, col):
        model = pickle.load(open(model_path, 'rb'))
        clusters = model.predict(rfmd_df[col])
        rfmd_df[col+"_Score"] = clusters

        return rfmd_df

    def k_means_clustering(self, df, n_clusters=5, score_metric='euclidean'):
        model = KMeans(n_clusters=n_clusters)
        clusters = model.fit_transform(df)
        score = metrics.silhouette_score(X, model.labels_, metric=score_metric)

        return dict(model=model, score=score, clusters=clusters)

    def mini_batch_k_means_clustering(self, df, col, n_clusters=5, score_metric='euclidean'):
        # Using k-means++ to initialize k-means clusters
        model = MiniBatchKMeans(n_clusters=n_clusters, init='k-means++',
                                batch_size=1000, max_iter=10).fit(df[col])

        score = metrics.silhouette_score(X, model.labels_, metric=score_metric)

        return dict(model=model, score=score)

    def get_kmeans_clusters(self, rfmd_df, col, cluster_type):
        # Covers cases for both saved data and rfm parameters based API calls
        if not self.document_id or not os.path.exists(self.get_models_path()+self.document_id+"_"+cluster_type+".sav"):
            # Remove outliers
            no_outlier_rfmd_df = self.fix_outliers(rfmd_df[[col]], col)

            model_data = self.mini_batch_k_means_clustering(
                no_outlier_rfmd_df, col, n_clusters=self.rfm_parameters.get("n_segments"))

            # Predict clusters
            clusters = model_data.get("model").predict(rfmd_df[col])
            rfmd_df[col+"_Score"] = clusters

            # Append and Save the model only if document_id exists
            if self.document_id:
                model_path = self.get_models_path()+self.document_id+"_"+cluster_type+".sav"
                self.save_kmeans_model(model_data.get("model"), model_path)

        else:
            model_path = self.get_models_path()+self.document_id+"_"+cluster_type+".sav"
            rfmd_df = self.load_predict_kmeans_model(model_path, rfmd_df, col)

        return rfmd_df
