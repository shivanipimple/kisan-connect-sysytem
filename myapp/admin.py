from django.contrib import admin
from django.contrib.auth.models import User
from .models import FarmerProfile, Order

# 1. Register the Order model simply
admin.site.register(Order)

# 2. Define the Advanced Admin view for FarmerProfile
class FarmerProfileAdmin(admin.ModelAdmin):
    # Columns shown in the list view table
    list_display = ('get_username', 'get_email', 'get_fullname', 'age', 'gender', 'address')
    
    # Search bar (reaches into the linked User model using __)
    search_fields = ('user__username', 'user__email', 'user__first_name')
    
    # Filter sidebar on the right
    list_filter = ('gender', 'age')

    # Methods to pull data from the linked User model
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'User ID'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

    def get_fullname(self, obj):
        return obj.user.first_name
    get_fullname.short_description = 'Full Name'

# 3. Register FarmerProfile with the custom admin class
admin.site.register(FarmerProfile, FarmerProfileAdmin)

from .models import Review

admin.site.register(Review)

# myapp/admin.py
from django.contrib import admin
from .models import ContactMessage

admin.site.register(ContactMessage)