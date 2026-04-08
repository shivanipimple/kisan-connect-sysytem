import os
import json
import random
import time
from datetime import timedelta

from django.db import models, transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings

from .models import (
    Order, Transaction, Review, Product,
    FarmerProfile, OrderStatusHistory,
    ContactMessage, AdminDocument, AdminReply,
)


# ────────────────────────────────────────────────
#  PUBLIC PAGES
# ────────────────────────────────────────────────

def index(request):
    products = Product.objects.all().order_by('-id')
    return render(request, 'app/index.html', {'products': products})

def Like(request):
    return render(request, 'app/like.html')

def Cart(request):
    return render(request, 'app/cart.html')

def checkout(request):
    return render(request, 'app/checkout.html')

def aboutus(request):
    return render(request, 'app/about_us.html')


# ── Contact Page ─────────────────────────────────
def contact_view(request):
    if request.method == "POST":
        name         = request.POST.get('name', '').strip()
        phone        = request.POST.get('phone', '').strip()
        email        = request.POST.get('email', '').strip()
        message_text = request.POST.get('message', '').strip()

        if name and phone and message_text:
            ContactMessage.objects.create(
                name=name, phone=phone,
                email=email or None,
                message=message_text
            )
            messages.success(request, "✅ Your message has been sent! We'll reply on WhatsApp soon.")
        else:
            messages.error(request, "Please fill in all required fields.")
        return redirect('contact')

    return render(request, 'app/contact.html')


# ────────────────────────────────────────────────
#  ORDERS
# ────────────────────────────────────────────────

