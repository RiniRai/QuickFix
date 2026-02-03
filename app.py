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

@app.route("/layout")
def layout():
    # Ensure user is logged in
    if "user_id" not in session:
        return redirect(url_for('login', next=request.path))
    
    # Decide what to render for logged-in users
    # For example, you can show homepage with user session info
    return render_template("home.html", user=session.get("user_id"))



#---dashboard route---
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for('login'))
    services = app_aws.get_user_services(session["user_id"], session["user_type"])
    return render_template("homeowner_dashboard.html", services=services)

#---about route---
@app.route("/about")
def about():
    """Defines the 'about' endpoint to fix the BuildError."""
    return render_template("about.html")

@app.route("/browse_services")
def browse_services():
    """Allows users to explore service categories."""
    return render_template("services.html")

@app.route("/service_providers")
def service_providers():
    """Displays the list of newly joined providers."""
    return render_template("providers.html")


#---Logout route---
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)