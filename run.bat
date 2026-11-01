call .\.venv\Scripts\activate.bat
python -m spacy download en_core_web_sm
uvicorn backend.app:app --reload
