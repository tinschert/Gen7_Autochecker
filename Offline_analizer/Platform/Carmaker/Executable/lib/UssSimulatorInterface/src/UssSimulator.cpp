#include "UssSimulator.h"

#ifdef XENO
// define on which CPU the USS thread should run 
#define USS_THREAD_XENO_CPU 		(3)
#endif

UssSimulator::UssSimulator()
{
#ifndef XENO
	/*Empty msgQueue*/
	std::queue<tMsg>().swap(m_multitester.m_msgQueue);
#endif
	this->InitializeMemberVariables();
}

void UssSimulator::InitializeMemberVariables(void)
{
	m_multitester.m_UssSimulatorLoopRunning = false;

	int k, l;
	// init multi tester data array
	for (k = 0; k < MAX_SENSOR; k++)
	{
		for (l = 0; l < MAX_ECHO; l++)
		{
			m_multitester.data.SensorData[k].EchoList[l].Amplitude = 0;
			m_multitester.data.SensorData[k].EchoList[l].Correlation = 0;
			m_multitester.data.SensorData[k].EchoList[l].Dist = 0;
			m_multitester.data.SensorData[k].EchoList[l].Height = 2;
			m_multitester.data.SensorData[k].EchoList[l].Type = NotDef;
			m_multitester.data.SensorData[k].EchoList[l].Sender = SInval;
		}
		m_multitester.data.SensorData[k].Clutter = 0;
		m_multitester.data.SensorData[k].Impedance.dFmin = 0;
		m_multitester.data.SensorData[k].Impedance.dZenv = 0;
		m_multitester.data.SensorData[k].Impedance.dZmin = 0;
		m_multitester.data.SensorData[k].Impedance.impTemp = 0;
		m_multitester.data.SensorData[k].Noise = 0;
		m_multitester.data.SensorData[k].CWLevel = 0;
		m_multitester.data.SensorData[k].NearRangeData.spAvgE = 0;
		m_multitester.data.SensorData[k].NearRangeData.spRingDownT = 0;

		m_multitester.data.SensorConfig[k].Config.SensorType = CONF_USS_SENSOR_TYPE_6_5;
		m_multitester.data.SensorConfig[k].Config.SiliconType = CONF_USS_SENSOR_SILICON_CC;
		m_multitester.data.SensorConfig[k].SensorCommunicationError = NoError;
		m_multitester.data.SensorConfig[k].SensorDataLineError = NoError;

	}
	m_multitester.data.TimeStamp = 0;
	m_multitester.data.Overcurrent_Front = 0;
	m_multitester.data.Overcurrent_Rear = 0;
	m_multitester.data.ShortVSEtoGND_Front = 0;
	m_multitester.data.ShortVSEtoGND_Rear = 0;

	m_multitester_statistics.iterations = 0;
	m_multitester_statistics.missingMsgs = 0;
	m_multitester_statistics.overruns = 0;
	m_multitester_statistics.readCount = 0;
	m_multitester_statistics.writeCount = 0;
	m_multitester.resetcalled = false;

	m_FirmwareMajor = 0;
	m_FirmwareMinor = 0;

	m_threadState = 0;

	m_missingMsgWarnTriggered = false;
	m_overrunsWarnTriggered = false;
	m_NoDataReceivedTriggered = false;

	m_SendFrontClusterData = true;
	m_SendRearClusterData = true;

	m_FiringStatusBuffer = 0x000000;
	m_FrontFiringState = 0x000000;
	m_RearFiringState = 0x000000;
	m_ReadFiringStatusEnabled = false;

	m_DataUpdateTimeStamp = 1;
	m_SensorFiringStateUpdateTimeStamp = 0;
}

uint8_t UssSimulator::EchoFrameArrayAccess(int8_t address)
{
	tMsg msg;
	int pos, i, j, s, NrOfEchoesFound;
	tEchoData data;
	unsigned int type, height, dist, amplitude, correlation, sender;
	double TemperaturEnvrionment_celsius = 20;
	double tempfactor = (2/(331.5+0.6*TemperaturEnvrionment_celsius)); //unit is [s/m]
	msg.startBytes = 0xFFFF;
	msg.address = address;
	msg.cmdIdentifier = ARRAY_ACCESS;
	uint32_t messageSize = 480;
	pos = 0;

	//ToDo: Handle return variables
	MutexAcquire();

	for (i = 0; i < MAX_SENSOR / 2; i++) {
		s = i + address * MAX_SENSOR / 2;
		NrOfEchoesFound = 0;

		for (j = 0; j < MAX_ECHO; j++) {

			data = m_multitester.data.SensorData[s].EchoList[j];

			type = data.Type < 0 ? 0 : data.Type > 3 ? 3 : data.Type;
			height = (unsigned int)(data.Height < 0.0 ? 0.0 : data.Height > 3.0 ? 3.0 : data.Height);
			dist = (unsigned int)((data.Dist < 0.0 ? 0.0 : data.Dist > 12000.0 ? 12000.0 : data.Dist) * tempfactor*100);
			amplitude = data.Amplitude;
			correlation = data.Correlation;

			if (dist > 0.01)
			{
				sender = (unsigned int)data.Sender + 1;
				NrOfEchoesFound++;
			}
			else
			{
				//set the sender of every empty echo to 0 if at least one echo was received
				if (NrOfEchoesFound > 0)
					sender = 0;
				//otherwise sent the Id of the sender
				else
					sender = (unsigned int)data.Sender + 1;
				type = 0;
				height = 0;
				amplitude = 0;
				correlation = 0;
				dist = 0;
			}

			msg.data[pos++] = 0x00 | ((amplitude & 0x3F) << 4) | (correlation & 0x0F);
			msg.data[pos++] = 0x00 | ((dist & 0x1FFF) << 2) | ((amplitude & 0x3F) >> 4);
			msg.data[pos++] = 0x00 | ((height & 0x03) << 7) | ((dist & 0x1FFF) >> 6);
			msg.data[pos++] = 0x00 | ((type & 0x03) << 6) | ((sender & 0x1F) << 1) | ((height & 0x03) >> 1);

		}
	}
	//ToDo: Handle return variables
	MutexRelease();

	return WriteMsg(&msg,messageSize);

}

