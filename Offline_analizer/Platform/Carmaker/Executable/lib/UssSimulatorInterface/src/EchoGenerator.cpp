/*
 *
 *	EchoGenerator.cpp
 *
 *  Created on: 07.02.2018
 * @author BNC1LR
 */

#include "EchoGenerator.h"

const double DE_ReflectionAngle = (double) (((double)(85) / (double)(180)) * (double)(M_PI));
double Delta_SensAlpha[MAX_SENSOR];

/* qsort struct comparison function (AllEchoesList.Dist float field) */
int StructCmpByDist(const void *a, const void *b)
{
	struct tAllEchoes *ia = (struct tAllEchoes *)a;
	struct tAllEchoes *ib = (struct tAllEchoes *)b;
	return (int)(100.f*ia->Dist - 100.f*ib->Dist);
	/* float comparison: returns negative if b > a
	and positive if a > b. We multiplied result by 100.0
	to preserve decimal fraction */
}

EchoGenerator::EchoGenerator(void)
{
	for (int i = 0; i < MAX_SENSOR; i++)
	{
		m_FirstEchoData.ObjectId[i] = 0;
		m_FirstEchoData.DE_Dist[i] = 0;
	}
}


EchoGenerator::~EchoGenerator(void)
{
}

void EchoGenerator::Init_Sensors(t_SensorData CurrentSensorData[MAX_SENSOR])
{
	int i;

	// calculate angle deltas between sensors (used in cross echo calculation)
	for (i=0;i<MAX_SENSOR-1;i++)
	{
		Delta_SensAlpha[i] = fabs(CurrentSensorData[i].Orientation_z-CurrentSensorData[i+1].Orientation_z);
		if (Delta_SensAlpha[i] > M_PI)
		{
			Delta_SensAlpha[i]=(2*M_PI)-Delta_SensAlpha[i];
		}
	}

}

void EchoGenerator::Init_Sensors(double SensorRotationsZ[MAX_SENSOR])
{
	uint8_t i = 0;
	// calculate angle deltas between sensors (used in cross echo calculation)
	for (i = 0;i < MAX_SENSOR - 1;i++)
	{
		Delta_SensAlpha[i] = fabs(SensorRotationsZ[i] - SensorRotationsZ[i + 1]);
		if (Delta_SensAlpha[i] > M_PI)
		{
			Delta_SensAlpha[i] = (2 * M_PI) - Delta_SensAlpha[i];
		}
	}
}

