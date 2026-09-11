@echo off
chcp 65001 > nul
title انتاجيتي - تثبيت وتشغيل تلقائي

echo.
echo  ╔══════════════════════════════════════╗
echo  ║     انتاجيتي - مركز الإنتاجية       ║
echo  ╚══════════════════════════════════════╝
echo.
echo  [1/3] جاري التحقق من Python...

python --version >nul 2>&1
if errorlevel 1 (
    echo  [خطأ] Python غير مثبت! حمّله من: https://python.org
    echo  تأكد من تفعيل "Add to PATH" عند التثبيت.
    pause
    exit /b
)

echo  [2/3] جاري تثبيت المكتبات المطلوبة...
pip install -r requirements.txt --quiet

if errorlevel 1 (
    echo  [خطأ] فشل تثبيت المكتبات. تحقق من اتصال الإنترنت.
    pause
    exit /b
)

echo  [3/3] تشغيل التطبيق...
echo.
python main.py
