#!/usr/bin/env python
"""
Test script to verify MongoDB connection and Flask app setup
"""
import sys

def test_imports():
    """Test if all required packages are installed"""
    print("Testing imports...")
    try:
        import flask
        print("✓ Flask installed")
    except ImportError:
        print("✗ Flask not installed")
        return False
    
    try:
        from flask_pymongo import PyMongo
        print("✓ Flask-PyMongo installed")
    except ImportError:
        print("✗ Flask-PyMongo not installed")
        return False
    
    try:
        import pymongo
        print(f"✓ pymongo installed (version: {pymongo.__version__})")
    except ImportError:
        print("✗ pymongo not installed")
        return False
    
    try:
        from flask_cors import CORS
        print("✓ flask-cors installed")
    except ImportError:
        print("⚠ flask-cors not installed (optional, will use manual CORS headers)")
    
    return True

def test_mongodb_connection():
    """Test MongoDB connection"""
    print("\nTesting MongoDB connection...")
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            from app.extensions import mongo
            # Try to access the database
            db = mongo.db
            # List collections (this will trigger a connection)
            collections = db.list_collection_names()
            print(f"✓ MongoDB connected successfully")
            print(f"  Database: {db.name}")
            print(f"  Collections: {collections}")
            return True
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        return False

def test_flask_app():
    """Test Flask app creation"""
    print("\nTesting Flask app...")
    try:
        from app import create_app
        app = create_app()
        print("✓ Flask app created successfully")
        print(f"  Template folder: {app.template_folder}")
        print(f"  Registered blueprints: {[bp.name for bp in app.blueprints.values()]}")
        return True
    except Exception as e:
        print(f"✗ Flask app creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("GitHub Webhook Receiver - Connection Test")
    print("=" * 50)
    
    imports_ok = test_imports()
    if not imports_ok:
        print("\n⚠ Please install missing packages:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    
    app_ok = test_flask_app()
    if not app_ok:
        print("\n⚠ Flask app setup has issues. Please check the error above.")
        sys.exit(1)
    
    mongodb_ok = test_mongodb_connection()
    if not mongodb_ok:
        print("\n⚠ MongoDB connection failed. Please check:")
        print("  1. MongoDB Atlas cluster is running")
        print("  2. Your IP is whitelisted in MongoDB Atlas")
        print("  3. Connection string in app/__init__.py is correct")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✓ All tests passed! You can run the application with:")
    print("  python run.py")
    print("=" * 50)
