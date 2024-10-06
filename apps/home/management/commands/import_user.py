import csv
from django.core.management.base import BaseCommand
from apps.home.models import UserProfile, BookCheckout, Book, User
from django.utils import timezone

class Command(BaseCommand):
    help = "Load user and checkout data from CSV file into the database"

    def handle(self, *args, **kwargs):
        with open('media/users_data.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames
            self.stdout.write(self.style.WARNING(f"CSV Headers: {headers}"))

            # Create a mapping from book_id (e.g., 'B488') to actual UUIDs
            book_mapping = {book.book_id: book.id for book in Book.objects.all()}

            for row in reader:
                user, created = User.objects.get_or_create(
                    username=row['user_name'],
                    defaults={
                        'first_name': row['user_name'],
                        'email': f"{row['user_name']}@example.com",
                        'last_login': timezone.now(),
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"User '{user.username}' created"))
                else:
                    self.stdout.write(self.style.WARNING(f"User '{user.username}' already exists"))

                user_profile, profile_created = UserProfile.objects.get_or_create(
                    user=user,
                    custom_user_id=row['user_id'],
                    defaults={
                        'mobile_no': '',  
                        'address': ''  
                    }
                )

                if profile_created:
                    self.stdout.write(self.style.SUCCESS(f"UserProfile for '{user.username}' created"))
                else:
                    self.stdout.write(self.style.WARNING(f"UserProfile for '{user.username}' already exists"))

                checkouts = row['past_checkouts'].split(', ')
                return_patterns = row['return_patterns'].split(', ')

                for checkout, pattern in zip(checkouts, return_patterns):
                    checkout = checkout.strip()  # Clean up
                    status = pattern.split(':')[1].strip()  # Get return status and clean

                    # Get the UUID from the book mapping
                    book_id = book_mapping.get(checkout)
                    if book_id is None:
                        self.stdout.write(self.style.ERROR(f"Book with ID '{checkout}' not found in database."))
                        continue

                    # Proceed to create the BookCheckout entry
                    try:
                        book_checkout, created = BookCheckout.objects.get_or_create(
                            user=user_profile,
                            book_id=book_id,
                            defaults={'return_status': status}
                        )
                        if created:
                            self.stdout.write(self.style.SUCCESS(f"Checkout created for book ID '{checkout}' with status '{status}'"))
                        else:
                            self.stdout.write(self.style.WARNING(f"Checkout already exists for book ID '{checkout}'"))

                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))