# PowerShell 脚本：测试本地 API
# 使用方法：在 backend 目录下运行 .\test_api.ps1

Write-Host "测试健康检查端点..." -ForegroundColor Green
$healthResponse = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET
Write-Host "健康检查结果：" -ForegroundColor Yellow
$healthResponse.Content
Write-Host ""

Write-Host "测试分析 API..." -ForegroundColor Green
$body = @{
    text = "今天天气真好，我出门了。但是突然下雨了，我很生气。然后我跑回家了，心情很沮丧。"
    mode = "drama_emotion"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/analyze" -Method POST -Body $body -ContentType "application/json"
    Write-Host "API 调用成功！" -ForegroundColor Green
    Write-Host "返回结果：" -ForegroundColor Yellow
    $response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
} catch {
    Write-Host "API 调用失败：" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "错误详情：" -ForegroundColor Red
        Write-Host $responseBody -ForegroundColor Red
    }
}

