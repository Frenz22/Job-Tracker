import os
from datetime import datetime
from functools import wraps

from bson.errors import InvalidId
from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, url_for
from pymongo import MongoClient
from werkzeug.security import check_password_hash, generate_password_hash


load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["Job_Tracker"]

applications = db["applications"]
users = db["users"]

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


ALLOWED_STATUSES = [
    "Saved",
    "Applied",
    "Interview",
    "Final Interview",
    "Offer",
    "Rejected"
]


# Create unique indexes
users.create_index("username", unique=True)
users.create_index("email", unique=True)


# check if the user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated_function


# Get an application owned by the logged-in user
def get_application(application_id, user_id):
    try:
        object_id = ObjectId(application_id)
    except InvalidId:
        return None

    return applications.find_one({
        "_id": object_id,
        "user_id": user_id
    })


# Register route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username:
            flash("Username is required.", "error")
            return render_template("register.html")

        if not email:
            flash("Email is required.", "error")
            return render_template("register.html")

        if not password:
            flash("Password is required.", "error")
            return render_template("register.html")

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
            return render_template("register.html")

        if users.find_one({"username": username}):
            flash("Username is already taken.", "error")
            return render_template("register.html")

        if users.find_one({"email": email}):
            flash("Email is already taken.", "error")
            return render_template("register.html")

        password_hash = generate_password_hash(password)

        user_id = users.insert_one({
            "username": username,
            "email": email,
            "password_hash": password_hash
        }).inserted_id

        session["user_id"] = str(user_id)

        return redirect(url_for("home"))

    return render_template("register.html")


# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username_or_email = request.form.get(
            "username_or_email",
            ""
        ).strip()

        password = request.form.get("password", "")

        if not username_or_email or not password:
            flash(
                "Please enter both username/email and password.",
                "error"
            )
            return render_template("login.html")

        if len(password) < 8:
            flash(
                "Password must be at least 8 characters.",
                "error"
            )
            return render_template("login.html")

        user = users.find_one({
            "$or": [
                {"username": username_or_email},
                {"email": username_or_email.lower()}
            ]
        })

        if not user:
            flash(
                "Invalid username/email or password.",
                "error"
            )
            return render_template("login.html")

        if not check_password_hash(
            user["password_hash"],
            password
        ):
            flash(
                "Invalid username/email or password.",
                "error"
            )
            return render_template("login.html")

        session["user_id"] = str(user["_id"])

        return redirect(url_for("home"))

    return render_template("login.html")


# Logout route
@app.route("/logout")
def logout():
    session.clear()

    flash(
        "You have been logged out.",
        "info"
    )

    return redirect(url_for("login"))


# Test account login route
@app.route("/test-login")
def test_login():
    test_user = users.find_one({
        "username": "Test"
    })

    if test_user:
        session["user_id"] = str(test_user["_id"])
        return redirect(url_for("home"))

    flash(
        "Test account not found.",
        "error"
    )

    return redirect(url_for("login"))


# Home route
@app.route("/")
@login_required
def home():
    user_id = ObjectId(session["user_id"])

    user = users.find_one({
        "_id": user_id
    })

    applications_list = list(
        applications.find({
            "user_id": user_id
        }).sort(
            "updated_at",
            -1
        )
    )

    return render_template(
        "index.html",
        applications=applications_list,
        username=user["username"],
        user_email=user["email"]
    )


# Add Application route
@app.route("/applications", methods=["POST"])
@login_required
def add_application():
    user_id = ObjectId(session["user_id"])

    company = request.form.get(
        "company",
        ""
    ).strip()

    position = request.form.get(
        "position",
        ""
    ).strip()

    location = request.form.get(
        "location",
        ""
    ).strip()

    date_applied = request.form.get(
        "date_applied",
        ""
    )

    status = request.form.get(
        "status",
        "Saved"
    )

    notes = request.form.get(
        "notes",
        ""
    ).strip()

    if status not in ALLOWED_STATUSES:
        status = "Saved"

    if not company or not position:
        flash(
            "Company and position are required.",
            "error"
        )
        return redirect(url_for("home"))

    now = datetime.now()

    timeline = [{
        "event": "Application Created",
        "date": now.strftime("%Y-%m-%d %H:%M"),
        "notes": status
    }]

    applications.insert_one({
        "user_id": user_id,
        "company": company,
        "position": position,
        "location": location,
        "date_applied": date_applied,
        "status": status,
        "notes": notes,
        "timeline": timeline,
        "interviews": [],
        "updated_at": now
    })

    return redirect(url_for("home"))


# Update Application Status route
@app.route(
    "/applications/<application_id>/status",
    methods=["POST"]
)
@login_required
def update_application_status(application_id):
    user_id = ObjectId(session["user_id"])

    try:
        object_id = ObjectId(application_id)
    except InvalidId:
        return {
            "success": False,
            "message": "Invalid application ID."
        }, 400

    application = applications.find_one({
        "_id": object_id,
        "user_id": user_id
    })

    if not application:
        return {
            "success": False,
            "message": "Application not found."
        }, 404

    data = request.get_json(silent=True) or {}
    new_status = data.get("status", "")

    if new_status not in ALLOWED_STATUSES:
        return {
            "success": False,
            "message": "Invalid status."
        }, 400

    old_status = application.get("status")

    if old_status == new_status:
        return {
            "success": True
        }

    now = datetime.now()

    timeline_event = {
        "event": f"Status changed to {new_status}",
        "date": now.strftime("%Y-%m-%d %H:%M"),
        "notes": ""
    }

    applications.update_one(
        {
            "_id": object_id,
            "user_id": user_id
        },
        {
            "$set": {
                "status": new_status,
                "updated_at": now
            },
            "$push": {
                "timeline": timeline_event
            }
        }
    )

    return {
        "success": True
    }


