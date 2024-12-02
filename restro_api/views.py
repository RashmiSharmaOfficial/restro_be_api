from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User, Restaurant, Slot, Table
from .serializers import UserSerializer, RestaurantSerializer, SlotSerializer, TableSerializer
from collections import defaultdict
from django.db.models import F
    
@api_view(['POST'])
def add_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET', 'PUT', 'DELETE'])
def user_detail(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        user.delete()
        return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# RESTAURANT APIs
@api_view(['GET', 'POST'])
def restaurants(request):
    if request.method == 'GET':
        restaurants = Restaurant.objects.all()
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = RestaurantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def restaurant_detail(request, restaurant_id):
    try:
        restaurant = Restaurant.objects.get(pk=restaurant_id)
    except Restaurant.DoesNotExist:
        return Response({"error": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = RestaurantSerializer(restaurant)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = RestaurantSerializer(restaurant, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        restaurant.delete()
        return Response({"message": "Restaurant deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# SLOT APIs
@api_view(['GET', 'POST'])
def slots(request):
    if request.method == 'GET':
        slots = Slot.objects.all()
        serializer = SlotSerializer(slots, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = SlotSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def slot_detail(request, slot_id):
    try:
        slot = Slot.objects.get(pk=slot_id)
    except Slot.DoesNotExist:
        return Response({"error": "Slot not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SlotSerializer(slot)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = SlotSerializer(slot, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        slot.delete()
        return Response({"message": "Slot deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# TABLE APIs
# Create Table (POST)
@api_view(['GET', 'POST'])
def tables(request):
    if request.method == 'GET':
        tables = Table.objects.all()
        serializer = TableSerializer(tables, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = TableSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Get a specific Table by ID (GET)
@api_view(['GET', 'PUT', 'DELETE'])
def table_detail(request, table_id):
    try:
        table = Table.objects.get(pk=table_id)
    except Table.DoesNotExist:
        return Response({"error": "Table not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TableSerializer(table)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = TableSerializer(table, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        table.delete()
        return Response({"message": "Table deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


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