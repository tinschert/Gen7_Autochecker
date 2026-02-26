# ADAS HIL Release

PLATFORM PART

Subversion: 2.17.1 [Architecture].[Major release].[Minor release]
TDP
	ADAS HIL TDP Release: 2.0 https://sites.inside-share3.bosch.com/sites/104307/Documents/TDP/TDP_ADAS_HIL/TDP_ADAS_HIL.pdf

Deliverables
	ADAS HIL branch release/ADAS_HIL_Platform_2.17.1 https://sourcecode01.de.bosch.com/projects/PJXIL/repos/adas_hil/browse
	ADAS SIM branch release/ADAS_HIL_Platform_2.17.1 https://sourcecode01.de.bosch.com/projects/PJXIL/repos/adas_sim/browse
	Platform branch release/ADAS_HIL_Platform_2.17.1 https://sourcecode01.de.bosch.com/projects/PJXIL/repos/platform/browse
	Carmaker branch release/ADAS_HIL_Platform_2.17.1 https://sourcecode01.de.bosch.com/projects/PJXIL/repos/carmaker/browse
	ADAS HIL VT studio repo branch release/ADAS_HIL_Platform_2.17.1 https://sourcecode01.de.bosch.com/projects/PJPH/repos/test_vteststudio_multiecu_hil/browse
	Restbus repo branch release/ADAS_HIL_Platform_2.17.1 https://sourcecode01.de.bosch.com/projects/PJXIL/repos/od_rbs/browse
	Restbus Scripts repo branch release/ADAS_HIL_Platform_2.17.1 https://sourcecode01.de.bosch.com/projects/PJXIL/repos/rbs_scripts/browse

Released for the Tool Software
	Refer to the BOM yaml file \Release\SW_BoM_ADAS_HIL_PF.yml

Taken quality measures and status of the measures as defined in TDP: all PASSED
	Infrastructure and Precondition Tests: InfraTesting_CLASSE_report.html InfraTesting_CM_1D_report.html
	Runtime test:InfraTesting_CLASSE_report.html InfraTesting_CM_1D_report.html
	Perception and Sensor simulation: SystemIntegration_CM.html
	Performance Test (KPIs): Jenkins report https://rb-jmaas.de.bosch.com/ADAS_HIL_Platform_Integration/view/Platform/job/Platform_nightly/ \\abtvdfs2.de.bosch.com\ismdfs\iad\verification\ODS\ADAS_HIL_concept\Classe\Jenkins\NIGHTLY_REPORTS\Platform_Nightly\JB_1836_2025-03-11_HIL3
	Restbus KPIs: see link above Jenkins report
	System Integration test: SystemIntegration_CM.html
	Customer project BOM list : \Release\SW_BoM_ADAS_HIL_PF.yml


Changelog Platform:
2.17.1
- Classe/Carmaker: added Project_ID string in init.can and customer database to identify projects
- Classe/Carmaker: enabled the rear wheel steering input in classe database
- Classe/Carmaker: driver override feature added but disabled
- Carmaker: Road object adapted for possible driving/parking alternate modulation
- Carmaker: fix for 40 object injection file in corner radars as they were frozen
- Test: added target develop ford for platform test catalog
- Release: python virtual environment TDP checks implemented for automated deployment
- Release: BOM updates, fixes for deployment, test case execution and compilation fixes when integrating in Ford project

2.17
- Classe/Carmaker: added a script to modify canoe can.ini file to reduce the amount of RAM memory needed
- Classe/Carmaker: added a sysvar to deactivate the adas long/lat control, used for Platform test catalog with DUT load
- Classe/Carmaker: added support for rear corner RA6 SGU radars
- Carmaker: python tests supported with TDP measures
- Carmaker: communication change for radar objects from APO to a custom made UDP server encoded with byte array
- Carmaker: increased objects to 40 per radar
- Carmaker: TDP monitoring implemented for UDP server
- Carmaker: Driver in the loop g29 realistic driving improved
- Test: added Python online tests with and without Device under test
- Test: variant changed from Dasy to MPC3EVO phi OD variant
- Test: offline analyzer golden examples available using python
- Restbus: created a separate repo Rbs_Scripts for platform restbus common scripts
- Config: removed radar carmaker sysvars
- Config: added python panels, removed old panels, changed logging to mf4
- Release: virtual environment added in BOM and baselined in NT folder