void EchoGenerator::CalcEchoData(t_SensorData CurrentSensorData[MAX_SENSOR], tMultiTesterDataIF * SensorData2MultiTester)
{
	int sens = 0;
	int obj = 0;
	int n = 0;

	int SensorApertureLookUp65[4]; //cm
	int SensorApertureLookUp60[4]; //cm

	SensorApertureLookUp65[0] = 70;
	SensorApertureLookUp65[1] = 88;
	SensorApertureLookUp65[2] = 113;
	SensorApertureLookUp65[3] = 280;

	SensorApertureLookUp60[0] = 71;
	SensorApertureLookUp60[1] = 76;
	SensorApertureLookUp60[2] = 84;
	SensorApertureLookUp60[3] = 115;

	int AllEchoCounter = 0;

	int DE_EchoCounter = 0;
	int CEL_EchoCounter = 0;
	int CER_EchoCounter = 0;

	double Object_DE_Array[OBJECT_ECHO_LIST_SIZE][3];
	double Object_CEL_Array[OBJECT_ECHO_LIST_SIZE][3];
	double Object_CER_Array[OBJECT_ECHO_LIST_SIZE][3];

	int index_dummy[OBJECT_ECHO_LIST_SIZE];

	double ObjectHeight, ObjectBearing, ObjectDist, ApertureCurrent, FirstEchoDistance;

	tRBSensorIncident SensorIncident;

	tAllEchoes AllEchoesList[MAX_ECHOES_CALC];

	uint32_t nearestObjectIds[MAX_SENSOR];
	double nearestObjectDist[MAX_SENSOR];
	for (sens = 0; sens < MAX_SENSOR; sens++)
	{
		nearestObjectIds[sens] = 0;
		nearestObjectDist[sens] = 50000;

		m_FirstEchoData.ObjectId[sens] = 0;
		m_FirstEchoData.DE_Dist[sens] = 0;
	}

	for(sens=0; sens<MAX_SENSOR; sens++)
	{
		if (CurrentSensorData[sens].SensorState == SENSOR_INACTIVE) continue; // when the sensor is not active we do not need to handle it further
		DE_EchoCounter = 0;
		CEL_EchoCounter = 0;
		CER_EchoCounter = 0;

		// init echo arrays
		memset(&AllEchoesList, 0, sizeof(tAllEchoes)*MAX_ECHOES_CALC);

		memset(&Object_DE_Array,  0, sizeof(Object_DE_Array[0][0])*OBJECT_ECHO_LIST_SIZE * 3);
		memset(&Object_CEL_Array, 0, sizeof(Object_CEL_Array[0][0])*OBJECT_ECHO_LIST_SIZE * 3);
		memset(&Object_CER_Array, 0, sizeof(Object_CER_Array[0][0])*OBJECT_ECHO_LIST_SIZE * 3);

		// cycle through all observed objects of the sensor
		// NOTE: It is expected that all objects in the AllObjectList are in the FOV of the Sensor
		for (obj=0; obj < MAX_OBJECTS; obj++)
		{
			//USS_DBG("Sensor:%d and Obj: %d\n", sens, obj);
			ObjectDist = CurrentSensorData[sens].AllObjectList[obj].NearPntDistance;
			if (ObjectDist > 0.01)
			{
				//USS_DBG("Sensor: %d , ObjectID: %d\n", sens + 1, CurrentSensorData[sens].AllObjectList[obj].GlobalId);
				ObjectBearing =  CurrentSensorData[sens].AllObjectList[obj].NearPntAlpha*180/M_PI;

				if (ObjectBearing >= 0) SensorIncident.ImgAreaNearPnt = -1; //Object in the left side of FOV
				if (ObjectBearing < 0) SensorIncident.ImgAreaNearPnt =   1; //Object in the right side of FOV

				SensorIncident.IncidentAlpha  = CurrentSensorData[sens].AllObjectList[obj].IncidentAlpha;
				SensorIncident.IncidentBeta  = CurrentSensorData[sens].AllObjectList[obj].IncidentBeta;

				// assign the maximum allowed sensor aperture dependant on object dist and sensor type (based on range)
				if (CurrentSensorData[sens].Range > 4)
				{
					if (ObjectDist <= SensorApertureLookUp65[0]) 		ApertureCurrent = 60;
					else if (ObjectDist <= SensorApertureLookUp65[1])	ApertureCurrent = 50;
					else if (ObjectDist <= SensorApertureLookUp65[2])	ApertureCurrent = 40;
					else if (ObjectDist <= SensorApertureLookUp65[3])	ApertureCurrent = 30;
					else ApertureCurrent = 20;
				}
				else
				{
					if (ObjectDist <= SensorApertureLookUp60[0])		ApertureCurrent = 70;
					else if (ObjectDist <= SensorApertureLookUp60[1]) 	ApertureCurrent = 60;
					else if (ObjectDist <= SensorApertureLookUp60[2])	ApertureCurrent = 50;
					else if (ObjectDist <= SensorApertureLookUp60[3])	ApertureCurrent = 40;
					else ApertureCurrent = 30;
				}

				// is the object still in the (new shaped) FOV?
				if (fabs(ObjectBearing) < ApertureCurrent)
				{
					CalcObjectFirstEchoes(	CurrentSensorData,
											sens, obj,
											SensorIncident,
											&Object_DE_Array[DE_EchoCounter][0],
											&Object_CEL_Array[CEL_EchoCounter][0],
											&Object_CER_Array[CER_EchoCounter][0]);

					ObjectHeight = CurrentSensorData[sens].AllObjectList[obj].Height;

					if (Object_DE_Array[DE_EchoCounter][0] != 0)
					{
						FirstEchoDistance = Object_DE_Array[DE_EchoCounter][0];
						
						if (FirstEchoDistance < nearestObjectDist[sens])
						{
							nearestObjectDist[sens] = FirstEchoDistance;
							nearestObjectIds[sens] = CurrentSensorData[sens].AllObjectList[obj].GlobalId;
						}
						
						if (ObjectHeight > CurrentSensorData[sens].HeightForHeightClassification)
						{
							Object_DE_Array[DE_EchoCounter][1] = FirstEchoHighObject;
							Object_DE_Array[DE_EchoCounter][2] = ObjectHeight;
							//Log("Object_DE_Array[DE_EchoCounter][1]: %u\n", (const char)Object_DE_Array[DE_EchoCounter][1]);
							DE_EchoCounter++;
							// add 2nd echo for objects higher than 50cm
							Object_DE_Array[DE_EchoCounter][0] = FirstEchoDistance + SECOND_ECHO_OFFSET;
							Object_DE_Array[DE_EchoCounter][1] = SecondEchoHighObject;
							Object_DE_Array[DE_EchoCounter][2] = ObjectHeight;
							DE_EchoCounter++;
							if ((sens == 0 || sens == 5 || sens == 6 || sens == 11) || (FirstEchoDistance > 200))
							{
								//add third echo if object is high and far away
								Object_DE_Array[DE_EchoCounter][0] = FirstEchoDistance + SECOND_ECHO_OFFSET + SECOND_ECHO_OFFSET;
								Object_DE_Array[DE_EchoCounter][1] = ThirdEchoHighObject;
								Object_DE_Array[DE_EchoCounter][2] = ObjectHeight;
								DE_EchoCounter++;
							}
						}
						else
						{
							Object_DE_Array[DE_EchoCounter][1] = FirstEchoLowObject;
							Object_DE_Array[DE_EchoCounter][2] = ObjectHeight;
							DE_EchoCounter++;
						}
					}

					if (Object_CEL_Array[CEL_EchoCounter][0] != 0)
					{
						FirstEchoDistance = Object_CEL_Array[CEL_EchoCounter][0];

						if (ObjectHeight > CurrentSensorData[sens].HeightForHeightClassification)
						{
							Object_CEL_Array[CEL_EchoCounter][1] = FirstEchoHighObject;
							Object_CEL_Array[CEL_EchoCounter][2] = ObjectHeight;
							CEL_EchoCounter++;
							// add 2nd echo for objects higher than 50cm
							Object_CEL_Array[CEL_EchoCounter][0] = FirstEchoDistance + SECOND_ECHO_OFFSET;
							Object_CEL_Array[CEL_EchoCounter][1] = SecondEchoHighObject;
							Object_CEL_Array[CEL_EchoCounter][2] = ObjectHeight;
							CEL_EchoCounter++;
						}
						else
						{
							Object_CEL_Array[CEL_EchoCounter][1] = FirstEchoLowObject;
							Object_CEL_Array[CEL_EchoCounter][2] = ObjectHeight;
							CEL_EchoCounter++;
						}
					}

					if (Object_CER_Array[CER_EchoCounter][0] != 0)
					{
						FirstEchoDistance = Object_CER_Array[CER_EchoCounter][0];

						if (ObjectHeight > CurrentSensorData[sens].HeightForHeightClassification)
						{
							Object_CER_Array[CER_EchoCounter][1] = FirstEchoHighObject;
							Object_CER_Array[CER_EchoCounter][2] = ObjectHeight;
							CER_EchoCounter++;
							// add CER_EchoCounter echo for objects higher than 50cm
							Object_CER_Array[CER_EchoCounter][0] = FirstEchoDistance + SECOND_ECHO_OFFSET;
							Object_CER_Array[CER_EchoCounter][1] = SecondEchoHighObject;
							Object_CER_Array[CER_EchoCounter][2] = ObjectHeight;
							CER_EchoCounter++;
						}
						else
						{
							Object_CER_Array[CER_EchoCounter][1] = FirstEchoLowObject;
							Object_CER_Array[CER_EchoCounter][2] = ObjectHeight;
							CER_EchoCounter++;
						}
					}
				}
				else
				{
					// aperture check failed, object outside fov
					// do nothing
				}
			 }
		}//for: objects

			
		// sort echo lists from small to large
		(void) BubbleSortDoubleArrayWithIdx(Object_DE_Array,  index_dummy, DE_EchoCounter);
		(void) BubbleSortDoubleArrayWithIdx(Object_CEL_Array, index_dummy, CEL_EchoCounter);
		(void) BubbleSortDoubleArrayWithIdx(Object_CER_Array, index_dummy, CER_EchoCounter);

		int m=0;
		AllEchoCounter = 0;

		//prevent echo list from having to much entries
		if ((DE_EchoCounter + CEL_EchoCounter + CER_EchoCounter) > MAX_ECHOES_CALC)
		{
			if (DE_EchoCounter > 20) DE_EchoCounter = 20;
			if (CEL_EchoCounter > 20) CEL_EchoCounter = 20;
			if (CER_EchoCounter > 20) CER_EchoCounter = 20;
		}

		for (m = 0; m<DE_EchoCounter; m++)
		{
			AllEchoesList[AllEchoCounter].Dist = Object_DE_Array[m][0];
			AllEchoesList[AllEchoCounter].Type = DE;
			AllEchoesList[AllEchoCounter].Sender = (tSensor) sens;
			AllEchoesList[AllEchoCounter].EchoClass = (tEchoClass) int(Object_DE_Array[m][1]);
			AllEchoesList[AllEchoCounter].Height = Object_DE_Array[m][2];
			AllEchoCounter++;
		}


		for (m = 0; m<CEL_EchoCounter; m++)
		{
			if (sens != 0 && sens != 6) // CEs from left sensor
			{
				AllEchoesList[AllEchoCounter].Dist = Object_CEL_Array[m][0];
				AllEchoesList[AllEchoCounter].Type = CE;
				AllEchoesList[AllEchoCounter].Sender = (tSensor) (sens-1);
				AllEchoesList[AllEchoCounter].EchoClass = (tEchoClass) int(Object_CEL_Array[m][1]);
				AllEchoesList[AllEchoCounter].Height = Object_CEL_Array[m][2];
				AllEchoCounter++;
			}
		}

		for (m = 0; m<CER_EchoCounter; m++)
		{
			if (sens != 5 && sens != 11) // CEs from right sensor
			{
				AllEchoesList[AllEchoCounter].Dist = Object_CER_Array[m][0];
				AllEchoesList[AllEchoCounter].Type = CE;
				AllEchoesList[AllEchoCounter].Sender = (tSensor) (sens+1);
				AllEchoesList[AllEchoCounter].EchoClass = (tEchoClass) int(Object_CER_Array[m][1]);
				AllEchoesList[AllEchoCounter].Height = Object_CER_Array[m][2];
				AllEchoCounter++;
			}
		}


		size_t AllEchoesListLen = sizeof(AllEchoesList) / sizeof(struct tAllEchoes);

		/* sort array using qsort functions */
		qsort(AllEchoesList, AllEchoesListLen, sizeof(struct tAllEchoes), StructCmpByDist);

		n=0;
				
		for (m=0; m<MAX_ECHOES_CALC; m++)
		{
			if (n < MAX_ECHO) //do not write more then MAX_ECHO (20) echoes
			{
				if (fabs(AllEchoesList[m].Dist) > 0.01)
				{

					SensorData2MultiTester->SensorData[sens].EchoList[n].Dist = AllEchoesList[m].Dist * 10; // in mm
					SensorData2MultiTester->SensorData[sens].EchoList[n].Sender = AllEchoesList[m].Sender;
					SensorData2MultiTester->SensorData[sens].EchoList[n].Type = AllEchoesList[m].Type;

					if (AllEchoesList[m].EchoClass == FirstEchoHighObject)
					{
						SensorData2MultiTester->SensorData[sens].EchoList[n].Amplitude = 32;
						SensorData2MultiTester->SensorData[sens].EchoList[n].Correlation = 15;
					}
					else if (AllEchoesList[m].EchoClass == SecondEchoHighObject)
					{
						SensorData2MultiTester->SensorData[sens].EchoList[n].Amplitude = 28;
						SensorData2MultiTester->SensorData[sens].EchoList[n].Correlation = 7;
					}
					else if (AllEchoesList[m].EchoClass == ThirdEchoHighObject)
					{
						SensorData2MultiTester->SensorData[sens].EchoList[n].Amplitude = 28;
						SensorData2MultiTester->SensorData[sens].EchoList[n].Correlation = 7;
					}
					else if (AllEchoesList[m].EchoClass == FirstEchoLowObject)
					{
						SensorData2MultiTester->SensorData[sens].EchoList[n].Amplitude = 20;
						SensorData2MultiTester->SensorData[sens].EchoList[n].Correlation = 9;
					}
					else
					{
						SensorData2MultiTester->SensorData[sens].EchoList[n].Amplitude = 0;
						SensorData2MultiTester->SensorData[sens].EchoList[n].Correlation = 0;
					}
					//if (sens == 5 && n==0) //|| sens == 9)
					//{
					//if (n==0)USS_DBG("Sensor %d - Echo %d - distance %f - Type %d  -  EchoClass %d \n", sens+1, n, SensorData2MultiTester->SensorData[sens].EchoList[n].Dist/1000, SensorData2MultiTester->SensorData[sens].EchoList[n].Type, AllEchoesList[m].EchoClass);
					//}
					n++;
				}
			}
		}
		//if (n > 0) USS_DBG("Calculated %d Echo(es) for Sensor %d\n", n, sens + 1);
	}//for: sens

	// Fill Echolists with mirrored CE
//	e.g. if there is a CE from S2->S3 we also add a CE from S3->S2 with the same attributes
	uint8_t sendSens = 0;
	uint8_t CeFound = 0;
	for(uint8_t recvSens = 0; recvSens < MAX_SENSOR; recvSens++)
	{
		for(uint8_t recvEcho = 0; recvEcho < MAX_ECHO; recvEcho++)
		{
			if (SensorData2MultiTester->SensorData[recvSens].EchoList[recvEcho].Type == CE)
			{//CE found in list of the receiving sensor
				CeFound = 0;
				sendSens = (uint8_t)SensorData2MultiTester->SensorData[recvSens].EchoList[recvEcho].Sender;
				//check if the CE already is in the list of the sending sensor
				for (uint8_t sendEcho = 0; sendEcho < MAX_ECHO; sendEcho++)
				{
					if ((SensorData2MultiTester->SensorData[sendSens].EchoList[sendEcho].Type == CE) &&
						(((uint8_t)SensorData2MultiTester->SensorData[sendSens].EchoList[sendEcho].Sender) == recvSens) &&
						RbCheckRange(SensorData2MultiTester->SensorData[sendSens].EchoList[sendEcho].Dist,SensorData2MultiTester->SensorData[recvSens].EchoList[recvEcho].Dist,((SECOND_ECHO_OFFSET*10)-1))
					   )
					{
						CeFound = 1;
						break;
					}
				}
				if (CeFound==0) //No CE form the sensor found so add the CE
				{
					for (uint8_t sendEcho = 0; sendEcho < MAX_ECHO; sendEcho++)
					{
						//find the index where the echo has to be injected
						if (SensorData2MultiTester->SensorData[recvSens].EchoList[recvEcho].Dist < SensorData2MultiTester->SensorData[sendSens].EchoList[sendEcho].Dist ||
								SensorData2MultiTester->SensorData[sendSens].EchoList[sendEcho].Dist == 0)
						{
							for (uint8_t iter = MAX_ECHO-1; iter > sendEcho; iter--)
							{// shift elements forward
								SensorData2MultiTester->SensorData[sendSens].EchoList[iter].Dist = SensorData2MultiTester->SensorData[sendSens].EchoList[iter-1].Dist;
								SensorData2MultiTester->SensorData[sendSens].EchoList[iter].Amplitude = SensorData2MultiTester->SensorData[sendSens].EchoList[iter-1].Amplitude;
								SensorData2MultiTester->SensorData[sendSens].EchoList[iter].Correlation = SensorData2MultiTester->SensorData[sendSens].EchoList[iter-1].Correlation;
								SensorData2MultiTester->SensorData[sendSens].EchoList[iter].Height = SensorData2MultiTester->SensorData[sendSens].EchoList[iter-1].Height;
								SensorData2MultiTester->SensorData[sendSens].EchoList[iter].Sender = SensorData2MultiTester->SensorData[sendSens].EchoList[iter-1].Sender;
								SensorData2MultiTester->SensorData[sendSens].EchoList[iter].Type = SensorData2MultiTester->SensorData[sendSens].EchoList[iter-1].Type;
							}
							//insert CE at correct position
							SensorData2MultiTester->SensorData[sendSens].EchoList[sendEcho].Dist = SensorData2MultiTester->SensorData[recvSens].EchoList[recvEcho].Dist;
							SensorData2MultiTester->SensorData[sendSens].EchoList[sendEcho].Amplitude = SensorData2MultiTester->SensorData[recvSens].EchoList[recvEcho].Amplitude;
							SensorData2MultiTester->SensorData[sendSens].EchoList[sendEcho].Correlation = SensorData2MultiTester->SensorData[recvSens].EchoList[recvEcho].Correlation;
							SensorData2MultiTester->SensorData[sendSens].EchoList[sendEcho].Height = SensorData2MultiTester->SensorData[recvSens].EchoList[recvEcho].Height;
							SensorData2MultiTester->SensorData[sendSens].EchoList[sendEcho].Sender = (tSensor)recvSens;
							SensorData2MultiTester->SensorData[sendSens].EchoList[sendEcho].Type = SensorData2MultiTester->SensorData[recvSens].EchoList[recvEcho].Type;
							break;
						}
					}
				}
			}
		}
	}

	for (sens = 0; sens < MAX_SENSOR; sens++)
	{
		m_FirstEchoData.ObjectId[sens] = nearestObjectIds[sens];
		m_FirstEchoData.DE_Dist[sens] = nearestObjectDist[sens];
	}
}

