@echo off
py "Z:\Soporte Alumbra\AlumbraLib\mantis.py"
SET src_folder=c:\temp\send
SET tar_folder="Z:\Soporte Alumbra\AlumbraLib"
for /f %%a IN ('dir "%src_folder%" /b') do move %src_folder%\%%a %tar_folder%