from rest_framework import serializers
from .models import User, Restaurant, Slot, Table, Booking
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['user_id', 'email', 'password', 'role', 'created_at']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)  # This will hash the password
        user.set_password(password)  # In case additional hashing is needed
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)  # Hash the new password
        instance.save()
        return instance

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'

class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = '__all__'
        
class SlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slot
        fields = ['id', 'restaurant', 'date', 'time', 'tables', 'created_at']
        read_only_fields = ['tables', 'created_at']  # Prevent direct modification of `tables`

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'customer_email', 'restaurant', 'slot', 'tables', 'num_of_people', 'created_at']