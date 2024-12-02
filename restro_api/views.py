from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User, Restaurant, Slot, Table, Booking
from .serializers import UserSerializer, RestaurantSerializer, SlotSerializer, TableSerializer, BookingSerializer
from collections import defaultdict
from django.db.models import F
from datetime import datetime
from django.contrib.auth import authenticate
    
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

@api_view(['POST'])
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    # Authenticate the user
    user = authenticate(username=email, password=password)

    if user is not None:
        return Response({"message": "Login successful."}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)
    
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
        # Retrieve the restaurant by its ID
        restaurant = Restaurant.objects.get(pk=restaurant_id)
    except Restaurant.DoesNotExist:
        return Response({"error": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # Serialize and return the restaurant details
        serializer = RestaurantSerializer(restaurant)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        # Update the restaurant details
        serializer = RestaurantSerializer(restaurant, data=request.data, partial=True)  # Allow partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Delete the restaurant
        restaurant.delete()
        return Response({"message": "Restaurant deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# SLOT APIs
#list and create slots
@api_view(['GET', 'POST'])
def slots(request, restaurant_id):
    if request.method == 'GET':
        # Filter slots by restaurant ID
        slots = Slot.objects.filter(restaurant_id=restaurant_id)
        
        # If no slots are found, return a 404 response
        if not slots:
            return Response({"message": "No slots found for this restaurant"}, status=404)

        # Serialize and return the slots for the specified restaurant
        serializer = SlotSerializer(slots, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Create a new slot
        data = request.data
        restaurant_id = data.get("restaurant")
        date = data.get("date")
        time = data.get("time")

        # Fetch the restaurant
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except Restaurant.DoesNotExist:
            return Response({"error": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)

        # Fetch tables for the restaurant
        tables = Table.objects.filter(restaurant=restaurant).values("id", "capacity", "quantity")
        if not tables:
            return Response({"error": "No tables found for this restaurant"}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare the tables data with initial remaining_quantity
        tables_data = [
            {"table_id": table["id"], "capacity": table["capacity"], "remaining_quantity": table["quantity"]}
            for table in tables
        ]

        # Add tables data to the slot
        data["tables"] = tables_data

        # Serialize and save
        serializer = SlotSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def auto_create_slots(request, restaurant_id):
    """
    Automatically creates slots for a restaurant based on its time slots and tables for a given date.
    """
    try:
        restaurant = Restaurant.objects.get(pk=restaurant_id)
    except Restaurant.DoesNotExist:
        return Response({"error": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)

    # Validate date input
    date = request.data.get("date")
    if not date:
        return Response({"error": "Date is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        datetime.strptime(date, "%Y-%m-%d")  # Validate date format
    except ValueError:
        return Response({"error": "Invalid date format."}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch the predefined time slots from the restaurant
    time_slots = restaurant.time_slots
    if not time_slots:
        return Response({"error": "Restaurant does not have predefined time slots."}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch tables for the restaurant
    tables = Table.objects.filter(restaurant=restaurant)
    if not tables.exists():
        return Response({"error": "No tables found for the restaurant."}, status=status.HTTP_404_NOT_FOUND)

    # Prepare slots and save them
    slots_data = []
    for time in time_slots:
        slot_tables = [
            {"table_id": table.id, "capacity": table.capacity, "remaining_quantity": table.quantity}
            for table in tables
        ]

        # Create the Slot object
        slot = Slot(
            restaurant=restaurant,
            date=date,
            time=time,
            tables=slot_tables
        )
        slot.save()
        slots_data.append(SlotSerializer(slot).data)

    return Response(slots_data, status=status.HTTP_201_CREATED)


#slot_detail API (Retrieve, Update, Delete Slot)
@api_view(['GET', 'PUT', 'DELETE'])
def slot_detail(request, restaurant_id, slot_id):
    try:
        # Fetch the slot
        slot = Slot.objects.get(pk=slot_id)
    except Slot.DoesNotExist:
        return Response({"error": "Slot not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # Serialize and return the slot details
        serializer = SlotSerializer(slot)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        # Update the slot details
        data = request.data

        # Ensure tables cannot be updated directly (if required)
        if "tables" in data:
            return Response({"error": "Tables cannot be updated directly"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SlotSerializer(slot, data=data, partial=True)  # Allow partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Delete the slot
        slot.delete()
        return Response({"message": "Slot deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# TABLE APIs
# Create Table (POST)
@api_view(['GET', 'POST'])
def restaurant_tables(request, restaurant_id):
    try:
        restaurant = Restaurant.objects.get(pk=restaurant_id)
    except Restaurant.DoesNotExist:
        return Response({"error": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # Fetch all tables for the specific restaurant
        tables = Table.objects.filter(restaurant=restaurant)
        serializer = TableSerializer(tables, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Add a single table to the restaurant
        data = request.data
        data['restaurant'] = restaurant_id
        serializer = TableSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#bulk add table
@api_view(['POST'])
def bulk_add_tables(request, restaurant_id):
    try:
        restaurant = Restaurant.objects.get(pk=restaurant_id)
    except Restaurant.DoesNotExist:
        return Response({"error": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)

    # Expecting an array of tables: [{"capacity": 4, "quantity": 2}, ...]
    table_data = request.data
    tables_to_add = []

    for table in table_data:
        tables_to_add.append(
            Table(
                restaurant=restaurant,  # Assign the actual Restaurant instance
                capacity=table['capacity'],
                quantity=table['quantity']
            )
        )

    Table.objects.bulk_create(tables_to_add)  # Bulk create tables
    return Response({"message": "Tables added successfully!"}, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def restaurant_table_detail(request, restaurant_id, table_id):
    try:
        table = Table.objects.get(pk=table_id, restaurant_id=restaurant_id)
    except Table.DoesNotExist:
        return Response({"error": "Table not found for the specified restaurant"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TableSerializer(table)
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Update the specific table
        data = request.data
        serializer = TableSerializer(table, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Delete the specific table
        table.delete()
        return Response({"message": "Table deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def book_table(request, restaurant_id, slot_id):
    data = request.data
    customer_email = data.get("customer_email")
    restaurant_id = data.get("restaurant_id")
    slot_id = data.get("slot_id")
    num_of_people = data.get("num_of_people")

    # Input validation
    try:
        restaurant = Restaurant.objects.get(id=restaurant_id)
    except Restaurant.DoesNotExist:
        return Response({"error": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        slot = Slot.objects.get(id=slot_id, restaurant=restaurant)
    except Slot.DoesNotExist:
        return Response({"error": "Slot not found"}, status=status.HTTP_404_NOT_FOUND)

    if num_of_people <= 0:
        return Response({"error": "Number of people must be greater than 0"}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch and sort tables for allocation
    tables = sorted(slot.tables, key=lambda x: x["capacity"], reverse=True)
    allocated_tables = []
    remaining_people = num_of_people

    for table in tables:
        if remaining_people <= 0:
            break

        if table["remaining_quantity"] > 0:
            # Determine how many tables to allocate
            tables_needed = (remaining_people + table["capacity"] - 1) // table["capacity"]
            allocated_quantity = min(tables_needed, table["remaining_quantity"])

            # Update allocation and remaining people
            allocated_tables.append({"table_id": table["table_id"], "allocated_quantity": allocated_quantity})
            table["remaining_quantity"] -= allocated_quantity
            remaining_people -= allocated_quantity * table["capacity"]

    if remaining_people > 0:
        return Response({"error": "Insufficient tables to accommodate the booking"}, status=status.HTTP_400_BAD_REQUEST)

    # Update slot's tables field
    slot.tables = tables
    slot.save()

    # Record the booking
    booking = Booking.objects.create(
        customer_email=customer_email,
        restaurant=restaurant,
        slot=slot,
        tables=allocated_tables,
        num_of_people=num_of_people
    )

    # Serialize and return booking details
    serializer = BookingSerializer(booking)
    return Response(serializer.data, status=status.HTTP_201_CREATED)



# API to get available dates and slots for a restaurant
# @api_view(['GET'])
# def get_available_dates(request, restaurant_id):
#     # Fetching all slots for a given restaurant
#     slots = Slot.objects.filter(restaurant_id=restaurant_id).values('date', 'id', 'time', 'restaurant_id', 'created_at')
    
#     # Grouping slots by date
#     date_slots = defaultdict(list)
#     for slot in slots:
#         # Convert date to string using isoformat
#         slot['date'] = slot['date'].isoformat()
#         slot['created_at'] = slot['created_at'].isoformat()  # Optionally convert created_at if it's a datetime object
        
#         date_slots[slot['date']].append({
#             "id": slot['id'],
#             "date": slot['date'],
#             "time": slot['time'],
#             "created_at": slot['created_at'],
#             "restaurant": slot['restaurant_id']
#         })
    
#     return Response(date_slots)

# @api_view(['POST'])
# def find_available_tables(request):
#     slot_id = request.data.get('slot_id')
#     num_people = request.data.get('num_people')

#     # Get the slot details
#     try:
#         slot = Slot.objects.get(id=slot_id)
#     except Slot.DoesNotExist:
#         return Response({"error": "Slot not found"}, status=status.HTTP_404_NOT_FOUND)

#     restaurant_id = slot.restaurant.id

#     # Fetch all available tables for the restaurant
#     tables = Table.objects.filter(restaurant_id=restaurant_id)

#     # Sort tables by capacity (smallest to largest)
#     tables = sorted(tables, key=lambda table: table.capacity)

#     # List to store selected tables
#     available_tables = []

#     remaining_people = num_people

#     for table in tables:
#         # Use smaller tables to fit the remaining people as closely as possible
#         while table.quantity > 0 and remaining_people >= table.capacity:
#             available_tables.append({'table_id': table.id, 'capacity': table.capacity})
#             remaining_people -= table.capacity
#             table.quantity -= 1

#         # If we can use this table for the exact remaining people
#         if table.quantity > 0 and 0 < remaining_people <= table.capacity:
#             available_tables.append({'table_id': table.id, 'capacity': table.capacity})
#             remaining_people = 0
#             table.quantity -= 1
#             break

#     # If there are still people left to accommodate, return an error
#     if remaining_people > 0:
#         return Response({"error": "Not enough tables available for the required number of people"})

#     return Response({
#         "message": "Tables found",
#         "tables": available_tables
#     })

# @api_view(['POST'])
# def update_table_quantity(request):
#     # Extract table_ids from the request
#     table_ids = request.data.get('table_ids')

#     # Decrease the quantity for each table
#     for table_id in table_ids:
#         table = Table.objects.get(id=table_id)
#         if table.quantity > 0:
#             table.quantity -= 1  # Decrease one table quantity
#             table.save()
#         else:
#             return Response({"error": f"Table with id {table_id} is not available."}, status=400)
    
#     return Response({"message": "Tables successfully booked!"})

# # Add Booking
# @api_view(['POST'])
# def add_booking(request):
#     if request.method == 'POST':
#         serializer = BookingSerializer(data=request.data)
#         if serializer.is_valid():
#             # Check if there's enough capacity in the selected slot for the number of people
#             slot = serializer.validated_data['slot']
#             tables = Table.objects.filter(restaurant=slot.restaurant, capacity__gte=slot.capacity)
#             total_capacity = sum(table.capacity * table.quantity for table in tables)
            
#             if total_capacity >= request.data['number_of_people']:
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             else:
#                 return Response({'error': 'Not enough available capacity'}, status=status.HTTP_400_BAD_REQUEST)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# # Get Bookings (for a restaurant)
# @api_view(['GET'])
# def get_bookings(request, restaurant_id):
#     if request.method == 'GET':
#         bookings = Booking.objects.filter(restaurant__id=restaurant_id)
#         serializer = BookingSerializer(bookings, many=True)
#         return Response(serializer.data)