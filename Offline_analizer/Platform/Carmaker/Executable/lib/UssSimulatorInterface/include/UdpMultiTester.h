/*
 *
 *	UdpMultiTester.h
 *
 *  Created on: 07.02.2018
 * @author BNC1LR
 */

#pragma once

#include "UssSimulator.h"

#ifdef XENO
#include <unistd.h>
#endif
//#include "RbDefines.h"

//#define MAX_ECHO         20

//#define OBJECT_ECHO_LIST_SIZE (MAX_OBJECTS*3)

#define UDP_HEADER  "\x6D\x74\x00\x00\x04\x08\x04"
#define UDP_START_BYTES "\xFF\xFF"

struct tbgsock {
	volatile int    Socket;
	struct sockaddr SockAddr;
	struct sockaddr PeerAddr;
	int             Protocol;
	int				Type;
};

class UdpMultiTester: public UssSimulator
{
public:
	UdpMultiTester(void);
	virtual ~UdpMultiTester(void);

	uint8_t Init(std::string IpMultiTester, uint16_t ListeningPort);
	uint8_t Init(uint8_t address) { return USSSIMULATOR_INVAL_ARG_ERR; } // call for USB, invalid for UDP
	uint8_t CloseUssSimulator(void);

	int m_mutexTimeout; //ms

private:
	uint8_t WriteCheck(void);
	uint8_t ReadCheck(void);
	uint8_t WriteMsg(void* msg, uint32_t messageSize);
	uint8_t ReadMsg(uint8_t readcheck, uint8_t address = NO_CLUSTER);
	uint8_t	ReadMsg(void);
	uint8_t ReadFirmware(void);
	tbgsock* bgsocket_open(struct sockaddr *addr, int type);

	//SOCKET* l_socket;
	tbgsock* m_tbgsocket;
	struct sockaddr_in AddressMultiTester;


#ifdef _WIN32
	int slen;
#else
	socklen_t slen;
#endif 


};

