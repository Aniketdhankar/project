from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import time, requests, os, openai
import joblib
from google.cloud import dialogflow_v2 as dialogflow
from dotenv import load_dotenv
import numpy as np
import pandas as pd
from flask_mail import Mail, Message

# -----------------
# App and Configuration
# -----------------
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a strong secret key

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail configuration
app.config.update(
    MAIL_SERVER='smtp.mail.yahoo.com',  # Yahoo's SMTP server
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='aniketsingh5566@yahoo.com',  # Your Yahoo email
    MAIL_PASSWORD='vptvlbuunmyoqbpd',            # Your app password
    MAIL_DEFAULT_SENDER='aniketsingh5566@yahoo.com'
)

# Initialize extensions
db = SQLAlchemy(app)
mail = Mail(app)

# Load environment variables
load_dotenv()
DIALOGFLOW_PROJECT_ID = os.getenv("DIALOGFLOW_PROJECT_ID")

# -----------------
# Models
# -----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    profile = db.relationship('MedicalProfile', backref='user', uselist=False)

class MedicalProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    date_of_birth = db.Column(db.String(20), nullable=False)
    blood_group = db.Column(db.String(10), nullable=False)
    allergies = db.Column(db.Text, nullable=True)
    existing_conditions = db.Column(db.Text, nullable=True)
    medications = db.Column(db.Text, nullable=True)
    emergency_contact_name = db.Column(db.String(120), nullable=False)
    emergency_contact_relationship = db.Column(db.String(50), nullable=False)
    emergency_contact_phone = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Donor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    blood_type = db.Column(db.String(10), nullable=False)
    organs = db.Column(db.String(200), nullable=False)
    contact = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    hla = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()

# -----------------
# Sample Data for Dashboard
# -----------------
schemes = {
    "ayushman": {
        "name": "Ayushman Bharat",
        "cardNumber": "AB-2024-1234-5678",
        "coverage": "₹5,00,000",
        "utilized": "₹75,000",
        "validTill": "31 Dec 2025",
        "status": "Active"
    },
    "state": {
        "name": "State Health Insurance",
        "cardNumber": "SHI-2024-8765-4321",
        "coverage": "₹3,00,000",
        "utilized": "₹25,000",
        "validTill": "15 Mar 2025",
        "status": "Active"
    }
}

recent_claims = [
    {"date": "15 Jan 2024", "hospital": "Apollo Hospitals", "amount": "₹45,000", "status": "Approved"},
    {"date": "03 Dec 2023", "hospital": "Max Healthcare", "amount": "₹30,000", "status": "Approved"},
    {"date": "28 Nov 2023", "hospital": "Fortis Hospital", "amount": "₹25,000", "status": "Processing"}
]

upcoming_appointments = [
    {"date": "22 Feb 2024", "doctor": "Dr. Sharma", "type": "Follow-up", "time": "10:30 AM"},
    {"date": "28 Feb 2024", "doctor": "Dr. Patel", "type": "Regular Checkup", "time": "2:15 PM"}
]

# Load the trained life expectancy model
model = joblib.load("life_expectancy_model.pkl")

# -----------------
# Routes
# -----------------
# Authentication Routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        if User.query.filter_by(username=username).first():
            flash("Username already exists. Please choose a different one.")
            return redirect(url_for("register"))
        new_user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            if not user.profile:
                return redirect(url_for("medical_profile"))
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password.")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop("user_id", None)
    flash("Logged out successfully.")
    return redirect(url_for("login"))

