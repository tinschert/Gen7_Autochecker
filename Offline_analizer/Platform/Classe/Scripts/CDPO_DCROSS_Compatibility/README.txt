Prior Manual Config should be:
* CDPO passive addresses: 192.168.0.21 and 192.168.2.21
OR 
* DCROSS passive addresses: 192.168.0.23 and 192.168.2.23

command to create .exe :
python -m PyInstaller  --onefile --icon=classe.ico --add-data "classe.ico;." --add-data "CDPO.png;." --add-data "DCROSS.png;." script_switch.py
without debug console :
python -m PyInstaller --onefile --windowed --icon=classe.ico --add-data "classe.ico;." --add-data "CDPO.png;." --add-data "DCROSS.png;." script_switch.py
python -m PyInstaller --noconsole --onefile --windowed --icon=classe.ico --add-data "classe.ico;." --add-data "CDPO.png;." --add-data "DCROSS.png;." script_switch.py