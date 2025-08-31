from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from listings.models import Listing
import random
import uuid
from decimal import Decimal

class Command(BaseCommand):
    help = 'Seeds the database with sample listings'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))

        # Create or get users
        users = []
        for i in range(5):
            username = f'user{i}'
            email = f'user{i}@example.com'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': email, 'password': 'password123'}
            )
            if created:
                user.set_password('password123')
                user.save()
            users.append(user)

        # Sample listing data
        locations = ['Paris, France', 'New York, USA', 'Tokyo, Japan', 'Cape Town, South Africa']
        titles = ['Cozy Apartment', 'Luxury Villa', 'Modern Loft', 'Beach House']
        descriptions = [
            'A charming apartment in the city center.',
            'A luxurious villa with stunning views.',
            'A modern loft with all amenities.',
            'A beachfront house perfect for relaxation.'
        ]

        # Create listings
        for i in range(10):
            Listing.objects.create(
                listing_id=uuid.uuid4(),
                host=random.choice(users),
                title=f"{random.choice(titles)} {i+1}",
                description=random.choice(descriptions),
                location=random.choice(locations),
                price_per_night=Decimal(random.uniform(50, 500)).quantize(Decimal('0.01')),
                max_guests=random.randint(1, 8)
            )

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {Listing.objects.count()} listings.'))