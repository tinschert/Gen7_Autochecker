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

#include "RbUltraSonics.h"

RbUltraSonics::RbUltraSonics(void)
{
	m_UssSimulatorAvailable = false;
	InitializeMemberVariables();
}

RbUltraSonics::RbUltraSonics(std::string IP, int32_t Port)
{
	m_IP = IP;
	m_Port = Port;
	p_UssSimulator = std::make_unique<UdpMultiTester>();
	m_UssSimulatorAvailable = true;
	InitializeMemberVariables();
}

RbUltraSonics::RbUltraSonics(uint8_t address)
{
	m_UssSimulatorAvailable = true;
#ifdef XENO
	m_address = address;
	p_UssSimulator = std::make_unique<UsbMultiTester>();
	InitializeMemberVariables();
#else
	USS_OUT("UssSimulator: USB multi tester is not supported for Windows and Linux environment!\n");
#endif
}

RbUltraSonics::~RbUltraSonics() = default;

void RbUltraSonics::InitializeMemberVariables(void)
{
	p_SensorModell = std::make_unique<EchoGenerator>();
	Init_SensorData2UssSimulator();
	m_SensorList.clear();
	std::fill(m_StatusFrameValueBuffer, m_StatusFrameValueBuffer + MAX_SENSOR, 0);
	std::fill(m_CommunicationLineErrorsBuffer, m_CommunicationLineErrorsBuffer + MAX_SENSOR, NoError);
	std::fill(m_SensorCommunicationErrorBuffer, m_SensorCommunicationErrorBuffer + MAX_SENSOR, NoError);
	std::fill(m_StatusFrameBuffer, m_StatusFrameBuffer + MAX_SENSOR, 0);
	std::fill(m_SensorTypeBuffer, m_SensorTypeBuffer + MAX_SENSOR, CONF_USS_SENSOR_TYPE_6_5);
	std::fill(m_SensorTypeDefault, m_SensorTypeDefault + MAX_SENSOR, CONF_USS_SENSOR_TYPE_6_5);
	std::fill(m_ShortVSEtoGndBuffer, m_ShortVSEtoGndBuffer + 2, 0);
	std::fill(m_OvercurrentBuffer, m_OvercurrentBuffer + 2, 0);
	std::fill(m_SensorFiringLastCorrectUpdate, m_SensorFiringLastCorrectUpdate + MAX_SENSOR, 0);
	m_firingchecktimeout_us = TIMEOUT_SENSOR_STATE_us;
	m_SensorFiringStateUpdateTimeStamp = 0;
	m_SensorFiringCheckState = false;
	m_SensorFiringCheckBuffer = false;
	m_ExpectedFirmwareVersionMajor = 0;
	m_ExpectedFirmwareVersionMinor = 0;
	m_SensorFiringStateFront = 0;
	m_SensorFiringStateRear = 0;
	m_UssThreadState_Buffer = 0;
}

void RbUltraSonics::Rb_Init(void)
{
	Init_SensorData2UssSimulator();
	Rb_ClearSensorList();
	m_status = USS_NO_ERROR;
	if (m_UssSimulatorAvailable)
	{
		p_UssSimulator->ResetThreadState();
		m_SensorFiringCheckBuffer = false;
		eUssSimulatorState res = USSSIMULATOR_OK;
		if (p_UssSimulator->getUssSimulatorType())
		{//USB
			res = (eUssSimulatorState)p_UssSimulator->Init(m_address);
		}
		else
		{//UDP
			res = (eUssSimulatorState)p_UssSimulator->Init(m_IP, m_Port);
		}
		Rb_SetStatus(res);
	}
	else
	{
		Rb_SetStatus(USSSIMULATOR_OK);
	}

}

void RbUltraSonics::Rb_InitSensorConfiguration(int8_t AllSensorsType, int8_t AllSensorsSilicon)
{

	m_SensorCfg.FrontSensorsType = AllSensorsType;
	m_SensorCfg.FrontSensorsSilicon = AllSensorsSilicon;

	m_SensorCfg.RearSensorsType = AllSensorsType;
	m_SensorCfg.RearSensorsSilicon = AllSensorsSilicon;

	m_SensorCfg.FrontCornerSensorsType = AllSensorsType;
	m_SensorCfg.FrontCornerSensorsSilicon = AllSensorsSilicon;

	m_SensorCfg.RearCornerSensorsType = AllSensorsType;
	m_SensorCfg.RearCornerSensorsSilicon = AllSensorsSilicon;
}

void RbUltraSonics::Rb_InitSensorConfiguration(int8_t AllSensorsType, int8_t AllSensorsSilicon, int8_t FrontCornerSensorsType, int8_t FrontCornerSensorsSilicon, int8_t RearCornerSensorsType, int8_t RearCornerSensorsSilicon)
{

	m_SensorCfg.FrontSensorsType = AllSensorsType;
	m_SensorCfg.FrontSensorsSilicon = AllSensorsSilicon;

	m_SensorCfg.RearSensorsType = AllSensorsType;
	m_SensorCfg.RearSensorsSilicon = AllSensorsSilicon;

	m_SensorCfg.FrontCornerSensorsType = FrontCornerSensorsType;
	m_SensorCfg.FrontCornerSensorsSilicon = FrontCornerSensorsSilicon;

	m_SensorCfg.RearCornerSensorsType = RearCornerSensorsType;
	m_SensorCfg.RearCornerSensorsSilicon = RearCornerSensorsSilicon;
}

void RbUltraSonics::Rb_InitSensorConfiguration(int8_t AllFrontSensorsType, int8_t AllFrontSensorsSilicon, int8_t AllRearSensorsType, int8_t AllRearSensorsSilicon, int8_t FrontCornerSensorsType, int8_t FrontCornerSensorsSilicon, int8_t RearCornerSensorsType, int8_t RearCornerSensorsSilicon)
{
	m_SensorCfg.FrontSensorsType = AllFrontSensorsType;
	m_SensorCfg.FrontSensorsSilicon = AllFrontSensorsSilicon;

	m_SensorCfg.RearSensorsType = AllRearSensorsType;
	m_SensorCfg.RearSensorsSilicon = AllRearSensorsSilicon;

	m_SensorCfg.FrontCornerSensorsType = FrontCornerSensorsType;
	m_SensorCfg.FrontCornerSensorsSilicon = FrontCornerSensorsSilicon;

	m_SensorCfg.RearCornerSensorsType = RearCornerSensorsType;
	m_SensorCfg.RearCornerSensorsSilicon = RearCornerSensorsSilicon;
}

void RbUltraSonics::Rb_TestRun_Start(double firingchecktimeout_us)
{
	m_firingchecktimeout_us = (uint64_t)(firingchecktimeout_us);

	double SensorRotationsZ[MAX_SENSOR];

	/*Set array to zero*/
	Init_SensorData2UssSimulator();
	if(m_UssSimulatorAvailable)
	{
		p_UssSimulator->ResetThreadState();
	}	

	if (m_SensorList.size() == MAX_SENSOR)
	{
		/*go through all sensor*/
		for (auto it_sens = m_SensorList.begin(); it_sens != m_SensorList.end(); it_sens++)
		{
			/*Only the z rotation of the sensors is needed*/
			SensorRotationsZ[(*it_sens)->GetSensorID()] = (*it_sens)->GetSensorCoordinates().GetRotationZ();
		}

		p_SensorModell->Init_Sensors(SensorRotationsZ);
	}
	else
	{
		/*number of sensors is not correct -> no further calculation from USS side*/
		m_status = ERR_SENSORLIST_INCOMPLETE;
		USS_OUT("UssSimulator: Number of Sensors is not correct! Target: %i, Current: %zi\n", MAX_SENSOR, m_SensorList.size());
		return;
	}

	if(m_UssSimulatorAvailable)
	{
		Rb_TestRun_Start_UssSimulator();
	}
	
}

void RbUltraSonics::Rb_TestRun_Start_UssSimulator(void)
{	
	eUssSimulatorState res = USSSIMULATOR_OK;

	p_UssSimulator->ResetThreadState();
	if (p_UssSimulator->isRunning() == false)
	{
		if (p_UssSimulator->getUssSimulatorType() == UDP)
		{
			res = (eUssSimulatorState)p_UssSimulator->Init(m_IP, m_Port);
		}
		else
		{
			res = (eUssSimulatorState)p_UssSimulator->Init(m_address);
		}
	
		Rb_SetStatus(res);	
	}

	/* set sensor config */
	WriteSensorConfiguration();

	/* disable all possible sensor faults */
	Rb_ClearAllSensorFaults();
}

