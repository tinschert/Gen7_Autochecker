LoadTestRun "EuroNCAP_Test_Automation/Runs/AEB_CCCscp_Start"

QuantSubscribe {EgoVehicle.Length Traffic.0.Width}
set overall_distance 210.95
set startPosition [expr $overall_distance - $Qu(EgoVehicle.Length) - $Qu(Traffic.0.Width)*0.5 - 2.9]

NamedValue set dsOff_ego $startPosition

Log "EgoLaenge = $Qu(EgoVehicle.Length) Distanz = $overall_distance TrafficBreite = $Qu(Traffic.0.Width) DSoff = $startPosition"

StartSim
