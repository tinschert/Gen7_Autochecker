/*******************************************************************************
author Robert Erhart, ett2si (18.10.2004 - 00:00:00)
author (c) Copyright Robert Bosch GmbH 2004, 2005.  All rights reserved.
*******************************************************************************/

#include "CModule.h"

/*----------------------------*/
/* init static class elements */
/*----------------------------*/
//CMutex CModuleInterface::m_Mutex_s( "ClaraSimComMutex", CREATEMUTEX );
uint16_t CModuleInterface::__moduleInstanceCounter__ = 0;