bool RbUltraSonics::Rb_CheckObject(int8_t SensorNumber, UssObject ObjectData, UssCoordinates EgoVehicle)
{
	tSensor SensorID = SensorIdToTSensor(SensorNumber);

	/*Check if the sensor number is within the allowed borders*/
	if (SensorNumber <= MAX_SENSOR && SensorNumber >= 1)
	{
		for (auto it_sens = m_SensorList.begin(); it_sens != m_SensorList.end(); it_sens++)
		{
			if (SensorID == (*it_sens)->GetSensorID())
			{
				//USS_DBG("Before AddObject\n");
				return (*it_sens)->AddObject(ObjectData, EgoVehicle);
			}
		}
	}
	else
	{
		USS_OUT("Rb_CheckObject: Sensor number has to be between 1 and %i. Current sensornumber is %i\n", MAX_SENSOR, SensorNumber);
		return false;
	}
	USS_OUT("Rb_CheckObject: Sensor number wasn't found in list. Current sensornumber is %i\n", SensorNumber);
	return false;
}

bool RbUltraSonics::Rb_CheckObject(int8_t SensorNumber, int32_t GlobalID, UssPoint NearPnt, double NearPntDistance, double NearPntAlpha, double IncidentAlpha, double IncidentBeta, double Height)
{
	tSensor SensorID = SensorIdToTSensor(SensorNumber);

	/*Check if the sensor number is within the allowed borders*/
	if (SensorNumber <= MAX_SENSOR && SensorNumber >= 1)
	{
		for (auto it_sens = m_SensorList.begin(); it_sens != m_SensorList.end(); it_sens++)
		{
			if (SensorID == (*it_sens)->GetSensorID())
			{
				//USS_DBG("Before AddObject\n");
				(*it_sens)->AddObject(GlobalID, NearPnt, NearPntDistance, NearPntAlpha, IncidentAlpha, IncidentBeta, Height);
				return true;
			}
		}
	}
	else
	{
		USS_OUT("Rb_CheckObject: Sensor number has to be between 1 and %i. Current sensornumber is %i\n", MAX_SENSOR, SensorNumber);
		return false;
	}
	USS_OUT("Rb_CheckObject: Sensor number wasn't found in list. Current sensornumber is %i\n", SensorNumber);
	return false;
}

void RbUltraSonics::Rb_WriteObject(int8_t SensorNumber, int32_t GlobalID, UssPoint NearPnt,	double NearPntDistance, double NearPntAlpha, double IncidentAlpha, double IncidentBeta, double Height)
{
	tSensor SensorID = SensorIdToTSensor(SensorNumber);

	/*Check if the sensor number is within the allowed borders*/
	if (SensorNumber <= MAX_SENSOR && SensorNumber >= 1)
	{
		for (auto it_sens = m_SensorList.begin(); it_sens != m_SensorList.end(); it_sens++)
		{
			if (SensorID == (*it_sens)->GetSensorID())
			{
			(*it_sens)->AddObject(GlobalID, NearPnt, NearPntDistance, NearPntAlpha, IncidentAlpha, IncidentBeta, Height);
			}
		}
	}
	else
	{
	USS_OUT("Rb_WriteObject: Sensor number has to be between 1 and %i. Current sensornumber is %i\n", MAX_SENSOR, SensorNumber);
	}
}

void RbUltraSonics::Rb_Calc(uint64_t Timestamp_us)
{
	//USS_DBG("Rb_Calc called!\n");
	/*Set array to zero*/
	Init_SensorData2UssSimulator();

	t_SensorData CurrentSensorData[MAX_SENSOR];
	std::vector<UssObjectData> curObj;
	uint8_t currObjCnt, sens, obj;
	uint32_t UssThreadState = 0;
	tSensor curSensor;

	/*Initialize CurrentSensorData array*/
	for (sens = 0; sens < MAX_SENSOR; sens++)
	{
		CurrentSensorData[sens].Position_x = 0;
		CurrentSensorData[sens].Position_y = 0;
		CurrentSensorData[sens].Position_z = 0;
		CurrentSensorData[sens].Orientation_y = 0;
		CurrentSensorData[sens].Orientation_z = 0;
		CurrentSensorData[sens].Aperture_Hoz = 0;
		CurrentSensorData[sens].Aperture_Vert = 0;
		CurrentSensorData[sens].Range = 0;
		CurrentSensorData[sens].SensorState = SENSOR_INACTIVE;

		for (obj = 0; obj < MAX_OBJECTS; obj++)
		{
			CurrentSensorData[sens].AllObjectList[obj].GlobalId = 0;
			CurrentSensorData[sens].AllObjectList[obj].Height = 0;
			CurrentSensorData[sens].AllObjectList[obj].NearPntDistance = 0;
			CurrentSensorData[sens].AllObjectList[obj].NearPntAlpha = 0;
			CurrentSensorData[sens].AllObjectList[obj].IncidentAlpha = 0;
			CurrentSensorData[sens].AllObjectList[obj].IncidentBeta = 0;
		}
	}

	if (!m_SensorList.empty())
	{
		for (auto it_sens = m_SensorList.begin(); it_sens != m_SensorList.end(); it_sens++)
		{
			if ((*it_sens)->GetSensorState() == SENSOR_INACTIVE) continue; // when the sensor is not active we do not need to handle it further
			currObjCnt = 0;
			curSensor = (*it_sens)->GetSensorID();
			CurrentSensorData[curSensor].Position_x = (*it_sens)->GetSensorCoordinates().GetPositionX();
			CurrentSensorData[curSensor].Position_y = (*it_sens)->GetSensorCoordinates().GetPositionY();
			CurrentSensorData[curSensor].Position_z = (*it_sens)->GetSensorCoordinates().GetPositionZ();
			CurrentSensorData[curSensor].Orientation_y = (*it_sens)->GetSensorCoordinates().GetRotationY();
			CurrentSensorData[curSensor].Orientation_z = (*it_sens)->GetSensorCoordinates().GetRotationZ();
			CurrentSensorData[curSensor].Aperture_Hoz = (*it_sens)->GetSensorApertureHorizontal();
			CurrentSensorData[curSensor].Aperture_Vert = (*it_sens)->GetSensorApertureVertical();
			CurrentSensorData[curSensor].Range = (*it_sens)->GetSensorRange();
			CurrentSensorData[curSensor].HeightForHeightClassification = (*it_sens)->GetHeightForHeightClassification();
			CurrentSensorData[curSensor].SensorState = (*it_sens)->GetSensorState();

			curObj = (*it_sens)->GetObjects();
			if (!curObj.empty())
			{
				for (std::vector<UssObjectData>::iterator it_obj = curObj.begin(); it_obj != curObj.end(); it_obj++)
				{
					CurrentSensorData[curSensor].AllObjectList[currObjCnt].GlobalId = it_obj->GlobalId;
					CurrentSensorData[curSensor].AllObjectList[currObjCnt].Height = it_obj->Height;
					CurrentSensorData[curSensor].AllObjectList[currObjCnt].NearPnt[0] = it_obj->NearPnt[0];
					CurrentSensorData[curSensor].AllObjectList[currObjCnt].NearPnt[1] = it_obj->NearPnt[1];
					CurrentSensorData[curSensor].AllObjectList[currObjCnt].NearPnt[2] = it_obj->NearPnt[2];
					CurrentSensorData[curSensor].AllObjectList[currObjCnt].NearPntDistance = it_obj->NearPntDistance;
					CurrentSensorData[curSensor].AllObjectList[currObjCnt].NearPntAlpha = it_obj->NearPntAlpha;
					CurrentSensorData[curSensor].AllObjectList[currObjCnt].IncidentAlpha = it_obj->IncidentAlpha;
					CurrentSensorData[curSensor].AllObjectList[currObjCnt].IncidentBeta = it_obj->IncidentBeta;
					currObjCnt++;
				}
			}
		}
	}

	m_SensorData2MultiTester.TimeStamp = Timestamp_us;
	p_SensorModell->CalcEchoData(CurrentSensorData, &m_SensorData2MultiTester);
	
	if (m_UssSimulatorAvailable)
	{
		p_UssSimulator->Transfer(&m_SensorData2MultiTester);

		if (m_SensorFiringCheckState)
		{
			if (!m_SensorFiringCheckBuffer)
			{
				std::fill(m_SensorFiringLastCorrectUpdate, m_SensorFiringLastCorrectUpdate + MAX_SENSOR, Timestamp_us);
				m_SensorFiringCheckBuffer = true;
			}
			if (Timestamp_us > (m_SensorFiringStateUpdateTimeStamp + UPDATE_RATE_SENSOR_STATE_us))
			{
				if (p_UssSimulator->GetFiringStatus() != USSSIMULATOR_OK)
				{
					USS_OUT("Error while queue the msg for GetFiringStatus\n");
				}
			}
			m_SensorFiringStateFront = p_UssSimulator->GetSensorFiringState(FRONT_CLUSTER);
			m_SensorFiringStateRear = p_UssSimulator->GetSensorFiringState(REAR_CLUSTER);

			uint8_t l_SensorStateErrorCnt = 0;

			m_SensorFiringStateUpdateTimeStamp = p_UssSimulator->GetSensorFiringStateUpdateTime();
			
			for (uint8_t sensor = 0; sensor < MAX_SENSOR / 2; sensor++)
			{
				/* Front sensor cluster */
				if ((CurrentSensorData[sensor].SensorState == SENSOR_ACTIVE && ((m_SensorFiringStateFront & p_UssSimulator->GetFiringStateMask(sensor)) == p_UssSimulator->GetFiringStateMask(sensor))) ||
					(CurrentSensorData[sensor].SensorState == SENSOR_INACTIVE && ((m_SensorFiringStateFront & p_UssSimulator->GetFiringStateMask(sensor)) == 0)))
				{
					m_SensorFiringLastCorrectUpdate[sensor] = m_SensorFiringStateUpdateTimeStamp;
				}
				else
				{
					//else keep the last value
				}

				if (Timestamp_us - m_SensorFiringLastCorrectUpdate[sensor] > m_firingchecktimeout_us)
				{
					//USS_OUT("Sensor %d error at time %llu. Last Update: %llu l_Timeout: %llu\n", sensor, m_SensorData2MultiTester.TimeStamp, m_SensorFiringLastCorrectUpdate[sensor], Timestamp_us - m_SensorFiringLastCorrectUpdate[sensor]);
					l_SensorStateErrorCnt++;
				}

				/* Rear Sensor cluster */
				if ((CurrentSensorData[sensor+MAX_SENSOR/2].SensorState == SENSOR_ACTIVE && ((m_SensorFiringStateRear & p_UssSimulator->GetFiringStateMask(sensor)) == p_UssSimulator->GetFiringStateMask(sensor))) ||
					(CurrentSensorData[sensor + MAX_SENSOR / 2].SensorState == SENSOR_INACTIVE && ((m_SensorFiringStateRear & p_UssSimulator->GetFiringStateMask(sensor)) == 0)))
				{ 
					m_SensorFiringLastCorrectUpdate[sensor + MAX_SENSOR / 2] = m_SensorFiringStateUpdateTimeStamp;
				}
				else
				{
					//else keep the last value
				}
			
				if (Timestamp_us - m_SensorFiringLastCorrectUpdate[sensor + MAX_SENSOR / 2] > m_firingchecktimeout_us)
				{
					//USS_OUT("Sensor %d error at time %llu. Last Update: %llu l_Timeout: %llu\n", sensor + MAX_SENSOR / 2, m_SensorData2MultiTester.TimeStamp, m_SensorFiringLastCorrectUpdate[sensor + MAX_SENSOR / 2], Timestamp_us - m_SensorFiringLastCorrectUpdate[sensor + MAX_SENSOR / 2]);
					l_SensorStateErrorCnt++;
				}


			}
			if (l_SensorStateErrorCnt >= MAX_SENSOR) // Set the error if no sensor is sending the correct status
			{
				Rb_SetStatus(USSSIMULATOR_SENSOR_STATUS_ERR);
			}
			
		}
		else
		{
			std::fill(m_SensorFiringLastCorrectUpdate, m_SensorFiringLastCorrectUpdate + MAX_SENSOR, Timestamp_us);
			m_SensorFiringCheckBuffer = false;
		}

		UssThreadState = p_UssSimulator->GetThreadState();
		if (UssThreadState != 0x00000)
		{
			if ((UssThreadState & ThreadState_MissingMsgErr) == ThreadState_MissingMsgErr)
			{
				Rb_SetStatus(USSSIMULATOR_COM_ERR);
			}
			else if ((UssThreadState & ThreadState_OverrunsErr) == ThreadState_OverrunsErr)
			{
				Rb_SetStatus(USSSIMULATOR_THREAD_ERR);
			}
			else if ((UssThreadState & ThreadState_NoDataRecErr) == ThreadState_NoDataRecErr)
			{
				Rb_SetStatus(USSSIMULATOR_NO_UPDATE_ERR);
			}
			else if ((UssThreadState & ThreadState_MissingMsgWarn) == ThreadState_MissingMsgWarn)
			{
				Rb_SetStatus(USSSIMULATOR_COM_WARN);
			}
			else if ((UssThreadState & ThreadState_OverrunsWarn) == ThreadState_OverrunsWarn)
			{
				Rb_SetStatus(USSSIMULATOR_THREAD_WARN);
			}
			else
			{
				Rb_SetStatus(USSSIMULATOR_INVAL_ARG_ERR);
			}
		}
	}
}

