//*****************************************************************************
// C O P Y R I G H T
//-----------------------------------------------------------------------------
// Copyright (c) 2018-2021 by Robert Bosch GmbH.            All rights reserved.
//
// This file is property of Robert Bosch GmbH. Any unauthorised copy, use or 
// distribution is an offensive act against international law and may me 
// prosecuted under federal law. Its content is company confidential.
//-----------------------------------------------------------------------------
// D E S C R I P T I O N
//-----------------------------------------------------------------------------
//    Purpose:        Interface to UssSimulator and echo generator                  
//-----------------------------------------------------------------------------
// N O T E S
//-----------------------------------------------------------------------------
//     Notes:
//-----------------------------------------------------------------------------
// A U T H O R   I D E N T I T Y
//-----------------------------------------------------------------------------
//      Network account       Name                   Department
//      ----------------      --------------------   ---------------------------
//      bnc1lr                Andreas Becker         XC-DA/EPA3
//
//******************************************************************************

#pragma once
#ifndef RB_ULTRASONICS_H_
#define RB_ULTRASONICS_H_


#include "RbDefines.h"
#include "UssSensor.h"
#include "UdpMultiTester.h"
#ifdef XENO
#include "UsbMultiTester.h"
#endif
#include "EchoGenerator.h"

#include <memory>

#define USSSIMULATORINTERFACE_VERSION_MAJOR 1
#define USSSIMULATORINTERFACE_VERSION_MINOR 17
#define USSSIMULATORINTERFACE_VERSION_PATCH 1

constexpr auto TIMEOUT_SENSOR_STATE_us = 5000000;
constexpr auto UPDATE_RATE_SENSOR_STATE_us = 100000; //100000 us = 100 ms = 10 Hz update rate


class RbUltraSonics
{
public:

	
	RbUltraSonics(void); // Use this constructor for use cases without UssSimulator (like SiL)
	
	/* RbUltraSonics
	* @brief Constructor for the RbUltraSonics class for the UDP communication with the UssSimulator
	* @param IpMultiTester - IP address of the multi tester (default "192.168.0.118")
	* @param ListeningPort - Port of the multi tester to listen to (default 8888)
	*/
	RbUltraSonics(std::string IpMultiTester, int32_t ListeningPort);
	
	/* RbUltraSonics
	* @brief Constructor for the RbUltraSonics class for the USB communication with the UssSimulator
	* @param address - Address of the UssSimulator (default 0)
	*/
	RbUltraSonics(uint8_t address);
	~RbUltraSonics(void);

	void Rb_Init(void);

	/* Rb_InitSensorConfiguration
	* @brief Initialize the sensor configuration and start UssSimulator (if not already running)
	* @param  AllSensorsType - Uss Sensor Type for all sensors - see @ref eUssSensorTypes
	* @param  AllSensorsSilicon - Uss silicon Type for all sensors - see @ref eUssSensorSilicon
	* @param  FrontCornerSensorsType - Uss sensor type for the front corner sensors (overwrites AllSesnsorsType) - see @ref eUssSensorTypes
	* @param  FrontCornerSensorsType - Uss silicon Type for front corner sensors - see @ref eUssSensorSilicon
	* @param  RearCornerSensorsType - Uss sensor type for the rear corner sensors (overwrites AllSesnsorsType) - see @ref eUssSensorTypes
	* @param  RearCornerSensorsType - Uss silicon Type for rear corner sensors - see @ref eUssSensorSilicon
	*/

	void Rb_InitSensorConfiguration(int8_t AllSensorsType, int8_t AllSensorsSilicon);
	void Rb_InitSensorConfiguration(int8_t AllSensorsType, int8_t AllSensorsSilicon, int8_t FrontCornerSensorsType, int8_t FrontCornerSensorsSilicon, int8_t RearCornerSensorsType, int8_t RearCornerSensorsSilicon);
	void Rb_InitSensorConfiguration(int8_t AllFrontSensorsType, int8_t AllFrontSensorsSilicon, int8_t AllRearSensorsType, int8_t AllRearSensorsSilicon, int8_t FrontCornerSensorsType, int8_t FrontCornerSensorsSilicon, int8_t RearCornerSensorsType, int8_t RearCornerSensorsSilicon);

	/* Rb_TestRun_Start
	* @brief Initialize sensor data for sensor model
	* @brief Write sensor data to multi tester, if configured
	* @brief Give the timeout for the firing check that should be used (optional)
	*/
	void Rb_TestRun_Start(double m_firingchecktimeout_us = TIMEOUT_SENSOR_STATE_us);
	
