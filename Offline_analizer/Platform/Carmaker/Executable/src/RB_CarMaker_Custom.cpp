/*
 * FILE:            RB_CarMaker_Custom.cpp
 * SW-COMPONENT:    RB_CarMaker_Custom
 * DESCRIPTION:     Implementation of the RB_CarMaker_Custom component
 * COPYRIGHT:       © 2017 - 2023 Robert Bosch GmbH
 * 
 * The reproduction, distribution and utilization of this file as
 * well as the communication of its contents to others without express
 * authorization is prohibited. Offenders will be held liable for the
 * payment of damages. All rights reserved in the event of the grant
 * of a patent, utility model or design.
 */


#include "RB_CarMaker_Custom.h"

#if not defined USS_SIM_TYPE
#error "USS_SIM_TYPE not defined"
#else
#define stringer(x) #x
#define TO_STR(x) stringer(x)
const char* UssSimType = TO_STR(USS_SIM_TYPE);
#endif

#if defined (SIMULATE_USS)
	#include "ussInterfaceAdapterFord.h"
#endif

#if defined (SIMULATE_RADAR)
//Radar
//#include "RbRadar.h"
#endif

//For Test Reports needed
#include "DataDict.h"
#include <stddef.h>
#include "DrivMan.h"
#include <Traffic.h>

#include "common/objectData.h"

#if defined (RB_INTERFACE_ON)
	#if defined (RB_VEH_MODEL_SIM_ON)
	#include "car/fillCarParameters.h"
	#include "car/carParametersDVAs.h"
	#include "motion/fillMotion.h"
	#include "motion/motionDVAs.h"
	#endif
	#if defined (RB_RADAR_OBJ_SIM_ON)
	#include "radarObject/fillRadarObjectData.h"
	#include "radarObject/radarObjectDataDVAs.h"
	#endif
	#if defined (RB_VIDEO_OBJ_SIM_ON)
	#include "videoObject/fillVideoObjectData.h"
	#include "videoObject/videoObjectDataDVAs.h"
	#endif
	#if defined (RB_LINE_SIM_ON)
	#include "groundTruth/fillLineData.h"
	#include "groundTruth/lineDataDVAs.h"
	#endif
	#if defined (RB_TRAFFIC_OBJ_SIM_ON)
	#include "traffic/fillTrafficObject.h"
	#include "traffic/trafficDVAs.h"
	#endif
	#if defined (RB_TRAFFIC_SIGN_SIM_ON)
	#include "trafficSign/fillTrafficSignData.h"
	#include "trafficSign/trafficSignDVAs.h"
	#endif
#endif

#include <Config.h> 
#if defined (UDP_INTERFACE_ON)
#include "UdpClient.h"
#endif

// for ROTA
#if defined(WITH_RadarTS)
#include "radarTS/RadarTS.h"
#include "Vehicle/Sensor_RadarRSI.h"
#endif

int RB_User_Init_First ()
{
	int ret{0};
	
	//**************************************************************************
	//USS - Multitester
	//**************************************************************************
#if defined (SIMULATE_USS)	
	CreateUssInterface();	
#endif

// #if defined (SIMULATE_RADAR)
// 	//Radar_Init_First();
// #endif

#if defined(WITH_RadarTS)
    ret = RadarTS_Init_First ();
#endif

	return ret;
}


int RB_User_Init ()
{
	int ret{0};
// #if defined (SIMULATE_RADAR)
// 	//Radar_Init();
// #endif

#if defined(WITH_RadarTS)
    ret = RadarTS_Init ();
#endif

    return ret;
}

void RB_Interface_DeclQuants()
{
#if defined (RB_INTERFACE_ON)
	#if defined (RB_RADAR_OBJ_SIM_ON)
		RB_Radar_DeclQuants();
	#endif
	#if defined (RB_VIDEO_OBJ_SIM_ON)
		RB_Video_DeclQuants();
	#endif
	#if defined (RB_TRAFFIC_OBJ_SIM_ON)
		RB_Traffic_DeclQuants();
	#endif
	#if defined (RB_TRAFFIC_SIGN_SIM_ON)
		RB_TrafficSign_DeclQuants();
	#endif
	#if defined (RB_LINE_SIM_ON)
		RB_GT_Line_DeclQuants();
	#endif
	#if defined (RB_VEH_MODEL_SIM_ON)
		RB_Car_Param_DeclQuants();
		RB_Motion_DeclQuants();
	#endif
#endif
}

