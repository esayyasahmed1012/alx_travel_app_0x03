from rest_framework import serializers
from .models import Listing, Booking
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ListingSerializer(serializers.ModelSerializer):
    host = UserSerializer(read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = ['listing_id', 'host', 'title', 'description', 'location', 'price_per_night', 'max_guests', 'average_rating', 'created_at', 'updated_at']
        read_only_fields = ['listing_id', 'created_at', 'updated_at']

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / reviews.count()
        return None

    def validate_price_per_night(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price per night must be positive.")
        return value

    def validate_max_guests(self, value):
        if value <= 0:
            raise serializers.ValidationError("Maximum guests must be positive.")
        return value

class BookingSerializer(serializers.ModelSerializer):
    listing = ListingSerializer(read_only=True)
    guest = UserSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = ['booking_id', 'listing', 'guest', 'start_date', 'end_date', 'total_price', 'created_at']
        read_only_fields = ['booking_id', 'total_price', 'created_at']

    def validate(self, data):
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError("End date must be after start date.")
        return data