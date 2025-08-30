"""
Quick Setup and Run Script
Run this script to setup and start the application
"""
import os
import sys
import subprocess
import time

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def run_command(command, description):
    print(f"\n➤ {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Failed")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Error: {e}")
        return False

def main():
    print_section("ContentAI Pro - Setup & Run Script")
    
    # Step 1: Install Python dependencies
    print_section("Step 1: Installing Python Dependencies")
    if not run_command("pip install -r backend/requirements.txt", "Installing Python packages"):
        print("\n⚠️  Please install dependencies manually: pip install -r backend/requirements.txt")
    
    # Step 2: Setup MySQL Database
    print_section("Step 2: Setting up MySQL Database")
    print("\n⚠️  Make sure MySQL is running with:")
    print("   - Username: root")
    print("   - Password: root")
    print("\nPress Enter to continue...")
    input()
    
    if run_command("python backend/database_setup.py", "Creating database and tables"):
        print("✅ Database setup complete!")
    else:
        print("\n⚠️  Please run manually: python backend/database_setup.py")
    
    # Step 3: Start Backend Server
    print_section("Step 3: Starting Backend Server")
    print("\n➤ Starting Flask backend server...")
    print("   The backend will run on: http://localhost:5000")
    print("\n⚠️  Keep this terminal open for the backend server")
    print("\nPress Ctrl+C to stop the server")
    
    # Instructions for frontend
    print_section("Step 4: Frontend Setup")
    print("\nTo access the frontend:")
    print("1. Open a new terminal/command prompt")
    print("2. Navigate to: frontend/")
    print("3. Open auth.html in your browser")
    print("   OR")
    print("   Use Live Server in VS Code")
    print("\n📌 Frontend URLs:")
    print("   - Login/Register: frontend/auth.html")
    print("   - Dashboard: frontend/index.html")
    print("   - History: frontend/pages/history.html")
    
    print_section("Starting Backend Server...")
    time.sleep(2)
    
    # Start the backend server
    os.chdir('backend')
    subprocess.run("python app.py", shell=True)

if __name__ == "__main__":
    main()