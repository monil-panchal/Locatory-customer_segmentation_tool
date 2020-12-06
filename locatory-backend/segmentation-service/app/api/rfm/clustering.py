import os
import pickle

from sklearn import metrics
from sklearn.cluster import KMeans, MiniBatchKMeans

from app.configs import cfg


class Clustering:
    __instance__ = None

    def __init__(self):
        """ Constructor.
        """
        if Clustering.__instance__ is None:
            Clustering.__instance__ = self
        else:
            raise Exception("You cannot create another Clustering class")

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

    def assign_clusters_based_scores(self, df, model, column, clusters):
        # Assign clusters
        df[column+"_Score"] = clusters

        # Prepare cluster to score mapping
        cluster_map = {k: v[0] for k, v in enumerate(
            list(model.cluster_centers_))}
        sorted_cluster_map = dict(
            sorted(cluster_map.items(), key=lambda item: item[1]))
        cluster_score_map = {v: int(k)+1 for k,
                             v in enumerate(sorted_cluster_map.keys())}

        # Replace clusters with scores
        df[column+"_Score"] = df[column+"_Score"].map(cluster_score_map)

        return df

    def load_predict_kmeans_model(self, model_path, rfmd_df, col):
        model = pickle.load(open(model_path, 'rb'))
        clusters = model.predict(rfmd_df[[col]])
        rfmd_df = self.assign_clusters_based_scores(
            rfmd_df, model, col, clusters)

        return rfmd_df

    def fix_outliers(self, df, column):
        df_copy = df.copy()

        # Ref: https://app.pluralsight.com/guides/cleaning-up-data-from-outliers
        # Finding outliers
        quartile1 = df[column].quantile(0.25)
        quartile3 = df[column].quantile(0.75)
        inter_quartile_range = quartile3 - quartile1

        df_copy["Is_Outlier"] = (df_copy[column] < (quartile1 - 1.5 * inter_quartile_range)
                                 ) | (df_copy[column] > (quartile3 + 1.5 * inter_quartile_range))

        # Dropping outliers
        df_copy = df_copy.loc[(df_copy["Is_Outlier"] != True)]
        df_copy.drop("Is_Outlier", axis=1, inplace=True)

        return df_copy

    def k_means_clustering(self, df, n_clusters=5, score_metric='euclidean'):
        model = KMeans(n_clusters=n_clusters)
        clusters = model.fit_transform(df)
        score = metrics.silhouette_score(
            df, model.labels_, metric=score_metric)

        return dict(model=model, score=score, clusters=clusters)

    def mini_batch_k_means_clustering(self, df, n_clusters=5, score_metric='euclidean'):
        # Using k-means++ to initialize k-means clusters
        model = MiniBatchKMeans(n_clusters=n_clusters, init='k-means++',
                                batch_size=1000, max_iter=10).fit(df)

        return dict(model=model)

    def get_kmeans_clustered_df(self, rfmd_df, col, cluster_type, document_id, n_segments):
        # Covers cases for both saved data and rfm parameters based API calls
        if not document_id or not os.path.exists(self.get_models_path()+document_id+"_"+cluster_type+".sav"):
            # Remove outliers
            no_outlier_rfmd_df = self.fix_outliers(rfmd_df[[col]], col)

            model_data = self.mini_batch_k_means_clustering(
                no_outlier_rfmd_df, n_clusters=n_segments)

            # Predict clusters
            clusters = model_data.get("model").predict(rfmd_df[[col]])
            rfmd_df = self.assign_clusters_based_scores(
                rfmd_df, model_data.get("model"), col, clusters)

            # Append and Save the model only if document_id exists
            if document_id:
                model_path = self.get_models_path()+document_id+"_"+cluster_type+".sav"
                self.save_kmeans_model(model_data.get("model"), model_path)

        else:
            model_path = self.get_models_path()+document_id+"_"+cluster_type+".sav"
            rfmd_df = self.load_predict_kmeans_model(model_path, rfmd_df, col)

        return rfmd_df