tMultiTesterDataIF RbUltraSonics::Rb_GetSensorData2MultiTester(void)
{
	return m_SensorData2MultiTester;
}

uint8_t RbUltraSonics::Rb_AddSensor(int8_t SensorNumber, double Position_x, double Position_y, double Position_z,
	double Orientation_y, double Orientation_z, double Range, double Aperture_Hoz, double Aperture_Vert)
{
	tSensor SensorID = SensorIdToTSensor(SensorNumber);
	/*Check if the sensor number is within the allowed borders*/
	if (SensorNumber <= MAX_SENSOR && SensorNumber >= 1)
	{
		/*Check if the sensor number is already assigned*/
		if (m_SensorList.empty() == false)
		{
			for (auto it_sens = m_SensorList.begin(); it_sens != m_SensorList.end(); it_sens++)
			{
				if (SensorID == (*it_sens)->GetSensorID())
				{
					USS_OUT("Rb_AddSensor: Sensor number already assigned. Newer information ignored!\n");
					return 2;
				}
			}
		}
		/*Create new sensor and add to list*/
		m_SensorList.push_back(std::make_unique<UssSensor>(SensorID, Position_x, Position_y, Position_z, Orientation_y, Orientation_z, Range, Aperture_Hoz, Aperture_Vert));
		return 0;
	}
	else
	{
		USS_OUT("Rb_AddSensor: Sensor number has to be between 1 and %i. Current sensornumber is %i\n", MAX_SENSOR, SensorNumber);
		return 1;
	}

}

uint8_t RbUltraSonics::Rb_AddSensor(int8_t SensorNumber, double Position_x, double Position_y, double Position_z,
	double Orientation_y, double Orientation_z, double Range, double Aperture_Hoz, double Aperture_Vert, 
	std::string Description, double HeightForHeightClassification, eSensorState SensorState)
{
	tSensor SensorID = SensorIdToTSensor(SensorNumber);
	/*Check if the sensor number is within the allowed borders*/
	if (SensorNumber <= MAX_SENSOR && SensorNumber >= 1)
	{
		/*Check if the sensor number is already assigned*/
		if (m_SensorList.empty() == false)
		{
			for (auto it_sens = m_SensorList.begin(); it_sens != m_SensorList.end(); it_sens++)
			{
				if (SensorID == (*it_sens)->GetSensorID())
				{
					USS_OUT("Rb_AddSensor: Sensor number already assigned. Newer information ignored!\n");
					return 2;
				}
			}
		}
		/*Create new sensor and add to list*/
		m_SensorList.push_back(std::make_unique<UssSensor>(SensorID, Position_x, Position_y, Position_z, Orientation_y, Orientation_z, Range, Aperture_Hoz, Aperture_Vert, Description, HeightForHeightClassification, SensorState));
		return 0;
	}
	else
	{
		USS_OUT("Rb_AddSensor: Sensor number has to be between 1 and %i. Current sensornumber is %i\n", MAX_SENSOR, SensorNumber);
		return 1;
	}

}

uint8_t RbUltraSonics::Rb_RemoveSensor(int8_t SensorNumber)
{
	tSensor SensorID = SensorIdToTSensor(SensorNumber);

	if (!m_SensorList.empty())
	{
		/*Check if the sensor number is within the allowed borders*/
		if (SensorNumber <= MAX_SENSOR && SensorNumber >= 1)
		{
			/*Check if the sensor number is in list*/
			for (auto it_sens = m_SensorList.begin(); it_sens != m_SensorList.end(); it_sens++)
			{
				if (SensorID == (*it_sens)->GetSensorID())
				{
					m_SensorList.erase(it_sens);
					return 0;
				}
			}

			USS_OUT("Rb_RemoveSensor: Sensor not found in list. Nothing removed!\n");
			return 2;
		}
		else
		{
			USS_OUT("Rb_RemoveSensor: Sensor number has to be between 1 and %i. Current sensornumber is %i\n", MAX_SENSOR, SensorNumber);
			return 1;
		}
		
	}
	return 3;
}