void EchoGenerator::CalcObjectFirstEchoes(t_SensorData CurrentSensorData[MAX_SENSOR], int SensorNumber, int Obj, tRBSensorIncident SensorIncid, double * DE_Dist, double * CE_Dist_Left, double * CE_Dist_Right)
{
	double AlphaBisectrixToObject;
	
	// evaluation of incident angles for <SensorNumber>
	// check if nearest object "reflection" is on the right side of bisectrix and alpha > DE_ReflectionAngle
	if ((SensorIncid.ImgAreaNearPnt >= 0)
	  &&(SensorIncid.IncidentAlpha >= DE_ReflectionAngle))
	{
		*DE_Dist = CurrentSensorData[SensorNumber].AllObjectList[Obj].NearPntDistance * 100; // m -> cm

		*CE_Dist_Left = 0; // no CE to the left

		AlphaBisectrixToObject = M_PI-fabs(CurrentSensorData[SensorNumber].AllObjectList[Obj].NearPntAlpha)-SensorIncid.IncidentBeta;

		if (((AlphaBisectrixToObject > (2*Delta_SensAlpha[SensorNumber])) || ((SensorIncid.IncidentAlpha + SensorIncid.IncidentBeta)  >  (M_PI + 0.05)))
		  &&((SensorNumber != 5) && (SensorNumber != 11)))
		{
			//  calc cross echo to the right for sensor SensorNumber
			if (CurrentSensorData[SensorNumber+1].SensorState == SENSOR_INACTIVE) //Sensor to the right is not active -> no cross echo
			{
				*CE_Dist_Right = 0;
			}
			else
			{
				*CE_Dist_Right = CalcCrossEcho(CurrentSensorData, SensorNumber, SensorNumber + 1, CurrentSensorData[SensorNumber].AllObjectList[Obj].GlobalId);
			}
			
		}
	}
	// check if nearest object "reflection" is on the left side of bisectrix and beta > DE_ReflectionAngle
	else if ((SensorIncid.ImgAreaNearPnt < 0)
		   &&(SensorIncid.IncidentBeta >= DE_ReflectionAngle))
	{
		*DE_Dist = CurrentSensorData[SensorNumber].AllObjectList[Obj].NearPntDistance * 100; // m -> cm

		*CE_Dist_Right = 0; //no CE to the right

		AlphaBisectrixToObject = M_PI-fabs(CurrentSensorData[SensorNumber].AllObjectList[Obj].NearPntAlpha)-SensorIncid.IncidentAlpha;

		if (((AlphaBisectrixToObject > (2*Delta_SensAlpha[SensorNumber-1])) || ((SensorIncid.IncidentAlpha + SensorIncid.IncidentBeta)  >  (M_PI + 0.05)))
		 &&((SensorNumber != 0) && (SensorNumber != 6)))
		{
			//  calc cross echo to the left for sensor SensorNumber
			if (CurrentSensorData[SensorNumber-1].SensorState == SENSOR_INACTIVE) //Sensor to the left is not active -> no cross echo
			{
				*CE_Dist_Left = 0;
			}
			else
			{
				*CE_Dist_Left = CalcCrossEcho(CurrentSensorData, SensorNumber, SensorNumber - 1, CurrentSensorData[SensorNumber].AllObjectList[Obj].GlobalId);
			}
		}

	}
	// no echo reflection
	else
	{
		*DE_Dist = 0;
		*CE_Dist_Right = 0;
		*CE_Dist_Left = 0;
	}

	return;
}

