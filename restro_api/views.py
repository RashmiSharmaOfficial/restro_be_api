from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User, Restaurant, Slot, Table
from .serializers import UserSerializer, RestaurantSerializer, SlotSerializer, TableSerializer
from collections import defaultdict
from django.db.models import F

# Create user (POST)
class AddUserView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def add_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Get all users (GET)
class GetUsersView(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


# Get user by ID (GET)
class GetUserView(APIView):
    def get(self, request, user_id):
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user)
        return Response(serializer.data)


# Update user (PUT)
class UpdateUserView(APIView):
    def put(self, request, user_id):
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete user (DELETE)
class DeleteUserView(APIView):
    def delete(self, request, user_id):
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        user.delete()
        return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class RestaurantListCreate(APIView):
    def get(self, request):
        restaurants = Restaurant.objects.all()
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RestaurantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RestaurantDetail(APIView):
    def get(self, request, pk):
        try:
            restaurant = Restaurant.objects.get(pk=pk)
        except Restaurant.DoesNotExist:
            return Response({"error": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = RestaurantSerializer(restaurant)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            restaurant = Restaurant.objects.get(pk=pk)
        except Restaurant.DoesNotExist:
            return Response({"error": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = RestaurantSerializer(restaurant, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            restaurant = Restaurant.objects.get(pk=pk)
        except Restaurant.DoesNotExist:
            return Response({"error": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)

        restaurant.delete()
        return Response({"message": "Restaurant deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class SlotListCreate(APIView):
    def get(self, request):
        slots = Slot.objects.all()
        serializer = SlotSerializer(slots, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SlotSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SlotDetail(APIView):
    def get(self, request, pk):
        try:
            slot = Slot.objects.get(pk=pk)
        except Slot.DoesNotExist:
            return Response({"error": "Slot not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = SlotSerializer(slot)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            slot = Slot.objects.get(pk=pk)
        except Slot.DoesNotExist:
            return Response({"error": "Slot not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = SlotSerializer(slot, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            slot = Slot.objects.get(pk=pk)
        except Slot.DoesNotExist:
            return Response({"error": "Slot not found"}, status=status.HTTP_404_NOT_FOUND)

        slot.delete()
        return Response({"message": "Slot deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# Create Table (POST)
@api_view(['POST'])
def add_table(request):
    if request.method == 'POST':
        serializer = TableSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Get all Tables (GET)
@api_view(['GET'])
def get_tables(request):
    if request.method == 'GET':
        tables = Table.objects.all()
        serializer = TableSerializer(tables, many=True)
        return Response(serializer.data)

# Get a specific Table by ID (GET)
@api_view(['GET'])
def get_table(request, pk):
    try:
        table = Table.objects.get(pk=pk)
    except Table.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TableSerializer(table)
        return Response(serializer.data)

# Update Table (PUT)
@api_view(['PUT'])
def update_table(request, pk):
    try:
        table = Table.objects.get(pk=pk)
    except Table.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = TableSerializer(table, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Delete Table (DELETE)
@api_view(['DELETE'])
def delete_table(request, pk):
    try:
        table = Table.objects.get(pk=pk)
    except Table.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        table.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# import pdb

# API to get available dates and slots for a restaurant
@api_view(['GET'])
def get_available_dates(request, restaurant_id):
    # Fetching all slots for a given restaurant
    slots = Slot.objects.filter(restaurant_id=restaurant_id).values('date', 'id', 'time', 'restaurant_id', 'created_at')
    
    # Grouping slots by date
    date_slots = defaultdict(list)
    for slot in slots:
        # Convert date to string using isoformat
        slot['date'] = slot['date'].isoformat()
        slot['created_at'] = slot['created_at'].isoformat()  # Optionally convert created_at if it's a datetime object
        
        date_slots[slot['date']].append({
            "id": slot['id'],
            "date": slot['date'],
            "time": slot['time'],
            "created_at": slot['created_at'],
            "restaurant": slot['restaurant_id']
        })
    
    return Response(date_slots)

@api_view(['POST'])
def find_available_tables(request):
    slot_id = request.data.get('slot_id')
    num_people = request.data.get('num_people')

    # Get the slot details
    try:
        slot = Slot.objects.get(id=slot_id)
    except Slot.DoesNotExist:
        return Response({"error": "Slot not found"}, status=status.HTTP_404_NOT_FOUND)

    restaurant_id = slot.restaurant.id

    # Fetch all available tables for the restaurant
    tables = Table.objects.filter(restaurant_id=restaurant_id)

    # Sort tables by capacity (smallest to largest)
    tables = sorted(tables, key=lambda table: table.capacity)

    # List to store selected tables
    available_tables = []

    remaining_people = num_people

    for table in tables:
        # Use smaller tables to fit the remaining people as closely as possible
        while table.quantity > 0 and remaining_people >= table.capacity:
            available_tables.append({'table_id': table.id, 'capacity': table.capacity})
            remaining_people -= table.capacity
            table.quantity -= 1

        # If we can use this table for the exact remaining people
        if table.quantity > 0 and 0 < remaining_people <= table.capacity:
            available_tables.append({'table_id': table.id, 'capacity': table.capacity})
            remaining_people = 0
            table.quantity -= 1
            break

    # If there are still people left to accommodate, return an error
    if remaining_people > 0:
        return Response({"error": "Not enough tables available for the required number of people"})

    return Response({
        "message": "Tables found",
        "tables": available_tables
    })

@api_view(['POST'])
def update_table_quantity(request):
    # Extract table_ids from the request
    table_ids = request.data.get('table_ids')

    # Decrease the quantity for each table
    for table_id in table_ids:
        table = Table.objects.get(id=table_id)
        if table.quantity > 0:
            table.quantity -= 1  # Decrease one table quantity
            table.save()
        else:
            return Response({"error": f"Table with id {table_id} is not available."}, status=400)
    
    return Response({"message": "Tables successfully booked!"})