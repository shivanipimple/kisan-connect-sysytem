# KisanConnect 
**Empowering Farmers through Digital Commerce & Smart Management**

KisanConnect is a modern, Full-Stack E-commerce platform designed to streamline the agricultural supply chain in India. It serves as a one-stop digital marketplace where farmers can purchase high-quality fertilizers, pesticides, seeds, and farming tools. 

The project features a robust **Django backend** to handle complex business logic and a **responsive frontend** with a specialized Admin Panel for managing the entire lifecycle of an order—from stock management to final delivery.

---

## 🌟 Key Features

### 🛒 Farmer Storefront (User Side)
* **Digital Marketplace:** Browse categorized agricultural products (Seeds, Tools, Fertilizers, Pesticides).
* **Interactive UI:** Smooth product cards with hover-zoom effects and a "Quick View" modal system for detailed product info.
* **Persistent Cart & Wishlist:** Uses JavaScript and LocalStorage to save items even after refreshing the page.
* **Smart Filtering:** Easily find products based on category and agricultural needs.
* **Mobile Responsive:** Designed to work perfectly on mobile devices for farmers on the go.

### 🛠 Admin Management Panel
* **Shop Management:** Full control over product listings (Add, Edit, Delete).
* **Order Lifecycle Handling:** Manage customer orders, track payments, and update delivery status.
* **Inventory Tracking:** Real-time monitoring of stock levels for essential farm inputs.
* **User Records:** Secure management of registered farmer profiles and contact details.

---

## 💻 Tech Stack

- **Backend:** Python, Django 4.x (MVC Architecture)
- **Frontend:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5
- **Database:** MySQL
- **Icons & UI:** FontAwesome 6, Google Fonts
- **State Management:** Browser LocalStorage API

---

## 📂 Project Structure

```text
KisanConnect/                <-- Your Root Folder
│
├── core/                    <-- Project Configuration (contains settings.py)
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── shop/                    <-- Product & Category Logic
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── models.py            <-- (Products, Category models)
│   ├── urls.py
│   └── views.py
│
├── orders/                  <-- Cart & Checkout Logic
│   ├── migrations/
│   ├── __init__.py
│   ├── models.py            <-- (Order, OrderItem models)
│   ├── urls.py
│   └── views.py
│
├── static/                  <-- CSS, JS, and Images
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── scripts.js
│   └── images/              <-- Static UI icons/logos
│
├── media/                   <-- Uploaded Product Photos
│   └── products/
│
├── templates/               <-- HTML Files
│   ├── base.html
│   ├── shop/
│   │   ├── index.html
│   │   └── product_detail.html
│   └── orders/
│       └── cart.html
│
├── manage.py
└── requirements.txt         <-- List of libraries (Django, mysqlclient, etc.)
