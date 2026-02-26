if strcmp(vehicle, 'Car')
    Simulink.Bus.cellToObject({
    {
	'cm6Wheels', {
	    {'FL',	1,'double', -1, 'real', 'Sample'};
	    {'FR',	1,'double', -1, 'real', 'Sample'};
	    {'RL',	1,'double', -1, 'real', 'Sample'};
	    {'RR',	1,'double', -1, 'real', 'Sample'};
	}
    }
    {
	'cm6WheelsTrq_stat', {
	    {'FL',	1,'cm6Map', -1, 'real', 'Sample'};
	    {'FR',	1,'cm6Map', -1, 'real', 'Sample'};
	    {'RL',	1,'cm6Map', -1, 'real', 'Sample'};
	    {'RR',	1,'cm6Map', -1, 'real', 'Sample'};
	}
    }
    });
elseif strcmp(vehicle, 'Truck')
    Simulink.Bus.cellToObject({
    {
	'cm6Wheels', {
	    {'FL',	1,'double', -1, 'real', 'Sample'};
	    {'FR',	1,'double', -1, 'real', 'Sample'};
	    {'RL',	1,'double', -1, 'real', 'Sample'};
	    {'RR',	1,'double', -1, 'real', 'Sample'};
	    {'RL2',	1,'double', -1, 'real', 'Sample'};
	    {'RR2',	1,'double', -1, 'real', 'Sample'};
	    {'FL2',	1,'double', -1, 'real', 'Sample'};
	    {'FR2',	1,'double', -1, 'real', 'Sample'};
	}
    }
    {
	'cm6WheelsTrq_stat', {
	    {'FL',	1,'cm6Map', -1, 'real', 'Sample'};
	    {'FR',	1,'cm6Map', -1, 'real', 'Sample'};
	    {'RL',	1,'cm6Map', -1, 'real', 'Sample'};
	    {'RR',	1,'cm6Map', -1, 'real', 'Sample'};
	    {'RL2',	1,'cm6Map', -1, 'real', 'Sample'};
	    {'RR2',	1,'cm6Map', -1, 'real', 'Sample'};
	    {'FL2',	1,'cm6Map', -1, 'real', 'Sample'};
	    {'FR2',	1,'cm6Map', -1, 'real', 'Sample'};
	}
    }
    });
end
Simulink.Bus.cellToObject({
% Input Bus
{
    'cm6ValveInArray', {
       	{'FL_Inlet',	1,'double', -1, 'real', 'Sample'};
       	{'FR_Inlet',	1,'double', -1, 'real', 'Sample'};
       	{'RL_Inlet',	1,'double', -1, 'real', 'Sample'};
       	{'RR_Inlet',	1,'double', -1, 'real', 'Sample'};
       	{'FL_Outlet',	1,'double', -1, 'real', 'Sample'};
       	{'FR_Outlet',	1,'double', -1, 'real', 'Sample'};
	{'RL_Outlet',	1,'double', -1, 'real', 'Sample'};
       	{'RR_Outlet',	1,'double', -1, 'real', 'Sample'};
	{'PV_1',	1,'double', -1, 'real', 'Sample'};
       	{'PV_2',	1,'double', -1, 'real', 'Sample'};
	{'SV_1',	1,'double', -1, 'real', 'Sample'};
       	{'SV_2',	1,'double', -1, 'real', 'Sample'};
	{'V_1',		1,'double', -1, 'real', 'Sample'};
       	{'V_2',		1,'double', -1, 'real', 'Sample'};
	{'V_3',		1,'double', -1, 'real', 'Sample'};
       	{'v_4',		1,'double', -1, 'real', 'Sample'};
    }
}
{
    'cmHydBrakeSystemIn', {
	{'Use_pMCInput', 	1, 'double', -1, 'real', 'Sample'};
	{'pMC_in',		1, 'double', -1, 'real', 'Sample'};
	{'Pedal',		1, 'double', -1, 'real', 'Sample'};
	{'Park', 		1, 'double', -1, 'real', 'Sample'};
	{'T_env', 		1, 'double', -1, 'real', 'Sample'};
	{'Valve',		1,'cm6ValveInArray', -1, 'real', 'Sample'};
	{'PumpCtrl', 		1, 'double', -1, 'real', 'Sample'};
	{'BooSignal', 		1, 'double', -1, 'real', 'Sample'};
    }
}
% Output Bus
{
    'cmHydBrakeSystemOut', {
    	{'Rel_SW',	1,'double', -1, 'real', 'Sample'};
    	{'pMC',		1,'double', -1, 'real', 'Sample'};
    	{'pWB',		1,'cm6Wheels', -1, 'real', 'Sample'};
    	{'Trq_WB',	1,'cm6Wheels', -1, 'real', 'Sample'};
    	{'Trq_PB',	1,'cm6Wheels', -1, 'real', 'Sample'};
    	{'PuRetVolt',	1,'double', -1, 'real', 'Sample'};
    	{'PedFrc',	1,'double', -1, 'real', 'Sample'};
    	{'PedTravel',	1,'double', -1, 'real', 'Sample'};
    	{'PistTravel',	1,'double', -1, 'real', 'Sample'};
	{'DiaphTravel',	1,'double', -1, 'real', 'Sample'};
    }
}
% CfgInput Bus
{
    'cmHydBrakeSystemCfgIn' , {
	{'VehicleClassId', 	1, 'double', -1, 'real', 'Sample'};
	{'nWheels', 	1, 'double', -1, 'real', 'Sample'};
	{'BrakeKind', 	1, 'double', -1, 'real', 'Sample'};
    }
}
% CfgOutput Bus
{
    'cm6Map', {
	{'x',	100,'double', -1, 'real', 'Sample'};
	{'z',	100,'double', -1, 'real', 'Sample'};
    }
}
{
    'cmHydBrakeSystemCfgOut' , {
	{'Trq_stat', 	1, 'cm6WheelsTrq_stat', -1, 'real', 'Sample'};
	{'Ped2pMC', 	1, 'cm6Map', -1, 'real', 'Sample'};
    }
}
});
