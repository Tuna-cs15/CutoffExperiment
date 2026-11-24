# run_all.ps1 - chay lai toan bo thi nghiem tu dau (giu nguyen thu muc src)
Set-Location -LiteralPath $PSScriptRoot

function Fail($msg) { Write-Host "LOI: $msg" -ForegroundColor Red; exit 1 }
function Check($what) { if ($LASTEXITCODE -ne 0) { Fail $what } }
function Stamp($msg) { Write-Host ("[{0}] {1}" -f (Get-Date -Format HH:mm:ss), $msg) -ForegroundColor Cyan }

# 0. Kiem tra file nguon
$need = "src\MergesortHybrid.java","src\DataGenerator.java","src\BenchmarkRunner.java",
        "src\analyze.py","src\analyze_forks.py","src\analyze_groups.py"
foreach ($f in $need) { if (-not (Test-Path $f)) { Fail "thieu file $f (dang dung dung thu muc goc chua?)" } }
if (-not (Select-String -Path src\BenchmarkRunner.java -Pattern "300_000_000L" -SimpleMatch -Quiet)) {
    Fail "BenchmarkRunner.java chua co doan khoi dong 0,3 giay (300_000_000L)"
}

# 1. Xoa ket qua cu va tao lai thu muc
Stamp "Xoa out, data, results, logs"
foreach ($d in "out","data","results","logs") {
    if (Test-Path $d) { Remove-Item $d -Recurse -Force }
}
New-Item -ItemType Directory -Force out,data,results,logs | Out-Null

# 2. Ghi lai moi truong
Stamp "Ghi moi truong"
Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors,MaxClockSpeed,L2CacheSize,L3CacheSize | Out-File logs\environment.txt
Get-CimInstance Win32_ComputerSystem | Select-Object TotalPhysicalMemory | Out-File -Append logs\environment.txt
Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version | Out-File -Append logs\environment.txt
cmd /c "java -version 2>&1" | Out-File -Append logs\environment.txt

# 3. Bien dich va kiem thu
Stamp "Bien dich"
javac -encoding UTF-8 -d out src\MergesortHybrid.java src\DataGenerator.java src\BenchmarkRunner.java
Check "javac"
cmd /c "java -cp out MergesortHybrid > logs\selftest.log 2>&1"
if (-not (Select-String -Path logs\selftest.log -Pattern "self-test: OK" -SimpleMatch -Quiet)) { Fail "self-test khong OK" }
Stamp "self-test OK"

# 4. Sinh du lieu
java -cp out DataGenerator data | Out-Null
Check "DataGenerator"

# 5. Ba lan chay JVM doc lap (CUTOFF 0..30)
foreach ($i in 1,2,3) {
    Stamp "Chay fork $i (khoang 5 phut)"
    cmd /c "java -Xms512m -Xmx1g -XX:+UseSerialGC -cp out BenchmarkRunner results\raw_fork$i.csv 30 5 30 > logs\benchmark_fork$i.log 2>&1"
    Check "fork $i"
    $n = (Get-Content "results\raw_fork$i.csv").Count
    if ($n -ne 14881) { Fail "fork $i co $n dong (can 14881)" }
    Start-Sleep -Seconds 10
}

# 6. Khao sat mo rong CUTOFF 0..64
Stamp "Chay ext64 (khoang 10 phut)"
cmd /c "java -Xms512m -Xmx1g -XX:+UseSerialGC -cp out BenchmarkRunner results\ext64.csv 30 5 64 > logs\ext64.log 2>&1"
Check "ext64"
$n = (Get-Content results\ext64.csv).Count
if ($n -ne 31201) { Fail "ext64 co $n dong (can 31201)" }

# 7. Phan tich
Stamp "Phan tich thong ke"
Copy-Item results\raw_fork1.csv results\raw_benchmark.csv
py src\analyze.py results\raw_benchmark.csv results | Out-File logs\analyze_fork1.txt -Encoding utf8
Check "analyze.py"
py src\analyze_forks.py results | Out-File logs\analyze_forks.txt -Encoding utf8
Check "analyze_forks.py"
New-Item -ItemType Directory -Force results\ext64 | Out-Null
py src\analyze.py results\ext64.csv results\ext64 | Out-File logs\analyze_ext64.txt -Encoding utf8
Check "analyze.py ext64"
py src\analyze_groups.py results\ext64.csv results\ext64 | Out-File results\ext64\groups.txt -Encoding utf8
Check "analyze_groups.py"

Stamp "HOAN TAT. Xem thu muc results"