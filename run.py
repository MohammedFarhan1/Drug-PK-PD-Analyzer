#!/usr/bin/env python3
"""
Drug PK/PD Analyzer - Modern Launcher
Advanced pharmacokinetic and pharmacodynamic analysis platform
"""

import os
import sys
import webbrowser
from threading import Timer
from dotenv import load_dotenv
from app import app

def setup_environment():
    """Setup environment and check requirements"""
    load_dotenv()
    
    # Check API key
    if not os.getenv('GROQ_API_KEY'):
        print("❌ GROQ_API_KEY not found!")
        print("📝 Please add your Groq API key to .env file")
        
        if not os.path.exists('.env'):
            if os.path.exists('.env.example'):
                import shutil
                try:
                    shutil.copy('.env.example', '.env')
                    print("✅ Created .env file from template")
                    print("🔑 Add your Groq API key and restart")
                except Exception as e:
                    print(f"❌ Failed to create .env: {e}")
            else:
                print("❌ No .env.example found")
        return False
    return True

def open_browser():
    """Open browser after delay"""
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = os.getenv('FLASK_PORT', '5000')
    url = f"http://{host}:{port}"
    webbrowser.open(url)

def main():
    print("🧬 Drug PK/PD Analyzer v2.0")
    print("=" * 50)
    
    if not setup_environment():
        return 1
    
    try:
        
        print("✅ Environment configured")
        print("🚀 Starting server...")
        
        host = os.getenv('FLASK_HOST', '127.0.0.1')
        port = int(os.getenv('FLASK_PORT', 5000))
        debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        
        print(f"🌐 Server: http://{host}:{port}")
        print("⏹️  Press Ctrl+C to stop")
        print("=" * 50)
        
        # Open browser after 2 seconds
        Timer(2.0, open_browser).start()
        
        app.run(debug=debug, host=host, port=port, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("📦 Run: pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

# For gunicorn deployment
__all__ = ['app']