	bool Rb_CheckObject(int8_t SensorNumber, UssObject ObjectData, UssCoordinates EgoVehicle);
	bool Rb_CheckObject(int8_t SensorNumber, int32_t GlobalID, UssPoint NearPnt, double NearPntDistance, double NearPntAlpha, double IncidentAlpha, double IncidentBeta, double Height);

	/*Rb_WriteObject
	* @brief Writes object data to the sensor object list.
	* @brief Only to be used, when data already is in Bosch compatible form!
	* @param SensorNumber 1-MAX_SENSOR (normally 12)
	* @param GlobalID of object
	* @param NearPntDistance [m]
	* @param NearPntAlpha [rad]
	* @param IncidentAlpha [rad]
	* @param IncidentBeta [rad]
	* @param Height [m]
	*/
	void Rb_WriteObject(int8_t SensorNumber, int32_t GlobalID, UssPoint NearPnt, double NearPntDistance, double NearPntAlpha, double IncidentAlpha, double IncidentBeta, double Height);

	/*Rb_Calc
	*@brief Calculate echoes based on input data and send them to the UssSimulator
	*@param optional: Timestamp_us the time in us when the simulation was updated, is used for monitoring if not 0
	*/
	void Rb_Calc(uint64_t Timestamp_us=0);

	/* Rb_GetSensorData2MultiTester
	* @brief Get the sensor data for the multi tester
	* @return sensor data for the multi tester
	*/
	tMultiTesterDataIF Rb_GetSensorData2MultiTester(void);

	/* Rb_AddSensor
	* @brief Add a new sensor to the sensor list with additional information.
	* @param SensorNumber 1-MAX_SENSOR (normally 12)
	* @param Position_x - Mounting position x of the sensor in system coordinates [m]
	* @param Position_y - Mounting position y of the sensor in system coordinates [m]
	* @param Position_z - Mounting position z of the sensor in system coordinates [m]
	* @param Orientation_y - Orientation of the sensor, rotation arround the y-axis [rad]
	* @param Orientation_z - Orientation of the sensor, rotation arround the z-axis [rad]
	* @param Range - Detection range of the sensor [m]
	* @param Aperture_Hoz - Horizontal opening angle of the simulated sensor [rad]
	* @param Aperture_Vert - Vertical opening angle of the simulated sensor [rad]
	* @return sensor added = 0 , otherwise values > 0
	*/
	uint8_t Rb_AddSensor(int8_t SensorNumber, double Position_x, double Position_y, double Position_z, double Orientation_y, double Orientation_z, double Range, double Aperture_Hoz, double Aperture_Vert);

	/* Rb_AddSensor
	* @brief Add a new sensor to the sensor list with additional information.
	* @param SensorNumber 1-MAX_SENSOR (normally 12)
	* @param Position_x - Mounting position x of the sensor in system coordinates [m]
	* @param Position_y - Mounting position y of the sensor in system coordinates [m]
	* @param Position_z - Mounting position z of the sensor in system coordinates [m]
	* @param Orientation_y - Orientation of the sensor, rotation arround the y-axis [rad]
	* @param Orientation_z - Orientation of the sensor, rotation arround the z-axis [rad]
	* @param Range - Detection range of the sensor [m]
	* @param Aperture_Hoz - Horizontal opening angle of the simulated sensor [rad]
	* @param Aperture_Vert - Vertical opening angle of the simulated sensor [rad]
	* @param Description - Additional description of the sensor, normally the position
	* @param HeightForHeightClassification - When an object is higher then this value it will be considered as "high" by the sensor [m]
	* @param SensorState - When the state is SENSOR_INACTIVE no calculations will be done. [SENSOR_ACTIVE; SENSOR_INACTIVE]
	* @return sensor added = 0 , otherwise values > 0
	*/
	uint8_t Rb_AddSensor(int8_t SensorNumber, double Position_x, double Position_y, double Position_z, double Orientation_y, double Orientation_z, double Range, double Aperture_Hoz, double Aperture_Vert, std::string Description, double HeightForHeightClassification, eSensorState SensorState);

	/* Rb_RemoveSensor
	* @brief Remove a single sensor from list
	* @param SensorNumber 1-MAX_SENSOR (normally 12)
	* @return sensor removed = 0 , otherwise values > 0
	*/
	uint8_t Rb_RemoveSensor(int8_t SensorNumber);