//time in ms
double UssSimulator::GetTime(void)
{
#ifndef XENO
	auto l_timestamp = std::chrono::system_clock::now();
	auto time_ns = std::chrono::time_point_cast<std::chrono::nanoseconds>(std::chrono::system_clock::now()).time_since_epoch().count();
#else
	auto time_ns = rt_timer_ticks2ns(rt_timer_read());
#endif 
	return time_ns * NANO_TO_MILLI_SEC;
}

void UssSimulator::SleepMs(unsigned int f_milliseconds)
{

#ifndef _WIN32
	// using NANOSLEEP(2) (see Linux Programmer's Manual) instead of Win function Sleep(1)
	struct timespec l_req , l_rem;

	l_req.tv_sec = f_milliseconds / 1000;
	l_req.tv_nsec = (f_milliseconds % 1000) * 1000;

	while(l_req.tv_sec > 0 || l_req.tv_nsec > 0)
	{
		int l_retVal = nanosleep(&l_req, &l_rem);

		if(l_retVal != 0)
		{
			// error encountered or interrupted by signal handler, 
			if(errno == EINTR)
			{
				// iterrupted, remaining time written to l_rem
				l_req = l_rem;
			}
		}
		else
		{
			return;
		}
	}
#elif defined XENO
	usleep(f_milliseconds);
#else
	Sleep(f_milliseconds);
#endif
}

void UssSimulator::SetThreadState(eThreadState threadstate)
{
	m_threadState = (m_threadState | threadstate);
}

void UssSimulator::ResetThreadState(eThreadState threadstate)
{
	m_threadState = (m_threadState & ~threadstate);
}

uint8_t UssSimulator::CreateMtThread(const char* strFuncName)
{
#if defined _WIN32
	m_UssSimulatorLoop = CreateThread(NULL, 0 , &ThreadProc, this, 0, NULL);
	if (m_UssSimulatorLoop == NULL)
	{
		PrintError("CreateThread", GetLastError());
		return USSSIMULATOR_THREAD_ERR;
	}
#elif defined XENO
	int error = rt_task_create(&m_UssSimulatorLoop, strFuncName,0,10,T_FPU | T_CPU(USS_THREAD_XENO_CPU));
	if(error != 0)
	{
		PrintError("CreateThread", error);
		return USSSIMULATOR_INVAL_ARG_ERR;
	}
	error = rt_task_start(&m_UssSimulatorLoop, &ThreadProc, this);
	if(error != 0)
	{
		PrintError("CreateThread", error);
		return USSSIMULATOR_INVAL_ARG_ERR;
	}
		
#else

	uint32_t error = pthread_create(&m_UssSimulatorLoop, NULL, &ThreadProc, this);
	if(error != 0)
	{
		PrintError("CreateThread", error);
		return USSSIMULATOR_THREAD_ERR;
	}

#endif
	return USSSIMULATOR_OK;
}


#ifdef _WIN32
	DWORD WINAPI UssSimulator::ThreadProc(LPVOID pvoid)
#elif defined XENO
	void UssSimulator::ThreadProc(void* pvoid)
#else
	void* UssSimulator::ThreadProc(void* pvoid)	
#endif
	{
		UssSimulator* loop = reinterpret_cast<UssSimulator*>(pvoid);
		loop->Loop();
		#ifdef _WIN32
			return 0;
		#elif defined XENO
			return;
		#else
			pthread_exit(0);
			return NULL;
		#endif
	}

uint8_t UssSimulator::MutexAcquire(void)
{
#ifdef _WIN32
	m_multitester.m_UssSimulatorMutex = OpenMutex(MUTEX_ALL_ACCESS,            // request full access
												  FALSE,                       // handle not inheritable
												  TEXT("m_UssSimulatorMutex"));// object name

#elif defined XENO
	rt_mutex_acquire(&m_multitester.m_UssSimulatorMutex, TM_INFINITE);
#else
	int l_time_ms = 0;
	while (l_time_ms < m_mutexTimeout)
	{
		int error = pthread_mutex_trylock(&m_multitester.m_UssSimulatorMutex);
		if (error == 0)
		{
			// got mutex, proceed with accessing the resource
			break;
		}
		else
		{
			//To Do: Handle warning
			//USS_DBG("Warning! pthread_mutex_trylock returned %i\n", error);
		}

		SleepMs(1);
		l_time_ms++;
	}

	if (l_time_ms >= m_mutexTimeout)
	{
		// timeout reached
		USS_OUT("Error getting mutex. USS Simulator busy\n");
	}
#endif

	return USSSIMULATOR_OK;
}

