@echo off
rem ── Local preview of the site ──────────────────────────────────────
rem recommendation.html loads data/*.json with fetch(), which browsers
rem block when a page is opened as a file://  — so the page looks empty.
rem This serves the folder over http://localhost:8000 instead, exactly
rem like GitHub Pages does. Close this window to stop the server.
cd /d "%~dp0"
echo.
echo   Homepage        : http://localhost:8000/
echo   Post-tour page  : http://localhost:8000/recommendation.html?type=freetour^&guide=quentin
echo   Book page       : http://localhost:8000/book/book-a-tour.html
echo.
echo   Close this window to stop the preview server.
echo.
start "" "http://localhost:8000/recommendation.html?type=freetour&guide=quentin"
python -m http.server 8000
