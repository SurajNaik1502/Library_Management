import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
import os
from django.conf import settings

class CollaborativeFilteringRecommender:
    def __init__(self, interactions_df):
        self.interactions_df = interactions_df
        self.user_item_matrix = None
        self.similarity_matrix = None

    def build_user_item_matrix(self):
        """
        Create a sparse user-item matrix with users as rows and books as columns.
        """
        self.user_item_matrix = self.interactions_df.pivot_table(
            index='user_id',
            columns='book_id',
            values='rating',
            fill_value=0
        )
        return csr_matrix(self.user_item_matrix.values)

    def calculate_similarity(self):
        """
        Calculate cosine similarity between users.
        """
        if self.user_item_matrix is None:
            self.build_user_item_matrix()
        self.similarity_matrix = cosine_similarity(self.user_item_matrix)
        return self.similarity_matrix

    def get_recommendations(self, user_id, top_n=5):
        """
        Recommend books based on user similarity.
        """
        if self.similarity_matrix is None:
            self.calculate_similarity()

        # Check if user_id is valid
        if user_id not in self.user_item_matrix.index:
            return f"User {user_id} not found in the dataset."

        user_idx = self.user_item_matrix.index.get_loc(user_id)
        similar_users = list(enumerate(self.similarity_matrix[user_idx]))
        similar_users = sorted(similar_users, key=lambda x: x[1], reverse=True)
        similar_users = [self.user_item_matrix.index[i] for i, score in similar_users[1:top_n+1]]

        # Recommend books borrowed by similar users
        recommended_books = set()
        for similar_user in similar_users:
            recommended_books.update(self.user_item_matrix.loc[similar_user].index[
                self.user_item_matrix.loc[similar_user] > 0
            ])

        # Filter out books the user has already borrowed/rated
        user_books = set(self.user_item_matrix.loc[user_id][self.user_item_matrix.loc[user_id] > 0].index)
        recommended_books = recommended_books - user_books

        return list(recommended_books) if recommended_books else f"No new recommendations for User {user_id}."

# Utility function to load datasets in Django
def load_data():
    # Define paths to your CSV files using Django's settings
    books_file_path = os.path.join(settings.MEDIA_ROOT, 'books_updated.csv')
    interactions_file_path = os.path.join(settings.MEDIA_ROOT, 'interactions.csv')
    users_file_path = os.path.join(settings.MEDIA_ROOT, 'users.csv')

    # Load CSV files into dataframes
    books_df = pd.read_csv(books_file_path)
    interactions_df = pd.read_csv(interactions_file_path)
    users_df = pd.read_csv(users_file_path)

    return books_df, interactions_df, users_df
