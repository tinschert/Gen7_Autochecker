/*
 * FILE:            ussInterfaceAdapterFord.h
 * SW-COMPONENT:    ussInterfaceAdapterFord
 * DESCRIPTION:     Header file for the ussInterfaceAdapterFord component
 * COPYRIGHT:       © 2017 - 2023 Robert Bosch GmbH
 * 
 * The reproduction, distribution and utilization of this file as
 * well as the communication of its contents to others without express
 * authorization is prohibited. Offenders will be held liable for the
 * payment of damages. All rights reserved in the event of the grant
 * of a patent, utility model or design.
 */

#ifndef USS_INTERFACE_ADAPTER_H_
#define USS_INTERFACE_ADAPTER_H_


#ifdef __cplusplus
extern "C" {
#endif


int CreateUssInterface(void);

int DeclareUssQuants(void);

int InitUssSensors(void);

int UpdateUssInterface(double dt);

int ClearUssInterface(void);

int CleanupUssInterface(void);


#ifdef __cplusplus
}
#endif


#endif /* USS_INTERFACE_ADAPTER_H_ */
