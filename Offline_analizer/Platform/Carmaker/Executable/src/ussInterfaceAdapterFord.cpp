/*
 * FILE:            ussInterfaceAdapterFord.cpp
 * SW-COMPONENT:    ussInterfaceAdapterFord
 * DESCRIPTION:     Implementation of the ussInterfaceAdapterFord component
 * COPYRIGHT:       © 2017 - 2023 Robert Bosch GmbH
 * 
 * The reproduction, distribution and utilization of this file as
 * well as the communication of its contents to others without express
 * authorization is prohibited. Offenders will be held liable for the
 * payment of damages. All rights reserved in the event of the grant
 * of a patent, utility model or design.
 */


#include "ussInterfaceAdapterFord.h"

#include "RbUltraSonics.h"
#include "Vehicle/Sensor_Object.h"
#include <cstring>
#include <CarMaker.h>
#include "Car/Car.h"
#include "Log.h"

constexpr unsigned int NUM_USSSIM = 2u;
const std::string IP_ADDR_USSSIM_1 = "192.168.0.119";
const std::string IP_ADDR_USSSIM_2 = "192.168.0.118";
constexpr int32_t ETH_PORT_USSSIM_1 = 8888;
constexpr int32_t ETH_PORT_USSSIM_2 = 8888;
constexpr uint8_t USB_ADDR_USSSIM = 0;
extern const char* UssSimType;

RbUltraSonics *RB_USS_1;
RbUltraSonics *RB_USS_2;

// indicates if tailgate is open (1) or closed (0)
static char tailgateOpen = 0;

// indicates if tailgate was open (1) or closed (0) in the last iteration; 
// used to avoid too many togglings of sensor states
static char tailgateOpenPrev = 0;

// ultrasonic sensor faults for front and rear sensor clusters
static tUssSensorErrorEnum ussSensorClusterFaults[NUM_USSSIM * 2];

struct tUssSensor 
{
	/// @brief Fault status of sensor
	tUssSensorErrorEnum sensorFault {NoError};

	/// @brief Firing state of sensor (0: no firing, 1: firing)
	int8_t firingState {0};

	/// @brief Status boolean indicating sensor is on the tailgate
	bool isTailgateSensor {false};

	/// @brief Status boolean indicating if the sensor is inactive if the tailgate is open
	bool isInactiveIfTailgateOpen {false};

	/// @brief X distance to nearest detected object 
	double ds_x {0.0};

	/// @brief Y distance to nearest detected object
	double ds_y {0.0};
};

static tUssSensor ussSensors [NUM_USSSIM * MAX_SENSOR];

// check if we should disable the sensor with index f_sensorIndex (also for better performance)
// f_sensorIndex must be within [0, NUM_USSSIM * MAX_SENSOR]
bool check_disable_sensor(unsigned int f_sensorIndex)
{
	if(f_sensorIndex >= NUM_USSSIM * MAX_SENSOR)
	{
		return false;
	}

	bool disable_sensor = false;
	disable_sensor |= (tailgateOpen && ussSensors[f_sensorIndex].isInactiveIfTailgateOpen);
	disable_sensor |= (!tailgateOpen && ussSensors[f_sensorIndex].isTailgateSensor);

	return disable_sensor;
}

/// @brief Updates the tUssSensor with relevant target near point data from the specified sensor
/// @param sensorID A CarMaker Object Sensor ID
/// @param sensorIndex The index of the tUssSensor to update
void updateUssSensorRelvTarget(unsigned int sensorID, unsigned int sensorIndex)
{
	const tObjectSensor* sensor = ObjectSensor_GetByIndex(sensorID);

	if (nullptr == sensor)
	{
		return;
	}

	ussSensors[sensorIndex].ds_x = sensor->relvTarget.NearPnt.ds[0];
	ussSensors[sensorIndex].ds_y = sensor->relvTarget.NearPnt.ds[1];
}

int CreateUssInterface(RbUltraSonics* &f_ussSimulator, std::string f_ip_addr, int32_t f_port)
{
	if (f_ussSimulator == NULL)
	{
		if (!strcmp(UssSimType,"UDP"))
		{
			f_ussSimulator = new RbUltraSonics(f_ip_addr, f_port); 
		}
		else
		{
			f_ussSimulator = new RbUltraSonics(USB_ADDR_USSSIM);
		}
	} 
		
	f_ussSimulator->Rb_Init();
	if (f_ussSimulator->Rb_GetStatus()!= USS_NO_ERROR)
	{
		return -1;
	}

	return 0;
}

