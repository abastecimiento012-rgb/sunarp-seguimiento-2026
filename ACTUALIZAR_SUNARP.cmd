@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
title SUNARP - Publicar datos centralizados
echo =======================================================
echo  SUNARP 2026 - ACTUALIZACION CENTRALIZADA DESDE EXCEL
echo =======================================================
echo.
where py >nul 2>&1
if errorlevel 1 (
  echo ERROR: No se encontro Python.
  echo Instala Python 3 desde https://www.python.org/downloads/
  echo y vuelve a ejecutar este archivo.
  goto :fin
)
py -3 -c "import openpyxl" >nul 2>&1
if errorlevel 1 (
  echo Preparando el lector de Excel...
  py -3 -m pip install --user openpyxl
  if errorlevel 1 (
    echo ERROR: No fue posible instalar openpyxl.
    goto :fin
  )
)
where gh >nul 2>&1
if errorlevel 1 (
  echo ERROR: Falta GitHub CLI.
  echo Instalalo desde https://cli.github.com/
  echo Despues vuelve a abrir este archivo.
  goto :fin
)
gh auth status >nul 2>&1
if errorlevel 1 (
  echo.
  echo Debes iniciar sesion en GitHub con tu propia cuenta.
  echo Tu clave nunca se guarda en el aplicativo publico.
  gh auth login
  if errorlevel 1 goto :fin
)
echo.
py -3 scripts\publicar_desde_excel.py
:fin
echo.
pause
endlocal
