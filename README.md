# flask_firestore_groq_app
Flask web application that connects to a Google Firestore database and uses the Groq AI API to summarize text fields in your database records. 

# Flask Firestore Groq Summarizer

A Flask web application that connects to Google Firestore, displays your database collections and documents, and uses Groq AI to generate concise summaries of text fields.

## Features

-  View Firestore collections and documents in a web dashboard
-  Summarize long text fields using Groq AI
-  Save AI-generated summaries back to Firestore
-  Bulk summarization for entire collections
-  Secure configuration using `.env` file

## Setup

**Prerequisites:**
- Python (version 3.8+ recommended)

### 1. Clone the repository
```
git clone <link>
```

### 2. Create and activate a virtual environment
```
python -m venv venv
```
On Windows:
```
venv\Scripts\activate
```
On macOS/Linux:
```
source venv/bin/activate
```

### 3. Install dependencies
```
pip install -r requirements.txt
```


### 4. Set up Firebase

- Go to [Firebase Console](https://console.firebase.google.com/), create a project, and enable Firestore.
- Download your service account JSON and place it in the project folder as `firebase-adminsdk.json`.

### 5. Set up Groq

- Get your API key from [Groq Console](https://console.groq.com/keys).

### 6. Create a `.env` file
```
GROQ_API_KEY=your_actual_groq_api_key_here
FIREBASE_PROJECT_ID=your_firebase_project_id
FLASK_ENV=development
FLASK_DEBUG=True
```
### 7. Run the app
```
python app.py
```


Then open [http://localhost:5000](http://localhost:5000) in your browser.

## Project Structure
```
.
├── firestore-flask-app/
│   ├── app.py                # Main Flask application file
│   ├── firebase-adminsdk.json # Firebase service account key (IMPORTANT: Keep this file secure and private)
│   ├── requirements.txt      # Python package dependencies
│   ├── templates/            # HTML templates for the web interface
│   │   ├── base.html         # Base template
│   │   ├── collection.html   # Template for viewing a collection
│   │   ├── document.html     # Template for viewing a single document
│   │   └── index.html        # Main dashboard template
│   ├── .env                  # Environment variables (IMPORTANT: Keep this file secure and private)
│   └── venv/                 # Python virtual environment (typically not committed)
└── README.md                 # This file
```
## Security Considerations
- **Sensitive Files:** The `firebase-adminsdk.json` file and the `.env` file contain sensitive credentials.
    - Ensure that these files are listed in your `.gitignore` file to prevent them from being accidentally committed to a public repository.
    - Never share these files publicly.
- **Flask Secret Key:** The `app.secret_key` in `app.py` is used to sign session cookies. For production environments, ensure this is a strong, random key and consider loading it from an environment variable rather than hardcoding it. (This is also mentioned in "Future Enhancements").

## Usage

- Browse your Firestore collections and documents.
- Click on a document to view details and generate AI summaries for text fields.
- Use "Bulk Summarize" to summarize all documents in a collection.

## Future Enhancements
- Enhanced error handling and user feedback mechanisms.
- Robust configuration management for different environments (e.g., development, staging, production).
- Implementation of input validation for all user-provided data.
- Utilization of asynchronous task queues (e.g., Celery, Flask-APScheduler) for long-running processes like bulk summarization to improve API responsiveness.
- Development of a comprehensive test suite, including unit and integration tests.
- Implementation of structured logging for better application monitoring and debugging.
- UI/UX improvements:
    - Allow users to dynamically configure which Firestore collections are displayed.
    - Enable users to select specific text fields for summarization via the UI.
    - Provide real-time progress indicators for bulk operations.
- Security: Move the hardcoded `app.secret_key` to an environment variable for better security.
- Code Structure: Refactor the Flask application to use Blueprints for better organization of routes and views as the application grows.