int CreateUssInterface()
{
	int ret = CreateUssInterface(RB_USS_1, IP_ADDR_USSSIM_1, ETH_PORT_USSSIM_1);
	if(ret != 0){
		delete RB_USS_1;
		RB_USS_1 = NULL;
	}

	ret = CreateUssInterface(RB_USS_2, IP_ADDR_USSSIM_2, ETH_PORT_USSSIM_2);
	if(ret != 0){
		delete RB_USS_2;
		RB_USS_2 = NULL;
	}
	return ret;
}

int DeclareUssQuants()
{
	DDefChar(NULL, "RB.RBS.Driver.Actions.openTailGate","", &tailgateOpen, DVA_IO_In);

	// UAQs for uss sensor faults 
	std::string uaq_base_name = "RB.Uss.";

	// for individual sensors
	for(unsigned int uss_sensor_index = 0; uss_sensor_index < NUM_USSSIM * MAX_SENSOR; uss_sensor_index++)
	{
		// Create a default prefix of format 'RB.Uss.S{index}.'
		std::string uaq_base_sensor_name = uaq_base_name + "S" + std::to_string(uss_sensor_index + 1) + ".";

		// Assign DDict default name for CarMaker UAQs
		tDDefault* df  = DDefaultCreate(uaq_base_sensor_name.c_str());
		
      	DDefChar(df, "SensorFault", "", reinterpret_cast<char*>(&ussSensors[uss_sensor_index].sensorFault), DVA_IO_Out);	
		DDefChar(df, "FiringState", "", reinterpret_cast<char*>(&ussSensors[uss_sensor_index].firingState), DVA_IO_In);
		DDefDouble(df, "ds.x", "m", &ussSensors[uss_sensor_index].ds_x, DVA_None);
		DDefDouble(df, "ds.y", "m", &ussSensors[uss_sensor_index].ds_y, DVA_None);
	}

	// for sensor clusters
	for(unsigned int uss_cluster_index = 0; uss_cluster_index < NUM_USSSIM; uss_cluster_index++)
	{
		// Create a default prefix of format 'RB.Uss.MT{index}.'
		std::string uaq_base_cluster_name = uaq_base_name + "MT" + std::to_string(uss_cluster_index + 1) + ".";

		// Assign DDict default name for CarMaker UAQs
		tDDefault* df  = DDefaultCreate(uaq_base_cluster_name.c_str());		

      	DDefChar(df, "RearSensorClusterFault", "", reinterpret_cast<char*>(&ussSensorClusterFaults[2 * uss_cluster_index]), DVA_IO_Out);
      	DDefChar(df, "FrontSensorClusterFault", "", reinterpret_cast<char*>(&ussSensorClusterFaults[2 * uss_cluster_index + 1]), DVA_IO_Out);
	}

	return 0;
}

