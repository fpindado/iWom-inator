:: ==================================================
::               Compile new version
:: ==================================================
:: Usage: compile_new_version <version number>
::
:: It will compile and zip the windows version, and copy and zip the
:: linux files needed to the folder ..\..\releases, removing all the
:: temporary folders.
::
:: Using 7zip. Please update path as needed.
:: ==================================================

:: Create filenames
set zip="C:\Cloud\MEGA\Portable\7-Zip\7z"
set win_file=iWom-update_python_windows_v%1.zip
set lin_file=iWom-update_python_linux_v%1.zip

:: Compile windows, and create .zip file
pyinstaller iWom-update.spec
cd dist
%zip% a %win_file% iWom-update
move %win_file% ..\..\releases
rmdir /s /q iWom-update

:: Create .zip file for linux (no need to compile)
mkdir iWom-update
cd iWom-update
copy ..\..\iWom-update.py .
mkdir config
copy ..\..\templates\*.* config
cd ..
%zip% a %lin_file% iWom-update
move %lin_file% ..\..\releases

:: Remove temporary folders of compiler
cd ..
rmdir /s /q dist build __pycache__