# Predictor Routes
@app.route('/predictor', methods=['GET'])
def predictor():
    return render_template("predictor.html")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        age = float(request.form.get("Age"))
        height_cm = float(request.form.get("Height_cm"))
        weight_kg = float(request.form.get("Weight_kg"))
        bmi = weight_kg / ((height_cm / 100.0) ** 2)
        smoking = int(request.form.get("Smoking"))
        alcohol = int(request.form.get("Alcohol"))
        bp_sys = float(request.form.get("BP_Systolic"))
        bp_dia = float(request.form.get("BP_Diastolic"))
        pulse = float(request.form.get("Pulse"))
        exercise = int(request.form.get("Exercise"))
        water_intake = float(request.form.get("Water_Intake_L"))
        sleep = float(request.form.get("Sleep_Hours"))
        education = int(request.form.get("Education"))
        income = float(request.form.get("Income_INR"))
        hypertension = int(request.form.get("Hypertension"))
        diabetes = int(request.form.get("Diabetes"))
        thyroid = int(request.form.get("Thyroid"))
        mental_health = int(request.form.get("Mental_Health"))
        fatty_liver = int(request.form.get("Fatty_Liver"))

        input_data = pd.DataFrame([{
            'Age': age,
            'Height_cm': height_cm,
            'Weight_kg': weight_kg,
            'BMI': bmi,
            'Smoking': smoking,
            'Alcohol': alcohol,
            'BP_Systolic': bp_sys,
            'BP_Diastolic': bp_dia,
            'Pulse': pulse,
            'Exercise': exercise,
            'Water_Intake_L': water_intake,
            'Sleep_Hours': sleep,
            'Education': education,
            'Income_INR': income,
            'Hypertension': hypertension,
            'Diabetes': diabetes,
            'Thyroid': thyroid,
            'Mental_Health': mental_health,
            'Fatty_Liver': fatty_liver
        }])
        
        prediction = model.predict(input_data)[0]
        prediction = np.round(prediction, 1)
        return render_template("predictor.html", prediction_text=f"Predicted Life Expectancy: {prediction} years")
    except Exception as e:
        return render_template("predictor.html", prediction_text="Error: " + str(e))

# Community and Reviews Routes
@app.route('/community', methods=['GET'])
def community():
    community_reviews = [
        {
            'hospital': 'Apollo Hospitals',
            'cleanliness': 4,
            'doctor': 5,
            'staff': 4,
            'pricing': 3,
            'review': 'Excellent service and friendly staff.',
            'proof': 'static/images/proof1.jpg'
        },
        {
            'hospital': 'Max Healthcare',
            'cleanliness': 3,
            'doctor': 4,
            'staff': 3,
            'pricing': 4,
            'review': 'Good experience but a bit expensive.',
            'proof': 'static/images/proof2.jpg'
        },
        {
            'hospital': 'Fortis Hospital',
            'cleanliness': 5,
            'doctor': 5,
            'staff': 5,
            'pricing': 4,
            'review': 'Outstanding care and service.',
            'proof': 'static/images/proof3.jpg'
        },
        {
            'hospital': 'Columbia Asia',
            'cleanliness': 4,
            'doctor': 4,
            'staff': 4,
            'pricing': 3,
            'review': 'Decent facility with good treatment.',
            'proof': 'static/images/proof4.jpg'
        }
    ]
    return render_template("community.html", reviews=community_reviews)

@app.route('/add_review', methods=['POST'])
def add_review():
    hospital = request.form.get('hospital')
    cleanliness = request.form.get('cleanliness')
    doctor = request.form.get('doctor')
    staff = request.form.get('staff')
    pricing = request.form.get('pricing')
    review_text = request.form.get('review_text')
    proof = request.files.get('proof')
    return jsonify({'success': True, 'message': 'Review added successfully!'})

# Medical Profile Routes
@app.route('/medical_profile', methods=['GET', 'POST'])
def medical_profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    user = User.query.get(session["user_id"])
    profile = user.profile
    if request.method == 'POST':
        full_name = request.form.get("fullName")
        date_of_birth = request.form.get("dateOfBirth")
        blood_group = request.form.get("bloodGroup")
        allergies = request.form.get("allergies")
        existing_conditions = request.form.get("existingConditions")
        medications = request.form.get("medications")
        emergency_contact_name = request.form.get("emergencyContactName")
        emergency_contact_relationship = request.form.get("emergencyContactRelationship")
        emergency_contact_phone = request.form.get("emergencyContactPhone")
        if profile:
            profile.full_name = full_name
            profile.date_of_birth = date_of_birth
            profile.blood_group = blood_group
            profile.allergies = allergies
            profile.existing_conditions = existing_conditions
            profile.medications = medications
            profile.emergency_contact_name = emergency_contact_name
            profile.emergency_contact_relationship = emergency_contact_relationship
            profile.emergency_contact_phone = emergency_contact_phone
        else:
            profile = MedicalProfile(
                full_name=full_name,
                date_of_birth=date_of_birth,
                blood_group=blood_group,
                allergies=allergies,
                existing_conditions=existing_conditions,
                medications=medications,
                emergency_contact_name=emergency_contact_name,
                emergency_contact_relationship=emergency_contact_relationship,
                emergency_contact_phone=emergency_contact_phone,
                user_id=user.id
            )
            db.session.add(profile)
        db.session.commit()
        flash("Medical profile saved successfully!")
        return redirect(url_for("dashboard"))
    return render_template("medical_profile.html", profile=profile)

