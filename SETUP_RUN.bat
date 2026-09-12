@echo off
chcp 65001 > nul
title انتاجيتي - مركز الإنتاجية الذكي

echo.
echo  ╔═════════════════════════════════════════════════════╗
echo  ║       🚀 تطبيق انتاجيتي - مركز الإنتاجية الذكي      ║
echo  ╚═════════════════════════════════════════════════════╝
echo.

if exist "dist\انتاجيتي.exe" (
    echo  [✓] تشغيل الملف التنفيذي المباشر...
    start "" "dist\انتاجيتي.exe"
    exit /b
)

echo  [1/3] جاري التحقق من Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo  [خطأ] لم يتم العثور على Python أو ملف dist\انتاجيتي.exe!
    echo  يرجى تحميل Python من: https://python.org وتفعيل "Add to PATH".
    pause
    exit /b
)

echo  [2/3] جاري تثبيت المكتبات المطلوبة...
pip install -r requirements.txt --quiet

if errorlevel 1 (
    echo  [خطأ] فشل تثبيت المكتبات.
    pause
    exit /b
)

echo  [3/3] تشغيل التطبيق عبر Python...
echo.
python main.py