uint8_t RbUltraSonics::Rb_SetSensorState(int8_t SensorNumber, eSensorState SensorState)
{
	tSensor SensorID = SensorIdToTSensor(SensorNumber);

	if (!m_SensorList.empty())
	{
		/*Check if the sensor number is within the allowed borders*/
		if (SensorNumber <= MAX_SENSOR && SensorNumber >= 1)
		{
			/*Check if the sensor number is in list*/
			for (auto it_sens = m_SensorList.begin(); it_sens != m_SensorList.end(); it_sens++)
			{
				if (SensorID == (*it_sens)->GetSensorID())
				{
					(*it_sens)->SetSensorState(SensorState);
					return 0;
				}
			}

            USS_OUT("Rb_SetSensorState: Sensor not found in list. No sensor state set!\n");
			return 2;
		}
		else
		{
            USS_OUT("Rb_SetSensorState: Sensor number has to be between 1 and %i. Current sensornumber is %i\n", MAX_SENSOR, SensorNumber);
			return 1;
		}
		
	}
	return 3;
}


int8_t RbUltraSonics::Rb_GetSensorFiringState(int8_t SensorNumber)
{
	if (!m_UssSimulatorAvailable)
	{
		return 0;
	}
	if (SensorNumber <= MAX_SENSOR / 2) //Front cluster
	{
		return ((m_SensorFiringStateFront & p_UssSimulator->GetFiringStateMask(SensorNumber - 1)) == p_UssSimulator->GetFiringStateMask(SensorNumber - 1));
	}
	else if (SensorNumber <= MAX_SENSOR) //Rear cluster
	{
		return ((m_SensorFiringStateRear & p_UssSimulator->GetFiringStateMask(SensorNumber - 1)) == p_UssSimulator->GetFiringStateMask(SensorNumber - 1));
	}
	else
	{
		USS_OUT("Rb_GetSensorFiringState: Sensor number has to be between 1 and %i. Current sensornumber is %i\n", MAX_SENSOR, SensorNumber);
		return 0;
	}
	return 0;
}

int8_t RbUltraSonics::Rb_SensorFaults(tUssSensorErrorEnum ui8_SensorFaultArray[MAX_SENSOR])
{
	uint8_t sensor;

	uint8_t statusFrameNo[MAX_SENSOR];
	bool sensorConfigChanged = false;
	bool sensorComErrChanged = false;

	for (sensor = 0; sensor < MAX_SENSOR; sensor++)
	{
		Reset_SensorFaultData(sensor);
		statusFrameNo[sensor] = 0;

		switch (ui8_SensorFaultArray[sensor])
		{
		case NoError:
			//nothing to do as values are set to default above
			//USS_DBG("Rb_SensorFaults: MANIPULATION_DEFAULT\n");
			break;
		case SHORT_TO_GROUND:
			m_SensorData2MultiTester.SensorConfig[sensor].SensorDataLineError = SHORT_TO_GROUND;
			//USS_DBG("Rb_SensorFaults: MANIPULATION_TO_GND\n");
			break;
		case SHORT_TO_SUPPLY:
			m_SensorData2MultiTester.SensorConfig[sensor].SensorDataLineError = SHORT_TO_SUPPLY;
			//USS_DBG("Rb_SensorFaults: MANIPULATION_TO_SUPPLY\n");
			break;
		case SENSOR_DISTURBED:
			//USS_DBG("Rb_SensorFaults: MANIPULATION_DISTURBENS\n");
			m_SensorData2MultiTester.SensorData[sensor].Clutter = 55;
			m_SensorData2MultiTester.SensorData[sensor].Noise = 55;
			m_SensorData2MultiTester.SensorData[sensor].CWLevel = 55;
			statusFrameNo[sensor] = 1;
			break;
		case SENSOR_COM_LINE_OPEN:
			m_SensorData2MultiTester.SensorConfig[sensor].SensorDataLineError = SENSOR_COM_LINE_OPEN;
			//USS_DBG("Rb_SensorFaults: MANIPULATION_OPEN\n");
			break;
		case SENSOR_BLOCKED:
			//USS_DBG("Rb_SensorFaults: MANIPULATION_BLOCKAGE\n");
			m_SensorData2MultiTester.SensorData[sensor].Impedance.dZmin = 50;
			m_SensorData2MultiTester.SensorData[sensor].Impedance.dFmin = 50;
			statusFrameNo[sensor] = 3;
			break;
		case SENSOR_VERSION_WRONG:
			if (m_SensorTypeDefault[sensor] == CONF_USS_SENSOR_TYPE_6_5)
			{
				m_SensorData2MultiTester.SensorConfig[sensor].Config.SensorType = CONF_USS_SENSOR_TYPE_6_0;
			}
			else
			{
				m_SensorData2MultiTester.SensorConfig[sensor].Config.SensorType = CONF_USS_SENSOR_TYPE_6_5;
			}
			break;
		case SENSOR_COMMUNICATION_ERROR:
			m_SensorData2MultiTester.SensorConfig[sensor].SensorCommunicationError = SENSOR_COMMUNICATION_ERROR;
			//USS_DBG("Rb_SensorFaults: MANIPULATION_COM\n");
			break;
		case SENSOR_INCORRECT_SENDPULSE:
			m_SensorData2MultiTester.SensorData[sensor].Impedance.dZenv = 210;
			statusFrameNo[sensor] = 3;
			break;
		case SENSOR_OUT_OF_SYNC:
			m_SensorData2MultiTester.SensorConfig[sensor].SensorCommunicationError = SENSOR_OUT_OF_SYNC;
			break;
		case SENSOR_INTERNAL_ERROR:
			m_SensorData2MultiTester.SensorData[sensor].Frame1Error.ADC_Test = 1;
			statusFrameNo[sensor] = 1;
			break;
		case SENSORCLUSTER_OVERCURRENT: //Overcurrent only is valid for the whole cluster -> wrong interface used -> default case
		default:
			USS_OUT("Set sensor faults - For sensor %d: wrong parameter. Allowed values 0,1,2,3,4,5,6,8,9,10,11 \n", sensor + 1);
			break;
		}
	}

	for (sensor = 0; sensor < MAX_SENSOR; sensor++)
	{
		if (m_CommunicationLineErrorsBuffer[sensor] != m_SensorData2MultiTester.SensorConfig[sensor].SensorDataLineError)
		{
			p_UssSimulator->SensorDataLineError(m_SensorData2MultiTester, sensor);
			m_CommunicationLineErrorsBuffer[sensor] = m_SensorData2MultiTester.SensorConfig[sensor].SensorDataLineError;
		}
		
		if (m_StatusFrameBuffer[sensor] != statusFrameNo[sensor])
		{
			if (statusFrameNo[sensor] == 3 || m_StatusFrameBuffer[sensor] == 3)
			{
				//reset the old status frame if set before
				if ((statusFrameNo[sensor] != m_StatusFrameBuffer[sensor]) && m_StatusFrameBuffer[sensor] != 0)
				{
					p_UssSimulator->StatusFrameAccess(m_SensorData2MultiTester, sensor, 1);
					m_StatusFrameBuffer[sensor] = statusFrameNo[sensor];
				}

				//set the new status frame
				if (m_StatusFrameValueBuffer[sensor] != ui8_SensorFaultArray[sensor])
				{
					m_StatusFrameValueBuffer[sensor] = ui8_SensorFaultArray[sensor];
					m_StatusFrameBuffer[sensor] = statusFrameNo[sensor];
					p_UssSimulator->StatusFrameAccess(m_SensorData2MultiTester, sensor, 3);
					p_UssSimulator->StatusFrameAccess(m_SensorData2MultiTester, sensor, 1);
				}
			}
			else if (statusFrameNo[sensor] == 1 || m_StatusFrameBuffer[sensor] == 1)
			{
				//reset the old status frame if set before
				if ((statusFrameNo[sensor] != m_StatusFrameBuffer[sensor]) && m_StatusFrameBuffer[sensor] != 0)
				{
					p_UssSimulator->StatusFrameAccess(m_SensorData2MultiTester, sensor, 3);
					m_StatusFrameBuffer[sensor] = statusFrameNo[sensor];
				}

				//set the new status frame
				if (m_StatusFrameValueBuffer[sensor] != ui8_SensorFaultArray[sensor])
				{
					m_StatusFrameValueBuffer[sensor] = ui8_SensorFaultArray[sensor];
					m_StatusFrameBuffer[sensor] = statusFrameNo[sensor];
					p_UssSimulator->StatusFrameAccess(m_SensorData2MultiTester, sensor, 1);
				}
			}
		}
		
		if (m_SensorTypeBuffer[sensor] != m_SensorData2MultiTester.SensorConfig[sensor].Config.SensorType)
		{
			m_SensorTypeBuffer[sensor] = (eUssSensorTypesConfiguration)m_SensorData2MultiTester.SensorConfig[sensor].Config.SensorType;
			sensorConfigChanged = true;
		}


		if (m_SensorCommunicationErrorBuffer[sensor] != m_SensorData2MultiTester.SensorConfig[sensor].SensorCommunicationError)
		{			
			m_SensorCommunicationErrorBuffer[sensor] = m_SensorData2MultiTester.SensorConfig[sensor].SensorCommunicationError;
			sensorComErrChanged = true;
		}
	}
	if (sensorConfigChanged)
	{
		p_UssSimulator->WriteSensorConfiguration(m_SensorData2MultiTester);
	}

	if (sensorComErrChanged)
	{
		p_UssSimulator->SensorCommunicationError(m_SensorData2MultiTester);
	}

	return USSSIMULATOR_OK;
}

