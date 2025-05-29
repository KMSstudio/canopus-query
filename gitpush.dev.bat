@echo off
pip freeze > requirements.txt
for /f "tokens=*" %%i in ('git rev-parse --abbrev-ref HEAD') do set CURRENT_BRANCH=%%i
git push origin %CURRENT_BRANCH%
