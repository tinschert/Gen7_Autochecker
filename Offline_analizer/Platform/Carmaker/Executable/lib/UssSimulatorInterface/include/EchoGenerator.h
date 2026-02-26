/*
 *
 *	EchoGenerator.h
 *
 *  Created on: 07.02.2018
 * @author BNC1LR
 */

#pragma once

#include <string.h>
#include <stdlib.h>
#include <cmath>

#include "RbDefines.h"
#include "UdpMultiTester.h"

#define MAX_ECHOES_CALC (60)

typedef struct tRbSensorIncident {
	double IncidentAlpha;
	double IncidentBeta;
	double ImgAreaNearPnt;
}tRBSensorIncident;

typedef enum tEchoClass {
	ClassNotDef = 0,
	FirstEchoHighObject = 1,
	SecondEchoHighObject = 2,
	ThirdEchoHighObject = 3,
	FirstEchoLowObject = 4,
	DisturbanceEcho = 5,
}tEchoClass;

typedef struct tAllEchoes {
	double Dist;
	tEchoType Type;
	tSensor Sender;
	tEchoClass EchoClass;
	double Height;
}tAllEchoes;

typedef struct tFirstEchoData {
	uint32_t ObjectId[MAX_SENSOR];
	double DE_Dist[MAX_SENSOR];
}tFirstEchoData;


class EchoGenerator
{
public:
	EchoGenerator(void);
	~EchoGenerator(void);

	void Init_Sensors(t_SensorData CurrentSensorData[MAX_SENSOR]);
	void Init_Sensors(double SensorRotationsZ[MAX_SENSOR]);
	void CalcEchoData(t_SensorData CurrentSensorData[MAX_SENSOR], tMultiTesterDataIF * SensorData2MultiTester);
	tFirstEchoData getFirstEchoData(void){return m_FirstEchoData;}


private:
	void CalcObjectFirstEchoes(t_SensorData CurrentSensorData[MAX_SENSOR], int SensorNumber, int Obj, tRBSensorIncident SensorIncid, double * DE_Dist, double * CE_Dist_Left, double * CE_Dist_Right);
	double CalcCrossEcho(t_SensorData CurrentSensorData[MAX_SENSOR], int sendingSensor, int listeningSensor, int WorldObj);
	double CalcSpacing(t_SensorData CurrentSensorData[MAX_SENSOR], int sendingSensor, int listeningSensor);
	double CalcCrossEcho_Wall(double spacing, double sendingSensorDE, double listeningSensorDE);
	int GetSensorObjIdByGlobalId(t_SensorData TargetSensorData, int GlobalId);
	void BubbleSortDoubleArrayWithIdx(double sortThis[][3], int indices[], int sizeOfBothArrays);
	void CoordRotateZ(double* point_xyz, double ang);
	void CoordTranslate(double translVec_xyz[3], const double point_xyz[3]);
	void Dist2Points_R3(double* dist, const double a_xyz[3], const double b_xyz[3]);
	uint8_t RbCheckRange(double ToBeChecked, double ReferenceValue, double Tolerance);

	tFirstEchoData m_FirstEchoData;
};