---------------# ADAS_HIL #-----------------------------------------------------------------------------------------------------------

- ['ADASXIL-1678']	-> Feature/ADASXIL-1678  drv torque v2
- ['ADASXIL-1950']	-> ADASXIL-1950 update venv to 1.0.1
- Add dash to the BOM
- added raw strings
- ['SOSFORDDAT-183855']	-> Feature/SOSFORDDAT-183855 update venv in PF
- ['ADASXIL-1929']	-> Feature/ADASXIL-1929 adas hil python framework tdp v1
- Update BOM wiht python-can library
- ['ADASXIL-1930']	-> Feature/ADASXIL-1930 adas hil develop change main target to phi
- ['ADASXIL-1909']	-> ADASXIL-1909 moved gui_main.py to Rbs_Scripts submodule
- ['ADASXIL-1854', 'ADASXIL-1910']	-> Feature/ADASXIL-1854 adas hil apo round2
--------------------------------------------------------------------------------------------------------------------------------------

---------------# adas_sim #-----------------------------------------------------------------------------------------------------------

- ['ADASXIL-1929']	-> Feature/ADASXIL-1929 adas hil python framework tdp v1
- ['ADASXIL-1929']	-> Feature/ADASXIL-1929 adas hil python framework tdp v1
- ['ADASXIL-1870', 'ADASXIL-1854']	-> Feature/ADASXIL-1854 adas hil apo round2
--------------------------------------------------------------------------------------------------------------------------------------

---------------# Platform #-----------------------------------------------------------------------------------------------------------

- ['ADASXIL-1944', 'ADASXIL-1678']	-> Feature/ADASXIL-1678  drv torque v2
- Fix for mf4 file on remote locaiton
- Feature/UDP Error Reporting
- Add arg parser
- ['ADASXIL-1914']	-> Add Image Comparison VMB to Platform
- fixed sysvar naming in sensor panel for the SGU radars
- \Tools\venv\Scripts\python.exe raw string in py files
- ['ADASXIL-1851']	-> Feature/ADASXIL-1851 adas hil sw arch offline evaluation tool
- ['ADASXIL-1851']	-> Feature/ADASXIL-1851 adas hil sw arch offline evaluation tool
- ['SOSFORDDAT-183855']	-> Feature/SOSFORDDAT-183855 update venv in PF Platform repo
- ['ADASXIL-1929']	-> Feature/ADASXIL-1929 adas hil python framework tdp v1
- ['ADASXIL-1934']	-> Added new script for modification of CAN.ini
- ['ADASXIL-1938']	-> added new script for updating test results to rqm
- ['ADASXIL-1735']	-> Feature/ADASXIL-1735 jenkins OD System Integration from release2.16
- ['ADASXIL-1936']	-> Added 1objXloc documentation and adapted the ppt naming
- ['ADASXIL-1902']	-> Feature/ADASXIL-1902 python testcase execution in jenkins
- ['ADASXIL-1929']	-> Feature/ADASXIL-1929 adas hil python framework tdp v1
- Add python-can in requirements files
- ['ADASXIL-1931']	-> updated CM infra test (WIC test at lower speed)
- ['ADASXIL-1900']	-> updated release note autogen with Carmaker submodule
- ['ADASXIL-1909']	-> ADASXIL-1909 moved gui_main.py to Rbs_Scripts submodule, deleted Gui_main_Qt.py since not used
- ['ADASXIL-1854', 'ADASXIL-1910']	-> Feature/ADASXIL-1854 adas hil apo round2
- ['ADASXIL-1902']	-> added new function for parsing xml report files
--------------------------------------------------------------------------------------------------------------------------------------

---------------# Carmaker #-----------------------------------------------------------------------------------------------------------

- ['ADASXIL-1678']	-> Feature/ADASXIL-1678  drv torque v2
- Feature/UDP Error Reporting
- Feature/tCSysVar optimization
- Feature/udp error checking updates
- ['ADASXIL-1870', 'ADASXIL-1854', 'ADASXIL-1910']	-> Feature/ADASXIL-1854 adas hil apo round2
--------------------------------------------------------------------------------------------------------------------------------------