def place_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = request.user.email.strip().lower() if request.user.is_authenticated else data.get('email', '').strip().lower()
            payment_method = data.get('paymentMethod')
            payment_status = 'Paid' if payment_method in ['UPI', 'Card'] else 'Unpaid'

            with transaction.atomic():
                new_order = Order.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    full_name=data.get('fullName'),
                    email=email,
                    mobile=data.get('mobile'),
                    address=data.get('address'),
                    city=data.get('city'),
                    pincode=data.get('pincode'),
                    payment_method=payment_method,
                    payment_status=payment_status,
                    total_amount=float(data.get('totalAmount', 0)),
                    items_json=json.dumps(data.get('cart')),
                    status='Pending'
                )
                OrderStatusHistory.objects.create(
                    order=new_order, status='Pending',
                    note=f'Order placed via {payment_method}. Status: {payment_status}'
                )
                if payment_status == 'Paid':
                    Transaction.objects.create(
                        order=new_order,
                        transaction_id=f"TXN-{new_order.id}-{random.randint(1000, 9999)}",
                        amount=new_order.total_amount,
                        payment_mode=payment_method
                    )
            return JsonResponse({'status': 'success', 'order_id': new_order.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def update_order_status(request, order_id, new_status):
    order = get_object_or_404(Order, id=order_id)
    order.status = new_status
    if new_status == 'Delivered':
        order.payment_status = 'Paid'
        Transaction.objects.get_or_create(
            order=order,
            defaults={
                'transaction_id': f"TXN-ORD-{order.id}",
                'amount': order.total_amount,
                'payment_mode': order.payment_method
            }
        )
    order.save()
    OrderStatusHistory.objects.create(order=order, status=new_status,
                                       note=f'Status updated to {new_status} by admin')
    return redirect('admin_orders')


@login_required
def my_orders(request):
    user_email = request.user.email.strip().lower()
    orders = Order.objects.filter(email__iexact=user_email).prefetch_related(
        'status_history', 'transactions').order_by('-id')

    for order in orders:
        try:
            order.items_list = json.loads(order.items_json) if order.items_json else []
        except:
            order.items_list = []

        history_records = order.status_history.all()
        order.history_dict = {
            (h.status if h.status != 'Pending' else 'Ordered'): h.changed_at
            for h in history_records
        }
        order.is_pickup = order.payment_method == 'SelfPickup' or order.status in ['ReadyForPickup', 'PickedUp']
        if not order.is_pickup:
            order.estimated_delivery = order.order_date + timedelta(days=5)

    return render(request, 'app/my_orders.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    user_email = request.user.email.strip().lower()
    order = get_object_or_404(Order, id=order_id, email__iexact=user_email)

    try:
        items_list = json.loads(order.items_json) if order.items_json else []
    except:
        items_list = []

    history_dict = {}
    for h in order.status_history.all().order_by('changed_at'):
        key = 'Ordered' if h.status == 'Pending' else h.status
        history_dict[key] = h.changed_at

    is_pickup = order.payment_method == 'SelfPickup' or order.status in ['ReadyForPickup', 'PickedUp']

    reviewed_product_ids = list(
        Review.objects.filter(order=order, user=request.user).values_list('product_id', flat=True)
    )

    for item in items_list:
        try:
            p = Product.objects.get(name__iexact=item.get('name', ''))
            item['product_id']       = p.id
            item['already_reviewed'] = p.id in reviewed_product_ids
        except Product.DoesNotExist:
            item['product_id']       = None
            item['already_reviewed'] = False

    existing_reviews = Review.objects.filter(order=order).select_related('user', 'product')

    return render(request, 'app/order_detail.html', {
        'order':               order,
        'items_list':          items_list,
        'history_dict':        history_dict,
        'is_pickup':           is_pickup,
        'transaction':         order.transactions.first(),
        'estimated_delivery':  order.order_date + timedelta(days=5),
        'existing_reviews':    existing_reviews,
        'reviewed_product_ids': reviewed_product_ids,
    })


# ────────────────────────────────────────────────
#  REVIEW
# ────────────────────────────────────────────────

@login_required
def add_review(request):
    order_id = request.POST.get('order_id')
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        rating     = request.POST.get('rating')
        comment    = request.POST.get('comment', '').strip()

        if not product_id or not order_id:
            messages.error(request, "Invalid review submission.")
            return redirect('my_orders')

        try:
            product = get_object_or_404(Product, id=int(product_id))
            order   = get_object_or_404(Order, id=int(order_id),
                                         email__iexact=request.user.email.strip().lower())

            if order.status != 'Delivered':
                messages.error(request, "You can only review delivered orders.")
                return redirect('order_detail', order_id=order_id)

            review, created = Review.objects.get_or_create(
                user=request.user, product=product, order=order,
                defaults={'rating': int(rating), 'comment': comment}
            )
            if created:
                messages.success(request, f"Review for '{product.name}' submitted! Thank you.")
            else:
                messages.info(request, f"You already reviewed '{product.name}'.")
        except Exception as e:
            messages.error(request, f"Error: {e}")

    return redirect('order_detail', order_id=order_id)


# ────────────────────────────────────────────────
#  AUTH
# ────────────────────────────────────────────────

def register_user(request):
    if request.method == "POST":
        fullname = request.POST.get('fullname')
        userid   = request.POST.get('userid')
        email    = request.POST.get('email').strip().lower()
        pass1    = request.POST.get('password')
        pass2    = request.POST.get('confirm_password')
        age      = request.POST.get('age')
        gender   = request.POST.get('gender')
        address  = request.POST.get('address')

        if pass1 != pass2:
            messages.error(request, "Passwords do not match!")
            return redirect('index')
        if User.objects.filter(username=userid).exists():
            messages.error(request, "This User ID is already taken.")
            return redirect('index')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered. Please login.")
            return redirect('index')
        try:
            user = User.objects.create_user(username=userid, email=email, password=pass1)
            user.first_name = fullname
            user.save()
            FarmerProfile.objects.create(user=user, age=age, gender=gender, address=address)
            logout(request)
            login(request, user)
            messages.success(request, f"Welcome to KisanConnect, {user.first_name}!")
            return redirect('index')
        except Exception as e:
            messages.error(request, f"Registration Error: {e}")
            return redirect('index')


def login_user(request):
    if request.method == "POST":
        uid  = request.POST.get('userid')
        pas  = request.POST.get('password')
        user = authenticate(request, username=uid, password=pas)
        if user:
            if user.is_superuser:
                messages.error(request, "Admins must login via the Admin Panel.")
                return redirect('index')
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect('index')
        messages.error(request, "Invalid User ID or Password.")
        return redirect('index')


def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('index')


# ────────────────────────────────────────────────
#  ADMIN AUTH & DASHBOARD
# ────────────────────────────────────────────────

def admin_login_view(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin_dashboard')
    if request.method == "POST":
        u    = request.POST.get('username')
        p    = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user and user.is_superuser:
            login(request, user)
            return redirect('admin_dashboard')
        messages.error(request, "Invalid Admin Credentials.")
    return render(request, 'app/admin/admin_login.html')


@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def admin_dashboard(request):
    revenue_data    = Transaction.objects.aggregate(total=models.Sum('amount'))
    recent_messages = ContactMessage.objects.all().order_by('-created_at')[:10]

    context = {
        'product_count':    Product.objects.count(),
        'order_count':      Order.objects.count(),
        'total_revenue':    revenue_data['total'] or 0,
        'recent_orders':    Order.objects.all().order_by('-order_date')[:5],
        'recent_messages':  recent_messages,
        'unread_count':     ContactMessage.objects.filter(is_read=False).count(),
    }
    return render(request, 'app/admin/admin_dashboard.html', context)


# ────────────────────────────────────────────────
#  COMMUNICATION — FILE UPLOAD & WHATSAPP
# ────────────────────────────────────────────────

def upload_admin_document(request):
    """
    AJAX: Receives a file from the admin dashboard and saves it.
    Returns the absolute URL so JS can open a wa.me share link.
    """
    if request.method == "POST" and request.FILES.get('document'):
        doc      = AdminDocument.objects.create(file=request.FILES['document'])
        file_url = request.build_absolute_uri(doc.file.url)
        return JsonResponse({'status': 'success', 'file_url': file_url, 'doc_id': doc.id})
    return JsonResponse({'status': 'error', 'message': 'No file uploaded'}, status=400)


def mark_message_read(request, msg_id):
    """AJAX: marks a ContactMessage as read."""
    if request.method == "POST":
        msg = get_object_or_404(ContactMessage, id=msg_id)
        msg.is_read = True
        msg.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)


def save_admin_reply(request):
    """Logs an admin reply (phone + message + optional doc)."""
    if request.method == "POST":
        phone = request.POST.get('phone', '')
        msg   = request.POST.get('message', '')
        doc   = request.FILES.get('document')
        reply = AdminReply.objects.create(customer_phone=phone, message=msg, document=doc)
        resp  = {'status': 'success'}
        if reply.document:
            resp['file_url'] = request.build_absolute_uri(reply.document.url)
        return JsonResponse(resp)
    return JsonResponse({'status': 'error'}, status=400)


# ────────────────────────────────────────────────
#  ADMIN — PRODUCTS
# ────────────────────────────────────────────────

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def product_list(request):
    products = Product.objects.all().order_by('-id')
    return render(request, 'app/admin/products.html', {'products': products})


@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def add_product(request):
    if request.method == "POST":
        product = Product(
            name=request.POST.get('name'),
            category=request.POST.get('category'),
            price=request.POST.get('price'),
            description=request.POST.get('description'),
            best_use=request.POST.get('best_use'),
            available_weights=request.POST.get('available_weights'),
            image=request.FILES.get('image')
        )
        product.save()
        messages.success(request, f"Product '{product.name}' added successfully!")
    return redirect('product_list')


@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def edit_product(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        product.name              = request.POST.get('name')
        product.category          = request.POST.get('category')
        product.price             = request.POST.get('price')
        product.description       = request.POST.get('description', '')
        product.best_use          = request.POST.get('best_use', '')
        product.available_weights = request.POST.get('available_weights', '')
        if request.FILES.get('image'):
            product.image = request.FILES['image']
        product.save()
        messages.success(request, f"Product '{product.name}' updated!")
        return redirect('product_list')
    return redirect('product_list')


@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def delete_product(request, id):
    if request.method == "POST":
        get_object_or_404(Product, id=id).delete()
        messages.success(request, "Product deleted.")
    return redirect('product_list')


# ────────────────────────────────────────────────
#  ADMIN — ORDERS / TRANSACTIONS / FARMERS
# ────────────────────────────────────────────────

def admin_orders(request):
    orders = Order.objects.all().order_by('-order_date')
    return render(request, 'app/admin/orders.html', {'orders': orders})


def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    try:
        cart_items = json.loads(order.items_json)
    except:
        cart_items = []
    return render(request, 'app/admin/order_detail.html', {'order': order, 'cart_items': cart_items})


def admin_transactions(request):
    txns = Transaction.objects.all().order_by('-timestamp')
    return render(request, 'app/admin/transactions.html', {'transactions': txns})


@login_required
def farmer_list(request):
    per_page    = request.GET.get('entries', 10)
    farmer_data = FarmerProfile.objects.select_related('user').all().order_by('-id')
    items_per_page = farmer_data.count() if per_page == 'all' else int(per_page)
    paginator  = Paginator(farmer_data, items_per_page or 10)
    page_obj   = paginator.get_page(request.GET.get('page'))
    return render(request, 'app/admin/farmer.html', {
        'page_obj': page_obj, 'current_entries': per_page
    })


# ── Admin Ratings ─────────────────────────────────
@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def rating_list(request):
    reviews        = Review.objects.select_related('user', 'product', 'order').order_by('-created_at')
    rating_filter  = request.GET.get('rating', '')
    product_filter = request.GET.get('product', '')
    if rating_filter:
        reviews = reviews.filter(rating=rating_filter)
    if product_filter:
        reviews = reviews.filter(product__id=product_filter)

    stats      = Review.objects.aggregate(avg_rating=Avg('rating'))
    avg_rating = round(stats['avg_rating'] or 0, 1)
    paginator  = Paginator(reviews, 15)
    page_obj   = paginator.get_page(request.GET.get('page'))

    return render(request, 'app/admin/ratings.html', {
        'page_obj':       page_obj,
        'avg_rating':     avg_rating,
        'total_reviews':  Review.objects.count(),
        'products':       Product.objects.all(),
        'rating_filter':  rating_filter,
        'product_filter': product_filter,
        'star_range':     range(1, 6),
    })


# ── Placeholders ──────────────────────────────────
def profile_settings(request):
    return render(request, 'app/admin/settings.html')

def order_list(request):
    return render(request, 'app/admin/orders.html')

def transaction_list(request):
    return render(request, 'app/admin/transactions.html')