/*!
*****************************************************************************
*
* \file sUDP.h
* \version   3.0
* \date Feb 27, 2013
* \author Sebastian Schwab
*****************************************************************************
* \brief Module for UDP communication
* \details
* The Module sUDP supports the usage of UDP communications within
* the CarMaker. Therefor it provides functions for sending and receiving
* UDP messages. These functions are architecture independend. Therefor
* the same code can be used for several architectures.
*
* The module supports only the sending an receiving of UDP messages. There is
* no protocol specified.
*
* \cond copyright
* (C) IPG Automotive GmbH
* Bannwaldallee 60             Phone  +49.721.98520.0
* 76185 Karlsruhe              Fax    +49.721.98520.99
* Germany                      WWW    www.ipg-automotive.com \endcond
*****************************************************************************
*/


#ifndef _SIMPLE_UDP__H_
#define _SIMPLE_UDP__H_
#if defined (LINUX)
#include <netinet/in.h>
#endif

struct sockaddr_in *saddrSrc;

typedef void (* tUDP_ReadFnc) (void *msg, int len, struct sockaddr_in *saddrSrc);

/*! \fn int UDP_New_InSocket (unsigned short inPort, tUDP_ReadFnc ReadFnc)
 * \brief Creates an UDP Socket
 * \details Does something really cool.
 * \param inPort the port given in.
 * \param ReadFnc whatever.
 * \returns SockID  \n >=0 -> SockID (can be reused for socket configurations like setsockopt() \n
 *                     -1 = not ok.
 */
int sUDP_New_InSocket (unsigned short inPort, tUDP_ReadFnc ReadFnc);
/*!
 * \brief Creates an UDP tudpOutSocket pointer
 * \details Does something really cool.
 * \param serverName servername input.
 * \param outPort Output Port.
 * \returns SockID
 */
int sUDP_New_OutSocket(char *serverName, unsigned short outPort);
/*!
 * \brief Creates an UDP tudpOutSocket pointer using an existing socket
 * \details Does something really cool.
 * \param serverName servername input.
 * \param outPort Output Port.
 * \param sockID existing socket ID
 * \returns SockID
 */
int sUDP_Set_OutSocket(char *serverName, unsigned short outPort, int sockID);


int sUDP_In(void);
int sUDP_SendMsg (int SockID, void *buf, int len);
int sUDP_ClearInSockets (int SockId);
int sUDP_Delete(void);
int sUDP_Cleanup (void);

#endif /* _SIMPLE_UDP__H_ */
