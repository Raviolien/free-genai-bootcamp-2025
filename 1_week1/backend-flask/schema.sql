DROP TABLE IF EXISTS study_sessions;
DROP TABLE IF EXISTS word_review_items;
DROP TABLE IF EXISTS groups;
DROP TABLE IF EXISTS study_activities;
DROP TABLE IF EXISTS words;

CREATE TABLE groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE study_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kanji TEXT NOT NULL,
    romaji TEXT NOT NULL,
    english TEXT NOT NULL
);

CREATE TABLE study_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    study_activity_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (group_id) REFERENCES groups (id),
    FOREIGN KEY (study_activity_id) REFERENCES study_activities (id)
);

CREATE TABLE word_review_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    study_session_id INTEGER NOT NULL,
    correct BOOLEAN NOT NULL,
    FOREIGN KEY (word_id) REFERENCES words (id),
    FOREIGN KEY (study_session_id) REFERENCES study_sessions (id)
);

-- Insert test data
INSERT INTO groups (id, name) VALUES (1, 'Test Group');
INSERT INTO study_activities (id, name) VALUES (1, 'Test Activity');
INSERT INTO words (id, kanji, romaji, english) VALUES (1, '漢字', 'kanji', 'Chinese characters'); 