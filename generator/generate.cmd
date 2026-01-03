@echo off
setlocal

:: Check if virtual environment exists, if not create it
if not exist venv (
    echo [INFO] Creating virtual environment...
    python -m venv venv
)

:: Activate the virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate

:: Install requirements
echo [INFO] Installing/Updating dependencies...
pip install -q -r requirements.txt

:: Run the site generator with asset compression
echo [INFO] Generating and publishing site...
python generate.py -i posts -o ../site

echo [SUCCESS] Site generation complete.
call deactivate