double EchoGenerator::CalcCrossEcho(t_SensorData CurrentSensorData[MAX_SENSOR], int sendingSensor, int listeningSensor, int WorldObj)
{
	double dist=0;
	double sendingSensorDE, listeningSensorDE, spacing;
	double t_NearPntCoords[3];
	double t_SensorCoords[3];

	signed int objIdSendingSensor = GetSensorObjIdByGlobalId(CurrentSensorData[sendingSensor], WorldObj);
	signed int objIdReceivingSensor = GetSensorObjIdByGlobalId(CurrentSensorData[listeningSensor], WorldObj);

	//if object is not found in both lists return zero
	if (objIdSendingSensor == -1 || objIdReceivingSensor == -1) return 0;

	// To find the direct Echo of sendingSensor
	sendingSensorDE = CurrentSensorData[sendingSensor].AllObjectList[objIdSendingSensor].NearPntDistance * 100; // *100 used for converting the value's to Centimeter

	// checking if the sum of alpha and beta of the sensor incident angle are 1 PI,  if yes --> wall CE calculation
	if ((((CurrentSensorData[sendingSensor].AllObjectList[objIdSendingSensor].IncidentAlpha+CurrentSensorData[sendingSensor].AllObjectList[objIdSendingSensor].IncidentBeta) <  (M_PI + 0.05))
	 &&  ((CurrentSensorData[sendingSensor].AllObjectList[objIdSendingSensor].IncidentAlpha+CurrentSensorData[sendingSensor].AllObjectList[objIdSendingSensor].IncidentBeta) >  (M_PI - 0.05))) &&
	    (((CurrentSensorData[listeningSensor].AllObjectList[objIdReceivingSensor].IncidentAlpha+CurrentSensorData[listeningSensor].AllObjectList[objIdReceivingSensor].IncidentBeta) <  (M_PI + 0.05))
	 &&  ((CurrentSensorData[listeningSensor].AllObjectList[objIdReceivingSensor].IncidentAlpha+CurrentSensorData[listeningSensor].AllObjectList[objIdReceivingSensor].IncidentBeta) >  (M_PI - 0.05))))
	{
		// To find the direct Echo of listeningSensor
		listeningSensorDE = CurrentSensorData[listeningSensor].AllObjectList[objIdReceivingSensor].NearPntDistance * 100; // *100 used for converting the value's to Centimeter

		// To calculate the Spacing between sending sensor & Listening Sensor
		spacing = CalcSpacing(CurrentSensorData,sendingSensor,listeningSensor);   // final Spacing value received in Centimeter

		// Cross eco's are calculated for wall
		dist = CalcCrossEcho_Wall(spacing,sendingSensorDE,listeningSensorDE);

		return dist;
	}
	else // --> for point CE calculation
	{
		//get the distance between NearestPoint of "sending sensor" + object to the "listening sensor"
		t_NearPntCoords[0] = CurrentSensorData[sendingSensor].AllObjectList[objIdSendingSensor].NearPnt[0];
		t_NearPntCoords[1] = CurrentSensorData[sendingSensor].AllObjectList[objIdSendingSensor].NearPnt[1];
		t_NearPntCoords[2] = CurrentSensorData[sendingSensor].AllObjectList[objIdSendingSensor].NearPnt[2];
		
		t_SensorCoords[0] = CurrentSensorData[sendingSensor].Position_x;
		t_SensorCoords[1] = CurrentSensorData[sendingSensor].Position_y;
		t_SensorCoords[2] = CurrentSensorData[sendingSensor].Position_z;

		//transform to vehicle coordinates
		CoordRotateZ(t_NearPntCoords, CurrentSensorData[sendingSensor].Orientation_z);
		CoordTranslate(t_NearPntCoords, t_SensorCoords);

		t_SensorCoords[0] = CurrentSensorData[listeningSensor].Position_x;
		t_SensorCoords[1] = CurrentSensorData[listeningSensor].Position_y;
		t_SensorCoords[2] = CurrentSensorData[listeningSensor].Position_z;

		Dist2Points_R3(&dist, t_NearPntCoords, t_SensorCoords);
		dist = dist * 100;
		dist += sendingSensorDE;

		return (dist / 2);
	}

	return 0;
}

