# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from apps.home.models import BookTest
from django.conf import settings
import os
from .forms import BookLocationForm

# Consolidate the imports
from .recommender import CollaborativeFilteringRecommender, load_data


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    try:
        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .recommender import CollaborativeFilteringRecommender, load_data
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
import os
from django.conf import settings
import requests
from bs4 import BeautifulSoup

<<<<<<< Updated upstream
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .recommender import CollaborativeFilteringRecommender, load_data
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
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
        self.user_item_matrix = self.interactions_df.pivot_table(
            index='user_id',
            columns='book_id',
            values='rating',
            fill_value=0
        )
        return csr_matrix(self.user_item_matrix.values)

    def calculate_similarity(self):
        if self.user_item_matrix is None:
            self.build_user_item_matrix()
        self.similarity_matrix = cosine_similarity(self.user_item_matrix)
        return self.similarity_matrix

    def get_recommendations(self, user_id, top_n=5):
        if self.similarity_matrix is None:
            self.calculate_similarity()
        if user_id not in self.user_item_matrix.index:
            return f"User {user_id} not found in the dataset."
        user_idx = self.user_item_matrix.index.get_loc(user_id)
        similar_users = list(enumerate(self.similarity_matrix[user_idx]))
        similar_users = sorted(similar_users, key=lambda x: x[1], reverse=True)
        similar_users = [self.user_item_matrix.index[i] for i, score in similar_users[1:top_n + 1]]
        recommended_books = set()
        for similar_user in similar_users:
            recommended_books.update(self.user_item_matrix.loc[similar_user].index[
                self.user_item_matrix.loc[similar_user] > 0
            ])
        user_books = set(self.user_item_matrix.loc[user_id][self.user_item_matrix.loc[user_id] > 0].index)
        recommended_books = recommended_books - user_books
        return list(recommended_books) if recommended_books else f"No new recommendations for User {user_id}."

def load_data():
    books_file_path = os.path.join(settings.MEDIA_ROOT, 'books_updated.csv')
    interactions_file_path = os.path.join(settings.MEDIA_ROOT, 'interactions.csv')
    books_df = pd.read_csv(books_file_path)
    interactions_df = pd.read_csv(interactions_file_path)
    return books_df, interactions_df

@login_required
def recommend_books(request):
    user_id = 'U001'
=======
@login_required
def recommend_books(request):
    user_id = request.user.id  # Assuming user_id is mapped to Django's User model
>>>>>>> Stashed changes

    # Load data
    books_df, interactions_df = load_data()

    # Instantiate the recommender system
    recommender = CollaborativeFilteringRecommender(interactions_df)

    # Get recommendations for the logged-in user
    recommended_books = recommender.get_recommendations(user_id=user_id, top_n=5)

    # Fetch book details for recommended book IDs
    if isinstance(recommended_books, list):
        recommended_book_details = books_df[books_df['book_id'].isin(recommended_books)]
        recommended_book_details = recommended_book_details.to_dict(orient='records')  # Convert to list of dictionaries
        
        # Add image URL to each book record
        for book in recommended_book_details:
            book['image_url'] = fetch_image_url(book['url'])
    else:
        recommended_book_details = []

    # Pass the recommendations to the template
    context = {
        'recommended_books': recommended_book_details,
    }

<<<<<<< Updated upstream
    return render(request, 'home/recommend_books.html', context)

def fetch_image_url(book_url):
    """
    Fetch the book cover image URL from the book's page.
    """
    try:
        response = requests.get(book_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        image_element = soup.find('img', class_='thumbnail')
        if image_element:
            image_url = 'http://books.toscrape.com/' + image_element['src']
            return image_url
    except Exception as e:
        print(f"Error fetching image URL: {e}")
    return None
=======
    return render(request, 'myapp/recommend_books.html', context)


def book_search(request):
    if request.is_ajax():
        query = request.GET.get('q', '')
        books = BookTest.objects.filter(title__icontains=query)[:10]  # Limit to 10 suggestions
        results = [{'title': book.title} for book in books]
        return JsonResponse(results, safe=False)

# View to find book location based on user input
def find_book_location(request):
    if request.method == 'POST':
        nearest_shelf = request.POST.get('shelf_number')
        book_name = request.POST.get('book_name')

        try:
            # Fetch book based on user input
            book = BookTest.objects.get(title=book_name)
            book_location = book.location  # Assuming location is stored in this field
            context = {
                'nearest_shelf': nearest_shelf,
                'book_location': book_location,
                'book': book,
            }
            return render(request, 'home/book_location_result.html', context)
        except BookTest.DoesNotExist:
            # Handle case where book is not found
            return render(request, 'home/book_location_result.html', {'error': 'Book not found'})

    # Render the form initially
    return render(request, 'home/book_location_form.html')
>>>>>>> Stashed changes
