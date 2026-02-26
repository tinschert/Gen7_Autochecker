This is a tool that is doing the following:
1)cloning the git repository that is configured in settings.txt
be default it is : ssh://git@sourcecode01.de.bosch.com:7999/forddat3vv/fd3_drv_prk_adas_xil_tests.git
2)it is doing a sparse checkout of the branch that is configured in settings.txt. By default it is the develop branch.
3)The sparse checkout is done on folder cm_project only.
4)it is copying the content of the cloned and sparse-checked out cm_project folder into the folder of the RBS\adas_sim
The idea is that the RBS will support both adas_sim and customer project repository.

!!!IMPORTANT!!!
Use file : start_me - out_of_CANoe.bat if you want to run standalone without CANoe.
File start_me.bat is used only from CANoe. Do not use it standalone.