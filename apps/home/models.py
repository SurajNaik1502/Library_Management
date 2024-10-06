from django.db import models
from django.contrib.auth.models import User
import uuid

# Book Model
class Book(models.Model):
    book_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
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

    combined_features = models.TextField(blank=True, null=True)
    

    def __str__(self):
        return self.title

# UserProfile extending Django's User model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    custom_user_id = models.CharField(max_length=100, unique=True)
    mobile_no = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username

import uuid
from django.core.exceptions import ValidationError
from django.db import models

class BookCheckout(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="checkouts")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, blank=True, null=True)
    return_status = models.CharField(max_length=20, default="Not Returned",)

    class Meta:
        unique_together = ('user', 'book')

    def clean(self):
        # Ensure that the book exists in the Book table
        if self.book is not None and not Book.objects.filter(book_id=self.book.book_id).exists():
            raise ValidationError(f"Book with id {self.book.book_id} does not exist.")

    def __str__(self):
        return f"User '{self.user.user.username}' - Book '{self.book.title}' ({self.return_status})"


# Interaction Model
class Interaction(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)  # ForeignKey to UserProfile
    book = models.ForeignKey(Book, on_delete=models.CASCADE)  # ForeignKey to Book
    rating = models.FloatField()  # Rating given by the user
    timestamp = models.DateTimeField(auto_now_add=True)  # Timestamp of the interaction

    def __str__(self):
        return f"{self.user.user.username} rated {self.book.title} with {self.rating}"
