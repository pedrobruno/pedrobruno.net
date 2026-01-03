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
python generate.py -i posts -o ../site -p

echo [SUCCESS] Site generation complete.

:: Transfer files using FileZilla
echo [INFO] Transferring files to server...
set "FILEZILLA=C:\Program Files\FileZilla FTP Client\filezilla.exe"
set "LOCAL_SITE=%~dp0..\site"
set "SITE_NAME=pedrobruno.net - site"

if exist "%FILEZILLA%" (
    start "" "%FILEZILLA%" --site="0/%SITE_NAME%" --local="%LOCAL_SITE%"
    echo [INFO] FileZilla launched with site: %SITE_NAME%
) else (
    echo [ERROR] FileZilla not found at: %FILEZILLA%
)

call deactivate