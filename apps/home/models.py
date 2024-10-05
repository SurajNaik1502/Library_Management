# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

from django.db import models
import uuid

class Book(models.Model):
    book_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # Use UUIDField
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    availability = models.IntegerField(default=0)
    num_reviews = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_excl_tax = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price_incl_tax = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    product_type = models.CharField(max_length=100, blank=True, null=True)
    stars = models.IntegerField(default=0)
    tax = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    url = models.URLField(max_length=255)

    def __str__(self):
        return self.title


from django.db import models
import uuid

class User(models.Model):
    user_id = models.CharField(max_length=10, unique=True)  # Unique user ID
    user_name = models.CharField(max_length=100)  # Name of the user
    age = models.IntegerField()  # Age of the user
    past_checkouts = models.TextField()  # Comma-separated list of book IDs checked out
    return_patterns = models.TextField()  # Comma-separated list of return statuses (book:status)

    def __str__(self):
        return f"{self.user_name} (ID: {self.user_id})"

class BookCheckout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="checkouts")
    book_id = models.CharField(max_length=10)  # Book ID (refers to the books checked out)
    return_status = models.CharField(max_length=20)  # Return status (e.g., 'On-Time', 'Late', 'Very Late')

    def __str__(self):
        return f"User {self.user.user_name} - Book {self.book_id} ({self.return_status})"




from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    custom_user_id = models.CharField(max_length=100, unique=True)  # Renamed to avoid clash
    mobile_no = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.user.username


class Interaction(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)  # ForeignKey to UserProfile
    book = models.ForeignKey(Book, on_delete=models.CASCADE)  # ForeignKey to Book
    rating = models.FloatField()  # Rating given by the user
    timestamp = models.DateTimeField(auto_now_add=True)  # Timestamp of the interaction

    def __str__(self):
        return f"{self.user} rated {self.book.title} with {self.rating}"
