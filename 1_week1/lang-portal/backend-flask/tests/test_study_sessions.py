import pytest
from datetime import datetime
import json

def test_create_study_session(client):
    # Test data
    study_session_data = {
        "group_id": 1,
        "study_activity_id": 1
    }
    
    response = client.post('/api/study-sessions', json=study_session_data)
    print(f"Response status: {response.status_code}")  # Debug print
    print(f"Response data: {response.data}")  # Debug print
    
    assert response.status_code == 201
    
    data = json.loads(response.data)
    assert 'id' in data
    assert data['group_id'] == study_session_data['group_id']
    assert 'group_name' in data
    assert 'activity_id' in data
    assert 'activity_name' in data
    assert 'start_time' in data
    assert 'end_time' in data
    assert 'review_items_count' in data
    assert data['review_items_count'] == 0

def test_create_study_session_missing_fields(client):
    # Missing required fields
    invalid_data = {
        "group_id": 1
        # missing study_activity_id
    }
    
    response = client.post('/api/study-sessions', json=invalid_data)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    assert "Missing required fields" in data["error"]

def test_review_study_session(client):
    # First create a study session
    study_session_data = {
        "group_id": 1,
        "study_activity_id": 1
    }
    create_response = client.post('/api/study-sessions', json=study_session_data)
    assert create_response.status_code == 201
    session_id = json.loads(create_response.data)['id']
    
    # Then submit a review
    review_data = {
        "word_id": 1,
        "correct": True
    }
    
    response = client.post(f'/api/study-sessions/{session_id}/review', json=review_data)
    assert response.status_code == 201
    
    data = json.loads(response.data)
    assert data['study_session_id'] == session_id
    assert data['word_id'] == review_data['word_id']
    assert data['correct'] == review_data['correct']

def test_review_study_session_invalid_session_id(client):
    review_data = {
        "word_id": 1,
        "correct": True
    }
    
    response = client.post('/api/study-sessions/99999/review', json=review_data)
    assert response.status_code == 404

def test_review_study_session_missing_fields(client):
    # First create a study session
    study_session_data = {
        "group_id": 1,
        "study_activity_id": 1
    }
    create_response = client.post('/api/study-sessions', json=study_session_data)
    session_id = json.loads(create_response.data)['id']
    
    # Test with missing fields
    invalid_review_data = {
        "word_id": 1
        # missing 'correct' field
    }
    
    response = client.post(f'/api/study-sessions/{session_id}/review', json=invalid_review_data)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data

@pytest.fixture
def client():
    from app import app
    app.config['TESTING'] = True
    app.config['DATABASE'] = ':memory:'  # Use in-memory SQLite database for testing
    
    with app.test_client() as client:
        # Set up test database tables
        with app.app_context():
            # Initialize database with schema
            cursor = app.db.cursor()
            
            # Drop existing tables first
            cursor.executescript('''
                DROP TABLE IF EXISTS word_review_items;
                DROP TABLE IF EXISTS study_sessions;
                DROP TABLE IF EXISTS groups;
                DROP TABLE IF EXISTS study_activities;
                
                CREATE TABLE IF NOT EXISTS groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS study_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS study_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL,
                    study_activity_id INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (group_id) REFERENCES groups (id),
                    FOREIGN KEY (study_activity_id) REFERENCES study_activities (id)
                );
                
                CREATE TABLE IF NOT EXISTS word_review_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    study_session_id INTEGER NOT NULL,
                    word_id INTEGER NOT NULL,
                    correct BOOLEAN NOT NULL,
                    FOREIGN KEY (study_session_id) REFERENCES study_sessions (id)
                );
                
                -- Insert test data
                INSERT INTO groups (name) VALUES ('Test Group');
                INSERT INTO study_activities (name) VALUES ('Test Activity');
            ''')
            app.db.commit()
            
        yield client
        
        # Clean up test database after tests
        with app.app_context():
            app.db.close() 