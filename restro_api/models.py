from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'owner')
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('customer', 'Customer'),
    ]

    user_id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True, null=False)
    password = models.CharField(max_length=255, null=False)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email is the required field for authentication

    def __str__(self):
        return self.email


class Restaurant(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey('User', on_delete=models.CASCADE)  # Referencing the User model
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    cuisine = models.CharField(max_length=255)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
    cost_for_two = models.DecimalField(max_digits=10, decimal_places=2)
    is_veg = models.BooleanField(default=False)
    working_days = models.JSONField(default=list)  # List of days ['Mon', 'Tue', 'Wed', ...]
    time_slots = models.JSONField(default=list)  # List of time slots ['09:00:00', '10:00:00', ...]
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Table(models.Model):
    id = models.AutoField(primary_key=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    capacity = models.IntegerField()
    quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.restaurant.name} - Table capacity: {self.capacity} Quantity: {self.quantity}"


class Slot(models.Model):
    id = models.AutoField(primary_key=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    date = models.DateField()  # Date for the slot
    time = models.TimeField()  # Time for the slot
    tables = models.JSONField(default=list)  # [{"table_id": 1, "capacity": 4, "remaining_quantity": 2}, ...]
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Slot {self.time} on {self.date}"

class Booking(models.Model):
    id = models.AutoField(primary_key=True)
    customer_email = models.EmailField()
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)
    tables = models.JSONField(default=list)  # [{"table_id": 1, "allocated_quantity": 1}, ...]
    num_of_people = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Booking for {self.number_of_people} people at {self.restaurant.name} on {self.slot.date} {self.slot.time}"
