#!/usr/bin/env python3
"""Test if the service account file can be found."""

import os

print("Current working directory:", os.getcwd())
print("File exists:", os.path.exists('raptorflow-477017-d75059f2c50f.json'))

# Set the environment variable
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'raptorflow-477017-d75059f2c50f.json'
print("Environment variable set:", os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))

# Try to read first few characters of the file
try:
    with open('raptorflow-477017-d75059f2c50f.json', 'r') as f:
        content = f.read(100)
        print("File readable, starts with:", content[:50].replace('\n', '\\n'))
except Exception as e:
    print("Error reading file:", e)
