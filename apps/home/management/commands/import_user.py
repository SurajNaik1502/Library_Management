import csv
from django.contrib.auth.models import User  # Import Django's built-in User model
from django.core.management.base import BaseCommand
from apps.home.models import UserProfile, BookCheckout, Book

class Command(BaseCommand):
    help = "Load user and checkout data from CSV file into the database"

    def handle(self, *args, **kwargs):
        with open('media/users_data.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames
            self.stdout.write(self.style.WARNING(f"CSV Headers: {headers}"))

            for row in reader:
                # Create or get User (Django's built-in User model)
                user, created = User.objects.get_or_create(
                    username=row['user_name'],  # or use email or other unique fields
                    defaults={
                        'first_name': row['user_name'],  # Optionally add first_name or other fields
                        'email': f"{row['user_name']}@example.com",  # Dummy email, change as necessary
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"User '{user.username}' created"))
                else:
                    self.stdout.write(self.style.WARNING(f"User '{user.username}' already exists"))

                # Now create or get the UserProfile
                user_profile, profile_created = UserProfile.objects.get_or_create(
                    user=user,  # Link the UserProfile to the newly created or existing User
                    custom_user_id=row['user_id'],  # Use the custom_user_id from CSV
                    defaults={
                        'mobile_no': '',  # Add relevant fields if any
                        'address': ''  # Add relevant fields if any
                    }
                )

                if profile_created:
                    self.stdout.write(self.style.SUCCESS(f"UserProfile for '{user.username}' created"))
                else:
                    self.stdout.write(self.style.WARNING(f"UserProfile for '{user.username}' already exists"))

                # Process past checkouts and return patterns
                checkouts = row['past_checkouts'].split(', ')
                return_patterns = row['return_patterns'].split(', ')

                for checkout, pattern in zip(checkouts, return_patterns):
                    book_id, status = pattern.split(':')
                    
                    # Ensure the book_id is valid (if it references a UUID, adjust accordingly)
                    if book_id.startswith('B'):  # Example check, modify as per your logic
                        # Proceed to create the BookCheckout with the book_id
                        BookCheckout.objects.get_or_create(
                            user=user_profile,
                            book_id=checkout,  # This should match your defined CharField
                            defaults={'return_status': status}
                        )
                        self.stdout.write(self.style.SUCCESS(f"Book '{checkout}' with return status '{status}' added for user '{user_profile.user.username}'"))
                    else:
                        self.stdout.write(self.style.ERROR(f"'{book_id}' is not a valid book ID."))