uint8_t UssSimulator::MutexRelease(void)
{
#ifdef _WIN32
	ReleaseMutex(m_multitester.m_UssSimulatorMutex);
#elif defined XENO
	rt_mutex_release(&m_multitester.m_UssSimulatorMutex);
#else
	int error = pthread_mutex_unlock(&m_multitester.m_UssSimulatorMutex);

	if (error != 0)
	{
		PrintError("pthread_mutex_unlock", error);
	}
#endif	
	return USSSIMULATOR_OK;
}

/* Put a message into the message queue. Called within main loop. */
uint8_t UssSimulator::EnqueueMsg (tMsg msg, uint32_t messageSize)
{
#ifdef XENO
	void *vmsg = rt_queue_alloc(&m_multitester.m_msgQueue, messageSize);
	if (vmsg == NULL)
		return USSSIMULATOR_INVAL_ARG_ERR;
	memcpy(vmsg, &msg, messageSize);
	if (rt_queue_send(&m_multitester.m_msgQueue, vmsg, messageSize, 0) < 0)
		return -1;
#else
	m_multitester.m_msgQueue.push(msg);
#endif
	return 0;

}


/* Fetch messages from the message queue and write them to the device */
uint8_t UssSimulator::DequeueMsg (void)
{
#ifdef XENO
	int  len;
	void *msg;
	while ((len = rt_queue_receive(&m_multitester.m_msgQueue, &msg, TM_NONBLOCK)) > 1) 
	{
		WriteMsg(&msg,len);
		ReadMsg();
		SleepMs(1);

		rt_queue_free(&m_multitester.m_msgQueue, msg);
	}

#else
	tMsg msg;
	if (m_multitester.m_msgQueue.empty())
		return 0;

	while (!m_multitester.m_msgQueue.empty())
	{
		msg = m_multitester.m_msgQueue.front();
		WriteMsg(&msg,sizeof(msg.data));
		ReadMsg(msg.cmdIdentifier,msg.address);
		SleepMs(1);
		m_multitester.m_msgQueue.pop();
	}
#endif
	return 0;
}


