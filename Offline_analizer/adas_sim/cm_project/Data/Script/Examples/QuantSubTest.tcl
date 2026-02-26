QuantSubscribe {Time Car.v}
StartSim
WaitForStatus running
WaitForCondition {$Qu(Time) > 10}

if {$Qu(Car.v) < 10} {
	StopSim
} else {
	WaitForCondition {$Qu(Time) > 20}
	StopSim
}

Log "Speed = $Qu(Car.v) Time=$Qu(Time)"