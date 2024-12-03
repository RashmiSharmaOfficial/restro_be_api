from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User, Restaurant, Slot, Table, Booking
from .serializers import UserSerializer, RestaurantSerializer, SlotSerializer, TableSerializer, BookingSerializer
from collections import defaultdict
from django.db.models import Q
from datetime import date, datetime, timedelta
from django.contrib.auth import authenticate
from django.db import transaction
from django.contrib.auth.hashers import make_password
    
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


@api_view(['POST'])
def register_or_login(request):
    """
    Handles user registration if the email doesn't exist or logs in if the user already exists.
    """
    email = request.data.get('email')
    password = request.data.get('password')
    role = request.data.get('role', 'customer')  # Default role is 'customer'

    if not email or not password:
        return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Check if the user already exists
        user = User.objects.get(email=email)

        # Try to authenticate the user
        authenticated_user = authenticate(username=email, password=password)
        if authenticated_user is not None:
            return Response({
                "email": email,
                "id": user.user_id,
                "role": user.role,
                "message": "Success login"
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid password."}, status=status.HTTP_401_UNAUTHORIZED)

    except User.DoesNotExist:
        # If user does not exist, create a new user
        hashed_password = make_password(password)  # Hash the password before saving
        user_data = {
            "email": email,
            "password": hashed_password,
            "role": role
        }
        serializer = UserSerializer(data=user_data)
        if serializer.is_valid():
            new_user = serializer.save()
            return Response({
                "email": new_user.email,
                "id": new_user.user_id,
                "role": new_user.role,
                "message": "User created successfully and logged in."
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   

# RESTAURANT APIs
@api_view(['GET', 'POST'])
def restaurants(request):
    if request.method == 'GET':
        restaurants = Restaurant.objects.all()
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        # Ensure that the email provided for the owner exists
        owner_email = request.data.get('owner')
        try:
            # Check if the user with this email exists
            owner = User.objects.get(pk=owner_email)
        except User.DoesNotExist:
            return Response({"error": "Owner with this email does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        
        # If the user exists, associate the restaurant with the user
        request.data['owner'] = owner_email  # Set the owner as the user's email

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

@api_view(['POST'])
def auto_create_multi_slots(request, restaurant_id):
    """
    Automatically creates slots for a restaurant based on its time slots and tables for a given date or range of dates.
    """
    try:
        restaurant = Restaurant.objects.get(pk=restaurant_id)
    except Restaurant.DoesNotExist:
        return Response({"error": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)

    # Validate date input
    start_date = request.data.get("startDate")
    end_date = request.data.get("endDate")

    if not start_date or not end_date:
        return Response({"error": "startDate and endDate are required."}, status=status.HTTP_400_BAD_REQUEST)
    
    # added today's date as default to start making slots
    today_date = date.today().strftime("%Y-%m-%d");
    
    try:
        start_date = datetime.strptime(today_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        return Response({"error": "Invalid date format. Use 'YYYY-MM-DD'."}, status=status.HTTP_400_BAD_REQUEST)

    if start_date > end_date:
        return Response({"error": "startDate cannot be after endDate."}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch the predefined time slots from the restaurant
    time_slots = restaurant.time_slots
    if not time_slots:
        return Response({"error": "Restaurant does not have predefined time slots."}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch tables for the restaurant
    tables = Table.objects.filter(restaurant=restaurant)
    if not tables.exists():
        return Response({"error": "No tables found for the restaurant."}, status=status.HTTP_404_NOT_FOUND)

    # Iterate over the date range and create slots
    slots_data = []
    current_date = start_date
    while current_date <= end_date:
        for time in time_slots:
            slot_tables = [
                {"table_id": table.id, "capacity": table.capacity, "remaining_quantity": table.quantity}
                for table in tables
            ]

            # Create the Slot object
            slot = Slot(
                restaurant=restaurant,
                date=current_date,
                time=time,
                tables=slot_tables
            )
            slot.save()
            slots_data.append(SlotSerializer(slot).data)

        current_date += timedelta(days=1)

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

@api_view(['GET'])
def search_restaurants(request):
    """
    Search for restaurants using a single keyword that can match multiple attributes.
    """
    try:
        # Get the search keyword from query params
        keyword = request.query_params.get('keyword', None)

        if not keyword:
            return Response({"error": "Keyword is required for search."}, status=status.HTTP_400_BAD_REQUEST)

        # Filter restaurants by matching the keyword in multiple fields
        restaurants = Restaurant.objects.filter(
            Q(name__icontains=keyword) |
            Q(city__icontains=keyword) |
            Q(area__icontains=keyword) |
            Q(cuisine__icontains=keyword) |
            Q(rating__icontains=keyword) |  # In case users search for ratings
            Q(cost_for_two__icontains=keyword)  # For cost-related searches
        )

        if not restaurants.exists():
            return Response({"message": "No restaurants found matching the keyword."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the data
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

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

def book_tab(num_people, seats):
    """
    Function to allocate tables with minimum wastage.
    Args:
    num_people (int): Number of people to accommodate.
    seats (dict): Dictionary with seat capacities and their available count.
    Returns:
    list: Allocated seats, or empty list if booking is not possible.
    """
    available_seats = []
    for capacity, count in seats.items():
        available_seats.extend([capacity] * count)
    available_seats.sort(reverse=True)

    # Try to allocate seats optimally
    allocated_seats = []
    total_people = 0
    for seat in available_seats:
        if total_people >= num_people:
            break
        if seat <= (num_people - total_people):
            allocated_seats.append(seat)
            total_people += seat

    # Check if enough seats were allocated
    if total_people >= num_people:
        return allocated_seats

    # If not, minimize wastage with combinations
    return minimize_wastage_combination(num_people, available_seats)

def minimize_wastage_combination(num_people, available_seats):
    """
    Reduce wastage by combining larger seats optimally.
    Args:
    num_people (int): Number of people to accommodate.
    available_seats (list): List of available seats.
    Returns:
    list: Optimal list of allocated seats.
    """
    best_combination = []
    best_wastage = float('inf')

    for i in range(1, len(available_seats) + 1):
        for combination in combinations(available_seats, i):
            if sum(combination) >= num_people:
                wastage = sum(combination) - num_people
                if wastage < best_wastage:
                    best_wastage = wastage
                    best_combination = combination
                if wastage == 0:
                    return list(best_combination)
    return list(best_combination)

@api_view(['POST'])
def book_table_api(request, restaurant_id, slot_id):
    data = request.data
    customer_email = data.get("customer_email")
    num_of_people = data.get("num_of_people")

    # Input validation
    try:
        restaurant = Restaurant.objects.get(id=restaurant_id)
    except Restaurant.DoesNotExist:
        return Response({"error": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)

    if num_of_people <= 0:
        return Response({"error": "Number of people must be greater than 0"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            # Lock the slot for this transaction
            slot = Slot.objects.select_for_update().get(id=slot_id, restaurant=restaurant)

            # Prepare seat availability data
            seat_map = {table["capacity"]: table["remaining_quantity"] for table in slot.tables}

            # Use the optimized logic to allocate tables
            allocated_seats = book_tab(num_of_people, seat_map)
            if not allocated_seats:
                return Response({"error": "Insufficient tables to accommodate the booking"}, status=status.HTTP_400_BAD_REQUEST)

            # Update table availability
            for seat in allocated_seats:
                for table in slot.tables:
                    if table["capacity"] == seat and table["remaining_quantity"] > 0:
                        table["remaining_quantity"] -= 1
                        break

            # Save the updated slot and booking
            slot.save()
            booking = Booking.objects.create(
                customer_email=customer_email,
                restaurant=restaurant,
                slot=slot,
                tables=allocated_seats,
                num_of_people=num_of_people
            )

        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Slot.DoesNotExist:
        return Response({"error": "Slot not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