uint8_t UssSimulator::Loop(void)
{
	double time_loop, time_echo_front, time_echo_rear, time_cycle; //time_status_frame;
	uint32_t loopcounter = 0;

	double looptime_Sum = 0, looptime_Max = 0, looptime_Min = 10;
	uint32_t l_missingMsgsOldFast = 0, l_missingMsgsOldSlow = 0, l_overrunsOldFast = 0, l_overrunsOldSlow = 0;
	uint32_t l_cycleCountFast = 0, l_cycleCountSlow = 0;
	
#ifdef XENO
	unsigned long overruns;
#endif

	m_multitester_statistics.time_echo_front = 0;
	m_multitester_statistics.time_echo_rear = 0;
	m_multitester_statistics.time_loop = 0;
	m_multitester_statistics.time_status_frame = 0;

	m_multitester.m_UssSimulatorLoopRunning = true;

	time_loop = GetTime();
	time_cycle = 0;

#if defined _WIN32
	/* Initialize mutex depending on environment*/
		this->m_multitester.m_UssSimulatorMutex = reinterpret_cast<HANDLE>(CreateMutex(NULL, false, TEXT("m_UssSimulatorMutex")));
	if (this->m_multitester.m_UssSimulatorMutex == NULL)
	{
		PrintError("CreateMutex", GetLastError());
		return USSSIMULATOR_MUTEX_ERR;
	}
#elif defined (XENO)
	int error = rt_mutex_create(&this->m_multitester.m_UssSimulatorMutex, "m_UssSimulatorMutex");
	rt_task_set_periodic(NULL, TM_NOW, PERIODIC_TIME_MS*1000000);

	if (error != 0)
	{
		PrintError("rt_mutex_create", error);
		return USSSIMULATOR_MUTEX_ERR;
	}
#else 
	// for Linux, the sockets library is initialized automatically so only create the mutex
	pthread_mutexattr_t attr;
	pthread_mutexattr_init(&attr);
	pthread_mutexattr_settype(&attr, PTHREAD_MUTEX_RECURSIVE_NP);

	uint32_t error = pthread_mutex_init(&this->m_multitester.m_UssSimulatorMutex, &attr);

	if (error != 0)
	{
		PrintError("pthread_mutex_init", error);
		return USSSIMULATOR_MUTEX_ERR;
	}
#endif


	while (m_multitester.m_UssSimulatorLoopRunning)
	{
		/*<Statistics and cycle check>*/
		loopcounter++;
		if (loopcounter > 1)
		{
			time_cycle = GetTime() - time_loop;
			looptime_Sum += time_cycle;
			if (time_cycle > looptime_Max) {
				looptime_Max = time_cycle;
				//USS_DBG("looptime_Max: %f\n", looptime_Max);
			}
			if (time_cycle < looptime_Min)
			{
				looptime_Min = time_cycle;
			}


#ifdef XENO
		overruns = 0;

		/* wait until next multiple */
		rt_task_wait_period(&overruns);
		m_multitester_statistics.overruns++;
#else
			/* Check if cycle time is violated */
			if (time_cycle > PERIODIC_TIME_MS)
			{
				m_multitester_statistics.overruns++;
				//USS_OUT("overruns: %d\n", m_multitester.overruns);
				//USS_OUT("time_cycle: %f\n", time_cycle);
			}
			else
			{
				while (time_cycle < PERIODIC_TIME_MS)
				{
					time_cycle = GetTime() - time_loop;
					SleepMs(1);
				}
			}
#endif
		}
		/*</Statistics and cycle check>*/

		if (m_multitester.resetcalled)
		{
			l_missingMsgsOldFast = 0;
			l_missingMsgsOldSlow = 0;
			l_overrunsOldFast = 0;
			l_overrunsOldSlow = 0;
			l_cycleCountFast = 0;
			l_cycleCountSlow = 0;
			m_multitester_statistics.missingMsgs = 0;
			m_multitester_statistics.overruns = 0;
			m_multitester_statistics.readCount = 0;
			m_multitester_statistics.writeCount = 0;
			m_multitester_statistics.iterations = 0;
			m_multitester.resetcalled = false;
		}

		time_loop = GetTime();

		if (m_SendFrontClusterData)
		{
			time_echo_front = GetTime();
			/* Send echo distances front */
			if (EchoFrameArrayAccess(FRONT_CLUSTER) != 0)
			{
				m_multitester_statistics.missingMsgs++;
			}
			else
			{
				m_multitester_statistics.writeCount++;
			}
			if (ReadMsg(ARRAY_ACCESS) != USSSIMULATOR_OK)
			{
				m_multitester_statistics.missingMsgs++;
			}
			else
			{
				m_multitester_statistics.readCount++;
			}
			m_multitester_statistics.time_echo_front += (GetTime() - time_echo_front);
			//wait 1 ms
			SleepMs(1);
		}

		if (m_SendRearClusterData)
		{
			time_echo_rear = GetTime();
			/* Send echo distances rear */
			if (EchoFrameArrayAccess(REAR_CLUSTER) != 0)
			{
				m_multitester_statistics.missingMsgs++;
			}
			else
			{
				m_multitester_statistics.writeCount++;
			}
			if (ReadMsg(ARRAY_ACCESS) != USSSIMULATOR_OK)
			{
				m_multitester_statistics.missingMsgs++;
			}
			else
			{
				m_multitester_statistics.readCount++;
			}
			m_multitester_statistics.time_echo_rear += (GetTime() - time_echo_rear);
			//wait 1 ms
			SleepMs(1);
		}

		/* send messages which are possibly waiting in the message queue */
		DequeueMsg();

		m_multitester_statistics.time_loop += (GetTime() - time_loop);
		m_multitester_statistics.iterations++;

		if (l_cycleCountFast >= 50) // 0.5 seconds (cycle time of thread is 10 ms)
		{
			if (CalculateDifference(m_multitester_statistics.missingMsgs, l_missingMsgsOldFast) > 40) // if the communication is not working we will get an increase of 4 each cycle
			{
				//recoverable error / warning
				SetThreadState(ThreadState_MissingMsgWarn);
				m_missingMsgWarnTriggered = true;
			}
			else if (m_missingMsgWarnTriggered)
			{
				ResetThreadState(ThreadState_MissingMsgWarn);
				m_missingMsgWarnTriggered = false;
			}
			if (CalculateDifference(m_multitester_statistics.overruns, l_overrunsOldFast) > 10)
			{
				//recoverable error / warning
				SetThreadState(ThreadState_OverrunsWarn);
				m_overrunsWarnTriggered = true;
			}
			else if(m_overrunsWarnTriggered)
			{
				ResetThreadState(ThreadState_OverrunsWarn);
				m_overrunsWarnTriggered = false;
			}

			l_missingMsgsOldFast = m_multitester_statistics.missingMsgs;
			l_overrunsOldFast = m_multitester_statistics.overruns;
			l_cycleCountFast = 0;
		}
		else
		{
			l_cycleCountFast++;
		}

		if (l_cycleCountSlow >= 500) // 5 seconds (cycle time of thread is 10 ms)
		{
			if (CalculateDifference(m_multitester_statistics.missingMsgs, l_missingMsgsOldSlow) > 100)
			{
				//non recoverable error
				SetThreadState(ThreadState_MissingMsgErr);
			}
			if (CalculateDifference(m_multitester_statistics.overruns, l_overrunsOldSlow) > 100)
			{
				//non recoverable error
				SetThreadState(ThreadState_OverrunsErr);
			}

			l_missingMsgsOldSlow = m_multitester_statistics.missingMsgs;
			l_overrunsOldSlow = m_multitester_statistics.overruns;
			l_cycleCountSlow = 0;
		}
		else
		{
			l_cycleCountSlow++;
		}

		if (m_multitester.data.TimeStamp != 0 && m_DataUpdateTimeStamp != 0)
		{
			if (m_DataUpdateTimeStamp == m_multitester.data.TimeStamp)
			{
				m_multitester_statistics.OldDataCount++;
			}
			else
			{
				m_DataUpdateTimeStamp = m_multitester.data.TimeStamp;
				m_multitester_statistics.OldDataCount = 0;
			}

			if (m_multitester_statistics.OldDataCount > 100) // no new data received from simulation for 1 second
			{
				SetThreadState(ThreadState_NoDataRecErr);
				m_NoDataReceivedTriggered = true;
			}
			else if (m_NoDataReceivedTriggered)
			{
				ResetThreadState(ThreadState_NoDataRecErr);
				m_NoDataReceivedTriggered = false;
			}

		}
	}

	return 0;
}

