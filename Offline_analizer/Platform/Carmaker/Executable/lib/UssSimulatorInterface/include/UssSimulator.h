#pragma once

#ifndef USS_SIMULATOR_H_
#define USS_SIMULATOR_H_

#include <stdio.h>
#include <time.h>
#include <queue>
#include <stdint.h>
#include <cstring>
#include <chrono>

#if defined _WIN32
	#include <winsock2.h>
	#include <WS2tcpip.h>
	#pragma comment(lib,"ws2_32.lib") //Winsock Library

#else
	#if defined(XENO64) 
		#include <alchemy/pipe.h>
		#include <alchemy/queue.h>
		#include <alchemy/mutex.h>
		#include <alchemy/task.h>
		#define T_FPU    0 	
		#define T_CPU(cpu)	 0
	#elif defined (XENO) //xenomai includes
		#include <native/task.h>
		#include <native/pipe.h>
		#include <native/types.h>
		#include <native/queue.h>
		#include <native/timer.h>
		#include <native/mutex.h>
	#endif

	/*common linux includes*/
	#include <sys/types.h>
	#include <sys/socket.h>
	#include <netinet/ip.h>
	#include <netinet/in.h>
	#include <arpa/inet.h>
	#include <ctime> // needed for Sleep function
	#include <cerrno> // needed for Sleep function
	typedef unsigned int DWORD;
	#define SOCKET_ERROR    (-1)
#endif

#include "RbDefines.h"

#define MAX_ECHO         20
#define OBJECT_ECHO_LIST_SIZE (MAX_OBJECTS*3)

/* Cycle time per loop */
#define PERIODIC_TIME_MS       10  

/* Maximum duration in ms after which a message is regarded as lost */
#define MSG_TIMEOUT_MS          9 

/* Timeout for receiving data from socket*/
#define SOCKET_READ_TIMEOUT_MILLI_SEC 2

constexpr auto SECOND_ECHO_OFFSET = 8;
constexpr auto m_mutexTimeout = 2; //ms
constexpr auto NANO_TO_MILLI_SEC = 1e-6;
/* Message struct with maximal length */
// struct tMsg
// {
// 	uint8_t address;
// 	uint8_t  cmdIdentifier;
// 	uint8_t  data[480];
// 	uint32_t msgSize;
// };

enum eMultiTesterType : uint8_t
{
	UDP = 0,
	USB = 1,
};

struct tMsg
{
	uint16_t startBytes;
	uint8_t	 address;
	uint8_t  cmdIdentifier;
	uint8_t  data[480];
	
};

typedef enum tEchoType
{
	NotDef = 0,
	DE = 2,
	CE = 3,
} tEchoType;


typedef struct tEchoData
{
	tSensor      Sender;
	tEchoType    Type;
	unsigned int Amplitude;
	double        Height;
	unsigned int  Correlation;
	double        Dist;
} tEchoData;


typedef struct tImpedance
{
	int8_t        dZmin;
	int8_t        dFmin;
	uint8_t       dZenv;
	int8_t        impTemp;
} tImpedance;


typedef struct tNearRangeData
{
	float        spRingDownT;
	float        spAvgE;
} tNearRangeData;


typedef struct tFrame1Errors
{
	uint8_t DRV_Stg;
	uint8_t PAR_Err;
	uint8_t DSP_SM;
	uint8_t Bus_Err;
	uint8_t DSP_Init;
	uint8_t MEM_Test;
	uint8_t ADC_Test;
	uint8_t Lock_EOL;
	uint8_t	OTP_CRC;
} tFrame1Errors;

typedef struct tSensorData
{
	tEchoData           EchoList[MAX_ECHO];
	tNearRangeData      NearRangeData;
	tImpedance          Impedance;
	tFrame1Errors		Frame1Error;
	uint8_t				Clutter;
	uint8_t				Noise;
	uint8_t				CWLevel;
} tSensorData;

