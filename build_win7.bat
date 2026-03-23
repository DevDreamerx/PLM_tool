@echo off
setlocal ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION
chcp 65001 >nul

cd /d "%~dp0"

echo [1/7] 检查 Python 3.8 ...
where py >nul 2>nul
if errorlevel 1 (
    echo 未找到 py 启动器。请先安装 Python 3.8.x for Windows。
    exit /b 1
)

py -3.8 -V >nul 2>nul
if errorlevel 1 (
    echo 未检测到 Python 3.8.x。
    echo 要生成适用于 Win7 的包，建议使用 Python 3.8.x 打包。
    exit /b 1
)

set "VENV_DIR=.venv-win7-build"
set "DIST_DIR=dist"
set "BUILD_DIR=build"
set "APP_NAME=技术状态管理助手"

echo [2/7] 创建打包虚拟环境 ...
if not exist "%VENV_DIR%\Scripts\python.exe" (
    py -3.8 -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo 创建虚拟环境失败。
        exit /b 1
    )
)

call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo 激活虚拟环境失败。
    exit /b 1
)

echo [3/7] 升级基础工具 ...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo 基础工具安装失败。
    exit /b 1
)

echo [4/7] 安装 Win7 打包依赖 ...
python -m pip install -r requirements-win7.txt
if errorlevel 1 (
    echo 依赖安装失败。
    exit /b 1
)

echo [5/7] 清理旧打包产物 ...
if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%"
if exist "__pycache__" rmdir /s /q "__pycache__"

echo [6/7] 执行 PyInstaller 打包 ...
python -m PyInstaller --clean --noconfirm main.spec
if errorlevel 1 (
    echo 打包失败。
    exit /b 1
)

echo [7/7] 打包完成
echo 输出文件: %CD%\dist\%APP_NAME%.exe
echo.
echo 说明:
echo 1. 该脚本按 Python 3.8.x 打包，以尽量兼容 Win7。
echo 2. 如需在 Win7 使用，请在一台干净的 Win7 机器上做一次实际启动验证。
echo 3. 若 Win7 缺少运行库，请安装 VC++ Runtime 后再测试。
pause