uint8_t UssSimulator::Transfer(tMultiTesterDataIF * data)
{

	if (!m_multitester.m_UssSimulatorLoopRunning)
		return USSSIMULATOR_COM_ERR;

	//ToDo: Handle return variables
	MutexAcquire();

	memcpy(&m_multitester.data, data, sizeof(tMultiTesterDataIF));

	//ToDo: Handle return variables
	MutexRelease();

	return USSSIMULATOR_OK;
}

uint8_t UssSimulator::WriteSensorConfiguration(tMultiTesterDataIF data)
{
	if (!m_multitester.m_UssSimulatorLoopRunning)
		return USSSIMULATOR_COM_ERR;

	const tSensorConfig *cfg = data.SensorConfig;

	tMsg sensorConfigMessage;
	sensorConfigMessage.cmdIdentifier = WRITE_SENSOR_CONF;
	uint32_t messageSize = 12;
	uint8_t  dummy_data[480];
	memset(dummy_data, '\0', sizeof(dummy_data)); // to prevent [-Wmaybe-uninitialized] warning
	memcpy(sensorConfigMessage.data, dummy_data, sizeof(dummy_data));
	
	//Front:
	sensorConfigMessage.address = FRONT_CLUSTER;

	uint8_t msg[12];
	int pos = 0;
	int i = 0;
	memset(msg, '\0', 12);

	for (i = 0; i < MAX_SENSOR / 2; i++)
	{
		msg[pos++] = cfg[i].Config.SensorType;
		msg[pos++] = cfg[i].Config.SiliconType;
	}

	memcpy(sensorConfigMessage.data, msg, sizeof(msg));
	EnqueueMsg(sensorConfigMessage,messageSize);

	//Rear:
	sensorConfigMessage.address = REAR_CLUSTER;
	pos = 0;
	memset(msg, '\0', 12);

	for (i = MAX_SENSOR / 2; i < MAX_SENSOR; i++)
	{
		msg[pos++] = cfg[i].Config.SensorType;
		msg[pos++] = cfg[i].Config.SiliconType;
	}
	memcpy(sensorConfigMessage.data, msg, sizeof(msg));
	EnqueueMsg(sensorConfigMessage,messageSize);

	return USSSIMULATOR_OK;
}

uint8_t UssSimulator::GetFiringStatus(void)
{
	if (!m_multitester.m_UssSimulatorLoopRunning)
		return USSSIMULATOR_COM_ERR;

	if (this->m_UssSimulatorType == USB)
	{
		printf("GetFiringStatus is not supported for USB UssSimulator!\n");
		return USSSIMULATOR_INVAL_ARG_ERR;
	}

	m_SensorFiringStateUpdateTimeStamp = m_multitester.data.TimeStamp;
	
	tMsg GetFiringStatusMsg;
	GetFiringStatusMsg.address = FRONT_CLUSTER;
	GetFiringStatusMsg.cmdIdentifier = FIRING_STATUS;
	uint32_t messageSize = 0;
	
	if (EnqueueMsg(GetFiringStatusMsg, messageSize) != 0)
		return USSSIMULATOR_QUEUE_ERR;

	GetFiringStatusMsg.address = REAR_CLUSTER;

	if (EnqueueMsg(GetFiringStatusMsg, messageSize) != 0)
		return USSSIMULATOR_QUEUE_ERR;

	return USSSIMULATOR_OK;
}

uint8_t UssSimulator::ShortVseToGnd(tMultiTesterDataIF data)
{
	if (!m_multitester.m_UssSimulatorLoopRunning)
		return USSSIMULATOR_COM_ERR;

	if ((data.ShortVSEtoGND_Front != 1 && data.ShortVSEtoGND_Front != 0)
		|| (data.ShortVSEtoGND_Rear != 1 && data.ShortVSEtoGND_Rear != 0))
		return USSSIMULATOR_INVAL_ARG_ERR;

	tMsg msg;
	msg.cmdIdentifier = 0x62;
	uint32_t messageSize = 1;
	uint8_t  dummy_data[480];
	memset(dummy_data, '\0', sizeof(dummy_data)); // to prevent [-Wmaybe-uninitialized] warning
	memcpy(msg.data, dummy_data, sizeof(dummy_data));

	msg.address = FRONT_CLUSTER;
	if (data.ShortVSEtoGND_Front == 0)
		msg.data[0] = 0x00;
	else
		msg.data[0] = 0xFF;

	if (EnqueueMsg(msg,messageSize) != 0)
		return USSSIMULATOR_QUEUE_ERR;

	msg.address = REAR_CLUSTER;
	if (data.ShortVSEtoGND_Rear == 0)
		msg.data[0] = 0x00;
	else
		msg.data[0] = 0xFF;

	if (EnqueueMsg(msg,messageSize) != 0)
		return USSSIMULATOR_QUEUE_ERR;

	return USSSIMULATOR_OK;
}