    /* Rb_SetSensorState
	* @brief Activate or deactivate a single sensor from list
	* @param SensorNumber 1-MAX_SENSOR (normally 12)
	* @param SensorState either SENSOR_ACTIVE or SENSOR_INACTIVE, the state to set 
	* @return state set = 0 , otherwise values > 0
	*/
	uint8_t Rb_SetSensorState(int8_t SensorNumber, eSensorState SensorState);

	/* Rb_GetSensorFiringState
	* @brief Get the current firing state of the requested senor
	* @param SensorNumber 1-MAX_SENSOR (normally 12)
	* @return 1: sensor has been fired , 0: sensor has not been fired
	*/
	int8_t Rb_GetSensorFiringState(int8_t SensorNumber);

	int8_t Rb_SensorFaults(tUssSensorErrorEnum CommunicationLineErrors[MAX_SENSOR]);
	int8_t Rb_SensorClusterFaults(tUssSensorErrorEnum SensorClusterErrors[2]);

	void Rb_ClearAllSensorFaults(void);
	void Rb_ClearSensorList(void);
	void Rb_ClearObjectList(int8_t SensorNumber);

	uint8_t Rb_Terminate(void);

	Rb_StatusList Rb_GetStatus(void);

	void Rb_ResetState(void);

	void Rb_GetStatusMessage(Rb_StatusList lStatus, Rb_FcnList lFcn, std::string & lStatusMessage);

	std::string GetUssSimulatorIpAddress(void);
	void SetUssSimulatorIpAddress(std::string IpAddress);
	int32_t GetUssSimulatorPort(void);
	void SetUssSimulatorPort(int32_t Port);

	uint8_t GetUssSimulatorFirmwareVersionMajor(void);
	uint8_t GetUssSimulatorFirmwareVersionMinor(void);

	void SetExpectedUssSimulatorFirmwareVersionMajor(uint8_t FirmwareMajor);
	void SetExpectedUssSimulatorFirmwareVersionMinor(uint8_t FirmwareMinor);

	uint8_t GetExpectedUssSimulatorFirmwareVersionMajor(void);
	uint8_t GetExpectedUssSimulatorFirmwareVersionMinor(void);

	bool EnableSensorFiringCheck(bool state);
	bool GetSensorFiringCheckState(void);

	void EnableEchoSending(bool FrontCluster, bool RearCluster);

	tMultiTesterStat GetMultiTesterStatistics(void);
	tFirstEchoData getFirstEchoData(void);

private:
	void InitializeMemberVariables(void);
	void Rb_TestRun_Start_UssSimulator(void);
	bool Rb_MultiTester_isRunning();
	void WriteSensorConfiguration();
	void Init_SensorData2UssSimulator();
	void Reset_SensorFaultData(uint8_t sensor);
	void Rb_SetStatus(eUssSimulatorState state);

	bool m_UssSimulatorAvailable;

	tMultiTesterDataIF m_SensorData2MultiTester;
	std::unique_ptr<UssSimulator> p_UssSimulator;
	std::unique_ptr<EchoGenerator> p_SensorModell;
	std::vector<std::unique_ptr<UssSensor>> m_SensorList;
	Rb_StatusList m_status;
	uint32_t m_UssThreadState_Buffer;
	uint8_t m_CommunicationLineErrorsBuffer[MAX_SENSOR];
	uint8_t m_SensorCommunicationErrorBuffer[MAX_SENSOR];
	uint8_t m_StatusFrameValueBuffer[MAX_SENSOR];
	uint8_t m_StatusFrameBuffer[MAX_SENSOR];
	eUssSensorTypesConfiguration m_SensorTypeBuffer[MAX_SENSOR];
	eUssSensorTypesConfiguration m_SensorTypeDefault[MAX_SENSOR];
	uint8_t m_ShortVSEtoGndBuffer[2];
	uint8_t m_OvercurrentBuffer[2];
	tRbSensorConfig m_SensorCfg;
	std::string m_IP;
	int32_t m_Port;
	uint8_t m_address;
	uint8_t m_ExpectedFirmwareVersionMajor;
	uint8_t m_ExpectedFirmwareVersionMinor;
	bool m_SensorFiringCheckBuffer;
	bool m_SensorFiringCheckState;
	uint64_t m_firingchecktimeout_us;
	uint64_t m_SensorFiringLastCorrectUpdate[MAX_SENSOR];
	uint64_t m_SensorFiringStateUpdateTimeStamp;
	uint32_t m_SensorFiringStateFront;
	uint32_t m_SensorFiringStateRear;

	/*Transform the different sensor id types*/
	uint8_t tSensorToSensorId(tSensor ID);
	tSensor SensorIdToTSensor(uint8_t ID);

};

#endif // !RB_ULTRASONICS_H_