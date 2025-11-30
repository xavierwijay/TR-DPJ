#!/usr/bin/env python
"""
Run script for VLAN Management System
This is the entry point for the application
"""
import os
import sys
from pathlib import Path

# Add backend folder to Python path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

# Import and run app
from app import create_app, db

if __name__ == '__main__':
    # Get environment
    env = os.getenv('FLASK_ENV', 'development')
    
    # Create app
    app = create_app(env)
    
    # Initialize database
    with app.app_context():
        db.create_all()
        print("✅ Database initialized")
    
    # Print info
    print(f"""
    ╔══════════════════════════════════════════════════════╗
    ║     VLAN Management System Web Application          ║
    ║                                                      ║
    ║  Environment: {env:20}            ║
    ║  Debug Mode: {'Enabled' if app.debug else 'Disabled':20}           ║
    ║                                                      ║
    ║  Starting server at:                                ║
    ║  → http://localhost:5000                            ║
    ║                                                      ║
    ║  Press CTRL+C to stop                               ║
    ╚══════════════════════════════════════════════════════╝
    """)
    
    # Run app
    app.run(debug=app.debug, host='0.0.0.0', port=5000)