typedef struct
{
	uint8_t SensorType;
	uint8_t SiliconType;
} cStructSensorConfig;

typedef struct tSensorConfig
{
	cStructSensorConfig        Config;
	uint8_t SensorDataLineError;
	uint8_t SensorCommunicationError;
} tSensorConfig;


/* Central data structure for sensor data interchanged with the UssSimulator */
typedef struct tMultiTesterDataIF
{
	tSensorData     SensorData[MAX_SENSOR];
	tSensorConfig   SensorConfig[MAX_SENSOR];
	uint8_t			ShortVSEtoGND_Front;
	uint8_t			ShortVSEtoGND_Rear;
	uint8_t			Overcurrent_Front;
	uint8_t			Overcurrent_Rear;
	uint64_t		TimeStamp;
} tMultiTesterDataIF;

typedef struct tMultiTesterStat
{
	double	 time_echo_front;
	double   time_echo_rear;
	double   time_status_frame;
	double	 time_loop;
	uint32_t	overruns;
	uint32_t	iterations;
	uint32_t	readCount;
	uint32_t	writeCount;
	uint32_t	missingMsgs;
	uint32_t	OldDataCount;
} tMultiTesterStat;

enum eMessageIds : uint8_t
{
	DEFAULT_NONE = 0x00,
	ARRAY_ACCESS = 0xAA,
	ONLINE_CHECK = 0xFE,
	READ_FIRMWARE = 0xF1,
	WRITE_SENSOR_CONF = 0x41,
	FIRING_STATUS = 0x3F,

	
};

enum eSensorFiringStateMask {
	SENSOR_FIRING_STATE_WRONG = 0x000000,
	SENSOR_FIRING_STATE_01_07 = 0x000001,
	SENSOR_FIRING_STATE_02_08 = 0x000010,
	SENSOR_FIRING_STATE_03_09 = 0x000100,
	SENSOR_FIRING_STATE_04_10 = 0x001000,
	SENSOR_FIRING_STATE_05_11 = 0x010000,
	SENSOR_FIRING_STATE_06_12 = 0x100000
};

enum
{
	FRONT_CLUSTER = 0x00,
	REAR_CLUSTER = 0x01,
	NO_CLUSTER = 0x02,
};

enum eThreadState
{
	ThreadState_NoError =		 0x00000,
	ThreadState_MissingMsgWarn = 0x00001,
	ThreadState_MissingMsgErr =  0x00010,
	ThreadState_OverrunsWarn =	 0x00100,
	ThreadState_OverrunsErr =	 0x01000,
	ThreadState_NoDataRecErr =	 0x10000
};


/* Internal interface data */
typedef struct tUssSimulatorDevice
{
#ifdef XENO
	RT_MUTEX m_UssSimulatorMutex;
	RT_QUEUE m_msgQueue;
#elif defined _WIN32
	void *m_UssSimulatorMutex;
#else
	pthread_mutex_t m_UssSimulatorMutex;
#endif

#ifndef XENO
	std::queue<tMsg> m_msgQueue;
#endif

	tMultiTesterDataIF	data;
	bool		m_UssSimulatorLoopRunning;
	bool		resetcalled;
} tUssSimulatorDevice;


class UssSimulator
{
public:
	UssSimulator();
	virtual	~UssSimulator() {};

	virtual uint8_t Init(std::string IpMultiTester, uint16_t ListeningPort) { return USSSIMULATOR_INVAL_ARG_ERR; }
	virtual uint8_t Init(uint8_t address) { return USSSIMULATOR_INVAL_ARG_ERR; }
	uint8_t Transfer(tMultiTesterDataIF *data);
	uint8_t WriteSensorConfiguration(tMultiTesterDataIF data);

	uint8_t ShortVseToGnd(tMultiTesterDataIF data);
	uint8_t SetOvercurrent(tMultiTesterDataIF data);
	uint8_t SensorDataLineError(tMultiTesterDataIF data, uint8_t sensorNo);
	uint8_t SensorCommunicationError(tMultiTesterDataIF data);
	uint8_t StatusFrameAccess(tMultiTesterDataIF data, uint8_t sensorNo, uint8_t frameNo);