// to Calculate the spacing between given sensors
double EchoGenerator::CalcSpacing(t_SensorData CurrentSensorData[MAX_SENSOR], int sendingSensor, int listeningSensor)
{
	double result = 0;
	// Value's Fetched from vehicle model in meter, used *100 for converting to centimeter
	result = sqrt(pow((double)((CurrentSensorData[listeningSensor].Position_x*100) - (CurrentSensorData[sendingSensor].Position_x*100)), 2)
		+ pow((double)((CurrentSensorData[listeningSensor].Position_y*100) - (CurrentSensorData[sendingSensor].Position_y*100)), 2));
		//+ pow((double)((CurrentSensorData[listeningSensor].Position_z*100) - (CurrentSensorData[sendingSensor].Position_z*100)), 2)); // removed due to 2d distance calculation is enough here, want to do 3D calculation, enable this line
	return result;
}

// to Calculate the CrossEco's for Wall
double EchoGenerator::CalcCrossEcho_Wall(double spacing, double sendingSensorDE, double listeningSensorDE)
{
	return (double) sqrt((pow(spacing, 2) / 4) + (sendingSensorDE * listeningSensorDE));
}

signed int EchoGenerator::GetSensorObjIdByGlobalId(t_SensorData TargetSensorData, int GlobalId)
{
	int i=0;
	for (i=0;i<MAX_OBJECTS;i++)
	{
		if(TargetSensorData.AllObjectList[i].GlobalId == GlobalId)
		{
			return i;
		}
	}

	return -1;

}

