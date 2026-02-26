/*
 *
 *	UdpMultiTester.cpp
 *
 *  Created on: 07.02.2018
 * @author BNC1LR
 */

#include "UdpMultiTester.h"

UdpMultiTester::UdpMultiTester(void)
{
	this->m_UssSimulatorType = UDP;
}


UdpMultiTester::~UdpMultiTester(void)
{
	//printf("~UdpMultiTester called\n");
	//CloseUssSimulator();
}

uint8_t UdpMultiTester::Init(std::string IpMultiTester, uint16_t ListeningPort)
{
	if (this->m_multitester.m_UssSimulatorLoopRunning)
		return USSSIMULATOR_BUSY_ERR;
	this->InitializeMemberVariables();
#if defined _WIN32
	WSADATA wsa;

	//Initialise winsock
	if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0)
	{
		PrintError("WSAStartup", WSAGetLastError());
		return USSSIMULATOR_COM_SOCKET_ERR;
	}
#endif

	//setup address structure
	memset((char *) &AddressMultiTester,0,sizeof(AddressMultiTester));
	AddressMultiTester.sin_family = AF_INET;
    AddressMultiTester.sin_port = htons(ListeningPort);
    
	if(inet_pton(AF_INET, IpMultiTester.c_str(), &AddressMultiTester.sin_addr)<=0)
	{
		PrintError("inet_pton: no valid network address given");
		return USSSIMULATOR_COM_SOCKET_ERR;
	}

	slen=sizeof(AddressMultiTester);

	//create socket
	m_tbgsocket = bgsocket_open((struct sockaddr *)&AddressMultiTester,SOCK_DGRAM);
	if (m_tbgsocket == NULL)
	{
		PrintError("bgsocket_open");
		return USSSIMULATOR_COM_SOCKET_ERR;
	}

	/* Online check of UssSimulator*/
	
	uint8_t l_counter_snt = 0, l_counter_rcv = 0, l_counter = 1;
	bool l_write_no_success = true, l_read_no_success = true;
	do {
		l_write_no_success = true;
		l_read_no_success = true;
		if (WriteCheck() == USSSIMULATOR_OK)
		{
			l_counter_snt++;
			l_write_no_success = false;
		}
		
		if (ReadCheck() == USSSIMULATOR_OK)
		{
			l_counter_rcv++;
			l_read_no_success = false;
		}

		if (l_counter > 5)
		{
			if (l_counter_snt < l_counter)
			{
				PrintError("WriteCheck");
				return USSSIMULATOR_COM_SEND_ERR;
			}
			if (l_counter_rcv < l_counter)
			{
				PrintError("ReadCheck");
				return USSSIMULATOR_COM_RECV_ERR;
			}
			
			return USSSIMULATOR_COM_ERR;
		}
		l_counter++;
		SleepMs(10);
	} while (l_write_no_success || l_read_no_success);

		
	/* Read firmware version of UssSimulator */
	if (ReadFirmware() != USSSIMULATOR_OK)
	{
		PrintError("ReadFirmware");
		return USSSIMULATOR_COM_SEND_ERR;
	}
	if (ReadMsg(READ_FIRMWARE) != USSSIMULATOR_OK)
	{
		PrintError("ReadFirmwareMessage");
		return USSSIMULATOR_COM_RECV_ERR;
	}
	//printf("UssSimulator: Firmware version %d.%d detected\n", getFirmwareMajor(), getFirmwareMinor());

	if (CreateMtThread("CommunicationThread") != USSSIMULATOR_OK)
	{
		PrintError("CreateMtThread");
		return USSSIMULATOR_THREAD_ERR;
	}

	SleepMs(1000);

	return USSSIMULATOR_OK;
}


uint8_t UdpMultiTester::CloseUssSimulator(void)
{
	//USS_DBG("CloseUssSimulator\n");
	if (m_multitester.m_UssSimulatorLoopRunning)
	{
		m_multitester.m_UssSimulatorLoopRunning = false;

#ifdef _WIN32
		uint8_t err = 0;
		
		//stop execution of mt thread
		WaitForMultipleObjects(1, &m_UssSimulatorLoop, TRUE, INFINITE);
		if (!CloseHandle(reinterpret_cast<HANDLE>(m_multitester.m_UssSimulatorMutex)))
		{
			USS_OUT("CloseHandle Mutex failed with error code: %d\n", GetLastError());
			err++;
		}
		if (!CloseHandle(m_UssSimulatorLoop))
		{
			USS_OUT("CloseHandle Loop failed with error code: %d\n", GetLastError());
			err++;
		}
		WSACleanup();
		//USS_DBG("Cleanup done\n");

		if (err != 0)
		{
			return USSSIMULATOR_COM_ERR;
		}
#elif defined XENO
		rt_queue_delete(&m_multitester.m_msgQueue);
		rt_mutex_delete(&m_multitester.m_UssSimulatorMutex);
		rt_task_delete(&m_UssSimulatorLoop);
		close(m_tbgsocket->Socket);
#else
		// wait for loop thread to terminate (call blocks main thread)
		pthread_join(m_UssSimulatorLoop, NULL);
		// for Linux, no cleanup of sockets library necessary
#endif
	}

	return USSSIMULATOR_OK;
}

