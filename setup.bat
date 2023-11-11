@echo off

REM Create a virtual environment
python -m venv .venv

REM Activate the virtual environment
.venv\Scripts\activate

REM Install dependencies from requirements.txt
pip install -r requirements.txt

REM Provide instructions to the user
echo Setup complete. Activate the virtual environment with '.venv\Scripts\activate'