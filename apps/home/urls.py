# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('recommend/', views.recommend_books, name='recommend_books'),
    # Matches any html file
    

    path('book-search/', views.book_search, name='book_search'),
    path('find-location/', views.find_book_location, name='book_location'),
]