uint8_t UdpMultiTester::WriteCheck(void)
{
	tMsg msg;

	msg.address = FRONT_CLUSTER;
	msg.cmdIdentifier = ONLINE_CHECK;
	uint32_t messageSize = 0;

	if (WriteMsg(&msg, messageSize) != USSSIMULATOR_OK)
	{
		printf("Problem sending data to multi tester\n");
		return USSSIMULATOR_COM_SEND_ERR;
	}

	return USSSIMULATOR_OK;
}

uint8_t UdpMultiTester::ReadCheck(void)
{
	if (ReadMsg(ONLINE_CHECK) != USSSIMULATOR_OK)
	{
		printf("Problem receiving data from multi tester\n");
		return USSSIMULATOR_COM_RECV_ERR;
	}
	return USSSIMULATOR_OK;
}

uint8_t UdpMultiTester::WriteMsg(void* message, uint32_t messageSize)
{
	uint32_t pos = 0;
	uint32_t i = 0;
	char l_msg[500];
	memset(l_msg, '\0', sizeof(l_msg));

	tMsg* msg = reinterpret_cast<tMsg*>(message);

	//UDP Header
	for (size_t i = 0; i < sizeof(UDP_HEADER) - 1; i++) l_msg[pos++] = UDP_HEADER[i];
	//Start Bytes
	for (size_t i = 0; i < (sizeof(UDP_START_BYTES) - 1); i++)l_msg[pos++] = UDP_START_BYTES[i];
	l_msg[pos++] = msg->address;
	l_msg[pos++] = msg->cmdIdentifier;

	//for (i=0;i<sizeof(message.data);i++)
	for (i = 0; i < messageSize; i++)
	{
		l_msg[pos++] = msg->data[i];
	}

	if (sendto(m_tbgsocket->Socket, (const char*)l_msg, sizeof(l_msg), 0, (struct sockaddr*)&AddressMultiTester, slen) == SOCKET_ERROR)
	{
		//USS_DBG("%.0f - sendto() failed with error code : %d\n", _GetTime(), WSAGetLastError());
		return USSSIMULATOR_COM_ERR;
	}
	/*
	printf("%.0f - Msg send : ",GetTime());
	for (int i = 9; i < messageSize;i++)
	{
		printf(" %02X",reinterpret_cast<uint8_t&>(l_msg[i]));

	}
	printf("\n");
	*/
	return USSSIMULATOR_OK;

}

uint8_t	UdpMultiTester::ReadMsg(void)
{
	return ReadMsg(DEFAULT_NONE);
}

