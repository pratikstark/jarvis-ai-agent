#!/usr/bin/env python3
"""
WSGI entry point for Jarvis AI Agent
This is the standard way to deploy Flask applications
"""

from app import app

if __name__ == "__main__":
    app.run() 