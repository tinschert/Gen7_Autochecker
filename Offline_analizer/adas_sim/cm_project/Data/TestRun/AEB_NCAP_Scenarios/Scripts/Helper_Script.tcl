Log "Reading file [info script]"


proc MyStartProc {key name args} {

    # Initialize global variables
	global homedirectory
	global date
	global egoName
	global titleOfResultFolder
	
	switch $key { 
		TestSeries {Log "MyStartProc TestSeries: $name"
		
				# ----------------------------------------------------------------------------------------------------------
				# DIRECTORY OF LOG FILE ---------------------------------------------------------------------------
				# ----------------------------------------------------------------------------------------------------------
			
				# CREATE NECESSARY VARIABLES -------------------------------------------------------------------------------
				# Set homedirectory
				set homedirectory [pwd]
				#Log $homedirectory
			
				# Create Date
				set date_raw [GetTime -d]
				set date_list [split $date_raw "-"]
				set date [join $date_list ""]
				#Log "The date is: $date"
				
				# Ego Name
				set vehicle [IFileValue $homedirectory/Data/TestRun/EuroNCAP_Test_Automation/AEB_NCAP_TestPlan.ts Step.1.Vehicle]
				set temp_vehicle [split $vehicle "/"]
				set l [llength $temp_vehicle]
				set egoName [lindex $temp_vehicle $l-1]
				#Log "The vehicle name is: $egoName"
				
			
				# CREATE DIRECTORY OF RESULT FOLDER ------------------------------------------------------------------------
				# Title of result folder - "<Date>_NCAP_Test_testseries_VAR"
				set var 1
				set  dateNCAPList [list]
				lappend dateNCAPList $date
				lappend dateNCAPList NCAP_Test
				lappend dateNCAPList testseries
				lappend dateNCAPList $var
				set defaultNameResultFolder [join $dateNCAPList "_"]
				#Log $defaultNameResultFolder
				
				# Check for existence of result folder
				set existenceOfDirectory [file isdirectory $homedirectory/SimOutput/$egoName/$defaultNameResultFolder/]
				#Log $existenceOfDirectory
				
				# Rename result folder if necessary
				if {$existenceOfDirectory == 0} {
					set titleOfResultFolder $defaultNameResultFolder
				}
				if {$existenceOfDirectory == 1} {
				
					while {$var < 1000} {
					#Log $var
					set  dateNewNCAPList [list]
					lappend dateNewNCAPList $date
					lappend dateNewNCAPList NCAP_Test
					lappend dateNewNCAPList testseries
					lappend dateNewNCAPList $var
					set titleOfResultFolderNew [join $dateNewNCAPList "_"]
					#Log $titleOfResultFolderNew
					incr var
					
					set existenceOfNewDirectory [file isdirectory $homedirectory/SimOutput/$egoName/$titleOfResultFolderNew/]
					#Log $existenceOfNewDirectory
					
					if {$existenceOfNewDirectory != 1} {
						break
						}
					}
					
					set titleOfResultFolder $titleOfResultFolderNew
				
				}
				#Log "The title of the result folder is: $titleOfResultFolder"
			
				# Create result folder
				file mkdir $homedirectory/SimOutput/$egoName/$titleOfResultFolder
		
		} 
		Group {Log "MyStartProc Group: $name"
		
		
		
		} 
		TestRunGroup {Log "MyStartProc TestRunGroup: $name"
		
		
		
		}
		TestRun {
		
				# -------------------------------------------------------------------------------------------------------
				# CREATION OF LOG FILE-----------------------------------------------------------------------------------
				# -------------------------------------------------------------------------------------------------------
				
				# -------------------------------------------------------------------------------------------------------
				# DATA EXTRACTION----------------------------------------------------------------------------------------
				# -------------------------------------------------------------------------------------------------------
				
				# General information -----------------------------------------------------------------------------------
				
				# Time
				set time_raw [GetTime -t]
				set time_list [split $time_raw ":"]
				set time [join $time_list ""]
				#Log "The time is: $time"
				
		
				# EGO VEHICLE ---------------------------------------------------------------------------------------------
				
				# Vehicle Weight
				set vehicleMass [IFileValue Vehicle Body.mass]
				
				# Vehicle Length
				set egoData [IFileValue Vehicle Vehicle.OuterSkin]
				set egoLength [lindex $egoData 3]
				#Log $egoData
				
				# Vehicle Width
				set egoWidth_half [lindex $egoData 1]
				set egoWidth [expr $egoWidth_half*2]
				#Log $egoWidth
				
				# Vehicle Height
				set egoHeight [lindex $egoData 5]
				#Log $egoHeight
				
				# Vehicle Sensor Set
				set numberOfSensors [IFileValue Vehicle Sensor.Param.N]
	
				# Sensor Name
				set bufferSensorNameList [list]
				for {set index 0} {$index < $numberOfSensors} {incr index} {
					set sensorName [IFileValue Vehicle Sensor.Param.$index.Name]
					#Log $sensorName
					lappend bufferSensorNameList $sensorName
					#Log $bufferSensorNameList
				}
				set sensorNameList [join $bufferSensorNameList "-"]
				
				# Sensor Type
				set bufferSensorTypeList [list]
				for {set index 0} {$index < $numberOfSensors} {incr index} {
					set sensorType [IFileValue Vehicle Sensor.Param.$index.Type]
					lappend bufferSensorTypeList $sensorType
				}
				set sensorTypeList [join $bufferSensorTypeList "-"]
				
				# Sensor Field of View
				set bufferSensorFoVhList [list]
				set bufferSensorFoVvList [list]
				for {set index 0} {$index < $numberOfSensors} {incr index} {
					set FoVData [IFileValue Vehicle Sensor.Param.$index.FoV]
					set sensorFoVh [lindex $FoVData 0]
					if {$sensorFoVh==""} {
						lappend bufferSensorFoVhList "n"
					} elseif {$sensorFoVh!=""} {
						lappend bufferSensorFoVhList $sensorFoVh
					}
					set sensorFoVv [lindex $FoVData 1]
					if {$sensorFoVv==""} {
						lappend bufferSensorFoVvList "n"
					} elseif {$sensorFoVv!=""} {
						lappend bufferSensorFoVvList $sensorFoVv
					}
				}
				set sensorFoVhList [join $bufferSensorFoVhList "-"]
				set sensorFoVvList [join $bufferSensorFoVvList "-"]
				
				# Sensor Mounting Position
				set bufferSensorPosxList [list]
				set bufferSensorPosyList [list]
				set bufferSensorPoszList [list]
				for {set index 0} {$index < $numberOfSensors} {incr index} {
					set PosData [IFileValue Vehicle Sensor.$index.pos]
					set sensorPosx [lindex $PosData 0]
					set sensorPosy [lindex $PosData 1]
					set sensorPosz [lindex $PosData 2]
					lappend bufferSensorPosxList $sensorPosx
					lappend bufferSensorPosyList $sensorPosy
					lappend bufferSensorPoszList $sensorPosz
				}
				set sensorPosxList [join $bufferSensorPosxList "-"]
				set sensorPosyList [join $bufferSensorPosyList "-"]
				set sensorPoszList [join $bufferSensorPoszList "-"]
				
				
				# TRAFFIC -----------------------------------------------------------------------------------------------
				
				# Number of Traffic objects
				set numberOfTrafficObjects [IFileValue TestRun Traffic.N]
				
				# Traffic Name
				set bufferTrafficNameList [list]
				for {set index 0} {$index < $numberOfTrafficObjects} {incr index} {
					set trafficName [IFileValue TestRun Traffic.$index.Name]
					lappend bufferTrafficNameList $trafficName
				}
				set trafficNameList [join $bufferTrafficNameList "-"]
				
				# Traffic Type
				set bufferTrafficTypeList [list]
				for {set index 0} {$index < $numberOfTrafficObjects} {incr index} {
					set trafficTypeRaw [IFileValue TestRun Traffic.$index.ObjectClass]
					#Log $trafficTypeRaw
					set trafficTypeRawList [split $trafficTypeRaw " "]
					set trafficType [join $trafficTypeRawList "_"]
					#Log $trafficType
					lappend bufferTrafficTypeList $trafficType
				}
				set trafficTypeList [join $bufferTrafficTypeList "-"]
				
				# Traffic dimensions
				set bufferTrafficWList [list]
				set bufferTrafficLList [list]
				set bufferTrafficHList [list]
				for {set index 0} {$index < $numberOfTrafficObjects} {incr index} {
					set dimensionsData [IFileValue TestRun Traffic.$index.Basics.Dimension]
					set trafficWidth [lindex $dimensionsData 0]
					set trafficLength [lindex $dimensionsData 1]
					set trafficHeight [lindex $dimensionsData 2]
					lappend bufferTrafficWList $trafficWidth
					lappend bufferTrafficLList $trafficLength
					lappend bufferTrafficHList $trafficHeight
				}
				set trafficWList [join $bufferTrafficWList "-"]
				set trafficLList [join $bufferTrafficLList "-"]
				set trafficHList [join $bufferTrafficHList "-"]
				
				
				# SCENARIO -----------------------------------------------------------------------------------------------
				
				# Testrun Name
				set testrun_raw [SimInfo testrun]
				set testrun_list [split $testrun_raw "/"]
				set m [llength $testrun_list]
				set testrun_aeb [lindex $testrun_list $m-1]
				#Log "The TestRun used is: $testrun_aeb"
				set testrun_aeb_list [split $testrun_aeb "_"]
				#Log "$testrun_aeb_list"
				set n [llength $testrun_aeb_list]
				#Log "$n"
				set testrunname [lindex $testrun_aeb_list $n-1]
				#Log "The test runs name only is: $testrunname"

				# Ego Speed
				set existenceOfvEgo [NamedValue exists v_ego_kph]
				if {$existenceOfvEgo == 0} {
					set vEgo "not_applicable"
				}
				if {$existenceOfvEgo == 1} {
					set vEgo [NamedValue get v_ego_kph]
				}
				
				# Target Speed
				set existenceOfvTgt [NamedValue exists v_tgt_kph]
				if {$existenceOfvTgt == 0} {
					set vTgt "not_applicable"
				}
				if {$existenceOfvTgt == 1} {
					set vTgt [NamedValue get v_tgt_kph]
				}
				
				# Hitpoint
				set existenceOfHitpoint [NamedValue exists hitpoint]
				if {$existenceOfHitpoint == 0} {
					set hitpoint "not_applicable"
				}
				if {$existenceOfHitpoint == 1} {
					set hitpoint [NamedValue get hitpoint]
				}
				#Log $hitpoint
				
				# Gap
				set existenceOfGap [NamedValue exists gap]
				if {$existenceOfGap == 0} {
					set gap "not_applicable"
				}
				if {$existenceOfGap == 1} {
					set gap [NamedValue get gap]
				}
				
				# Target Deceleration Rate
				set existenceOfDecl [NamedValue exists decl_tgt]
				if {$existenceOfDecl == 0} {
					set decl_tgt "not_applicable"
				}
				if {$existenceOfDecl == 1} {
					set decl_tgt [NamedValue get decl_tgt]
				}
				
				# Category
				set category [IFileValue TestRun Traffic.0.ObjectClass]
				
				
				# ----------------------------------------------------------------------------------------------------------
				# NAME OF LOG FILE ---------------------------------------------------------------------------
				# ----------------------------------------------------------------------------------------------------------
				
				# Title of result file - "<Time>_<TestRunName>_<vEgo>kph"
				set vEgoList [list]
				lappend vEgoList vEgo
				lappend vEgoList $vEgo
				lappend vEgoList kph
				set vEgokph [join $vEgoList ""]
				set timeNamevEgoList [list]
				lappend timeNamevEgoList $time
				lappend timeNamevEgoList $testrunname
				lappend timeNamevEgoList $vEgokph
				set timeNamevEgo [join $timeNamevEgoList "_"]
				
				set titleOfResultFile $timeNamevEgo
				#Log $titleOfResultFile
		
				SetResultFName $homedirectory/SimOutput/$egoName/$titleOfResultFolder/$titleOfResultFile
				OpenSLog SimOutput/$egoName/$titleOfResultFolder/$titleOfResultFile.log
				
				
				# -----------------------------------------------------------------------------------------------------------
				# CONTENT OF SCRIPT FILE ------------------------------------------------------------------------------------
				# -----------------------------------------------------------------------------------------------------------

				# Date
				Log file "date: $date,"
				# Time
				Log file "time: $time,"
				Log file ""
				Log file ""
				
				# Ego
				Log file "name: $egoName,"
				Log file "height: $egoHeight,"
				Log file "length: $egoLength,"
				Log file "width: $egoWidth,"
				Log file "mass: $vehicleMass,"
				Log file "numberOfSensors: $numberOfSensors,"
				Log file "name: $sensorNameList,"
				Log file "type: $sensorTypeList,"
				Log file "FoVh: $sensorFoVhList,"
				Log file "FoVv: $sensorFoVvList,"
				Log file "Posx: $sensorPosxList,"
				Log file "Posy: $sensorPosyList,"
				Log file "Posz: $sensorPoszList,"
				Log file ""
				
				# Traffic
				Log file "numberOfTrafficObjects: $numberOfTrafficObjects,"
				Log file "name: $trafficNameList,"
				Log file "type: $trafficTypeList,"
				Log file "width: $trafficWList,"
				Log file "length: $trafficLList,"
				Log file "height: $trafficHList,"
				Log file ""


				# Scenario 
				Log file "name: $testrunname,"
				Log file "vEgoStart: $vEgo,"
				Log file "vTgtStart: $vTgt,"
				Log file "hitpoint: $hitpoint,"
				Log file "dist: $gap,"
				Log file "a: $decl_tgt,"
				Log file "category: $category"
				Log file " "
				
				
				
				#------------------------------------------------------------------------------------------------------------
				# CCCscp_start SPECIFIC CALCULATIONS
				#------------------------------------------------------------------------------------------------------------
				
				set dimensionsData [IFileValue TestRun Traffic.0.Basics.Dimension]
				set trafficWidth [lindex $dimensionsData 0]
				
				
				if {$testrunname == "CCCscp-Start"} {
					set startDistance [expr 210.95 - $egoLength - $trafficWidth*0.5 - 2.9]
					NamedValue set dsOff_ego $startDistance
				}
			
			
		}
		
    }
}






