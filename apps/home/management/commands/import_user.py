import csv
from django.core.management.base import BaseCommand
from apps.home.models import User, BookCheckout

class Command(BaseCommand):
    help = "Load user and checkout data from CSV file into the database"

    def handle(self, *args, **kwargs):
        with open('media/users_data.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames
            self.stdout.write(self.style.WARNING(f"CSV Headers: {headers}"))

            for row in reader:
                # Create or get User
                user, created = User.objects.get_or_create(
                    user_id=row['user_id'],
                    defaults={
                        'user_name': row['user_name'],
                        'age': row['age'],
                        'past_checkouts': row['past_checkouts'],
                        'return_patterns': row['return_patterns']
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"User '{user.user_name}' created"))
                else:
                    self.stdout.write(self.style.WARNING(f"User '{user.user_name}' already exists"))

                # Process past checkouts and return patterns
                checkouts = row['past_checkouts'].split(', ')
                return_patterns = row['return_patterns'].split(', ')

                for checkout, pattern in zip(checkouts, return_patterns):
                    book_id, status = pattern.split(':')
                    BookCheckout.objects.get_or_create(
                        user=user,
                        book_id=checkout,
                        defaults={'return_status': status}
                    )
                    self.stdout.write(self.style.SUCCESS(f"Book '{checkout}' with return status '{status}' added for user '{user.user_name}'"))

