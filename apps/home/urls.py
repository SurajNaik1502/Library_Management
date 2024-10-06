# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    # path('recommend-books/', views.recommend_books, name='recommend_books'),
    path('dialogflow-webhook/', views.dialogflow_webhook, name='dialogflow_webhook'),
    path('chatbot/', views.chat_bot, name='chat_bot'),
    path('scanner/',views.scanner,  name='scanner'),

    # Matches any html file
    

    path('book-search/', views.book_search, name='book_search'),
    path('find-location/', views.find_book_location, name='book_location'),
]
