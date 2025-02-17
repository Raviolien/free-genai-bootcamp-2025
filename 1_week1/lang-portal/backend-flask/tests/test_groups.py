import pytest
import json

def test_get_group_words_raw(client):
    with client.application.app_context():
        # Test data setup
        cursor = client.application.db.cursor()
        cursor.executescript('''
            -- Insert test group
            INSERT INTO groups (name) VALUES ('Test Group');
            
            -- Insert test words
            INSERT INTO words (kanji, romaji, english, parts) 
            VALUES 
                ('犬', 'inu', 'dog', '["animal", "friend"]'),
                ('猫', 'neko', 'cat', '["animal", "pet"]');
                
            -- Link words to group
            INSERT INTO word_groups (group_id, word_id) 
            VALUES 
                (1, 1),
                (1, 2);
        ''')
        client.application.db.commit()

        # Test successful retrieval
        response = client.get('/groups/1/words/raw')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'group_id' in data
        assert 'group_name' in data
        assert 'words' in data
        
        assert data['group_id'] == 1
        assert data['group_name'] == 'Test Group'
        assert len(data['words']) == 2
        
        # Verify first word
        assert data['words'][0]['kanji'] == '犬'
        assert data['words'][0]['romaji'] == 'inu'
        assert data['words'][0]['english'] == 'dog'
        assert data['words'][0]['parts'] == ['animal', 'friend']
        
        # Verify second word
        assert data['words'][1]['kanji'] == '猫'
        assert data['words'][1]['romaji'] == 'neko'
        assert data['words'][1]['english'] == 'cat'
        assert data['words'][1]['parts'] == ['animal', 'pet']

def test_get_group_words_raw_nonexistent_group(client):
    with client.application.app_context():
        response = client.get('/groups/999/words/raw')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Group not found'

@pytest.fixture
def client():
    from app import app
    app.config['TESTING'] = True
    app.config['DATABASE'] = ':memory:'  # Use in-memory SQLite database for testing
    
    with app.test_client() as client:
        # Set up test database tables
        with app.app_context():
            cursor = app.db.cursor()
            
            # Drop existing tables first
            cursor.executescript('''
                DROP TABLE IF EXISTS word_groups;
                DROP TABLE IF EXISTS words;
                DROP TABLE IF EXISTS groups;
                
                CREATE TABLE IF NOT EXISTS groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    words_count INTEGER DEFAULT 0
                );
                
                CREATE TABLE IF NOT EXISTS words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kanji TEXT NOT NULL,
                    romaji TEXT NOT NULL,
                    english TEXT NOT NULL,
                    parts TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS word_groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL,
                    word_id INTEGER NOT NULL,
                    FOREIGN KEY (group_id) REFERENCES groups (id),
                    FOREIGN KEY (word_id) REFERENCES words (id)
                );
            ''')
            app.db.commit()
            
        yield client
        
        # Clean up test database after tests
        with app.app_context():
            app.db.close() 