int8_t RbUltraSonics::Rb_SensorClusterFaults(tUssSensorErrorEnum SensorClusterErrors[2])
{

	m_SensorData2MultiTester.ShortVSEtoGND_Front = 0;
	m_SensorData2MultiTester.ShortVSEtoGND_Rear = 0;
	m_SensorData2MultiTester.Overcurrent_Front = 0;
	m_SensorData2MultiTester.Overcurrent_Rear = 0;

	if (SensorClusterErrors[FRONT_CLUSTER] == SHORT_TO_SUPPLY)
	{
		m_SensorData2MultiTester.ShortVSEtoGND_Front = 1;
	}

	if (SensorClusterErrors[FRONT_CLUSTER] == SENSORCLUSTER_OVERCURRENT)
	{
		m_SensorData2MultiTester.Overcurrent_Front = 1;
	}

	if (SensorClusterErrors[REAR_CLUSTER] == SHORT_TO_SUPPLY)
	{
		m_SensorData2MultiTester.ShortVSEtoGND_Rear = 1;
	}

	if (SensorClusterErrors[REAR_CLUSTER] == SENSORCLUSTER_OVERCURRENT)
	{
		m_SensorData2MultiTester.Overcurrent_Rear = 1;
	}

	if (m_ShortVSEtoGndBuffer[0] != m_SensorData2MultiTester.ShortVSEtoGND_Front)
	{
		p_UssSimulator->ShortVseToGnd(m_SensorData2MultiTester);
		m_ShortVSEtoGndBuffer[0] = m_SensorData2MultiTester.ShortVSEtoGND_Front;
	}

	if (m_ShortVSEtoGndBuffer[1] != m_SensorData2MultiTester.ShortVSEtoGND_Rear)
	{
		p_UssSimulator->ShortVseToGnd(m_SensorData2MultiTester);
		m_ShortVSEtoGndBuffer[1] = m_SensorData2MultiTester.ShortVSEtoGND_Rear;
	}

	if (m_OvercurrentBuffer[0] != m_SensorData2MultiTester.Overcurrent_Front)
	{
		p_UssSimulator->SetOvercurrent(m_SensorData2MultiTester);
		m_OvercurrentBuffer[0] = m_SensorData2MultiTester.Overcurrent_Front;
	}

	if (m_OvercurrentBuffer[1] != m_SensorData2MultiTester.Overcurrent_Rear)
	{
		p_UssSimulator->SetOvercurrent(m_SensorData2MultiTester);
		m_OvercurrentBuffer[1] = m_SensorData2MultiTester.Overcurrent_Rear;
	}

	return USSSIMULATOR_OK;
}

void RbUltraSonics::Rb_ClearAllSensorFaults(void)
{
	if (!m_UssSimulatorAvailable)
	{
		return;
	}
	/* disable all possible sensor faults */

	// Reset error buffers
	std::fill(m_StatusFrameValueBuffer, m_StatusFrameValueBuffer + MAX_SENSOR, 0);
	std::fill(m_CommunicationLineErrorsBuffer, m_CommunicationLineErrorsBuffer + MAX_SENSOR, NoError);
	std::fill(m_SensorCommunicationErrorBuffer, m_SensorCommunicationErrorBuffer + MAX_SENSOR, NoError);
	std::fill(m_StatusFrameBuffer, m_StatusFrameBuffer + MAX_SENSOR, 0);
	std::fill(m_SensorTypeBuffer, m_SensorTypeBuffer + MAX_SENSOR, CONF_USS_SENSOR_TYPE_6_5);
	std::fill(m_ShortVSEtoGndBuffer, m_ShortVSEtoGndBuffer + 2, 0);
	std::fill(m_OvercurrentBuffer, m_OvercurrentBuffer + 2, 0);

	for (uint8_t sensor = 0; sensor < MAX_SENSOR; sensor++)
	{
		Reset_SensorFaultData(sensor);
		p_UssSimulator->SensorDataLineError(m_SensorData2MultiTester, sensor);
		p_UssSimulator->StatusFrameAccess(m_SensorData2MultiTester, sensor, 3);
		p_UssSimulator->StatusFrameAccess(m_SensorData2MultiTester, sensor, 1);
	}

	m_SensorData2MultiTester.ShortVSEtoGND_Front = 0;
	m_SensorData2MultiTester.ShortVSEtoGND_Rear = 0;
	m_SensorData2MultiTester.Overcurrent_Front = 0;
	m_SensorData2MultiTester.Overcurrent_Rear = 0;

	p_UssSimulator->SetOvercurrent(m_SensorData2MultiTester);
	p_UssSimulator->ShortVseToGnd(m_SensorData2MultiTester);
	p_UssSimulator->SensorCommunicationError(m_SensorData2MultiTester);
}

void RbUltraSonics::Rb_ClearSensorList(void)
{
	if (!m_SensorList.empty())
	{
		for (uint8_t sens = 0; sens < MAX_SENSOR; sens++)
		{
			Rb_RemoveSensor(sens+1);
		}
		m_SensorList.clear();
	}
}

void RbUltraSonics::Rb_ClearObjectList(int8_t SensorNumber)
{
	tSensor SensorID = SensorIdToTSensor(SensorNumber);

	if (m_SensorList.empty())
	{
		return;
	}

	/*Check if the sensor number is within the allowed borders*/
	if (SensorNumber <= MAX_SENSOR && SensorNumber >= 1)
	{
		/*Check if the sensor number is in list*/
		for (auto it_sens = m_SensorList.begin(); it_sens != m_SensorList.end(); it_sens++)
		{
			if (SensorID == (*it_sens)->GetSensorID())
			{
				(*it_sens)->ClearObjects();
				return;
			}
		}
		//USS_DBG("Rb_ClearObjectList: Sensor not found in list. Nothing removed!\n");
	}
	else
	{
		USS_OUT("Rb_ClearObjectList: Sensor number has to be between 1 and %i. Current sensornumber is %i\n", MAX_SENSOR, SensorNumber);
	}
}

uint8_t RbUltraSonics::Rb_Terminate(void)
{
	if (m_UssSimulatorAvailable)
	{
		p_UssSimulator->ResetThreadState();
		return p_UssSimulator->CloseUssSimulator();
	}
	return USSSIMULATOR_OK;
}

Rb_StatusList RbUltraSonics::Rb_GetStatus(void)
{
	return m_status;
}

void RbUltraSonics::Rb_ResetState(void)
{
	m_status = USS_NO_ERROR;
	if (m_UssSimulatorAvailable)
	{
		p_UssSimulator->ResetThreadState();
	}
}