# Dashboard and Other Routes
@app.route('/')
def dashboard():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    user = User.query.get(session["user_id"])
    profile = user.profile
    return render_template('dashboard.html', schemes=schemes, recent_claims=recent_claims,
                           upcoming_appointments=upcoming_appointments, profile=profile)

@app.route('/verify_coverage', methods=['POST'])
def verify_coverage():
    time.sleep(1.5)
    return jsonify({
        "message": "Coverage Verified Successfully",
        "description": "Your insurance coverage is active and valid."
    })

@app.route('/submit_claim', methods=['POST'])
def submit_claim():
    hospital = request.form.get('hospital')
    amount = request.form.get('amount')
    date_of_service = request.form.get('date')
    new_claim = {"date": date_of_service, "hospital": hospital, "amount": amount, "status": "Processing"}
    recent_claims.insert(0, new_claim)
    return jsonify({
        "message": "Claim Submitted Successfully",
        "description": "Your claim has been received and is being processed."
    })

@app.route('/book_appointment', methods=['POST'])
def book_appointment():
    doctor = request.form.get('doctor')
    appointment_date = request.form.get('appointmentDate')
    appointment_time = request.form.get('appointmentTime')
    new_appointment = {
        "date": appointment_date,
        "doctor": doctor,
        "type": "New Appointment",
        "time": appointment_time
    }
    upcoming_appointments.append(new_appointment)
    return jsonify({
        "message": "Appointment Scheduled",
        "description": "Your appointment has been confirmed."
    })

@app.route('/update_profile', methods=['POST'])
def update_profile():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    return jsonify({
        "message": "Profile Updated",
        "description": "Your profile has been updated successfully."
    })

@app.route('/ayushman_data', methods=['GET'])
def ayushman_data():
    api_url = "https://api.example.com/ayushman"  # Replace with your real API endpoint
    params = {"cardNumber": schemes["ayushman"]["cardNumber"]}
    try:
        response = requests.get(api_url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        schemes["ayushman"].update({
            "coverage": data.get("coverage", schemes["ayushman"]["coverage"]),
            "utilized": data.get("utilized", schemes["ayushman"]["utilized"]),
            "validTill": data.get("validTill", schemes["ayushman"]["validTill"]),
            "status": data.get("status", schemes["ayushman"]["status"])
        })
        return jsonify(data)
    except requests.RequestException as e:
        return jsonify({"error": "Failed to fetch Ayushman data", "details": str(e)}), 500

@app.route('/ambulance_tracking')
def ambulance_tracking():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    return render_template('ambulance_tracking.html')

@app.route('/predictive_response')
def predictive_response():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    return render_template('predictive_response.html')


def book_ambulance():
    if not session.get("user_id"):
        return jsonify({'error': 'User not logged in'}), 401

    user = User.query.get(session["user_id"])
    if not user or not user.profile:
        return jsonify({'error': 'User profile not found'}), 400

    # Define hospitals (could be replaced with a database lookup)
    hospitals_dict = {
        "hospitalA": {"name": @app.route('/ambulance_booking', methods=['GET', 'POST'], endpoint='ambulance_booking')"Sapthagiri Hospital", "lat": 13.0709, "lng": 77.5027, "email": "krishkmalvia.cse@skit.org.in"},
        "hospitalB": {"name": "NRR Hospital", "lat": 13.07252, "lng": 77.50359, "email": "krishkmalvia.cse@skit.org.in"},
        "hospitalC": {"name": "Kruthika Hospital", "lat": 13.068696, "lng": 77.559915, "email": "krishkmalvia.cse@skit.org.in"}
    }
    
    if request.method == 'GET':
        # Convert dictionary to list for template
        hospitals = []
        for key, details in hospitals_dict.items():
            details['id'] = key
            hospitals.append(details)
        return render_template("ambulance_booking.html", hospitals=hospitals)

    # POST: Process booking request
    data = request.get_json()
    hospital_id = data.get("hospital_id")
    # Instead of receiving user location from the client,
    # we define a static user location here.
    static_user_location = {"lat": 12.9889, "lng": 77.5641}

    if not hospital_id:
        return jsonify({'error': 'Hospital selection is required'}), 400

    hospital = hospitals_dict.get(hospital_id)
    if not hospital:
        return jsonify({'error': 'Invalid hospital selection'}), 400

    # Build email with patient's medical profile
    profile = user.profile
    email_body = f"""
Patient Medical Profile:
-----------------------------
Name: {profile.full_name}
Date of Birth: {profile.date_of_birth}
Blood Group: {profile.blood_group}
Allergies: {profile.allergies}
Existing Conditions: {profile.existing_conditions}
Medications: {profile.medications}
Emergency Contact: {profile.emergency_contact_name} - {profile.emergency_contact_phone}
"""
    msg = Message(subject="Ambulance Booking – Patient Medical Profile",
                  recipients=[hospital["email"]],
                  body=email_body)
    try:
        mail.send(msg)
    except Exception as e:
        return jsonify({'error': 'Failed to send email', 'details': str(e)}), 500

    # Use the Google Routes Preferred API to calculate route details.
    import requests
    GOOGLE_ROUTES_API_KEY = os.getenv("GOOGLE_ROUTES_API_KEY")
    routes_url = f"https://routes.googleapis.com/directions/v2:computeRoutes?key={GOOGLE_ROUTES_API_KEY}"
    payload = {
        "origin": {
            "location": {
                "latLng": {
                    "latitude": hospital['lat'],
                    "longitude": hospital['lng']
                }
            }
        },
        "destination": {
            "location": {
                "latLng": {
                    "latitude": static_user_location.get("lat"),
                    "longitude": static_user_location.get("lng")
                }
            }
        },
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_AWARE",
        "computeAlternativeRoutes": False
    }
    routes_response = requests.post(routes_url, json=payload)
    if routes_response.status_code == 200:
        routes_data = routes_response.json()
        if routes_data.get("routes"):
            route = routes_data["routes"][0]
            if route.get("legs"):
                leg = route["legs"][0]
                eta = leg.get("duration", {}).get("text", "N/A")
                distance = leg.get("distance", {}).get("text", "N/A")
            else:
                eta = "N/A"
                distance = "N/A"
        else:
            eta = "N/A"
            distance = "N/A"
    else:
        eta = "N/A"
        distance = "N/A"

    return jsonify({
        'message': 'Ambulance booked and medical profile sent to hospital',
        'ETA': eta,
        'distance': distance
    })




@app.route('/chatbot')
def chatbot():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    return render_template('chatbot.html')

def detect_intent_texts(project_id, session_id, text, language_code='en'):
    session_client = dialogflow.SessionsClient()
    session_path = session_client.session_path(project_id, session_id)
    text_input = dialogflow.types.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)
    try:
        response = session_client.detect_intent(session=session_path, query_input=query_input)
        return response.query_result.fulfillment_text
    except Exception as e:
        print(f"Dialogflow API error: {e}")
        return "Sorry, I am having trouble understanding that."