uint8_t UdpMultiTester::ReadMsg(uint8_t readcheck, uint8_t address)
{
	//clear the buffer by filling null, it might have previously received data
	char answer[500];
	memset(answer, '\0', 500);

	int answerlen = 8;
	if (readcheck == READ_FIRMWARE)
	{
		answerlen = 9;
	}
	else if (readcheck == FIRING_STATUS)
	{
		answerlen = 13;
	}

	/*try to receive some data, this is a blocking call*/
	int response = recvfrom(m_tbgsocket->Socket, answer, answerlen, 0, (struct sockaddr*)&AddressMultiTester, &slen);

	if (response == SOCKET_ERROR)
	{
		//USS_DBG("recvfrom() failed with error code : %d\n", WSAGetLastError());
		//USS_DBG("->readcheck: %d\n", readcheck);
		return USSSIMULATOR_COM_ERR;
	}
	if (readcheck == FIRING_STATUS) 
	{
		/* if Firing status response is expected but not received, read the msgbuffer once more to check if the message is there*/
		if (reinterpret_cast<uint8_t&>(answer[6]) != 0x06) 
		{
			response = recvfrom(m_tbgsocket->Socket, answer, answerlen, 0, (struct sockaddr*)&AddressMultiTester, &slen);
			if (response == SOCKET_ERROR)
			{
				//USS_DBG("recvfrom() failed with error code : %d\n", WSAGetLastError());
				//USS_DBG("->readcheck: %d\n", readcheck);
				return USSSIMULATOR_COM_ERR;
			}
		}
	}
	//printf("Msg rcvd : ");
	//for (int i = 7; i < response;i++)
	//{
	//	printf(" %d", ((unsigned char)answer[i]));
	//}
	//printf("\n");

	if (readcheck == ARRAY_ACCESS) /* array access called */
	{
		if (reinterpret_cast<uint8_t&>(answer[7]) == ARRAY_ACCESS)
		{
			return USSSIMULATOR_OK; // ack received
		}
		else
		{
			return USSSIMULATOR_COM_ERR; //no ack received
		}
			
	}
	else if (readcheck == ONLINE_CHECK) /* online check */
	{
		if (reinterpret_cast<uint8_t&>(answer[7]) == ONLINE_CHECK)
		{
			return USSSIMULATOR_OK; // ack received
		}
		else
		{
			return USSSIMULATOR_COM_ERR; //no ack received
		}
			
	}
	else if (readcheck == READ_FIRMWARE) /* read firmware */
	{
		if (reinterpret_cast<uint8_t&>(answer[6]) == 0x02)
		{
			m_FirmwareMajor = reinterpret_cast<uint8_t&>(answer[7]);
			m_FirmwareMinor = reinterpret_cast<uint8_t&>(answer[8]);
			return USSSIMULATOR_OK;
		}
		else
		{
			return USSSIMULATOR_COM_ERR;
		}
			

	}
	else if (readcheck == FIRING_STATUS) /* Read firing status */
	{
		if (reinterpret_cast<uint8_t&>(answer[6]) == 0x06)
		{
			m_FiringStatusBuffer = 0;
			for (uint8_t sensor = 0; sensor < MAX_SENSOR / 2; sensor++)
			{
				if (reinterpret_cast<uint8_t&>(answer[sensor + 7]) == 1)
					m_FiringStatusBuffer = m_FiringStatusBuffer | GetFiringStateMask(sensor);
			}
			if (address == FRONT_CLUSTER)
			{
				m_FrontFiringState = m_FiringStatusBuffer;
			}
			else if (address == REAR_CLUSTER)
			{
				m_RearFiringState = m_FiringStatusBuffer;
			}
			else
			{
				return USSSIMULATOR_INVAL_ARG_ERR;
			}
				
			return USSSIMULATOR_OK;
		}
		else
			return USSSIMULATOR_COM_ERR;
	}

	return USSSIMULATOR_OK; 
}

uint8_t UdpMultiTester::ReadFirmware(void)
{
	tMsg msg;

	msg.address = FRONT_CLUSTER;
	msg.cmdIdentifier = READ_FIRMWARE;
	uint32_t messageSize = 0;

	if (WriteMsg(&msg,messageSize) != USSSIMULATOR_OK)
	{
		USS_OUT("Problem sending data to multi tester\n");
		return USSSIMULATOR_COM_ERR;
	}

	return USSSIMULATOR_OK;
}

tbgsock* UdpMultiTester::bgsocket_open(struct sockaddr *addr, int type)
{
	tbgsock    *bgsock = (tbgsock*)calloc(sizeof(tbgsock), 1);

	if (bgsock == NULL)
		return NULL;

	bgsock->Type = type;
	if (type == SOCK_DGRAM)
		bgsock->Protocol = IPPROTO_UDP;
	else
		bgsock->Protocol = 0;
	bgsock->SockAddr = *addr;

	bgsock->Socket = socket(bgsock->SockAddr.sa_family, bgsock->Type, bgsock->Protocol);
	
	if (bgsock->Socket < 0)
	{
		USS_OUT("Socket was not created!\n");
		USS_OUT("Error number: %d\n", errno);
	}

#ifndef _WIN32
	struct timeval read_timeout;
	read_timeout.tv_sec = 0;
	read_timeout.tv_usec = SOCKET_READ_TIMEOUT_MILLI_SEC * 1000;
	if (setsockopt(bgsock->Socket, SOL_SOCKET, SO_RCVTIMEO, (const char*)&read_timeout, sizeof(read_timeout)) < 0)
	{
		USS_OUT("Socket options were not changed!\n");
		USS_OUT("Error number: %d\n", errno);
	}
	
#else
	DWORD timeout = SOCKET_READ_TIMEOUT_MILLI_SEC;
	setsockopt(bgsock->Socket, SOL_SOCKET, SO_RCVTIMEO, (char*)&timeout, sizeof(timeout));
#endif
	
	return bgsock;
}


