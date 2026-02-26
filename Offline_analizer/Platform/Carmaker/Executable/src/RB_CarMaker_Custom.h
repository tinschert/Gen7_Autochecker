/*
 * FILE:            RB_CarMaker_Custom.h
 * SW-COMPONENT:    RB_CarMaker_Custom
 * DESCRIPTION:     Header file for the RB_CarMaker_Custom component
 * COPYRIGHT:       © 2017 - 2023 Robert Bosch GmbH
 * 
 * The reproduction, distribution and utilization of this file as
 * well as the communication of its contents to others without express
 * authorization is prohibited. Offenders will be held liable for the
 * payment of damages. All rights reserved in the event of the grant
 * of a patent, utility model or design.
 */


#ifndef RB_CARMAKER_CUSTOM_H_
#define RB_CARMAKER_CUSTOM_H_

#ifdef __cplusplus
extern "C" {
#endif


int RB_User_Init_First(void);

int RB_User_Init(void);

int RB_User_DeclQuants(void);

int RB_User_TestRun_Start_atBegin(void);

int RB_User_TestRun_Start_atEnd(void);

int RB_User_TestRun_Start_StaticCond_Calc(void);

int RB_User_VehicleControl_Calc(double dt);

int RB_User_Calc(double dt);

int RB_User_TestRun_End_First(void);

int RB_User_TestRun_End(void);

int RB_User_TestRun_Start_Finalize(void);

int RB_User_Out(const unsigned CycleNo);

int RB_User_End (void);

int RB_User_Cleanup (void);


#ifdef __cplusplus
}
#endif

#endif /* RB_CARMAKER_CUSTOM_H_ */
