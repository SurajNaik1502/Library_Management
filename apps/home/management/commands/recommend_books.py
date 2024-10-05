# apps/home/management/commands/recommend_books.py

from django.core.management.base import BaseCommand
from apps.home.models import Book, UserInteraction
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix

class Command(BaseCommand):
    help = "Recommend books based on user interactions using collaborative filtering"

    def handle(self, *args, **kwargs):
        # Step 1: Load interactions data from the Django models
        interactions = UserInteraction.objects.values('user_id', 'book_id', 'rating')

        # Step 2: Create a DataFrame
        interactions_df = pd.DataFrame(list(interactions))

        if interactions_df.empty:
            self.stdout.write(self.style.WARNING('No interactions found in the database.'))
            return

        # Step 3: Pivot table to create the user-item matrix
        user_item_matrix = interactions_df.pivot_table(index='user_id', columns='book_id', values='rating', fill_value=0)

        # Step 4: Build sparse matrix for memory efficiency
        user_item_sparse_matrix = csr_matrix(user_item_matrix.values)

        # Step 5: Compute cosine similarity between users
        similarity_matrix = cosine_similarity(user_item_sparse_matrix)

        # Step 6: Recommend books for each user
        user_id = 'U001'  # Replace with user input
        if user_id not in user_item_matrix.index:
            self.stdout.write(self.style.ERROR(f"User {user_id} not found in the dataset."))
            return

        user_idx = user_item_matrix.index.get_loc(user_id)
        similar_users = list(enumerate(similarity_matrix[user_idx]))
        similar_users = sorted(similar_users, key=lambda x: x[1], reverse=True)
        similar_users = [user_item_matrix.index[i] for i, score in similar_users[1:6]]  # Top 5 similar users

        recommended_books = set()
        for similar_user in similar_users:
            recommended_books.update(user_item_matrix.loc[similar_user].index[user_item_matrix.loc[similar_user] > 0])

        user_books = set(user_item_matrix.loc[user_id][user_item_matrix.loc[user_id] > 0].index)
        recommended_books -= user_books

        if recommended_books:
            recommended_books_list = Book.objects.filter(id__in=recommended_books)
            self.stdout.write(f"Recommended books for user {user_id}:")
            for book in recommended_books_list:
                self.stdout.write(f"- {book.title}")
        else:
            self.stdout.write(f"No new recommendations for user {user_id}.")
