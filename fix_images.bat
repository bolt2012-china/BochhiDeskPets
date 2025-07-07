@echo off
setlocal enabledelayedexpansion

for %%f in (Bochhi/DeskPets/*.gif) do (
  echo Fixing %%f
  magick convert "%%f" -strip "fixed/%%~nxf"
)

echo All images processed. Fixed images are in 'fixed' folder.
pause