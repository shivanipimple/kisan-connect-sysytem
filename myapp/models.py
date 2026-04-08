from django.db import models
from django.contrib.auth.models import User
import json


### Farmer Registration ###
class FarmerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Organic', 'Organic'),
        ('Seeds', 'Seeds'),
        ('Fertilizers', 'Fertilizers'),
        ('Pesticides', 'Pesticides'),
        ('Tools', 'Tools'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='products/')
    best_use = models.TextField(blank=True, null=True)
    available_weights = models.CharField(max_length=100, default="1kg, 5kg, 10kg")

    def __str__(self):
        return self.name


### Order Model ###
class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Packed', 'Packed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
        ('ReadyForPickup', 'Ready for Pickup'),
        ('PickedUp', 'Picked Up'),
    )
    PAYMENT_STATUS = (
        ('Unpaid', 'Unpaid'),
        ('Paid', 'Paid'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='orders')
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)

    payment_method = models.CharField(max_length=20)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='Unpaid')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    items_json = models.TextField()
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.full_name}"

    def get_items(self):
        try:
            return json.loads(self.items_json)
        except (json.JSONDecodeError, TypeError):
            return []

    @property
    def first_item_image(self):
        items = self.get_items()
        if items and len(items) > 0:
            image_path = items[0].get('image')
            if image_path:
                if not (image_path.startswith('http') or image_path.startswith('/')):
                    return f"/media/{image_path}"
                return image_path
        return None


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20)
    changed_at = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"Order #{self.order.id} → {self.status} at {self.changed_at}"


class Transaction(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transactions')
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Tx {self.transaction_id} for Order {self.order.id}"


### ✅ FIXED Review Model (properly outside Transaction class) ###
class Review(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='reviews')

    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # One review per product per order
        unique_together = ('user', 'product', 'order')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} → {self.product.name} ({self.rating}★)"

    def star_range(self):
        return range(1, 6)
    


    # models.py around line 137

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)  # Make sure this is indented!
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.name}"
    

    # myapp/models.py

class AdminDocument(models.Model):
    file = models.FileField(upload_to='admin_docs/%Y/%m/%d/')  # <--- Added 4 spaces here
    uploaded_at = models.DateTimeField(auto_now_add=True)     # <--- Added 4 spaces here

    def __str__(self):
        return f"Doc {self.id} - {self.uploaded_at}"

    # models.py
class AdminReply(models.Model):
    customer_phone = models.CharField(max_length=20)
    message = models.TextField(null=True, blank=True)
    document = models.FileField(upload_to='admin_replies/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)