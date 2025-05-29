@echo off
set /p commit_message="Commit message: "
git add .
git commit -m "%commit_message%"
for /f "tokens=*" %%i in ('git rev-parse --abbrev-ref HEAD') do set CURRENT_BRANCH=%%i
git push origin %CURRENT_BRANCH%
