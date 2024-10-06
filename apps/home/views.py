# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
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

import difflib  # Import difflib for finding close matches
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt  # Import csrf_exempt
from .models import Book

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
