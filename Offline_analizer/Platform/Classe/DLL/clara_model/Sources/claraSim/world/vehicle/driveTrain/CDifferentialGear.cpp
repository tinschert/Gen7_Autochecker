/*******************************************************************************
author Robert Erhart, ett2si (12.11.2004 - 00:00:00)
author (c) Copyright Robert Bosch GmbH 2004-2024. All rights reserved.
*******************************************************************************/

#include "CDifferentialGear.h"

/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CDifferentialGear::CDifferentialGear()
{
    /* Initialization parameter */
    addMessageParameter( p_uCenter, 1.5, CDifferentialGearDoc::p_uCenter );
    addMessageParameter( p_uFront, 3.75, CDifferentialGearDoc::p_uFront );
    addMessageParameter( p_uRear, 3.44, CDifferentialGearDoc::p_uRear );

    addMessageInput( i_nWheelRightFront, 0.0 );
    addMessageInput( i_nWheelLeftFront, 0.0 );
    addMessageInput( i_nWheelRightRear, 0.0 );
    addMessageInput( i_nWheelLeftRear, 0.0 );
    addMessageInput( i_MPowerTrain, 0.0 );
    addMessageInput( i_frontWheelDrive, 0.0 );
    addMessageInput( i_rearWheelDrive, 0.0 );

    addMessageOutput( o_nDifferentialGear, 0.0, CDifferentialGearDoc::o_nDifferentialGear );
    addMessageOutput( o_differentialGearRatio, 0.0, CDifferentialGearDoc::o_differentialGearRatio );
    addMessageOutput( o_MWheelRightFront, 0.0, CDifferentialGearDoc::o_MWheelRightFront );
    addMessageOutput( o_MWheelLeftFront, 0.0, CDifferentialGearDoc::o_MWheelLeftFront );
    addMessageOutput( o_MWheelRightRear, 0.0, CDifferentialGearDoc::o_MWheelRightRear );
    addMessageOutput( o_MWheelLeftRear, 0.0, CDifferentialGearDoc::o_MWheelLeftRear );
}
CDifferentialGear::~CDifferentialGear()
{}

/*------------------*/
/* public methods  */
/*------------------*/
void CDifferentialGear::init( IMessage<CFloat>& f_nWheelRightFront,
                              IMessage<CFloat>& f_nWheelLeftFront,
                              IMessage<CFloat>& f_nWheelRightRear,
                              IMessage<CFloat>& f_nWheelLeftRear,
                              IMessage<CFloat>& f_MPowerTrain,
                              IMessage<CBool>& f_frontWheelDrive,
                              IMessage<CBool>& f_rearWheelDrive )
{
    /* Connect input with internal variables */
    i_nWheelRightFront.link( f_nWheelRightFront );
    i_nWheelLeftFront.link( f_nWheelLeftFront );
    i_nWheelRightRear.link( f_nWheelRightRear );
    i_nWheelLeftRear.link( f_nWheelLeftRear );
    i_MPowerTrain.link( f_MPowerTrain );
    i_frontWheelDrive.link( f_frontWheelDrive );
    i_rearWheelDrive.link( f_rearWheelDrive );

    /* Initialization messages */
    initializationMessages();
}

/*------------------*/
/* private methods */
/*------------------*/
void CDifferentialGear::calc( CFloat f_dT, CFloat f_time )
{
    /* front-wheel-drive */
    if( i_frontWheelDrive && !i_rearWheelDrive )
    {
        /* RPM of drive train */
        o_differentialGearRatio = p_uFront;
        o_nDifferentialGear =
            p_uFront * ( i_nWheelRightFront + i_nWheelLeftFront ) / 2.0;

        /* Torque of the wheels */
        o_MWheelRightFront = p_uFront / 2.0 * i_MPowerTrain;
        o_MWheelLeftFront  = o_MWheelRightFront;
        o_MWheelRightRear  = 0.0;
        o_MWheelLeftRear   = 0.0;
    }
    /* rear-wheel-drive */
    else if( !i_frontWheelDrive && i_rearWheelDrive )
    {
        /* RPM of drive train */
        o_differentialGearRatio = p_uRear;
        o_nDifferentialGear =
            p_uRear * ( i_nWheelRightRear + i_nWheelLeftRear ) / 2.0;

        /* Torque of the wheels */
        o_MWheelRightFront = 0.0;
        o_MWheelLeftFront  = 0.0;
        o_MWheelRightRear  = p_uRear / 2.0 * i_MPowerTrain;
        o_MWheelLeftRear   = o_MWheelRightRear;
    }
    /* 4wheel-drive */
    else if( i_frontWheelDrive && i_rearWheelDrive )
    {
        /* RPM of drive train */
        o_differentialGearRatio = ( p_uRear + p_uFront ) / 2.0 * p_uCenter;
        o_nDifferentialGear =
            p_uCenter / 2.0 *
            ( p_uFront / 2.0 * ( i_nWheelRightFront + i_nWheelLeftFront )
              + p_uRear / 2.0 * ( i_nWheelRightRear + i_nWheelLeftRear ) );

        /* Torque of the wheels */
        o_MWheelRightFront = p_uFront / 2.0 * p_uCenter / 2.0 * i_MPowerTrain;
        o_MWheelLeftFront = o_MWheelRightFront;
        o_MWheelRightRear = p_uRear / 2.0 * p_uCenter / 2.0 * i_MPowerTrain;
        o_MWheelLeftRear  = o_MWheelRightRear;
    }
    else
    {
        exit( 100 ); // Et: ToDo Error definieren
    }
}

