@echo off
chcp 65001 > NUL
title مركز الإنتاجية الذكي - تثبيت وتشغيل
echo ========================================================
echo        🚀 مركز الإنتاجية الذكي | Productivity Hub
echo ========================================================
echo.

IF EXIST "dist\ProductivityHub.exe" (
    echo [1/2] تشغيل التطبيق التجميعي المستقل (EXE)...
    start "" "dist\ProductivityHub.exe"
    goto END
)

echo [1/2] جاري فحص وتثبيت المكتبات اللازمة تلقائياً...
pip install -r requirements.txt

echo.
echo [2/2] جاري تشغيل التطبيق...
python main.py

:END
echo.
echo تم التشغيل بنجاح!
pause
