rem These variables are used by the doxygen configuration files Doxyfile_*
set OUTPUT_DIRECTORY_CAPL=//abtvdfs2.de.bosch.com/ismdfs/ilm/abt/DASy_Testing/Tooling/Tools_Documentation/Common_Lib/capl
set OUTPUT_DIRECTORY_CSHARP=//abtvdfs2.de.bosch.com/ismdfs/ilm/abt/DASy_Testing/Tooling/Tools_Documentation/Common_Lib/csharp

rem First remove the output directories, this is not done by doxygen
rmdir /S /Q "%OUTPUT_DIRECTORY_CAPL%"
rmdir /S /Q "%OUTPUT_DIRECTORY_CSHARP%"

rem Create the documentation
"C:\Program Files\doxygen\bin\doxygen.exe" Doxyfile_capl
"C:\Program Files\doxygen\bin\doxygen.exe" Doxyfile_csharp

rem Exit code for Jenkins
exit 0