from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
import os
# IMPORT YOUR NEW AWS FILE
import app_aws 

app = Flask(__name__)
app.secret_key = 'your-secret-key'

#home route
@app.route("/")
def home():
    return render_template("home.html") # Matches your new white card UI




#signup route
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user_type = request.form.get("user_type")
        
        # Call function from app_aws.py
        if app_aws.create_user(username, password, user_type):
            app_aws.send_notification(f"New user: {username}")
            flash("Success! Please log in.", "success")
            return redirect(url_for('login'))
    return render_template("signup.html")

#---login route---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = app_aws.get_user_by_username(username)
        
        if user and check_password_hash(user['password'], password):
            session["user_id"] = username
            session["user_type"] = user["user_type"]
            return redirect(url_for('layout'))
        flash("Invalid credentials", "error")
    return render_template("login.html")
#---layout route---
@app.route("/layout")
def layout():
    # Ensure user is logged in
    if "user_id" not in session:
        return redirect(url_for('login', next=request.path))
    
    # Decide what to render for logged-in users
    # For example, you can show homepage with user session info
    return render_template("home.html", user=session.get("user_id"))





#---about route---
@app.route("/about")
def about():
    """Defines the 'about' endpoint to fix the BuildError."""
    return render_template("about.html")

#---browse services route---
@app.route("/browse_services")
def browse_services():
    """Allows users to explore service categories."""
    return render_template("services.html")


# Hardcoded providers (you can replace with DB query later)
ALL_PROVIDERS = [
    {
        "id": 1,
        "name": "Amit Electricals",
        "image_url": "electrician.jpg",
        "location": "Delhi",
        "rating": 4.6,
        "about": "Expert in electrical wiring, repairs, and installations.",
        "service_type": "electrical",
         # ADD THIS
        "services": [
            {"name": "Fan Installation", "price": 300},
            {"name": "Wiring Repair", "price": 500}
        ],

        # ADD REVIEWS ALSO
        "reviews": [
            {"user": "Rahul", "rating": 5, "comment": "Very professional"},
            {"user": "Sneha", "rating": 4, "comment": "Good service"}
        ]
    }
    ,
    {
        "id": 2,
        "name": "SparkPro Services",
        "image_url": "electrician2.jpg",
        "location": "Noida",
        "rating": 4.4,
        "about": "Fast and reliable electrical services for homes and offices.",
        "service_type": "electrical",
         # ADD THIS
        "services": [
            {"name": "Fan Installation", "price": 300},
            {"name": "Wiring Repair", "price": 500}
        ],

        # ADD REVIEWS ALSO
        "reviews": [
            {"user": "Rahul", "rating": 5, "comment": "Very professional"},
            {"user": "Sneha", "rating": 4, "comment": "Good service"}
        ]
    },
     {
        "id": 3,
        "name": "SparkPro Services",
        "image_url": "cleaning.jpg",
        "location": "Noida",
        "rating": 4.4,
        "about": "Fast and reliable electrical services for homes and offices.",
        "service_type": "cleaning",
         # ADD THIS
        "services": [
            {"name": "Fan Installation", "price": 300},
            {"name": "Wiring Repair", "price": 500}
        ],

        # ADD REVIEWS ALSO
        "reviews": [
            {"user": "Rahul", "rating": 5, "comment": "Very professional"},
            {"user": "Sneha", "rating": 4, "comment": "Good service"}
        ]
    }
    
]

@app.route("/services/<service_name>")
def service_providers(service_name):
    # Filter providers for this service
    providers = [p for p in ALL_PROVIDERS if p['service_type'] == service_name.lower()]
    return render_template(
        "providers_list.html",
        service_name=service_name.capitalize(),
        providers=providers
    )


@app.route("/provider/<int:provider_id>")
def provider_detail(provider_id):
    # Find the provider
    provider = next((p for p in ALL_PROVIDERS if p['id'] == provider_id), None)
    if not provider:
        flash("Provider not found", "error")
        return redirect(url_for('home'))

    # Find similar providers (same service_type, exclude current)
    similar_providers = [
        p for p in ALL_PROVIDERS
        if p['service_type'] == provider['service_type'] and p['id'] != provider_id
    ]

    return render_template(
        "provider_detail.html",
        provider=provider,
        similar_providers=similar_providers
    )

@app.route("/profile")
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("profile.html")

@app.route("/book/<int:provider_id>", methods=["POST"])
def book_service(provider_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    date = request.form.get("date")
    time = request.form.get("time")
    notes = request.form.get("notes")

    success = app_aws.create_booking(
        session["user_id"],
        provider_id,
        date,
        time,
        notes
    )

    if success:
        app_aws.send_notification(
            f"New booking by {session['user_id']}"
        )
        flash("Booking successful!", "success")
    else:
        flash("Booking failed!", "error")

    return redirect(url_for("provider_detail", provider_id=provider_id))


@app.route("/my_bookings")
def my_bookings():

    if "user_id" not in session:
        return redirect(url_for("login"))

    bookings = app_aws.get_bookings_by_user(session["user_id"])

    return render_template("my_bookings.html", bookings=bookings)


#---Logout route---
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":

    app.run(debug=True)  

    
