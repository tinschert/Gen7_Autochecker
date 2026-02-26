/*******************************************************************************
 $Source: CTransmission.cpp $
 $Date: 2016/06/01 16:22:25CEST $
 $Revision: 1.6 $

 author Robert Erhart, ett2si (10.11.2004 - 00:00:00)
 author (c) Copyright Robert Bosch GmbH 2004, 2005, 2011. All rights reserved.
 *******************************************************************************/

#include "CTransmission.h"

/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CTransmission::CTransmission():
    m_gearRatioInternal( 0 ),
    m_gearPositionInternal( 0 )
{
    /* Initialization parameter */
    addMessageParameter( p_nMaxEngineShift, 6000, CTransmissionDoc::p_nMaxEngineShift );
    addMessageParameter( p_nMinEngineShift, 1500, CTransmissionDoc::p_nMinEngineShift );
    addMessageParameter( p_transmissionMode, automatic, CTransmissionDoc::p_transmissionMode );
    addMessageParameter( p_gearPositionTargetMin, 1, CTransmissionDoc::p_gearPositionTargetMin );
    CFloat x1[] = { -1, 0, 1, 2, 3, 4, 5, 6 }; //gear position
    CFloat y1[] = { -3.403, 0, 4.171, 2.340, 1.521, 1.143, 0.867, 0.691 };
    addMessageParameter( p_gearRatioXGearLever, CFloatVector( x1, 8 ), CTransmissionDoc::p_gearRatioXGearLever );
    addMessageParameter( p_gearRatioYRatio, CFloatVector( y1, 8 ), CTransmissionDoc::p_gearRatioYRatio );


    addMessageInput( i_MdEngine, 0.0 );
    addMessageInput( i_MdEngineRequest, 0.0 );
    addMessageInput( i_nDifferentialGear, 0.0 );
    addMessageInput( i_clutch, 0.0 );
    addMessageInput( i_gearStick, 0 );
    addMessageInput( i_sailingRequest, false );


    addMessageOutput( o_gearPosition, 0, CTransmissionDoc::o_gearPosition );
    addMessageOutput( o_gearStick, 0, CTransmissionDoc::o_gearStick );
    addMessageOutput( o_shifting, false, CTransmissionDoc::o_shifting );
    addMessageOutput( o_gearRatio, 0, CTransmissionDoc::o_gearRatio );
    addMessageOutput( o_gearPositionTarget, 0, CTransmissionDoc::o_gearPositionTarget );
    addMessageOutput( o_MdTransmission,  0.0, CTransmissionDoc::o_MdTransmission );
    addMessageOutput( o_nTransmission,  0.0, CTransmissionDoc::o_nTransmission );
}
CTransmission::~CTransmission()
{
}

/*------------------*/
/* public methods  */
/*------------------*/
void CTransmission::init( IMessage<CFloat>& f_MdEngine, IMessage<CFloat>& f_MdEngineRequest,
                          IMessage<CFloat>& f_nDifferentialGear, IMessage<CFloat>& f_clutch, IMessage<CInt>& f_gearStick, IMessage<CBool>&   f_sailingRequest )
{
    /* Connect input with internal variables */
    i_MdEngine.link( f_MdEngine );
    i_MdEngineRequest.link( f_MdEngineRequest );
    i_nDifferentialGear.link( f_nDifferentialGear );
    i_clutch.link( f_clutch );
    i_gearStick.link( f_gearStick );

    i_sailingRequest.link( f_sailingRequest );


    /* Initialization messages */
    initializationMessages();

    /* Initialization gear change filter and tables */
    lowPass2ndOrder.init( 0.5, 0.125, 1, static_cast<CFloat>(o_gearPosition) );
    gearRatioTable.init( p_gearRatioXGearLever, p_gearRatioYRatio, 0 );
    CFloat x2[] = { 0, 50, 100, 200, 400, 500, 600, 700 }; //EngineTorque or Torque Request?
    CFloat y2[] = { 1800, 2000, 3500, 4000, 5000, 6000, 6000, 6000 }; //nEngine
    shiftUpTable.init( 8, x2, y2, 0 );
    CFloat x3[] = { 0, 50, 100, 200, 400, 500, 600, 700 }; //EngineTorque or Torque Request?
    CFloat y3[] = { 1000, 1000, 1500, 2500, 3000, 3000, 3000, 3000 }; //nEngine
    shiftDownTable.init( 8, x3, y3, 0 );

    /* Re-Initialization depended messages */
    // o_gearPosition.init( i_gearStick ); // allow user-specific, independent initialization of o_gearPosition
    o_gearStick.init( i_gearStick );
    o_gearRatio.init( gearRatioTable.get(static_cast<CFloat>(o_gearPosition) ) );
    o_gearPositionTarget.init( o_gearPosition );

    /* Initialization variable */
    m_gearPositionInternal = static_cast<CFloat>(o_gearPosition);
}