int InitUssSensors(RbUltraSonics* f_ussSimulator, unsigned int f_startIndex)
{
	if(f_ussSimulator != NULL)
	{
		//clear sensor list, so that updated data will be considered
		f_ussSimulator->Rb_ClearSensorList();
	}
	

	for(unsigned int i = 0; i < MAX_SENSOR && f_startIndex <= MAX_SENSOR; i++)
	{
		std::string sensorName = "S" + std::to_string(f_startIndex + i + 1);

		// read out additional info about the sensor (is it related to tailgate?)
		ussSensors[f_startIndex + i].isTailgateSensor = 
			(iGetBoolOpt(SimCore.Vhcl.Inf, ("is_tailgate_" + sensorName).c_str(), 0) != 0);

		ussSensors[f_startIndex + i].isInactiveIfTailgateOpen = 
			(iGetBoolOpt(SimCore.Vhcl.Inf, ("is_inactive_if_tailgate_open_" + sensorName).c_str(), 0) != 0);
		
		int sensorId = ObjectSensor_FindIndexForName(sensorName.c_str());

		if(f_ussSimulator == NULL)
		{
			if(sensorId != -1)
			{
				// we found a carmaker sensor but the respective simulator is not available -> error
				std::string msg = "Vehicle has ultrasonic sensor " + sensorName
				+ " but needed multitester is not configured\n";
				LogErrStr(EC_Init, msg.c_str());
				return -1;
			}
			
			continue;
		}

		if(sensorId == -1)
		{
			// add dummy sensor
			f_ussSimulator->Rb_AddSensor(
				i + 1, 			// SensorNumber
				0.0,			// Position_x,
				0.0, 			// Position_y, 
				0.0, 			// Position_z
				0.0,			// Orientation_y
				0.0,			// Orientation_z
				0.0, 			// Range
				0.0, 			// Aperture_Hoz
				0.0, 			// Aperture_Vert, 
				"n/a",			// Description
				0.0, 			// HeightForHeightClassification
				SENSOR_INACTIVE // SensorState
			);
			continue;
		}

		f_ussSimulator->Rb_AddSensor(	
			i + 1, 
			(ObjectSensor[sensorId].bs.Pos_B[0]),
			(ObjectSensor[sensorId].bs.Pos_B[1]),
			(ObjectSensor[sensorId].bs.Pos_B[2]),
			ObjectSensor[sensorId].rot_zyx[1], 
			ObjectSensor[sensorId].rot_zyx[2],
#if CM_NUMVER > 90000
			ObjectSensor[sensorId].Range,
			ObjectSensor[sensorId].FoV[0], 
			ObjectSensor[sensorId].FoV[1]
#else
			ObjectSensor[sensorId].range,
			ObjectSensor[sensorId].alpha * 2.0, 
			ObjectSensor[sensorId].theta * 2.0
#endif
		);

		// check if we should disable this sensor (also for better performance)
		bool l_disable_sensor = check_disable_sensor(f_startIndex + i);

		if(l_disable_sensor)
		{
			ObjectSensor_Disable(sensorId);
			f_ussSimulator->Rb_SetSensorState(i + 1, SENSOR_INACTIVE);
		}
		else
		{
			ObjectSensor_Enable(sensorId);
			f_ussSimulator->Rb_SetSensorState(i + 1, SENSOR_ACTIVE);
		}
	}

	if(f_ussSimulator != NULL)
	{
		f_ussSimulator->Rb_InitSensorConfiguration(	(int8_t)iGetLongOpt(SimCore.Vhcl.Inf, "All_Sensors_type", 2), 
										(int8_t)iGetLongOpt(SimCore.Vhcl.Inf, "All_Sensors_Silicon", 5)
										);
		f_ussSimulator->Rb_TestRun_Start();
		if (f_ussSimulator->Rb_GetStatus()!= USS_NO_ERROR)
		{
			Log("GetStatus returned %d\n",f_ussSimulator->Rb_GetStatus());
			std::string msg = "Could not initialize UssSimulator (IP: " 
				+ f_ussSimulator->GetUssSimulatorIpAddress() + ", Port:" 
				+ std::to_string(f_ussSimulator->GetUssSimulatorPort()) + ").\n";
			LogErrStr(EC_Init, msg.c_str());
			return -1;
		}
		// enable sensor firing state check
		f_ussSimulator->EnableSensorFiringCheck(true);
	}	

	return 0;
}

int InitUssSensors()
{
	int ret = InitUssSensors(RB_USS_1, 0);
	if(ret != 0){
		return ret;
	}

	ret = InitUssSensors(RB_USS_2, MAX_SENSOR);
	return ret;
}

