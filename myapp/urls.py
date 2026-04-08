from django.urls import path
from . import views

urlpatterns = [  

    # ── Public ──────────────────────────────────────
    path('',          views.index,    name='index'),
    path('like/',     views.Like,     name='like'),
    path('cart/',     views.Cart,     name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('contact/',  views.contact_view, name='contact'),
        path('about/',  views.aboutus, name='aboutus'),


    # ── Orders ──────────────────────────────────────
    path('place-order/',                views.place_order,  name='place_order'),
    path('my-orders/',                  views.my_orders,    name='my_orders'),
    path('my-orders/<int:order_id>/',   views.order_detail, name='order_detail'),

    # ── Review ──────────────────────────────────────
    path('add-review/', views.add_review, name='add_review'),

    # ── Auth ────────────────────────────────────────
    path('register/', views.register_user, name='register'),
    path('login/',    views.login_user,    name='login'),
    path('logout/',   views.logout_view,   name='logout'), 

    # ── Admin Auth ──────────────────────────────────
    path('kisan-admin/login/',     views.admin_login_view, name='admin_login'),
    path('kisan-admin/dashboard/', views.admin_dashboard,  name='admin_dashboard'),

    # ── Admin Products ───────────────────────────────
    path('kisan-admin/products/',                  views.product_list,   name='product_list'),
    path('kisan-admin/add-product/',               views.add_product,    name='add_product'),
    path('kisan-admin/product/edit/<int:id>/',     views.edit_product,   name='edit_product'),
    path('kisan-admin/product/delete/<int:id>/',   views.delete_product, name='delete_product'),

    # ── Admin Orders ─────────────────────────────────
    path('kisan-admin/orders/',                                           views.admin_orders,       name='admin_orders'),
    path('kisan-admin/order/<int:order_id>/',                           views.admin_order_detail, name='admin_order_detail'),
    path('kisan-admin/order/update/<int:order_id>/<str:new_status>/',   views.update_order_status,name='update_order_status'),

    # ── Admin Transactions / Farmers / Ratings ───────
    path('kisan-admin/transactions/', views.admin_transactions, name='admin_transactions'),
    path('kisan-admin/farmers/',      views.farmer_list,        name='farmer_list'),  
    path('kisan-admin/settings/',     views.profile_settings,   name='settings'),
    path('kisan-admin/ratings/',      views.rating_list,        name='rating_list'),

    # ── Communication (AJAX) ─────────────────────────
    path('upload-doc/',           views.upload_admin_document, name='upload_doc'),
    path('save-reply/',           views.save_admin_reply,      name='save_reply'),
    path('mark-read/<int:msg_id>/', views.mark_message_read,   name='mark_read'),
] 