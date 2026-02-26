/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/* 
 * File:   RTS_GUI_Apo.h
 * Author: iwt
 *
 * Created on 6. August 2021, 10:29
 */

#ifndef RADARTS_APOMSG_H_
#define RADARTS_APOMSG_H_

#ifdef __cplusplus
extern "C" {
#endif
    
enum {
    ApoCh_RadarTS = 8,
    ApoCh_ARS = 9
};
    
    
enum {
    GUI_AllPnt = 0,
    GUI_SelPnt = 1,
    GUI_ARS_near = 2,
    GUI_ARS_far = 3,
    GUI_SqrPnt = 4,
    GUI_ARS_SqrPnt = 5
};

typedef struct tPoint {
    float	Tar_Ang;
    float	Tar_Ang_elev;
    float	Tar_Dist;
    float	Tar_RCSValue;
    float       Tar_Vel;
} tPoint;

typedef struct tRadarTS_APO {
    int MsgType;
    int CluIdx;
    tPoint *gpnt;
} tRadarTS_APO;

//int MaxAPOMsgSize;

void RadarTS_ApoMsg_Send (tRadarTS_APO* rts, int MaxPt, int Ch);

#ifdef __cplusplus
}
#endif

#endif /* RADARTS_APOMSG_H */

