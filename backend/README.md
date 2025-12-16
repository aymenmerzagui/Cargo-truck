python3 -m venv venv
# activate your virtual environment
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# install dependencies
pip install -r requirements.txt

# run FastAPI
uvicorn main:app --reload
