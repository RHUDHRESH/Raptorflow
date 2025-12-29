# Python Version Configuration
# Force Python 3.11 for compatibility

# Environment setup
export PYTHON_VERSION=3.11

# Virtual environment setup
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
