from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv
from groq import Groq
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Initialize Firebase Admin SDK
cred = credentials.Certificate('firebase-adminsdk.json')
firebase_admin.initialize_app(cred, {
    'projectId': os.getenv('FIREBASE_PROJECT_ID'),
})

# Initialize Firestore client
db = firestore.client()

# Initialize Groq client
groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))

class FirestoreManager:
    """Handle Firestore database operations"""
    
    @staticmethod
    def get_all_documents(collection_name):
        """Retrieve all documents from a specified collection"""
        try:
            docs = db.collection(collection_name).get()
            documents = []
            for doc in docs:
                doc_data = doc.to_dict()
                doc_data['id'] = doc.id
                documents.append(doc_data)
            return documents
        except Exception as e:
            print(f"Error fetching documents: {e}")
            return []
    
    @staticmethod
    def get_document(collection_name, doc_id):
        """Retrieve a specific document"""
        try:
            doc_ref = db.collection(collection_name).document(doc_id)
            doc = doc_ref.get()
            if doc.exists:
                doc_data = doc.to_dict()
                doc_data['id'] = doc.id
                return doc_data
            return None
        except Exception as e:
            print(f"Error fetching document: {e}")
            return None
    
    @staticmethod
    def update_document(collection_name, doc_id, data):
        """Update a document with new data"""
        try:
            doc_ref = db.collection(collection_name).document(doc_id)
            doc_ref.update(data)
            return True
        except Exception as e:
            print(f"Error updating document: {e}")
            return False

class GroqSummarizer:
    """Handle Groq API operations for text summarization"""
    
    @staticmethod
    def summarize_text(text, max_sentences=3):
        """Summarize text using Groq API"""
        if not text or len(text.strip()) < 10:
            return "Text too short to summarize"
        
        try:
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a helpful assistant that summarizes text concisely in {max_sentences} sentences or less. Provide clear, informative summaries."
                    },
                    {
                        "role": "user",
                        "content": f"Please summarize the following text: {text}"
                    }
                ],
                model="llama3-8b-8192",
                temperature=0.3,
                max_tokens=200
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Error with Groq API: {e}")
            return f"Error generating summary: {str(e)}"
    
    @staticmethod
    def summarize_document_fields(document, fields_to_summarize):
        """Summarize specific fields in a document"""
        summaries = {}
        for field in fields_to_summarize:
            if field in document and isinstance(document[field], str):
                summary = GroqSummarizer.summarize_text(document[field])
                summaries[f"{field}_summary"] = summary
        return summaries

# Routes
@app.route('/')
def index():
    """Main dashboard showing available collections"""
    return render_template('index.html')

@app.route('/collections/<collection_name>')
def view_collection(collection_name):
    """Display all documents in a collection"""
    documents = FirestoreManager.get_all_documents(collection_name)
    return render_template('collection.html', 
                         documents=documents, 
                         collection_name=collection_name)

@app.route('/document/<collection_name>/<doc_id>')
def view_document(collection_name, doc_id):
    """Display a specific document with summarization options"""
    document = FirestoreManager.get_document(collection_name, doc_id)
    if not document:
        flash('Document not found', 'error')
        return redirect(url_for('index'))
    
    return render_template('document.html', 
                         document=document, 
                         collection_name=collection_name,
                         doc_id=doc_id)

@app.route('/summarize', methods=['POST'])
def summarize_fields():
    """API endpoint to summarize document fields"""
    data = request.get_json()
    collection_name = data.get('collection_name')
    doc_id = data.get('doc_id')
    fields_to_summarize = data.get('fields', [])
    
    document = FirestoreManager.get_document(collection_name, doc_id)
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    summaries = GroqSummarizer.summarize_document_fields(document, fields_to_summarize)
    
    # Optionally save summaries back to Firestore
    if summaries:
        FirestoreManager.update_document(collection_name, doc_id, summaries)
    
    return jsonify({
        'success': True,
        'summaries': summaries,
        'message': f'Generated {len(summaries)} summaries'
    })

@app.route('/bulk-summarize/<collection_name>')
def bulk_summarize(collection_name):
    """Summarize text fields for all documents in a collection"""
    documents = FirestoreManager.get_all_documents(collection_name)
    text_fields = ['description', 'content', 'notes', 'feedback', 'comment']
    
    summary_results = []
    
    for doc in documents:
        doc_summaries = {}
        for field in text_fields:
            if field in doc and isinstance(doc[field], str) and len(doc[field]) > 20:
                summary = GroqSummarizer.summarize_text(doc[field])
                doc_summaries[f"{field}_summary"] = summary
        
        if doc_summaries:
            # Update document in Firestore with summaries
            FirestoreManager.update_document(collection_name, doc['id'], doc_summaries)
            summary_results.append({
                'doc_id': doc['id'],
                'summaries_added': len(doc_summaries)
            })
    
    return jsonify({
        'success': True,
        'processed_documents': len(summary_results),
        'results': summary_results
    })

if __name__ == '__main__':
    app.run(debug=True)