	uint8_t getFirmwareMajor(void);
	uint8_t getFirmwareMinor(void);

	uint8_t getUssSimulatorType(void);
	
	uint32_t GetThreadState(void);
	void ResetThreadState(void);
	bool isRunning();

	void SetSensorClusterSendState(bool EnableFrontCluster, bool EnableRearCluster); /* Enable/Disable if there shall be sent echo data for the specified cluster*/
	bool GetSensorClusterSendState(uint8_t SensorCluster); /* Get the state of the echo sending for specified cluster */
	eSensorFiringStateMask GetFiringStateMask(uint8_t sensor);

	void EnableSenssorFiringStateCheck(bool FiringStatusCheck); /* Enable/Disable if the firing status of the ECU shall be checked. */
	bool GetSensorFiringStateCheckStatus(void); /*  State of firing status monitoring. */
	uint8_t GetFiringStatus(void);
	uint32_t GetSensorFiringState(uint8_t SensorCluster); /* Get Firing Status from ECU */
	uint64_t GetSensorFiringStateUpdateTime(void);
	tMultiTesterStat GetMultiTesterStatistics(void);

	virtual uint8_t CloseUssSimulator(void) { return USSSIMULATOR_INVAL_ARG_ERR; }


protected:
	void InitializeMemberVariables(void);
	uint8_t CreateMtThread(const char* strFuncName);
	uint8_t MutexAcquire(void);
	uint8_t MutexRelease(void);
	uint8_t EnqueueMsg(tMsg msg, uint32_t messageSize);
	uint8_t DequeueMsg(void);
	uint8_t Loop(void);
	uint8_t EchoFrameArrayAccess(int8_t address);

	void SleepMs(unsigned int f_milliseconds);
	double GetTime(void); /*Returns the current pc time in ms*/
	void PrintError(const char* i_strFunctionName);
	void PrintError(const char* i_strFunctionName, uint32_t i_ulongErrorNumber);

	uint8_t m_FirmwareMajor;
	uint8_t m_FirmwareMinor;
	uint8_t m_UssSimulatorType;
	uint32_t m_threadState;
	bool m_missingMsgWarnTriggered;
	bool m_overrunsWarnTriggered;
	bool m_NoDataReceivedTriggered;

	tUssSimulatorDevice m_multitester;
	tMultiTesterStat m_multitester_statistics;

	bool m_SendFrontClusterData;
	bool m_SendRearClusterData;

	bool m_ReadFiringStatusEnabled;
	uint32_t m_FiringStatusBuffer;
	uint32_t m_FrontFiringState;
	uint32_t m_RearFiringState;

	uint64_t m_SensorFiringStateUpdateTimeStamp;
	uint64_t m_DataUpdateTimeStamp;

#ifdef _WIN32
	HANDLE m_UssSimulatorLoop;
	static DWORD WINAPI ThreadProc( LPVOID pvoid );
#elif defined XENO
	RT_TASK m_UssSimulatorLoop;
	static void ThreadProc(void* pvoid);
#else
	pthread_t m_UssSimulatorLoop;
	static void* ThreadProc(void* pvoid);
#endif



private:
	virtual uint8_t WriteMsg(void* msg, uint32_t messageSize) { return USSSIMULATOR_INVAL_ARG_ERR; }
	virtual	uint8_t ReadMsg(void) { return USSSIMULATOR_INVAL_ARG_ERR; }
	virtual	uint8_t ReadMsg(uint8_t readcheck, uint8_t address = NO_CLUSTER) { return USSSIMULATOR_INVAL_ARG_ERR; }

	void SetThreadState(eThreadState threadstate);
	void ResetThreadState(eThreadState threadstate);

};

#endif /* USS_SIMULATOR_H_ */