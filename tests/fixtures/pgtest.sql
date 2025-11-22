-- Drop database if exists (for clean testing)
DROP DATABASE IF EXISTS testdb;
CREATE DATABASE testdb;

-- Connect to testdb
\c testdb

-- Create tables
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    comment_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE post_categories (
    post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
    PRIMARY KEY (post_id, category_id)
);

-- Insert sample data
INSERT INTO users (username, email) VALUES
    ('alice', 'alice@example.com'),
    ('bob', 'bob@example.com'),
    ('charlie', 'charlie@example.com'),
    ('diana', 'diana@example.com');

INSERT INTO categories (name, description) VALUES
    ('Technology', 'Posts about technology and software'),
    ('Science', 'Scientific discoveries and research'),
    ('News', 'Current events and news');

INSERT INTO posts (user_id, title, content, published) VALUES
    (1, 'First Post', 'This is my first post!', true),
    (1, 'Learning PostgreSQL', 'PostgreSQL is awesome', true),
    (2, 'Hello World', 'Just saying hello', true),
    (3, 'Database Backups', 'Why backups are important', false),
    (4, 'Testing 123', 'This is a test post', true);

INSERT INTO post_categories (post_id, category_id) VALUES
    (1, 1),
    (2, 1),
    (3, 3),
    (4, 1),
    (5, 2);

INSERT INTO comments (post_id, user_id, comment_text) VALUES
    (1, 2, 'Great post!'),
    (1, 3, 'Thanks for sharing'),
    (2, 4, 'Very helpful'),
    (3, 1, 'Totally agree'),
    (5, 2, 'Interesting perspective');

-- Create indexes
CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_comments_post_id ON comments(post_id);
CREATE INDEX idx_posts_published ON posts(published);

-- Create a view
CREATE VIEW published_posts AS
SELECT 
    p.id,
    p.title,
    u.username,
    p.created_at
FROM posts p
JOIN users u ON p.user_id = u.id
WHERE p.published = true;

-- Verify data
SELECT 'Users:' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'Posts:', COUNT(*) FROM posts
UNION ALL
SELECT 'Comments:', COUNT(*) FROM comments
UNION ALL
SELECT 'Categories:', COUNT(*) FROM categories;