void RbUltraSonics::Rb_SetStatus(eUssSimulatorState state)
{
	switch (state)
	{
	case USSSIMULATOR_OK:
		m_status = USS_NO_ERROR;
		break;
	case USSSIMULATOR_INVAL_ARG_ERR:
		m_status = ERR_INVALID_ARGUMENT;
		break;
	case USSSIMULATOR_THREAD_ERR:
		m_status = ERR_USSSIM_COMMUNICATION_THREAD_ERR;
		break;
	case USSSIMULATOR_THREAD_WARN:
		m_status = ERR_USSSIM_COMMUNICATION_THREAD_WARN;
		break;
	case USSSIMULATOR_QUEUE_ERR:
		m_status = ERR_INVALID_ARGUMENT;
		break;
	case USSSIMULATOR_MUTEX_ERR:
		m_status = ERR_INVALID_ARGUMENT;
		break;
	case USSSIMULATOR_COM_ERR:
		m_status = ERR_USSSIM_COMMUNICATION_NO_RESPONSE;
		break;
	case USSSIMULATOR_COM_WARN:
		m_status = ERR_USSSIM_COMMUNICATION_WARN;
		break;
	case USSSIMULATOR_COM_SOCKET_ERR:
		m_status = ERR_USSSIM_COMMUNICATION_SOCKET_ERR;
		break;
	case USSSIMULATOR_COM_SEND_ERR:
		m_status = ERR_USSSIM_COMMUNICATION_NOT_SENT;
		break;
	case USSSIMULATOR_COM_RECV_ERR:
		m_status = ERR_USSSIM_COMMUNICATION_NO_RESPONSE;
		break;
	case USSSIMULATOR_DEV_ERR:
		m_status = ERR_USSSIM_DEVICE_ERR;
		break;
	case USSSIMULATOR_BUSY_ERR:
		m_status = ERR_USSSIM_COMMUNICATION_STILL_RUNNING;
		break;
	case USSSIMULATOR_SENSOR_STATUS_ERR:
		m_status = ERR_SENSORDATA_WRONG_STATUS;
		break;
	case USSSIMULATOR_NO_UPDATE_ERR:
		m_status = ERR_USSSIM_COMMUNICATION_NO_UPDATE;
		break;
	case USSSIMULATOR_THREAD_ERR_HEALED:
		m_status = USS_CLEAR_ERROR;
		break;
	default:
		m_status = ERR_UNEXPECTED_ERROR;
		break;
	}

}



void RbUltraSonics::Init_SensorData2UssSimulator(void)
{
	int k, l;
	// init multi tester data array
	for (k = 0; k < MAX_SENSOR; k++)
	{
		for (l = 0; l < MAX_ECHO; l++)
		{
			m_SensorData2MultiTester.SensorData[k].EchoList[l].Amplitude = 0;
			m_SensorData2MultiTester.SensorData[k].EchoList[l].Correlation = 0;
			m_SensorData2MultiTester.SensorData[k].EchoList[l].Dist = 0;
			m_SensorData2MultiTester.SensorData[k].EchoList[l].Height = 2;
			m_SensorData2MultiTester.SensorData[k].EchoList[l].Type = NotDef;
			m_SensorData2MultiTester.SensorData[k].EchoList[l].Sender = SInval;
		}
		Reset_SensorFaultData(k);
	}
	m_SensorData2MultiTester.TimeStamp = 0;
}

void RbUltraSonics::Reset_SensorFaultData(uint8_t sensor)
{
	m_SensorData2MultiTester.SensorData[sensor].Clutter = 30;
	m_SensorData2MultiTester.SensorData[sensor].Noise = 22;
	m_SensorData2MultiTester.SensorData[sensor].CWLevel = 0;
	m_SensorData2MultiTester.SensorData[sensor].Impedance.dFmin = 0;// -29;
	m_SensorData2MultiTester.SensorData[sensor].Impedance.dZenv = 0;
	m_SensorData2MultiTester.SensorData[sensor].Impedance.dZmin = 0;//-28;
	m_SensorData2MultiTester.SensorData[sensor].Impedance.impTemp = 40;
	m_SensorData2MultiTester.SensorData[sensor].Frame1Error.ADC_Test = 0;
	m_SensorData2MultiTester.SensorData[sensor].Frame1Error.Bus_Err = 0;
	m_SensorData2MultiTester.SensorData[sensor].Frame1Error.DRV_Stg = 0;
	m_SensorData2MultiTester.SensorData[sensor].Frame1Error.DSP_Init = 0;
	m_SensorData2MultiTester.SensorData[sensor].Frame1Error.DSP_SM = 0;
	m_SensorData2MultiTester.SensorData[sensor].Frame1Error.Lock_EOL = 0;
	m_SensorData2MultiTester.SensorData[sensor].Frame1Error.MEM_Test = 0;
	m_SensorData2MultiTester.SensorData[sensor].Frame1Error.OTP_CRC = 0;
	m_SensorData2MultiTester.SensorData[sensor].Frame1Error.PAR_Err = 0;

	m_SensorData2MultiTester.SensorData[sensor].NearRangeData.spAvgE = 0;
	m_SensorData2MultiTester.SensorData[sensor].NearRangeData.spRingDownT = 0;
	m_SensorData2MultiTester.SensorConfig[sensor].SensorDataLineError = NoError;
	m_SensorData2MultiTester.SensorConfig[sensor].Config.SensorType = m_SensorTypeDefault[sensor];
	m_SensorData2MultiTester.SensorConfig[sensor].SensorCommunicationError = NoError;
}

void RbUltraSonics::Rb_GetStatusMessage(Rb_StatusList lStatus, Rb_FcnList lFcn, std::string & lStatusMessage)
{
	switch (lStatus)
	{
		case ERR_SENSORLIST_INCOMPLETE:
			if (lFcn == RB_TESTRUN_START)
				lStatusMessage = "Rb_TestRun_Start: Number of Sensors is not correct!";
			break;

		case ERR_USSSIM_COMMUNICATION_STILL_RUNNING:
			if (lFcn == RB_INIT)
				lStatusMessage = "Rb_Init: UssSimulator is still running!";
			break;
		default:
			break;

	}
}

bool RbUltraSonics::Rb_MultiTester_isRunning(void)
{
	return p_UssSimulator->isRunning();
}