@app.route('/dialogflow', methods=['POST'])
def dialogflow_webhook():
    data = request.get_json()
    user_input = data.get("query", "")
    if not user_input:
        return jsonify({"reply": "Please enter a valid message."})
    session_id = session.get("user_id", "anonymous")
    bot_response = detect_intent_texts(DIALOGFLOW_PROJECT_ID, session_id, user_input)
    return jsonify({"reply": bot_response})

@app.route('/api/donors', methods=['GET', 'POST'])
def donors_api():
    if request.method == 'POST':
        data = request.get_json()
        new_donor = Donor(
            name=data.get('name'),
            age=data.get('age'),
            blood_type=data.get('blood_type'),
            organs=data.get('organs'),
            contact=data.get('contact'),
            location=data.get('location'),
            hla=data.get('hla')
        )
        db.session.add(new_donor)
        db.session.commit()
        return jsonify({"message": "Donor registered successfully!"}), 201
    else:
        donors = Donor.query.all()
        donors_list = [{
            "name": donor.name,
            "age": donor.age,
            "blood_type": donor.blood_type,
            "organs": donor.organs,
            "contact": donor.contact,
            "location": donor.location,
            "hla": donor.hla
        } for donor in donors]
        return jsonify(donors_list)

@app.route('/api/search', methods=['GET'])
def search_donors():
    location_query = request.args.get('location', '')
    hla_query = request.args.get('hla', '')
    results = Donor.query.filter(
        Donor.location.ilike(f"%{location_query}%"),
        Donor.hla.ilike(f"%{hla_query}%")
    ).all()
    results_list = [{
        "name": donor.name,
        "age": donor.age,
        "blood_type": donor.blood_type,
        "organs": donor.organs,
        "contact": donor.contact,
        "location": donor.location,
        "hla": donor.hla
    } for donor in results]
    return jsonify(results_list)

@app.route('/organ_donor')
def organ_donor():
    return render_template("organ_donor.html")

# -----------------
# Run the Application
# -----------------
if __name__ == '__main__':
    app.run(debug=True)
