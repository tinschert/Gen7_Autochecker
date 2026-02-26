/******************************************************************************
 **  CarMaker - Version 10.0.1
 **  Vehicle Dynamics Simulation Toolkit
 **
 **  Copyright (C)   IPG Automotive GmbH
 **                  Bannwaldallee 60             Phone  +49.721.98520.0
 **                  76185 Karlsruhe              Fax    +49.721.98520.99
 **                  Germany                      WWW    www.ipg-automotive.com
 ******************************************************************************/
/*
 *
 * RadarTS.h
 *
 *      Author: prk, iwt
 */

#ifndef RadarTS_H_
#define RadarTS_H_
#include <infoc.h>
#ifdef __cplusplus
extern "C" {
#endif
    
/* External Interface for RadarTS module */
int  RadarTS_Init_First (void);
int  RadarTS_Init (void);
void RadarTS_DeclQuants(void);
void RadarTS_TestRun_Start_atBegin (void);
int  RadarTS_TestRun_Start_atEnd (void);
void RadarTS_Out(const unsigned CycleNo);
void RadarTS_Exit(void);
void RadarTS_TestRun_End (void);

#ifdef __cplusplus
}
#endif
#endif /* RadarTS_H_ */

