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
from .recommender import CollaborativeFilteringRecommender, load_data

@login_required
def recommend_books(request):
    user_id = request.user.id  # Assuming you have user_id mapping to Django's User model

    # Load data
    books_df, interactions_df, users_df = load_data()

    # Instantiate the recommender system
    recommender = CollaborativeFilteringRecommender(interactions_df)

    # Get recommendations for the logged-in user
    recommended_books = recommender.get_recommendations(user_id=user_id, top_n=5)

    # Pass the recommendations to the template
    context = {
        'recommended_books': recommended_books,
    }

    return render(request, 'myapp/recommend_books.html', context)
