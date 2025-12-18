@echo off
powershell -Command "$content = Get-Content 'c:\Users\hp\OneDrive\Desktop\Raptorflow\src\pages\app\MuseChatPage.jsx' -Raw; $content -replace '                  \)}\)', '                  ))' | Set-Content 'c:\Users\hp\OneDrive\Desktop\Raptorflow\src\pages\app\MuseChatPage.jsx'"
