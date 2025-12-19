@echo off
chcp 65001 >nul
echo 测试本地 API
echo.

echo [1/2] 测试健康检查端点...
curl.exe http://localhost:8000/health
echo.
echo.

echo [2/2] 测试分析 API...
curl.exe -X POST http://localhost:8000/api/analyze ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"今天天气真好，我出门了。但是突然下雨了，我很生气。然后我跑回家了。\",\"mode\":\"drama_emotion\"}"
echo.
echo.

pause

