"""
MySQL Database Setup Script
Run this script to create the database and tables
"""
import pymysql
import hashlib
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'charset': 'utf8mb4'
}

def create_database():
    """Create the ContentAI database if it doesn't exist"""
    connection = None
    cursor = None
    
    try:
        # Connect to MySQL server
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS content_ai_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("✅ Database 'content_ai_db' created successfully!")
        
        # Use the database
        cursor.execute("USE content_ai_db")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL,
                is_active BOOLEAN DEFAULT TRUE,
                INDEX idx_email (email)
            )
        """)
        print("✅ Users table created successfully!")
        
        # Create content_history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                content_type VARCHAR(50) NOT NULL,
                prompt TEXT NOT NULL,
                generated_content TEXT NOT NULL,
                model_used VARCHAR(100) DEFAULT 'gpt2',
                parameters JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                is_deleted BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_created_at (created_at),
                INDEX idx_content_type (content_type)
            )
        """)
        print("✅ Content history table created successfully!")
        
        # Create sessions table for better session management
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                session_token VARCHAR(255) UNIQUE NOT NULL,
                ip_address VARCHAR(45),
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_session_token (session_token),
                INDEX idx_user_id (user_id)
            )
        """)
        print("✅ Sessions table created successfully!")
        
        # Create favorites table (optional feature)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                content_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (content_id) REFERENCES content_history(id) ON DELETE CASCADE,
                UNIQUE KEY unique_favorite (user_id, content_id)
            )
        """)
        print("✅ Favorites table created successfully!")
        
        # Commit the changes
        connection.commit()
        
        print("\n" + "="*50)
        print("🎉 Database setup completed successfully!")
        print("="*50)
        
        # Show table information
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("\n📊 Created tables:")
        for table in tables:
            print(f"  - {table[0]}")
            
    except pymysql.Error as e:
        print(f"❌ Error: {e}")
        if connection:
            connection.rollback()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def create_test_user():
    """Create a test user for development"""
    connection = None
    cursor = None
    
    try:
        connection = pymysql.connect(**DB_CONFIG, database='content_ai_db')
        cursor = connection.cursor()
        
        # Create a test user
        test_email = "test@example.com"
        test_password = hashlib.sha256("password123".encode()).hexdigest()
        test_name = "Test User"
        
        cursor.execute("""
            INSERT IGNORE INTO users (name, email, password_hash)
            VALUES (%s, %s, %s)
        """, (test_name, test_email, test_password))
        
        connection.commit()
        
        if cursor.rowcount > 0:
            print(f"\n✅ Test user created:")
            print(f"  Email: {test_email}")
            print(f"  Password: password123")
        else:
            print(f"\n ℹ️ Test user already exists")
            
    except pymysql.Error as e:
        print(f"❌ Error creating test user: {e}")
        if connection:
            connection.rollback()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == "__main__":
    print("🚀 Starting MySQL Database Setup...")
    print("="*50)
    create_database()
    create_test_user()
    print("\n✨ Setup complete! You can now run the application.")
