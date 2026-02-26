Simulink.Bus.cellToObject({
{
    'cm31VCSteering', {
	{'Ang',			1, 'double', -1, 'real', 'Sample'};
	{'AngVel',		1, 'double', -1, 'real', 'Sample'};
	{'AngAcc',		1, 'double', -1, 'real', 'Sample'};
	{'Trq',			1, 'double', -1, 'real', 'Sample'};
    }
}
{
    'cm31VCRider', {
	{'RollAng',		1, 'double', -1, 'real', 'Sample'};
	{'RollAngVel',		1, 'double', -1, 'real', 'Sample'};
    }
}
{
    'cm31UserSignal', {
	{'s0',		1, 'double', -1, 'real', 'Sample'};
	{'s1',		1, 'double', -1, 'real', 'Sample'};
	{'s2',		1, 'double', -1, 'real', 'Sample'};
	{'s3',		1, 'double', -1, 'real', 'Sample'};
	{'s4',		1, 'double', -1, 'real', 'Sample'};
    }
}
{
    'cm31VCLights', {
	{'LowBeam',		1, 'double', -1, 'real', 'Sample'};
	{'HighBeam',		1, 'double', -1, 'real', 'Sample'};
	{'Daytime',		1, 'double', -1, 'real', 'Sample'};
	{'ParkL',		1, 'double', -1, 'real', 'Sample'};
	{'ParkR',		1, 'double', -1, 'real', 'Sample'};
	{'IndL',		1, 'double', -1, 'real', 'Sample'};
	{'IndR',		1, 'double', -1, 'real', 'Sample'};
	{'FogFrontL',		1, 'double', -1, 'real', 'Sample'};
	{'FogFrontR',		1, 'double', -1, 'real', 'Sample'};
	{'FogRear',		1, 'double', -1, 'real', 'Sample'};
	{'Brake',		1, 'double', -1, 'real', 'Sample'};
	{'Reverse',		1, 'double', -1, 'real', 'Sample'};
    }
}
{
    'cmVehicleControlIn', {
	{'SST',			1, 'double', -1, 'real', 'Sample'};
	{'Key',			1, 'double', -1, 'real', 'Sample'};
	{'UserSignal',		1, 'cm31UserSignal', -1, 'real', 'Sample'};
	{'GearNo',		1, 'double', -1, 'real', 'Sample'};
	{'SelectorCtrl',	1, 'double', -1, 'real', 'Sample'};
	{'Brake', 		1, 'double', -1, 'real', 'Sample'};
	{'BrakePark', 		1, 'double', -1, 'real', 'Sample'};
	{'BrakeLever', 		1, 'double', -1, 'real', 'Sample'};
	{'Clutch', 		1, 'double', -1, 'real', 'Sample'};
	{'Gas', 		1, 'double', -1, 'real', 'Sample'};
	{'Steering',		1, 'cm31VCSteering', -1, 'real', 'Sample'};
	{'Rider',		1, 'cm31VCRider', -1, 'real', 'Sample'};
	{'Lights',		1, 'cm31VCLights', -1, 'real', 'Sample'};
    }
}
{
    'cmVehicleControlOut', {
	{'SST',			1, 'double', -1, 'real', 'Sample'};
	{'Key',			1, 'double', -1, 'real', 'Sample'};
	{'UserSignal',		1, 'cm31UserSignal', -1, 'real', 'Sample'};
	{'GearNo',		1, 'double', -1, 'real', 'Sample'};
	{'SelectorCtrl',	1, 'double', -1, 'real', 'Sample'};
	{'Brake', 		1, 'double', -1, 'real', 'Sample'};
	{'BrakePark', 		1, 'double', -1, 'real', 'Sample'};
	{'BrakeLever', 		1, 'double', -1, 'real', 'Sample'};
	{'Clutch', 		1, 'double', -1, 'real', 'Sample'};
	{'Gas', 		1, 'double', -1, 'real', 'Sample'};
	{'Steering',		1, 'cm31VCSteering', -1, 'real', 'Sample'};
	{'Rider',		1, 'cm31VCRider', -1, 'real', 'Sample'};
	{'Lights',		1, 'cm31VCLights', -1, 'real', 'Sample'};
    }
}
});
