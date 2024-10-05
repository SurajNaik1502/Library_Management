import csv
import uuid
from django.core.management.base import BaseCommand
from apps.home.models import Book

class Command(BaseCommand):
    help = "Load books data from CSV file into the database"

    def handle(self, *args, **kwargs):
        # Load books data
        with open('media/books_updated.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames
            self.stdout.write(self.style.WARNING(f"CSV Headers: {headers}"))

            for row in reader:
                # Check if book_id is provided, else generate a UUID
                try:
                    book_id = uuid.UUID(row['book_id'])  # Validate if it's a correct UUID
                except ValueError:
                    book_id = uuid.uuid4()  # Generate new UUID if not valid

                book, created = Book.objects.get_or_create(
                    book_id=book_id,
                    defaults={
                        'title': row['title'],
                        'category': row['category'],
                        'description': row['description'],
                        'availability': row['availability'],
                        'num_reviews': row['num_reviews'],
                        'price': row['price'],
                        'price_excl_tax': row['price_excl_tax'],
                        'price_incl_tax': row['price_incl_tax'],
                        'product_type': row['product_type'],
                        'stars': row['stars'],
                        'tax': row['tax'],
                        'url': row['url']
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Book '{book.title}' created"))
                else:
                    self.stdout.write(self.style.WARNING(f"Book '{book.title}' already exists"))