void EchoGenerator::BubbleSortDoubleArrayWithIdx(double sortThis[][3], int indices[], int sizeOfBothArrays)
{
	int i,j;
	for (i = sizeOfBothArrays -1; i >0; i--)
	{
		for (j = 0; j < i; j++)
		{
			if (sortThis[j][0] > sortThis[j + 1][0])
			{
				double swpDist	 = sortThis[j][0];
				double swpEchoClass = sortThis[j][1];
				double swpHeight = sortThis[j][2];

				int swpIdx = indices[j];

				sortThis[j][0] = sortThis[j + 1][0];
				sortThis[j][1] = sortThis[j + 1][1];
				sortThis[j][2] = sortThis[j + 1][2];

				sortThis[j + 1][0] = swpDist;
				sortThis[j + 1][1] = swpEchoClass;
				sortThis[j + 1][2] = swpHeight;

				indices[j] = indices[j + 1];
				indices[j + 1] = swpIdx;
			}
		}
	}
}

void EchoGenerator::CoordRotateZ(double* point_xyz, double ang)
{
	double temp_xyz[3] = { 0,0,0 };

	temp_xyz[0] = point_xyz[0] * cos(ang) - point_xyz[1] * sin(ang);
	temp_xyz[1] = point_xyz[0] * sin(ang) + point_xyz[1] * cos(ang);
	temp_xyz[2] = point_xyz[2];

	point_xyz[0] = temp_xyz[0];
	point_xyz[1] = temp_xyz[1];
	point_xyz[2] = temp_xyz[2];
}

void EchoGenerator::CoordTranslate(double translVec_xyz[3], const double point_xyz[3])
{
	translVec_xyz[0] += point_xyz[0];
	translVec_xyz[1] += point_xyz[1];
	translVec_xyz[2] += point_xyz[2];
}

void EchoGenerator::Dist2Points_R3(double* dist, const double a_xyz[3], const double b_xyz[3])
{
	*dist = sqrt((a_xyz[0] - b_xyz[0])*(a_xyz[0] - b_xyz[0]) + (a_xyz[1] - b_xyz[1])*(a_xyz[1] - b_xyz[1]) + (a_xyz[2] - b_xyz[2])*(a_xyz[2] - b_xyz[2]));
}

uint8_t EchoGenerator::RbCheckRange(double ToBeChecked, double ReferenceValue, double Tolerance)
{
	if(ToBeChecked >= (ReferenceValue-Tolerance) && ToBeChecked <= (ReferenceValue+Tolerance))
	{
		return 1;
	}

	return 0;
}