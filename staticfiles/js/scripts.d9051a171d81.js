function validateForm(event) {
            let isValid = true;
            const name = document.getElementById('regName').value;
            const nameRegex = /^[A-Za-z\s]+$/;
            if (!nameRegex.test(name)) {
                document.getElementById('nameError').style.display = 'block';
                isValid = false;
            } else {
                document.getElementById('nameError').style.display = 'none';
            }
  
            const age = document.getElementById('regAge').value;
            const ageRegex = /^[0-9]+$/;
            if (!ageRegex.test(age)) {
                document.getElementById('ageError').style.display = 'block';
                isValid = false;
            } else {
                document.getElementById('ageError').style.display = 'none';
            }

            const pass = document.getElementById('regPass').value;
            const confirmPass = document.getElementById('regConfirmPass').value;
            if (pass !== confirmPass) {
                document.getElementById('passError').style.display = 'block';
                isValid = false;
            } else {
                document.getElementById('passError').style.display = 'none';
            }

            if (!isValid) {
                event.preventDefault();
            } else {
                alert("Registration Successful!");
            }
            return isValid;
        } 

        document.getElementById('regAge').addEventListener('input', function (e) {
            this.value = this.value.replace(/[^0-9]/g, '');
        });

        document.getElementById('regName').addEventListener('input', function (e) {
            this.value = this.value.replace(/[0-9]/g, '');
        });





       async function sendOTPRequest(event) {
    // 1. Get Values
    const email = document.getElementById('regEmail').value;
    const name = document.getElementById('regName').value;
    const age = document.getElementById('regAge').value;
    const gender = document.getElementById('regGender').value;
    const address = document.getElementById('regAddress').value;
    const pass = document.getElementById('regPass').value;
    const confirmPass = document.getElementById('regConfirmPass').value;

    // 2. Comprehensive Validation
    if(!email || !name || !age || !gender || !address || !pass) {
        alert("Please fill in all fields.");
        return;
    }

    if(pass !== confirmPass) {
        document.getElementById('passError').style.display = 'block';
        return;
    } else {
        document.getElementById('passError').style.display = 'none';
    }

    // 3. UI Loading State
    const btn = document.getElementById('otpBtn');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Sending OTP...';
    btn.disabled = true;

    // 4. Send Request to Django
    const formData = new FormData(document.getElementById('registrationForm'));
    
    try {
        // Inside your sendOTPRequest function
// To this (Manual path for testing):
const response = await fetch("/send-otp/", {  // This MUST match the name in urls.py
    method: 'POST',
    body: formData,
    headers: {
        'X-CSRFToken': '{{ csrf_token }}'
    }
});
        
        const result = await response.json();

        if (result.success) {
            // SUCCESS: Switch to OTP View
            document.getElementById('registrationFields').style.display = 'none';
            document.getElementById('otpSection').style.display = 'block';
            document.getElementById('regModalTitle').innerText = 'Verify Your Email';
        } else {
            // ERROR from Backend
            alert("Error: " + result.message);
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    } catch (error) {
        console.error("Fetch Error:", error);
        alert("Network error. Please check if your Django server is running and URLs are correct.");
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

function backToReg() {
    document.getElementById('registrationFields').style.display = 'block';
    document.getElementById('otpSection').style.display = 'none';
    document.getElementById('regModalTitle').innerText = 'Farmer Registration';
}





 
        
        
        let cartCount = 0;
        function addToCart() {
            cartCount++;
            const badge = document.getElementById('cart-count');
            badge.innerText = cartCount;
            badge.style.transform = "scale(1.3)";
            setTimeout(() => badge.style.transform = "scale(1)", 200); 
        }

        let wishlistCount = 0;
        function toggleWishlist(element) {
            element.classList.toggle('active');
            element.classList.toggle('fas');
            element.classList.toggle('far');
            const badge = document.getElementById('wishlist-count');
            if (element.classList.contains('active')) {
                wishlistCount++;
            } else {
                wishlistCount--;
            }
            badge.innerText = wishlistCount;
        }






// १. प्रॉडक्ट कार्टमध्ये ॲड करणे
function addToCart(id, name, price, image) {
    let cart = JSON.parse(localStorage.getItem('myCart')) || [];

    let exists = cart.find(item => item.id === id);
    if (exists) {
        exists.quantity += 1;
    } else {
        cart.push({
            id: id,
            name: name,
            price: price,
            image: image,
            quantity: 1
        });
    }

    localStorage.setItem('myCart', JSON.stringify(cart));
    updateCartCount(); // काउंट अपडेट करा
    
    // अलर्टऐवजी छोटे नोटिफिकेशन दिले तर चांगले दिसेल
    alert(name + " कार्टमध्ये ॲड झाले!");
}

// १. बॅग आयकॉनवरील काउंट अपडेट करणे
function updateCartCount() {
    let cart = JSON.parse(localStorage.getItem('myCart')) || [];
    const cartBadge = document.getElementById('cart-count');
    if (cartBadge) {
        let totalItems = cart.reduce((total, item) => total + item.quantity, 0);
        cartBadge.innerText = totalItems;
    }
}

// पेज लोड झाल्यावर लगेच काउंट अपडेट करा
document.addEventListener('DOMContentLoaded', updateCartCount);








// १. बॅग आयकॉनवरील काउंट अपडेट करणे
function updateCartCount() {
    let cart = JSON.parse(localStorage.getItem('myCart')) || [];
    const cartBadge = document.getElementById('cart-count');
    if (cartBadge) {
        let totalItems = cart.reduce((total, item) => total + item.quantity, 0);
        cartBadge.innerText = totalItems;
    }
}

function updateWishlistCount() {
    let wishlist = JSON.parse(localStorage.getItem('myWishlist')) || [];
    let badge = document.getElementById('wishlist-count');
    if (badge) badge.innerText = wishlist.length;
}

// २. होम पेज लोड झाल्यावर हार्ट रेड करण्यासाठी
function checkHeartStatus() {
    let wishlist = JSON.parse(localStorage.getItem('myWishlist')) || [];
    document.querySelectorAll('.wishlist-btn').forEach(btn => {
        let productId = String(btn.getAttribute('data-id'));
        if (wishlist.some(item => String(item.id) === productId)) {
            btn.classList.replace('far', 'fas');
            btn.classList.add('text-danger');
        } else {
            btn.classList.replace('fas', 'far');
            btn.classList.remove('text-danger');
        }
    });
}

// ३. टोगल फंक्शन - हे सर्वात महत्त्वाचे आहे
function toggleWishlist(id, name, price, image, element) {
    let wishlist = JSON.parse(localStorage.getItem('myWishlist')) || [];
    let productId = String(id);
    let index = wishlist.findIndex(item => String(item.id) === productId);

    if (index > -1) {
        // Remove from wishlist
        wishlist.splice(index, 1);
        element.classList.replace('fas', 'far');
        element.classList.remove('text-danger');
    } else {
        // Add to wishlist
        wishlist.push({ id: productId, name: name, price: price, image: image });
        element.classList.replace('far', 'fas');
        element.classList.add('text-danger');
    }

    localStorage.setItem('myWishlist', JSON.stringify(wishlist));
    updateWishlistCount();
}

// ४. पेज लोड झाल्यावर सर्व फंक्शन्स रन करा
document.addEventListener('DOMContentLoaded', () => {
    updateCartCount();
    updateWishlistCount();
    checkHeartStatus(); 
});



// function toggleWishlist(id, name, price, image, element) {
//     let wishlist = JSON.parse(localStorage.getItem('myWishlist')) || [];
//     let index = wishlist.findIndex(item => item.id === id);

//     if (index > -1) {
//         // DISLIKE: जर आधीच असेल तर काढून टाका
//         wishlist.splice(index, 1);
//         element.classList.remove('fas', 'text-danger');
//         element.classList.add('far');
//         console.log("Removed from wishlist");
//     } else {
//         // LIKE: नसेल तर ॲड करा
//         wishlist.push({ id: id, name: name, price: price, image: image });
//         element.classList.remove('far');
//         element.classList.add('fas', 'text-danger');
//         console.log("Added to wishlist");
//     }

//     localStorage.setItem('myWishlist', JSON.stringify(wishlist));
//     updateWishlistCount();
// }

// // होम पेज लोड झाल्यावर कोणते हार्ट रेड करायचे हे ठरवण्यासाठी
// function checkHeartStatus() {
//     let wishlist = JSON.parse(localStorage.getItem('myWishlist')) || [];
//     // सर्व विशलिस्ट आयकॉन्स शोधा (तुमच्या आयकॉनला 'wishlist-btn' क्लास द्या)
//     document.querySelectorAll('.wishlist-btn').forEach(btn => {
//         let productId = btn.getAttribute('data-id');
//         if (wishlist.some(item => item.id === productId)) {
//             btn.classList.remove('far');
//             btn.classList.add('fas', 'text-danger');
//         }
//     });
// }

// document.addEventListener('DOMContentLoaded', () => {
//     updateCartCount();
//     updateWishlistCount();
//     checkHeartStatus(); // हार्ट चेक करा
// });