uint8_t UssSimulator::SetOvercurrent(tMultiTesterDataIF data)
{
	if (!m_multitester.m_UssSimulatorLoopRunning)
		return USSSIMULATOR_COM_ERR;

	if ((data.Overcurrent_Front != 1 && data.Overcurrent_Front != 0)
		|| (data.Overcurrent_Rear != 1 && data.Overcurrent_Rear != 0))
		return USSSIMULATOR_INVAL_ARG_ERR;

	tMsg msg;
	msg.cmdIdentifier = 0x6C;
	uint32_t messageSize = 1;
	uint8_t  dummy_data[480];
	memset(dummy_data, '\0', sizeof(dummy_data)); // to prevent [-Wmaybe-uninitialized] warning
	memcpy(msg.data, dummy_data, sizeof(dummy_data));

	msg.address = FRONT_CLUSTER;
	if (data.Overcurrent_Front == 0)
		msg.data[0] = 0x00;
	else
		msg.data[0] = 0xFF;

	if (EnqueueMsg(msg, messageSize) != 0)
		return USSSIMULATOR_QUEUE_ERR;

	msg.address = REAR_CLUSTER;
	if (data.Overcurrent_Rear == 0)
		msg.data[0] = 0x00;
	else
		msg.data[0] = 0xFF;

	if (EnqueueMsg(msg, messageSize) != 0)
		return USSSIMULATOR_QUEUE_ERR;

	return USSSIMULATOR_OK;
}

uint8_t UssSimulator::SensorDataLineError(tMultiTesterDataIF data, uint8_t sensorNo)
{
	if (!m_multitester.m_UssSimulatorLoopRunning)
		return USSSIMULATOR_COM_ERR;
	const tSensorConfig *cfg = data.SensorConfig;

	if (sensorNo < 0 || sensorNo >= SInval
		|| (cfg[sensorNo].SensorDataLineError != NoError && cfg[sensorNo].SensorDataLineError != SHORT_TO_GROUND &&
			cfg[sensorNo].SensorDataLineError != SHORT_TO_SUPPLY && cfg[sensorNo].SensorDataLineError != SENSOR_COM_LINE_OPEN)) {
		return USSSIMULATOR_INVAL_ARG_ERR;
	}

	tMsg msg;
	msg.cmdIdentifier = 0x3A;
	uint32_t messageSize = 2;
	uint8_t  dummy_data[480];
	memset(dummy_data, '\0', sizeof(dummy_data)); // to prevent [-Wmaybe-uninitialized] warning
	memcpy(msg.data, dummy_data, sizeof(dummy_data));
	msg.address = FRONT_CLUSTER;

	if (sensorNo < MAX_SENSOR / 2) { //Front sensor
		msg.address = FRONT_CLUSTER;
		msg.data[0] = sensorNo;
	}
	else {//Rear sensor
		msg.address = REAR_CLUSTER;
		msg.data[0] = sensorNo - (MAX_SENSOR / 2);
	}

	msg.data[1] = cfg[sensorNo].SensorDataLineError;

	if (EnqueueMsg(msg,messageSize) != 0)
		return USSSIMULATOR_QUEUE_ERR;

	return USSSIMULATOR_OK;
}


uint8_t UssSimulator::SensorCommunicationError(tMultiTesterDataIF data)
{
	if (!m_multitester.m_UssSimulatorLoopRunning)
		return USSSIMULATOR_COM_ERR;
	const tSensorConfig* cfg = data.SensorConfig;
	uint8_t dataFront[MAX_SENSOR / 2];
	uint8_t dataRear[MAX_SENSOR / 2];
	memset(dataFront, '\0', sizeof(dataFront));
	memset(dataRear, '\0', sizeof(dataRear));

	for (uint8_t sensorNo = 0; sensorNo < MAX_SENSOR; ++sensorNo)
	{
		if(cfg[sensorNo].SensorCommunicationError != NoError && 
			cfg[sensorNo].SensorCommunicationError != SENSOR_COMMUNICATION_ERROR &&
			cfg[sensorNo].SensorCommunicationError != SENSOR_OUT_OF_SYNC)
		{
			continue; // No valid value given
		}
		if (sensorNo < MAX_SENSOR / 2) { //Front sensor
			dataFront[sensorNo] = cfg[sensorNo].SensorCommunicationError;
		}
		else {//Rear sensor
			dataRear[sensorNo - (MAX_SENSOR / 2)] = cfg[sensorNo].SensorCommunicationError;
		}
	}

	tMsg msg;
	msg.cmdIdentifier = 0x5E;
	uint32_t messageSize = 6;
	uint8_t  dummy_data[480];
	memset(dummy_data, '\0', sizeof(dummy_data)); // to prevent [-Wmaybe-uninitialized] warning
	memcpy(msg.data, dummy_data, sizeof(dummy_data));
	
	msg.address = FRONT_CLUSTER;

	for (uint8_t sensor = 0; sensor < MAX_SENSOR / 2; ++sensor)
	{
		if (dataFront[sensor] == SENSOR_COMMUNICATION_ERROR)
		{
			msg.data[sensor] = 0x02; // Set Inv Ins Par error
		}
		if (dataFront[sensor] == SENSOR_OUT_OF_SYNC)
		{
			msg.data[sensor] = 0x08; // Set Rep CLK ADJ error
		}
		else
		{
			msg.data[sensor] = 0x00;
		}	
	}

	if (EnqueueMsg(msg, messageSize) != 0)
		return USSSIMULATOR_QUEUE_ERR;

	msg.address = REAR_CLUSTER;

	for (uint8_t sensor = 0; sensor < MAX_SENSOR / 2; ++sensor)
	{
		if (dataRear[sensor] == SENSOR_COMMUNICATION_ERROR)
		{
			msg.data[sensor] = 0x02; // Set Inv Ins Par error
		}
		if (dataRear[sensor] == SENSOR_OUT_OF_SYNC)
		{
			msg.data[sensor] = 0x08; // Set Rep CLK ADJ error
		}
		else
		{
			msg.data[sensor] = 0x00;
		}
	}

	if (EnqueueMsg(msg, messageSize) != 0)
		return USSSIMULATOR_QUEUE_ERR;

	return USSSIMULATOR_OK;
}