# Edit Application route
@app.route(
    "/applications/<application_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_application(application_id):
    user_id = ObjectId(session["user_id"])

    user = users.find_one({
        "_id": user_id
    })

    application = get_application(
        application_id,
        user_id
    )

    if not application:
        try:
            ObjectId(application_id)
        except InvalidId:
            flash(
                "Invalid application ID.",
                "error"
            )
            return redirect(url_for("home"))

        flash(
            "Application not found or you don't have permission to access it.",
            "error"
        )
        return redirect(url_for("home"))

    if request.method == "POST":
        company = request.form.get(
            "company",
            ""
        ).strip()

        position = request.form.get(
            "position",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        date_applied = request.form.get(
            "date_applied",
            ""
        )

        status = request.form.get(
            "status",
            "Saved"
        )

        notes = request.form.get(
            "notes",
            ""
        ).strip()

        if status not in ALLOWED_STATUSES:
            status = "Saved"

        if not company or not position:
            flash(
                "Company and position are required.",
                "error"
            )

            return render_template(
                "edit.html",
                application=application,
                username=user["username"]
            )

        old_status = application.get("status")
        timeline = application.get("timeline", [])
        now = datetime.now()

        if old_status != status:
            timeline.append({
                "event": f"Status changed to {status}",
                "date": now.strftime("%Y-%m-%d %H:%M"),
                "notes": ""
            })

        applications.update_one(
            {
                "_id": application["_id"],
                "user_id": user_id
            },
            {
                "$set": {
                    "company": company,
                    "position": position,
                    "location": location,
                    "date_applied": date_applied,
                    "status": status,
                    "notes": notes,
                    "timeline": timeline,
                    "updated_at": now
                }
            }
        )

        return redirect(url_for("home"))

    return render_template(
        "edit.html",
        application=application,
        username=user["username"]
    )


# Delete Application route
@app.route(
    "/applications/<application_id>/delete",
    methods=["POST"]
)
@login_required
def delete_application(application_id):
    user_id = ObjectId(session["user_id"])

    try:
        object_id = ObjectId(application_id)
    except InvalidId:
        flash(
            "Invalid application ID.",
            "error"
        )
        return redirect(url_for("home"))

    result = applications.delete_one({
        "_id": object_id,
        "user_id": user_id
    })

    if result.deleted_count == 0:
        flash(
            "Application not found or you don't have permission to delete it.",
            "error"
        )

    return redirect(url_for("home"))


# Add Interview route
@app.route(
    "/applications/<application_id>/interviews",
    methods=["POST"]
)
@login_required
def add_interview(application_id):
    user_id = ObjectId(session["user_id"])

    application = get_application(
        application_id,
        user_id
    )

    if not application:
        try:
            ObjectId(application_id)
        except InvalidId:
            flash(
                "Invalid application ID.",
                "error"
            )
            return redirect(url_for("home"))

        flash(
            "Application not found.",
            "error"
        )
        return redirect(url_for("home"))

    interview_type = request.form.get(
        "interview_type",
        ""
    ).strip()

    interview_date = request.form.get(
        "interview_date",
        ""
    )

    interviewer = request.form.get(
        "interviewer",
        ""
    ).strip()

    interview_notes = request.form.get(
        "interview_notes",
        ""
    ).strip()

    if not interview_type or not interview_date:
        flash(
            "Interview type and date are required.",
            "error"
        )

        return redirect(
            url_for(
                "edit_application",
                application_id=application_id
            )
        )

    interviews = application.get(
        "interviews",
        []
    )

    interviews.append({
        "type": interview_type,
        "date": interview_date,
        "interviewer": interviewer,
        "notes": interview_notes
    })

    applications.update_one(
        {
            "_id": application["_id"],
            "user_id": user_id
        },
        {
            "$set": {
                "interviews": interviews,
                "updated_at": datetime.now()
            }
        }
    )

    return redirect(
        url_for(
            "edit_application",
            application_id=application_id
        )
    )


# Delete Interview route
@app.route(
    "/applications/<application_id>/interviews/<int:interview_index>/delete",
    methods=["POST"]
)
@login_required
def delete_interview(
    application_id,
    interview_index
):
    user_id = ObjectId(session["user_id"])

    application = get_application(
        application_id,
        user_id
    )

    if not application:
        try:
            ObjectId(application_id)
        except InvalidId:
            flash(
                "Invalid application ID.",
                "error"
            )
            return redirect(url_for("home"))

        flash(
            "Application not found.",
            "error"
        )

        return redirect(url_for("home"))

    interviews = application.get(
        "interviews",
        []
    )

    if (
        interview_index < 0
        or interview_index >= len(interviews)
    ):
        flash(
            "Invalid interview index.",
            "error"
        )

        return redirect(
            url_for(
                "edit_application",
                application_id=application_id
            )
        )

    interviews.pop(interview_index)

    applications.update_one(
        {
            "_id": application["_id"],
            "user_id": user_id
        },
        {
            "$set": {
                "interviews": interviews,
                "updated_at": datetime.now()
            }
        }
    )

    return redirect(
        url_for(
            "edit_application",
            application_id=application_id
        )
    )


# Format dates to MMM DD, YYYY format for display
@app.template_filter("format_date")
def format_date(value):
    if not value:
        return ""

    try:
        date = datetime.strptime(
            value,
            "%Y-%m-%d"
        )

        return date.strftime("%b") + f" {date.day}, {date.year}"

    except (ValueError, TypeError):
        return value


# Custom 404 page
@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)