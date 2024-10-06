# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin

# Register your models here.
from .models import Book, UserProfile, BookCheckout, Interaction, BookTest

admin.site.register(Book)
admin.site.register(UserProfile)
admin.site.register(BookCheckout)
admin.site.register(Interaction)
admin.site.register(BookTest)