void RbUltraSonics::WriteSensorConfiguration(void)
{
	int sensor;

	//Default settings
	for (sensor = 0; sensor < MAX_SENSOR; sensor++)
		m_SensorData2MultiTester.SensorConfig[sensor].Config.SensorType = CONF_USS_SENSOR_TYPE_6_5;
	for (sensor = 0; sensor < MAX_SENSOR; sensor++)
		m_SensorData2MultiTester.SensorConfig[sensor].Config.SiliconType = CONF_USS_SENSOR_SILICON_CC;

	//Sensor type configuration
	//All front sensors
	if (m_SensorCfg.FrontSensorsType != USS_SENSOR_TYPE_6_5)
	{
		for (sensor = 0;sensor < MAX_SENSOR/2;sensor++)
		{
			switch (m_SensorCfg.FrontSensorsType)
			{
			case USS_SENSOR_NOT_USED:
				m_SensorData2MultiTester.SensorConfig[sensor].Config.SensorType = CONF_USS_SENSOR_NOT_USED;
				break;
			case USS_SENSOR_TYPE_6_0:
				m_SensorData2MultiTester.SensorConfig[sensor].Config.SensorType = CONF_USS_SENSOR_TYPE_6_0;
				break;
			case USS_SENSOR_TYPE_6_1:
				m_SensorData2MultiTester.SensorConfig[sensor].Config.SensorType = CONF_USS_SENSOR_TYPE_6_1;
				break;
			case USS_SENSOR_TYPE_6_5:
				m_SensorData2MultiTester.SensorConfig[sensor].Config.SensorType = CONF_USS_SENSOR_TYPE_6_5;
				break;
			case USS_SENSOR_TYPE_6_50:
				m_SensorData2MultiTester.SensorConfig[sensor].Config.SensorType = CONF_USS_SENSOR_TYPE_6_50;
				break;
			case USS_SENSOR_TYPE_6_51:
				m_SensorData2MultiTester.SensorConfig[sensor].Config.SensorType = CONF_USS_SENSOR_TYPE_6_51;
				break;
			default:
				m_SensorData2MultiTester.SensorConfig[sensor].Config.SensorType = CONF_USS_SENSOR_NOT_USED;
				break;
			}
		}
	}
	//All rear sensors
	if (m_SensorCfg.RearSensorsType != USS_SENSOR_TYPE_6_5)
	{
		for (sensor = MAX_SENSOR/2; sensor < MAX_SENSOR; sensor++)
		{
			switch (m_SensorCfg.RearSensorsType)
			{
			case USS_SENSOR_NOT_USED:
				m_SensorData2MultiTester.SensorConfig[sensor].Config.SensorType = CONF_USS_SENSOR_NOT_USED;
				break;
			case USS_SENSOR_TYPE_6_0:
				m_SensorData2MultiTester.SensorConfig[sensor].Config.SensorType = CONF_USS_SENSOR_TYPE_6_0;
				break;
			case USS_SENSOR_TYPE_6_1:
				m_SensorData2MultiTester.SensorConfig[sensor].Config.SensorType = CONF_USS_SENSOR_TYPE_6_1;
				break;
			case USS_SENSOR_TYPE_6_5:
				m_SensorData2MultiTester.SensorConfig[sensor].Config.SensorType = CONF_USS_SENSOR_TYPE_6_5;
				break;
			case USS_SENSOR_TYPE_6_50:
				m_SensorData2MultiTester.SensorConfig[sensor].Config.SensorType = CONF_USS_SENSOR_TYPE_6_50;
				break;
			case USS_SENSOR_TYPE_6_51:
				m_SensorData2MultiTester.SensorConfig[sensor].Config.SensorType = CONF_USS_SENSOR_TYPE_6_51;
				break;
			default:
				m_SensorData2MultiTester.SensorConfig[sensor].Config.SensorType = CONF_USS_SENSOR_NOT_USED;
				break;
			}
		}
	}
	//FrontCorner
	if (m_SensorCfg.FrontCornerSensorsType != m_SensorCfg.FrontSensorsType)
	{
		switch (m_SensorCfg.FrontCornerSensorsType)
		{
		case USS_SENSOR_NOT_USED:
			m_SensorData2MultiTester.SensorConfig[0].Config.SensorType = CONF_USS_SENSOR_NOT_USED;
			m_SensorData2MultiTester.SensorConfig[5].Config.SensorType = CONF_USS_SENSOR_NOT_USED;
			break;
		case USS_SENSOR_TYPE_6_0:
			m_SensorData2MultiTester.SensorConfig[0].Config.SensorType = CONF_USS_SENSOR_TYPE_6_0;
			m_SensorData2MultiTester.SensorConfig[5].Config.SensorType = CONF_USS_SENSOR_TYPE_6_0;
			break;
		case USS_SENSOR_TYPE_6_1:
			m_SensorData2MultiTester.SensorConfig[0].Config.SensorType = CONF_USS_SENSOR_TYPE_6_1;
			m_SensorData2MultiTester.SensorConfig[5].Config.SensorType = CONF_USS_SENSOR_TYPE_6_1;
			break;
		case USS_SENSOR_TYPE_6_5:
			m_SensorData2MultiTester.SensorConfig[0].Config.SensorType = CONF_USS_SENSOR_TYPE_6_5;
			m_SensorData2MultiTester.SensorConfig[5].Config.SensorType = CONF_USS_SENSOR_TYPE_6_5;
			break;
		case USS_SENSOR_TYPE_6_50:
			m_SensorData2MultiTester.SensorConfig[0].Config.SensorType = CONF_USS_SENSOR_TYPE_6_50;
			m_SensorData2MultiTester.SensorConfig[5].Config.SensorType = CONF_USS_SENSOR_TYPE_6_50;
			break;
		case USS_SENSOR_TYPE_6_51:
			m_SensorData2MultiTester.SensorConfig[0].Config.SensorType = CONF_USS_SENSOR_TYPE_6_51;
			m_SensorData2MultiTester.SensorConfig[5].Config.SensorType = CONF_USS_SENSOR_TYPE_6_51;
			break;
		default:
			m_SensorData2MultiTester.SensorConfig[0].Config.SensorType = CONF_USS_SENSOR_NOT_USED;
			m_SensorData2MultiTester.SensorConfig[5].Config.SensorType = CONF_USS_SENSOR_NOT_USED;
			break;
		}
	}
	//RearCorner
	if (m_SensorCfg.RearCornerSensorsType != m_SensorCfg.RearSensorsType)
	{
		switch (m_SensorCfg.RearCornerSensorsType)
		{
		case USS_SENSOR_NOT_USED:
			m_SensorData2MultiTester.SensorConfig[6].Config.SensorType = CONF_USS_SENSOR_NOT_USED;
			m_SensorData2MultiTester.SensorConfig[11].Config.SensorType = CONF_USS_SENSOR_NOT_USED;
			break;
		case USS_SENSOR_TYPE_6_0:
			m_SensorData2MultiTester.SensorConfig[6].Config.SensorType = CONF_USS_SENSOR_TYPE_6_0;
			m_SensorData2MultiTester.SensorConfig[11].Config.SensorType = CONF_USS_SENSOR_TYPE_6_0;
			break;
		case USS_SENSOR_TYPE_6_1:
			m_SensorData2MultiTester.SensorConfig[6].Config.SensorType = CONF_USS_SENSOR_TYPE_6_1;
			m_SensorData2MultiTester.SensorConfig[11].Config.SensorType = CONF_USS_SENSOR_TYPE_6_1;
			break;
		case USS_SENSOR_TYPE_6_5:
			m_SensorData2MultiTester.SensorConfig[6].Config.SensorType = CONF_USS_SENSOR_TYPE_6_5;
			m_SensorData2MultiTester.SensorConfig[11].Config.SensorType = CONF_USS_SENSOR_TYPE_6_5;
			break;
		case USS_SENSOR_TYPE_6_50:
			m_SensorData2MultiTester.SensorConfig[6].Config.SensorType = CONF_USS_SENSOR_TYPE_6_50;
			m_SensorData2MultiTester.SensorConfig[11].Config.SensorType = CONF_USS_SENSOR_TYPE_6_50;
			break;
		case USS_SENSOR_TYPE_6_51:
			m_SensorData2MultiTester.SensorConfig[6].Config.SensorType = CONF_USS_SENSOR_TYPE_6_51;
			m_SensorData2MultiTester.SensorConfig[11].Config.SensorType = CONF_USS_SENSOR_TYPE_6_51;
			break;
		default:
			m_SensorData2MultiTester.SensorConfig[6].Config.SensorType = CONF_USS_SENSOR_NOT_USED;
			m_SensorData2MultiTester.SensorConfig[11].Config.SensorType = CONF_USS_SENSOR_NOT_USED;
			break;
		}
	}
	//Sensor silicon configuration
	//All front sensors
	if (m_SensorCfg.FrontSensorsSilicon != USS_SENSOR_SILICON_CC)
	{
		for (sensor = 0; sensor < MAX_SENSOR/2; sensor++)
		{
			switch (m_SensorCfg.FrontSensorsSilicon)
			{
			case USS_SENSOR_SILICON_AA:
				m_SensorData2MultiTester.SensorConfig[sensor].Config.SiliconType = CONF_USS_SENSOR_SILICON_AA;
				break;
			case USS_SENSOR_SILICON_AB:
				m_SensorData2MultiTester.SensorConfig[sensor].Config.SiliconType = CONF_USS_SENSOR_SILICON_AB;
				break;
			case USS_SENSOR_SILICON_BA:
				m_SensorData2MultiTester.SensorConfig[sensor].Config.SiliconType = CONF_USS_SENSOR_SILICON_BA;
				break;
			case USS_SENSOR_SILICON_CA:
				m_SensorData2MultiTester.SensorConfig[sensor].Config.SiliconType = CONF_USS_SENSOR_SILICON_CA;
				break;
			case USS_SENSOR_SILICON_BB:
				m_SensorData2MultiTester.SensorConfig[sensor].Config.SiliconType = CONF_USS_SENSOR_SILICON_BB;
				break;
			case USS_SENSOR_SILICON_CC:
				m_SensorData2MultiTester.SensorConfig[sensor].Config.SiliconType = CONF_USS_SENSOR_SILICON_CC;
				break;
			default:
				m_SensorData2MultiTester.SensorConfig[sensor].Config.SiliconType = CONF_USS_SENSOR_SILICON_CC;
				break;
			}
		}
	}

	//All rear sensors
	if (m_SensorCfg.RearSensorsSilicon != USS_SENSOR_SILICON_CC)
	{
		for (sensor = MAX_SENSOR/2; sensor < MAX_SENSOR; sensor++)
		{
			switch (m_SensorCfg.RearSensorsSilicon)
			{
			case USS_SENSOR_SILICON_AA:
				m_SensorData2MultiTester.SensorConfig[sensor].Config.SiliconType = CONF_USS_SENSOR_SILICON_AA;
				break;
			case USS_SENSOR_SILICON_AB:
				m_SensorData2MultiTester.SensorConfig[sensor].Config.SiliconType = CONF_USS_SENSOR_SILICON_AB;
				break;
			case USS_SENSOR_SILICON_BA:
				m_SensorData2MultiTester.SensorConfig[sensor].Config.SiliconType = CONF_USS_SENSOR_SILICON_BA;
				break;
			case USS_SENSOR_SILICON_CA:
				m_SensorData2MultiTester.SensorConfig[sensor].Config.SiliconType = CONF_USS_SENSOR_SILICON_CA;
				break;
			case USS_SENSOR_SILICON_BB:
				m_SensorData2MultiTester.SensorConfig[sensor].Config.SiliconType = CONF_USS_SENSOR_SILICON_BB;
				break;
			case USS_SENSOR_SILICON_CC:
				m_SensorData2MultiTester.SensorConfig[sensor].Config.SiliconType = CONF_USS_SENSOR_SILICON_CC;
				break;
			default:
				m_SensorData2MultiTester.SensorConfig[sensor].Config.SiliconType = CONF_USS_SENSOR_SILICON_CC;
				break;
			}
		}
	}
	//FrontCorner
	if (m_SensorCfg.FrontCornerSensorsSilicon != m_SensorCfg.FrontSensorsSilicon)
	{
		switch (m_SensorCfg.FrontCornerSensorsSilicon)
		{
		case USS_SENSOR_SILICON_AA:
			m_SensorData2MultiTester.SensorConfig[0].Config.SiliconType = CONF_USS_SENSOR_SILICON_AA;
			m_SensorData2MultiTester.SensorConfig[5].Config.SiliconType = CONF_USS_SENSOR_SILICON_AA;
			break;
		case USS_SENSOR_SILICON_AB:
			m_SensorData2MultiTester.SensorConfig[0].Config.SiliconType = CONF_USS_SENSOR_SILICON_AB;
			m_SensorData2MultiTester.SensorConfig[5].Config.SiliconType = CONF_USS_SENSOR_SILICON_AB;
			break;
		case USS_SENSOR_SILICON_BA:
			m_SensorData2MultiTester.SensorConfig[0].Config.SiliconType = CONF_USS_SENSOR_SILICON_BA;
			m_SensorData2MultiTester.SensorConfig[5].Config.SiliconType = CONF_USS_SENSOR_SILICON_BA;
			break;
		case USS_SENSOR_SILICON_CA:
			m_SensorData2MultiTester.SensorConfig[0].Config.SiliconType = CONF_USS_SENSOR_SILICON_CA;
			m_SensorData2MultiTester.SensorConfig[5].Config.SiliconType = CONF_USS_SENSOR_SILICON_CA;
			break;
		case USS_SENSOR_SILICON_BB:
			m_SensorData2MultiTester.SensorConfig[0].Config.SiliconType = CONF_USS_SENSOR_SILICON_BB;
			m_SensorData2MultiTester.SensorConfig[5].Config.SiliconType = CONF_USS_SENSOR_SILICON_BB;
			break;
		case USS_SENSOR_SILICON_CC:
			m_SensorData2MultiTester.SensorConfig[0].Config.SiliconType = CONF_USS_SENSOR_SILICON_CC;
			m_SensorData2MultiTester.SensorConfig[5].Config.SiliconType = CONF_USS_SENSOR_SILICON_CC;
			break;
		default:
			m_SensorData2MultiTester.SensorConfig[0].Config.SiliconType = CONF_USS_SENSOR_SILICON_CC;
			m_SensorData2MultiTester.SensorConfig[5].Config.SiliconType = CONF_USS_SENSOR_SILICON_CC;
			break;
		}
	}
	//RearCorner
	if (m_SensorCfg.RearCornerSensorsSilicon != m_SensorCfg.RearSensorsSilicon)
	{
		switch (m_SensorCfg.RearCornerSensorsSilicon)
		{
		case USS_SENSOR_SILICON_AA:
			m_SensorData2MultiTester.SensorConfig[6].Config.SiliconType = CONF_USS_SENSOR_SILICON_AA;
			m_SensorData2MultiTester.SensorConfig[11].Config.SiliconType = CONF_USS_SENSOR_SILICON_AA;
			break;
		case USS_SENSOR_SILICON_AB:
			m_SensorData2MultiTester.SensorConfig[6].Config.SiliconType = CONF_USS_SENSOR_SILICON_AB;
			m_SensorData2MultiTester.SensorConfig[11].Config.SiliconType = CONF_USS_SENSOR_SILICON_AB;
			break;
		case USS_SENSOR_SILICON_BA:
			m_SensorData2MultiTester.SensorConfig[6].Config.SiliconType = CONF_USS_SENSOR_SILICON_BA;
			m_SensorData2MultiTester.SensorConfig[11].Config.SiliconType = CONF_USS_SENSOR_SILICON_BA;
			break;
		case USS_SENSOR_SILICON_CA:
			m_SensorData2MultiTester.SensorConfig[6].Config.SiliconType = CONF_USS_SENSOR_SILICON_CA;
			m_SensorData2MultiTester.SensorConfig[11].Config.SiliconType = CONF_USS_SENSOR_SILICON_CA;
			break;
		case USS_SENSOR_SILICON_BB:
			m_SensorData2MultiTester.SensorConfig[6].Config.SiliconType = CONF_USS_SENSOR_SILICON_BB;
			m_SensorData2MultiTester.SensorConfig[11].Config.SiliconType = CONF_USS_SENSOR_SILICON_BB;
			break;
		case USS_SENSOR_SILICON_CC:
			m_SensorData2MultiTester.SensorConfig[6].Config.SiliconType = CONF_USS_SENSOR_SILICON_CC;
			m_SensorData2MultiTester.SensorConfig[11].Config.SiliconType = CONF_USS_SENSOR_SILICON_CC;
			break;
		default:
			m_SensorData2MultiTester.SensorConfig[0].Config.SiliconType = CONF_USS_SENSOR_SILICON_CC;
			m_SensorData2MultiTester.SensorConfig[5].Config.SiliconType = CONF_USS_SENSOR_SILICON_CC;
			break;
		}
	}

	for (uint8_t sensor = 0; sensor < MAX_SENSOR; sensor++)
	{
		m_SensorTypeBuffer[sensor] = (eUssSensorTypesConfiguration)m_SensorData2MultiTester.SensorConfig[sensor].Config.SensorType;
		m_SensorTypeDefault[sensor] = (eUssSensorTypesConfiguration)m_SensorData2MultiTester.SensorConfig[sensor].Config.SensorType;
	}

	//write it to UssSimulator
	Rb_SetStatus((eUssSimulatorState)p_UssSimulator->WriteSensorConfiguration(m_SensorData2MultiTester));
}
uint8_t RbUltraSonics::tSensorToSensorId(tSensor ID) { return ((uint8_t)ID) + 1; }

