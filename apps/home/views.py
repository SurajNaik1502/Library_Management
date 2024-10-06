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

from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .models import Book

from .recommender import CollaborativeFilteringRecommender, load_data
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
import os
from django.conf import settings
import requests
from bs4 import BeautifulSoup

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

import difflib  # Import difflib for finding close matches
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt  # Import csrf_exempt
from .models import Book


@login_required
def recommend_books(request):
    user_id = request.user.id  # Assuming user_id is mapped to Django's User model

@csrf_exempt  # Disable CSRF protection for this view
def dialogflow_webhook(request):
    if request.method == 'POST':
        # Log the raw request body
        print("Raw request body:", request.body)

        # Parse the incoming request
        req = json.loads(request.body)
        print("Parsed request body:", req)

        # Extract parameters from Dialogflow request
        intent = req.get('queryResult', {}).get('intent', {}).get('displayName')
        parameters = req.get('queryResult', {}).get('parameters', {})
        print("Extracted Intent:", intent)
        print("Extracted Parameters:", parameters)

        # Ensure book_title is extracted properly
        book_title = parameters.get('book_title', None)  # Default to None if not found
        if not book_title:  # If no book title was provided
            response_text = "I couldn't understand the book title. Could you please repeat it?"
            return JsonResponse({"fulfillmentText": response_text})

        # Handle Provide Book Details Intent
        if intent == 'Provide Book Details Intent':
            print(f"Book title extracted: {book_title}")
            
            try:
                book = Book.objects.get(title__iexact=book_title)
                is_available = book.availability > 0
                print(f"Book availability: {is_available} (availability: {book.availability})")
                
                if is_available:
                    response_text = f"The book '{book_title}' is available for borrowing."
                else:
                    response_text = f"Sorry, the book '{book_title}' is currently not available."
            except Book.DoesNotExist:
                # Find similar books
                similar_books = Book.objects.values_list('title', flat=True)
                matching_books = difflib.get_close_matches(book_title, similar_books, n=3, cutoff=0.6)  # Adjust cutoff as needed
                suggestions = ', '.join(matching_books) if matching_books else "No suggestions available."
                response_text = f"Sorry, we don't have the book '{book_title}' in our library. Did you mean: {suggestions}?"

        # Handle Borrow Book Intent
        elif intent == 'Borrow Book Intent':
            print(f"Book title extracted: {book_title}")

            try:
                book = Book.objects.get(title__iexact=book_title)
                if book.availability > 0:
                    book.availability -= 1  # Decrease availability
                    book.save()  # Save the updated availability
                    response_text = f"You've successfully borrowed '{book_title}'."
                else:
                    # Find similar books
                    similar_books = Book.objects.values_list('title', flat=True)
                    matching_books = difflib.get_close_matches(book_title, similar_books, n=3, cutoff=0.6)
                    suggestions = ', '.join(matching_books) if matching_books else "No suggestions available."
                    response_text = f"Sorry, '{book_title}' is currently out of stock. Did you mean: {suggestions}?"
            except Book.DoesNotExist:
                # Find similar books
                similar_books = Book.objects.values_list('title', flat=True)
                matching_books = difflib.get_close_matches(book_title, similar_books, n=3, cutoff=0.6)
                suggestions = ', '.join(matching_books) if matching_books else "No suggestions available."
                response_text = f"Sorry, we don't have the book '{book_title}' in our library. Did you mean: {suggestions}?"

        # Handle Check Availability Intent
        elif intent == 'Check Availability Intent':
            print(f"Book title extracted: {book_title}")

            try:
                book = Book.objects.get(title__iexact=book_title)
                if book.availability > 0:
                    response_text = f"The book '{book_title}' is available for borrowing."
                else:
                    # Find similar books
                    similar_books = Book.objects.values_list('title', flat=True)
                    matching_books = difflib.get_close_matches(book_title, similar_books, n=3, cutoff=0.6)
                    suggestions = ', '.join(matching_books) if matching_books else "No suggestions available."
                    response_text = f"Sorry, '{book_title}' is currently out of stock. Did you mean: {suggestions}?"
            except Book.DoesNotExist:
                # Find similar books
                similar_books = Book.objects.values_list('title', flat=True)
                matching_books = difflib.get_close_matches(book_title, similar_books, n=3, cutoff=0.6)
                suggestions = ', '.join(matching_books) if matching_books else "No suggestions available."
                response_text = f"Sorry, we don't have the book '{book_title}' in our library. Did you mean: {suggestions}?"

        # Handle Default Welcome Intent
        elif intent == 'Default Welcome Intent':
            response_text = "Welcome to our library! How can I assist you today?"

        # Default fallback response for unhandled intents
        else:
            print(f"Unhandled Intent: {intent}")
            response_text = "I'm not sure how to handle that request."

        print("Response text:", response_text)

        # Return the response to Dialogflow
        return JsonResponse({
            "fulfillmentText": response_text
        })
    else:
        print("Invalid request method:", request.method)
        return JsonResponse({"error": "Invalid request method. Only POST allowed."}, status=405)


from django.shortcuts import render

# View to render the chatbot page
def chat_bot(request):
    return render(request, 'home/chatbot.html')

def scanner(request):
    return render(request, 'ISBN-Barcode-Scanner/index.html')

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