int UpdateUssInterface(RbUltraSonics* f_ussSimulator, unsigned int f_startIndex, double dt)
{
	if(f_ussSimulator == NULL)
	{
		return 0;
	}

	if(f_startIndex > MAX_SENSOR)
	{
		return -1;
	}
	
	for(unsigned int i = 0; i < MAX_SENSOR && f_startIndex <= MAX_SENSOR; i++)
	{
		std::string sensorName = "S" + std::to_string(f_startIndex + i + 1);
		
		int sensorId = ObjectSensor_FindIndexForName(sensorName.c_str());

		int8_t SensorNumber = i + 1;

		f_ussSimulator->Rb_ClearObjectList(SensorNumber);

		if(sensorId == -1)
		{
			continue;
		}

		// check if tailgate changed position compared to last cycle
		if(tailgateOpen != tailgateOpenPrev)
		{
			// check if we should disable this sensor (also for better performance)
			bool l_disable_sensor = check_disable_sensor(f_startIndex + i);

			if(l_disable_sensor)
			{
				ObjectSensor_Disable(sensorId);
				f_ussSimulator->Rb_SetSensorState(SensorNumber, SENSOR_INACTIVE);
			}
			else
			{
				ObjectSensor_Enable(sensorId);
				f_ussSimulator->Rb_SetSensorState(SensorNumber, SENSOR_ACTIVE);
			}
		}

		// Assign relevant target quantities to output DDicts
		updateUssSensorRelvTarget(sensorId, f_startIndex + i);

		for(int objNr = 0; objNr < ObjectSensor[sensorId].nObsvObjects; objNr++)
		{
			//UssObjectWorld ObjectData;

			const tObjectSensorObj* sensorObject = ObjectSensor_GetObject(sensorId, objNr);

			if (sensorObject != NULL && sensorObject->dtct == 1) 
			{
				UssPoint NearPnt;
				NearPnt.SetPositionX(sensorObject->NearPnt.ds[0]);
				NearPnt.SetPositionY(sensorObject->NearPnt.ds[1]);
				NearPnt.SetPositionZ(sensorObject->NearPnt.ds[2]);

				f_ussSimulator->Rb_CheckObject(
					SensorNumber,
					sensorObject->ObjId,
					NearPnt,
					sensorObject->NearPnt.ds_p,
					sensorObject->NearPnt.alpha_p,
					sensorObject->incangle[0],
					sensorObject->incangle[1],
					sensorObject->h
				);
			}			
		}
	}

	// Create a temporary array of sensor error enums and copy existing value in
	tUssSensorErrorEnum tempSensorFaults[MAX_SENSOR] = {};
	for (int i = 0; i < MAX_SENSOR; i++)
	{
		tempSensorFaults[i] = ussSensors[i + f_startIndex].sensorFault;
	}

	f_ussSimulator->Rb_SensorFaults(tempSensorFaults);

	// Copy any changes in sensor enum back to the main structures
	for (int i = 0; i < MAX_SENSOR; i++)
	{
		ussSensors[i + f_startIndex].sensorFault = tempSensorFaults[i];
	}

	unsigned int l_multitester_index = f_startIndex / MAX_SENSOR;
	
	f_ussSimulator->Rb_SensorClusterFaults(&ussSensorClusterFaults[l_multitester_index]);

	f_ussSimulator->Rb_Calc((uint64_t)(1e6 * SimCore.TimeWC));

	for(unsigned int i = 0; i < MAX_SENSOR && f_startIndex <= MAX_SENSOR; i++)
	{
		ussSensors[i + f_startIndex].firingState = f_ussSimulator->Rb_GetSensorFiringState(i+1);
	}

	return 0;
}

int UpdateUssInterface(double dt)
{
	if (	SimCore.State != SCState_StartSim 
		&& SimCore.State != SCState_StartLastCycle 
		&& SimCore.State != SCState_Simulate )
	{
		return 0;
	}

	int ret = UpdateUssInterface(RB_USS_1, 0, dt);
	if(ret != 0){
		return ret;
	}

	ret = UpdateUssInterface(RB_USS_2, MAX_SENSOR, dt);

	tailgateOpenPrev = tailgateOpen;
	
	return ret;
}

int ClearUssInterface(void)
{
	const int numUssSensors = NUM_USSSIM * MAX_SENSOR;
	for (int i = 0; i < numUssSensors; i++)
	{
		ussSensors[i].firingState = 0;
	}

	if(RB_USS_1 != NULL)
	{
		for (auto sensor = 0; sensor < MAX_SENSOR; ++sensor)
		{
			RB_USS_1->Rb_ClearObjectList(sensor);
		}
		RB_USS_1->Rb_Calc((uint64_t)(1e6 * SimCore.TimeWC));
	}
	
	if(RB_USS_2 != NULL)
	{
		for (auto sensor = 0; sensor < MAX_SENSOR; ++sensor)
		{
			RB_USS_2->Rb_ClearObjectList(sensor);
		}
		RB_USS_2->Rb_Calc((uint64_t)(1e6 * SimCore.TimeWC));
	}


	return 0;
}

int CleanupUssInterface(void)
{
	delete RB_USS_1;
	RB_USS_1 = NULL;
	delete RB_USS_2;
	RB_USS_2 = NULL;

	return 0;
}