uint8_t UssSimulator::StatusFrameAccess(tMultiTesterDataIF data, uint8_t sensorNo, uint8_t frameNo)
{
	//USS_DBG("StatusFrameAccess called\n")
	if (!m_multitester.m_UssSimulatorLoopRunning)
		return USSSIMULATOR_COM_ERR;

	uint8_t t_sensor = 0;
	tMsg msg;
	msg.cmdIdentifier = 0x5F;
	uint32_t messageSize = 6;

	uint8_t  dummy_data[480];
	memset(dummy_data, '\0', sizeof(dummy_data)); // to prevent [-Wmaybe-uninitialized] warning
	memcpy(msg.data, dummy_data, sizeof(dummy_data));

	if (sensorNo < MAX_SENSOR / 2)
	{
		msg.address = FRONT_CLUSTER;
		t_sensor = sensorNo;
	}
	else
	{
		msg.address = REAR_CLUSTER;
		t_sensor = sensorNo - MAX_SENSOR / 2;
	}
	msg.data[0] = (uint8_t)t_sensor;
	msg.data[1] = (uint8_t)frameNo - 1; //starts with 0 in msg

	switch (frameNo)
	{
	case 1:
	{
		uint8_t cw_noise, noise, clutter, DRV_Stg, PAR_Err, DSP_SM, Bus_Err, DSP_Init, MEM_Test, ADC_Test, Lock_EOL, OTP_CRC;

		noise = (uint8_t)((data.SensorData[sensorNo].Noise < 0.0 ? 0.0 : data.SensorData[sensorNo].Noise > 63.0 ? 63.0 : data.SensorData[sensorNo].Noise));
		clutter = (uint8_t)((data.SensorData[sensorNo].Clutter < 0.0 ? 0.0 : data.SensorData[sensorNo].Clutter > 63.0 ? 63.0 : data.SensorData[sensorNo].Clutter));
		cw_noise = (uint8_t)((data.SensorData[sensorNo].CWLevel < 0.0 ? 0.0 : data.SensorData[sensorNo].CWLevel > 63.0 ? 63.0 : data.SensorData[sensorNo].CWLevel));
		
		DRV_Stg = (uint8_t)((data.SensorData[sensorNo].Frame1Error.DRV_Stg < 0.0 ? 0.0 : data.SensorData[sensorNo].Frame1Error.DRV_Stg > 1.0 ? 1.0 : data.SensorData[sensorNo].Frame1Error.DRV_Stg));
		PAR_Err = (uint8_t)((data.SensorData[sensorNo].Frame1Error.PAR_Err < 0.0 ? 0.0 : data.SensorData[sensorNo].Frame1Error.PAR_Err > 1.0 ? 1.0 : data.SensorData[sensorNo].Frame1Error.PAR_Err));
		DSP_SM = (uint8_t)((data.SensorData[sensorNo].Frame1Error.DSP_SM < 0.0 ? 0.0 : data.SensorData[sensorNo].Frame1Error.DSP_SM > 1.0 ? 1.0 : data.SensorData[sensorNo].Frame1Error.DSP_SM));
		Bus_Err = (uint8_t)((data.SensorData[sensorNo].Frame1Error.Bus_Err < 0.0 ? 0.0 : data.SensorData[sensorNo].Frame1Error.Bus_Err > 1.0 ? 1.0 : data.SensorData[sensorNo].Frame1Error.Bus_Err));
		DSP_Init = (uint8_t)((data.SensorData[sensorNo].Frame1Error.DSP_Init < 0.0 ? 0.0 : data.SensorData[sensorNo].Frame1Error.DSP_Init > 1.0 ? 1.0 : data.SensorData[sensorNo].Frame1Error.DSP_Init));
		MEM_Test = (uint8_t)((data.SensorData[sensorNo].Frame1Error.MEM_Test < 0.0 ? 0.0 : data.SensorData[sensorNo].Frame1Error.MEM_Test > 1.0 ? 1.0 : data.SensorData[sensorNo].Frame1Error.MEM_Test));
		ADC_Test = (uint8_t)((data.SensorData[sensorNo].Frame1Error.ADC_Test < 0.0 ? 0.0 : data.SensorData[sensorNo].Frame1Error.ADC_Test > 1.0 ? 1.0 : data.SensorData[sensorNo].Frame1Error.ADC_Test));
		Lock_EOL = (uint8_t)((data.SensorData[sensorNo].Frame1Error.Lock_EOL < 0.0 ? 0.0 : data.SensorData[sensorNo].Frame1Error.Lock_EOL > 1.0 ? 1.0 : data.SensorData[sensorNo].Frame1Error.Lock_EOL));
		OTP_CRC = (uint8_t)((data.SensorData[sensorNo].Frame1Error.OTP_CRC < 0.0 ? 0.0 : data.SensorData[sensorNo].Frame1Error.OTP_CRC > 1.0 ? 1.0 : data.SensorData[sensorNo].Frame1Error.OTP_CRC));
		
		msg.data[5] = 0x00 | (DSP_SM) | (PAR_Err << 1) | (DRV_Stg << 2) |(0x01 << 4);
		msg.data[4] = 0x00 | (OTP_CRC << 2) | (Lock_EOL << 3) | (ADC_Test << 4) | (MEM_Test << 5) | (DSP_Init << 6) | (Bus_Err << 7) |  ((cw_noise & 0x30) >> 4) ;
		msg.data[3] = 0x00 | ((cw_noise & 0xF) << 4) | ((noise & 0x3C) >> 2);
		msg.data[2] = 0x00 | ((noise & 0x3) << 6) | (clutter & 0x3F);

		break;
	}
	case 3:
	{
		uint8_t impTemp, dZenv;
		int32_t dZmin, dFmin;
		const tImpedance ImpData = data.SensorData[sensorNo].Impedance;

		impTemp = (uint8_t)(1 + floor((ImpData.impTemp < -40.0 ? -40.0 : ImpData.impTemp > 148.0 ? 148.0 : ImpData.impTemp) + 40.0) / 3.0);
		dZenv = (uint8_t)((ImpData.dZenv < 0.0 ? 0.0 : ImpData.dZenv > 255.0 ? 255.0 : ImpData.dZenv));
		dZmin = (int32_t)((ImpData.dZmin < -64.0 ? -64.0 : ImpData.dZmin > 63.0 ? 63.0 : ImpData.dZmin));
		if (dZmin < 0) dZmin += 128;
		dFmin = (int32_t)(ImpData.dFmin < -64.0 ? -64.0 : ImpData.dFmin > 63.0 ? 63.0 : ImpData.dFmin);
		if (dFmin < 0) dFmin += 128;

		msg.data[5] = 0x00 | (0x03 << 4) | ((impTemp & 0x3C) >> 2);
		msg.data[4] = 0x00 | ((impTemp & 0x3) << 6) | ((dZenv & 0xFC) >> 2);
		msg.data[3] = 0x00 | ((dZenv & 0x3) << 7) | ((dZmin & 0x3E) >> 1);
		msg.data[2] = 0x00 | ((dZmin & 0x1) << 7) | (dFmin & 0x7F);

		break;
	}
	default: //no other frame currently needed
		break;
	}

	if (EnqueueMsg(msg,messageSize) != 0)
		return USSSIMULATOR_QUEUE_ERR;

	return USSSIMULATOR_OK;
}