int RB_User_DeclQuants ()
{

#if CM_NUMVER < 120000
	//Declare Quantities for TestReport
	DDefInt(NULL, "DM.ManNo", "", &DrivMan.ActualMan.No, DVA_None);
	DDefDouble(NULL, "DM.ManStartTime", "", &DrivMan.ActualMan.StartTime ,DVA_None);
	DDefDouble(NULL, "DM.ManStartDist", "m", &DrivMan.ActualMan.StartDist ,DVA_None);
#else
	//Declare Quantities for TestReport
	DDefInt(NULL, "DM.ManNo", "", &DrivMan.ActStepLong.No, DVA_None);
	DDefDouble(NULL, "DM.ManStartTime", "", &DrivMan.ActStepLong.StartTime ,DVA_None);
	DDefDouble(NULL, "DM.ManStartDist", "m", &DrivMan.ActStepLong.StartDist ,DVA_None);
#endif

	//**************************************************************************
	//USS - Multitester
	//**************************************************************************
#if defined (SIMULATE_USS)
	DeclareUssQuants();
#endif

#if !defined (RB_INT_VARIANT_HANDLING_ON)
	RB_Interface_DeclQuants();
#endif

	return 0;
}

int RB_User_TestRun_Start_atBegin()
{
	return 0;
}


int RB_User_TestRun_Start_atEnd()
{
	int ret{0};

#if defined(RB_INT_VARIANT_HANDLING_ON)
	RB_Interface_DeclQuants();
#endif	

#if defined(WITH_RadarTS)
    //if (SimCore.IsFirstInit != 0)
    //    return 0;
	if(RadarRSICount != 0)
	{
		RadarTS_DeclQuants();
		ret = RadarTS_TestRun_Start_atEnd ();
	}
#endif

    return ret;

}

int RB_User_TestRun_Start_StaticCond_Calc()
{
	return 0;
}

int RB_User_TestRun_Start_Finalize(void)
{
	if(!SimCore.IsRegularInit)
	{
		return 0;
	}

	//**************************************************************************
	//USS - Multitester
	//**************************************************************************
#if defined (SIMULATE_USS)
	int ret = InitUssSensors();
	if(ret != 0)
	{
		return ret;
	}	
#endif

	return 0;
}


int RB_User_VehicleControl_Calc(double dt)
{
	return 0;
}

int RB_User_Calc (double dt)
{	
	static double timeCounter {0.0};
	timeCounter += dt;
	
	//**************************************************************************
	//USS - Multitester
	//**************************************************************************
#if defined (SIMULATE_USS)
	UpdateUssInterface(dt);
#endif

#if defined (RB_INTERFACE_ON)
	#if defined (RB_RADAR_OBJ_SIM_ON)
		fillRadarObjectData();
	#endif
	#if defined (RB_VIDEO_OBJ_SIM_ON)
		fillVideoObjectData();
	#endif
	#if defined (RB_TRAFFIC_OBJ_SIM_ON)
		fillTrafficObject();
	#endif
	#if defined (RB_TRAFFIC_SIGN_SIM_ON)
		fillTrafficSign();
	#endif
	#if defined (RB_LINE_SIM_ON)
		fillGroundTruthLineData();
	#endif
	#if defined (RB_VEH_MODEL_SIM_ON)
		fillCarParameters();
		fillMotion();
	#endif
#endif

// #if defined (SIMULATE_RADAR)
// 	//Radar_Calc(dt);
// #endif

#if defined (UDP_INTERFACE_ON)
	const bool isValidSimState = SimCore.State == SCState_Idle || SimCore.State == SCState_Simulate; 
    const double updateCycleTime = static_cast<double>(Config::UdpClient::TRANSMIT_UDP_DATA_CYCLE_TIME_MS) / 1000.0;
    if (timeCounter > updateCycleTime && isValidSimState)
    {
        extern tRbRadarData g_radarData;
        sendRadarDataUDP(g_radarData, Config::UdpClient::CARMAKER_UDP_TARGET_IP_ADDRESS, Config::UdpServerApp::LISTENING_PORT);
        timeCounter = 0.0;
    }
#endif

	return 0;
}

int RB_User_TestRun_End_First(void)
{	
	return 0;
}

int RB_User_Out(const unsigned CycleNo)
{
#if defined(WITH_RadarTS)
    if(RadarRSICount != 0)
	{
		RadarTS_Out(CycleNo);
	}
#endif

	return 0;
}

int RB_User_TestRun_End(void)
{
	//**************************************************************************
	//USS - Multitester
	//**************************************************************************
#if defined (SIMULATE_USS)
	ClearUssInterface();
#endif
	return 0;
}

int RB_User_End ()
{
	return 0;
}


int RB_User_Cleanup ()
{
// #if defined (SIMULATE_RADAR)
// 	//Radar_Cleanup();
// #endif
#if defined (SIMULATE_USS)
	CleanupUssInterface();
#endif

#if defined(WITH_RadarTS)
    RadarTS_Exit();
#endif

	return 0;
}