/*------------------*/
/* private methods */
/*------------------*/
void CTransmission::calc( CFloat f_dT, CFloat f_time )
{
    o_gearStick = i_gearStick;

    /* calculate target gear */
    if( ( !o_shifting ) && ( f_dT != 0 ) ) //if f_dT zero, no shifting process is possible, because of lowPass2ndOrder Filter for clutch process
    {
        calcGearStep();
    }

    /* calculate shifting process */
    if( o_gearPositionTarget != o_gearPosition )
    {
        o_shifting = true;
    }

    /* gear change */
    if( p_transmissionMode == automatic || p_transmissionMode == semiAutomatic )
    {
        if( ::sim::abs( m_gearPositionInternal - ( CFloat ) o_gearPositionTarget ) < 0.001 )
        {
            o_gearPosition = o_gearPositionTarget;
            o_shifting = false;
        }
        else
        {
            m_gearPositionInternal = lowPass2ndOrder.get( ( CFloat ) o_gearPositionTarget, f_dT );
        }
    }
    else
    {
        //p_transmissionMode == manual
        m_gearPositionInternal = o_gearPositionTarget * ( 1 - i_clutch );
        if( m_gearPositionInternal == o_gearPositionTarget )
        {
            o_gearPosition = o_gearPositionTarget;
            o_shifting = false;
        }
    }

    /* calculation gearRatio */
    m_gearRatioInternal = gearRatioTable.get( m_gearPositionInternal );

    /* transmission torque and RPM output */
    if( i_gearStick == 0 or i_sailingRequest )
    {
        /* transmission torque output: gear stick "N" */
        o_MdTransmission = 0.0;
        if( i_MdEngineRequest > 0 )
        {
            o_nTransmission = 600.0;
        }
        else
        {
            o_nTransmission = 0.0;
        }
    }
    else
    {
        /* transmission torque output */
        o_MdTransmission = m_gearRatioInternal * i_MdEngine;

        if( p_transmissionMode == automatic || p_transmissionMode == semiAutomatic )
        {
            /* transmission RPM output */
            if( i_MdEngineRequest > 0 )
            {
                o_nTransmission = ::sim::max( ( m_gearRatioInternal * i_nDifferentialGear ), ( CFloat ) 600.0 );
            }
            else
            {
                o_nTransmission = ::sim::max( ( m_gearRatioInternal * i_nDifferentialGear ), ( CFloat ) 0.0 );
            }
        }
        else
        {
            //p_transmissionMode == manual
            if( i_clutch <= 0.01 )
            {
                o_nTransmission = m_gearRatioInternal * i_nDifferentialGear;
            }
            else
            {
                //ToDo: calculation of o_nTransmission: differential equation
                o_nTransmission = m_gearRatioInternal * i_nDifferentialGear * ( 1 - i_clutch ) + 600 * i_clutch * ( i_MdEngineRequest / 50 );
            }
        }
    }

    /* gearRatio */
    o_gearRatio = m_gearRatioInternal;
}

/* calculation of the gearPositionTarget */
/* 1. Motordrehzahl Schaltziel
 * Ausgangsmoment
 * Kennlinie nEngine Hochschalten
 * Kennlinie nEngine Runterschalten
 * Momentenkriterium fuer Hochschalten und Runterschalten
 * Anpassung Kennlinie nEngine aufgrund
 * angefordertem Motormoment. (kleines Motormoment -> geringe Drehzahl
 * grosses Motormoment -> hohe Drehzahlbandbreite)
 * Wartezeit zwischen Schaltvorgaengen (>3s??)
 * max Mdind bei nEngine notwendig????
 * Idee: Hochschaltverhinderung bzw. Runterschaltaufforderung
 * wenn angefordertes Moment viel groesser
 * geliefertes Motormoment?? Beachte: maxRPM Motor
 * Drehzahl
 * */
void CTransmission::calcGearStep()
{
    if( p_transmissionMode == automatic )
    {
        /* current nEngine */
        o_nTransmission = gearRatioTable.get(static_cast<CFloat>(o_gearPositionTarget) ) * i_nDifferentialGear;

        /* calc new gearPosition */
        if( o_nTransmission > shiftUpTable.get( i_MdEngineRequest ) )
        {
            o_gearPositionTarget = o_gearPositionTarget + 1;
        }
        else if( o_nTransmission < shiftDownTable.get( i_MdEngineRequest ) )
        {
            o_gearPositionTarget = o_gearPositionTarget - 1;
        }

        /* current nEngine */
        o_nTransmission = gearRatioTable.get( static_cast<CFloat>(o_gearPositionTarget) ) * i_nDifferentialGear;

        /* limit min/max RPM of engine */
        if( p_nMaxEngineShift < o_nTransmission )
        {
            o_gearPositionTarget = o_gearPositionTarget + 1;
        }
        else if( p_nMinEngineShift > o_nTransmission )
        {
            o_gearPositionTarget = o_gearPositionTarget - 1;
        }

        /* limit gearPosition: (gearPosition >= 1) <= gearStick */
        o_gearPositionTarget = ::sim::max( o_gearPositionTarget, p_gearPositionTargetMin ); // lower bound on target gear
        o_gearPositionTarget = ::sim::min( o_gearPositionTarget, i_gearStick );             // absolute bound on gear: upper bound (if i_gearStick > 0); forced zero/negative value (if i_gearStick == 0 or ==-1)
    }
    else
    {
        o_gearPositionTarget = i_gearStick;
    }
}