uint8_t UssSimulator::getFirmwareMajor(void)
{
	return m_FirmwareMajor;
}

uint8_t UssSimulator::getFirmwareMinor(void)
{
	return m_FirmwareMinor;
}

uint8_t UssSimulator::getUssSimulatorType(void)
{
	return m_UssSimulatorType;
}

uint32_t UssSimulator::GetThreadState(void)
{
	return m_threadState;
}

void UssSimulator::ResetThreadState(void)
{
	m_threadState = 0x0;
	m_multitester.resetcalled = true;
}

bool UssSimulator::isRunning()
{
	return m_multitester.m_UssSimulatorLoopRunning;
}

void UssSimulator::SetSensorClusterSendState(bool EnableFrontCluster, bool EnableRearCluster)
{
	m_SendFrontClusterData = EnableFrontCluster;
	m_SendRearClusterData = EnableRearCluster;
}

bool UssSimulator::GetSensorClusterSendState(uint8_t SensorCluster)
{
	if (SensorCluster == FRONT_CLUSTER)
		return m_SendFrontClusterData;
	if (SensorCluster == REAR_CLUSTER)
		return m_SendRearClusterData;

	return 0;
}

void UssSimulator::EnableSenssorFiringStateCheck(bool FiringStatusCheck) { m_ReadFiringStatusEnabled = FiringStatusCheck; }

bool UssSimulator::GetSensorFiringStateCheckStatus(void) { return m_ReadFiringStatusEnabled; }

uint32_t UssSimulator::GetSensorFiringState(uint8_t SensorCluster)
{
	if (SensorCluster == FRONT_CLUSTER)
		return m_FrontFiringState;
	if (SensorCluster == REAR_CLUSTER)
		return m_RearFiringState;

	return 0;
}

uint64_t UssSimulator::GetSensorFiringStateUpdateTime(void)
{
	return m_SensorFiringStateUpdateTimeStamp;
}

eSensorFiringStateMask UssSimulator::GetFiringStateMask(uint8_t sensor)
{
	switch (sensor + 1)
	{
	case 1:
	case 7:
		return SENSOR_FIRING_STATE_01_07;
	case 2:
	case 8:
		return SENSOR_FIRING_STATE_02_08;
	case 3:
	case 9:
		return SENSOR_FIRING_STATE_03_09;
	case 4:
	case 10:
		return SENSOR_FIRING_STATE_04_10;
	case 5:
	case 11:
		return SENSOR_FIRING_STATE_05_11;
	case 6:
	case 12:
		return SENSOR_FIRING_STATE_06_12;

	default:
		return SENSOR_FIRING_STATE_WRONG;
	}

	return SENSOR_FIRING_STATE_WRONG;

}

tMultiTesterStat UssSimulator::GetMultiTesterStatistics(void)
{
	return m_multitester_statistics;
}

void UssSimulator::PrintError(const char* i_strFunctionName)
{
	printf("UssSimulator: ");
	printf(i_strFunctionName);
	printf(" was not successfull!\n");
}

void UssSimulator::PrintError(const char* i_strFunctionName, uint32_t i_ulongErrorNumber)
{
	PrintError(i_strFunctionName);
	printf("Function returned %u\n", i_ulongErrorNumber);
}