tSensor RbUltraSonics::SensorIdToTSensor(uint8_t ID) { return (tSensor)(ID - 1); }

std::string RbUltraSonics::GetUssSimulatorIpAddress(void)
{
	return m_IP;
}

void RbUltraSonics::SetUssSimulatorIpAddress(std::string IpAddress)
{
	m_IP = IpAddress;
}

int32_t RbUltraSonics::GetUssSimulatorPort(void)
{
	return m_Port;
}

void RbUltraSonics::SetUssSimulatorPort(int32_t Port)
{
	m_Port = Port;
}

uint8_t RbUltraSonics::GetUssSimulatorFirmwareVersionMajor(void)
{
	if (!m_UssSimulatorAvailable)
	{
		return 0;
	}
	return p_UssSimulator->getFirmwareMajor();
}

uint8_t RbUltraSonics::GetUssSimulatorFirmwareVersionMinor(void)
{
	if (!m_UssSimulatorAvailable)
	{
		return 0;
	}
	return p_UssSimulator->getFirmwareMinor();
}

void RbUltraSonics::SetExpectedUssSimulatorFirmwareVersionMajor(uint8_t FirmwareMajor)
{
	m_ExpectedFirmwareVersionMajor = FirmwareMajor;
}

void RbUltraSonics::SetExpectedUssSimulatorFirmwareVersionMinor(uint8_t FirmwareMinor)
{
	m_ExpectedFirmwareVersionMinor = FirmwareMinor;
}

uint8_t RbUltraSonics::GetExpectedUssSimulatorFirmwareVersionMajor(void)
{
	return m_ExpectedFirmwareVersionMajor;
}

uint8_t RbUltraSonics::GetExpectedUssSimulatorFirmwareVersionMinor(void)
{
	return m_ExpectedFirmwareVersionMinor;
}

bool RbUltraSonics::EnableSensorFiringCheck(bool state)
{
	m_SensorFiringCheckState = state;
	if (m_UssSimulatorAvailable)
	{
		p_UssSimulator->EnableSenssorFiringStateCheck(state);
	}	
	return m_SensorFiringCheckState;
}

bool RbUltraSonics::GetSensorFiringCheckState(void)
{
	return m_SensorFiringCheckState;
}

tMultiTesterStat RbUltraSonics::GetMultiTesterStatistics(void)
{
	if (!m_UssSimulatorAvailable)
	{
		return tMultiTesterStat();
	}
	return (p_UssSimulator->GetMultiTesterStatistics());
}

tFirstEchoData RbUltraSonics::getFirstEchoData(void)
{
	return p_SensorModell->getFirstEchoData();;
}

void RbUltraSonics::EnableEchoSending(bool FrontCluster, bool RearCluster)
{
	p_UssSimulator->SetSensorClusterSendState(FrontCluster,RearCluster);
}