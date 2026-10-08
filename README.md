# Frenz Job Tracker

Frenz Job Tracker is a web-based job application tracking system built with Flask and MongoDB.

It helps users keep track of their job applications, organize them by application status, and manage important details such as company, position, location, application date, notes, and interviews.

## Features

* User registration and login
* Login using username or email
* Password hashing
* Test account login
* Add job applications
* Edit job applications
* Delete job applications
* Update application status
* Drag and drop applications between status columns
* Search applications
* Manage visible Kanban columns
* Track application dates
* Manage interview information
* Application timeline
* Flash messages for errors and notifications
* Custom 404 page
* Responsive dashboard

## Application Statuses

Applications can be organized into six statuses:

* Saved
* Applied
* Interview
* Final Interview
* Offer
* Rejected

## Technologies Used

* Python
* Flask
* MongoDB
* PyMongo
* HTML
* CSS
* JavaScript
* Jinja2
* python-dotenv
* Werkzeug
* Gunicorn

## Project Structure

```text
Job Tracker/
├── static/
│   └── style.css
├── template/
│   ├── 404.html
│   ├── edit.html
│   ├── index.html
│   ├── login.html
│   └── register.html
├── venv/
├── .env
├── requirements.txt
├── app.py
└── README.md
```

## Requirements

Before running the project, make sure you have:

* Python 3.x
* MongoDB
* pip

## Installation

### 1. Clone the Repository

Clone the project and open the project folder:

```bash
git clone <your-repository-url>
cd "Job Tracker"
```

### 2. Create a Virtual Environment

For Windows:

```bash
python -m venv venv
```

Activate the virtual environment:

```bash
venv\Scripts\activate
```

For macOS/Linux:

```bash
python3 -m venv venv
```

Activate the virtual environment:

```bash
source venv/bin/activate
```

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root.

```env
MONGO_URI=mongodb://localhost:27017/
SECRET_KEY=your-secret-key
```

### MongoDB

The application uses the following MongoDB database:

```text
Job_Tracker
```

The application uses these collections:

```text
users
applications
```

Make sure MongoDB is running before starting the application.

## Running the Application

Start the Flask application with:

```bash
python app.py
```

The application will normally be available at:

```text
http://127.0.0.1:5000
```

Open the address in your web browser.

## User Authentication

Users can create an account through the registration page.

The application allows users to log in using either:

* Username
* Email address

Passwords are hashed using Werkzeug before they are stored in the database.

The application also provides a logout function that clears the current session.

## Test Account

The login and registration pages include an option to access a test account.

The test account must exist in the MongoDB `users` collection with the username:

```text
Test
```

The application uses this account to provide quick access without requiring the user to enter login credentials.

## Job Applications

Each job application can contain:

* Company
* Position
* Location
* Date Applied
* Status
* Notes
* Timeline
* Interviews

Applications are displayed on the dashboard using a Kanban-style layout.

## Kanban Board

The dashboard organizes applications into columns based on their current status.

The columns are:

```text
Saved
Applied
Interview
Final Interview
Offer
Rejected
```

Applications can be moved between columns using drag and drop.

The application status can also be changed through the application card menu.

When an application's status changes, the change is recorded in its timeline.

## Search

The dashboard includes a search field for finding applications.

Search can be used to find applications based on information displayed on the application cards, such as:

* Company
* Position
* Location

## Manage Columns

The **Manage Columns** feature allows users to hide or show Kanban status columns.

The selected column settings are stored in the browser using `localStorage`.

This allows the dashboard to remember which columns the user has chosen to display.

## Editing Applications

Applications can be edited from the application card.

The Edit Application page allows users to update:

* Company
* Position
* Location
* Date Applied
* Status
* Notes

The page also displays existing interview information associated with the application.

Applications can be deleted from the Edit Application page.

## Interviews

Applications can contain interview information, including:

* Interview type
* Interview date
* Interviewer
* Interview notes

Existing interviews can be deleted from the Edit Application page.

## Application Timeline

The application keeps a timeline of important changes.

For example, when an application is created, an initial timeline event is recorded.

When the application's status changes, another timeline event is added.

This allows the application history to be tracked over time.

## Database

MongoDB is used to store user and application data.

The main collections are:

### `users`

Stores user account information such as:

* Username
* Email
* Password hash

### `applications`

Stores job application information such as:

* User ID
* Company
* Position
* Location
* Application date
* Status
* Notes
* Timeline
* Interviews
* Last updated time

## Security

Passwords are not stored as plain text. They are hashed using Werkzeug's password hashing functions.

The application also uses user IDs to make sure users can only access their own job applications.

For local development, sensitive configuration values are stored in the `.env` file.

Do not commit your `.env` file to a public repository.

A `.gitignore` file should include:

```text
.env
venv/
__pycache__/
*.pyc
```

For deployment, use a strong `SECRET_KEY` and a secure MongoDB connection string.

## Error Handling

The application includes a custom 404 page for pages that do not exist.

The application also handles invalid application IDs and attempts to access applications that do not belong to the current user.

## Deployment

The project includes Gunicorn in `requirements.txt` for production deployment.

Gunicorn can be used to run the Flask application with:

```bash
gunicorn app:app
```

The exact deployment configuration depends on the hosting platform being used.

Before deploying, make sure the following are configured:

* MongoDB connection
* `MONGO_URI`
* `SECRET_KEY`
* Production environment variables
* Gunicorn
* Application start command

## Development

To run the application locally:

```bash
python app.py
```

The application currently runs with Flask's development server.

For production deployment, use a production WSGI server such as Gunicorn instead of Flask's development server.

## Future Improvements

Possible future improvements include:

* Application statistics and analytics
* More advanced filtering and sorting
* Resume and cover letter management
* Interview scheduling
* Email reminders
* Exporting application data
* Improved account management
* Additional application tracking features

## License

This project is for educational and personal use.
