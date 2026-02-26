/*******************************************************************************
author Robert Erhart, ett2si (20.12.2004 - 00:00:00)
author (c) Copyright Robert Bosch GmbH 2004-2024. All rights reserved.
*******************************************************************************/

#include "CStaticTwoWheeler.h"

/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CStaticTwoWheeler::CStaticTwoWheeler():
    m_FxFront( 0.0 ), m_FxRear( 0.0 ),
    m_FyFront( 0.0 ), m_FyRear( 0.0 ),
    m_RvFxFront( 0.0 ), m_RvFxRear( 0.0 ),
    m_RvFyFront( 0.0 ), m_RvFyRear( 0.0 ),
    m_Fz( 0.0 ),  m_FxMass( 0.0 ), m_FyMass( 0.0 ), m_tau( 0.0 ),
    m_pF(), m_pR(),
    m_fF(), m_fR(), m_fCoG(),
    m_RvfF(), m_RvfR(), m_RvfCoG(),
    m_crossProductF(), m_crossProductR(), m_crossProductArticulation()
{

    addMessageParameter( p_g, 9.81, CStaticTwoWheelerDoc::p_g );

    addMessageInput( i_FzFrontSuspension, 0.0 );
    addMessageInput( i_FFrontWheelLateral, 0.0 );
    addMessageInput( i_RvFFrontWheelLateral, 0.0 );
    addMessageInput( i_FFrontWheelLongitudinal, 0.0 );
    addMessageInput( i_RvFFrontWheelLongitudinal, 0.0 );
    addMessageInput( i_FzRearSuspension, 0.0 );
    addMessageInput( i_FRearWheelLateral, 0.0 );
    addMessageInput( i_RvFRearWheelLateral, 0.0 );
    addMessageInput( i_FRearWheelLongitudinal, 0.0 );
    addMessageInput( i_RvFRearWheelLongitudinal, 0.0 );
    addMessageInput( i_FairResistance, 0.0 );
    addMessageInput( i_wheelAngleFront, 0.0 );
    addMessageInput( i_wheelAngleRear, 0.0 );
    addMessageInput( i_beta, 0.0 );
    addMessageInput( i_xWheelFront, 0.0 );
    addMessageInput( i_yWheelFront, 0.0 );
    addMessageInput( i_xWheelRear, 0.0 );
    addMessageInput( i_yWheelRear, 0.0 );
    addMessageInput( i_h, 0.0 );
    addMessageInput( i_m, 0.0 );
    addMessageInput( i_angleRollPitchYawSurface, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_angleRollPitchYawSuspension, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_FxyzArticulation, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_xyzArticulation, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );

    addMessageOutput( o_FChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ), CStaticTwoWheelerDoc::o_FChassis );
    addMessageOutput( o_FvRChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ), CStaticTwoWheelerDoc::o_FvRChassis );
    addMessageOutput( o_Fn, CFloat( 0.0 ), CStaticTwoWheelerDoc::o_Fn );
    addMessageOutput( o_MRollPitchYawChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ), CStaticTwoWheelerDoc::o_MRollPitchYawChassis );
    addMessageOutput( o_MvRRollPitchYawChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ), CStaticTwoWheelerDoc::o_MvRRollPitchYawChassis );
}

CStaticTwoWheeler::~CStaticTwoWheeler()
{}

/*------------------*/
/* public methods  */
/*------------------*/
void CStaticTwoWheeler::init( IMessage<CFloat>& f_FzFrontSuspension,
                              IMessage<CFloat>& f_FFrontWheelLateral,
                              IMessage<CFloat>& f_RvFFrontWheelLateral,
                              IMessage<CFloat>& f_FFrontWheelLongitudinal,
                              IMessage<CFloat>& f_RvFFrontWheelLongitudinal,
                              IMessage<CFloat>& f_FzRearSuspension,
                              IMessage<CFloat>& f_FRearWheelLateral,
                              IMessage<CFloat>& f_RvFRearWheelLateral,
                              IMessage<CFloat>& f_FRearWheelLongitudinal,
                              IMessage<CFloat>& f_RvFRearWheelLongitudinal,
                              IMessage<CFloat>& f_FairResistance,
                              IMessage<CFloat>& f_wheelAngleFront,
                              IMessage<CFloat>& f_wheelAngleRear,
                              IMessage<CFloat>& f_beta,
                              IMessage<CFloat>& f_xWheelFront,
                              IMessage<CFloat>& f_yWheelFront,
                              IMessage<CFloat>& f_xWheelRear,
                              IMessage<CFloat>& f_yWheelRear,
                              IMessage<CFloat>& f_h,
                              IMessage<CFloat>& f_m,
                              IMessage<CFloatVectorXYZ>& f_angleRollPitchYawSurface,
                              IMessage<CFloatVectorXYZ>& f_angleRollPitchYawSuspension,
                              IMessage<CFloatVectorXYZ>& f_FxyzArticulation,
                              IMessage<CFloatVectorXYZ>& f_xyzArticulation )
{
    /* Connect input with internal variables */
    i_FzFrontSuspension.link( f_FzFrontSuspension );
    i_FFrontWheelLateral.link( f_FFrontWheelLateral );
    i_RvFFrontWheelLateral.link( f_RvFFrontWheelLateral );
    i_FFrontWheelLongitudinal.link( f_FFrontWheelLongitudinal );
    i_RvFFrontWheelLongitudinal.link( f_RvFFrontWheelLongitudinal );
    i_FzRearSuspension.link( f_FzRearSuspension );
    i_FRearWheelLateral.link( f_FRearWheelLateral );
    i_RvFRearWheelLateral.link( f_RvFRearWheelLateral );
    i_FRearWheelLongitudinal.link( f_FRearWheelLongitudinal );
    i_RvFRearWheelLongitudinal.link( f_RvFRearWheelLongitudinal );
    i_FairResistance.link( f_FairResistance );
    i_wheelAngleFront.link( f_wheelAngleFront );
    i_wheelAngleRear.link( f_wheelAngleRear );
    i_beta.link( f_beta );
    i_xWheelFront.link( f_xWheelFront );
    i_yWheelFront.link( f_yWheelFront );
    i_xWheelRear.link( f_xWheelRear );
    i_yWheelRear.link( f_yWheelRear );
    i_h.link( f_h );
    i_m.link( f_m );
    i_angleRollPitchYawSurface.link( f_angleRollPitchYawSurface );
    i_angleRollPitchYawSuspension.link( f_angleRollPitchYawSuspension );
    i_FxyzArticulation.link( f_FxyzArticulation );
    i_xyzArticulation.link( f_xyzArticulation );

    /* Initialization messages */
    initializationMessages();

    /* Initialization variable */
}

/*------------------*/
/* private methods */
/*------------------*/
void CStaticTwoWheeler::calc( CFloat f_dT, CFloat f_time )
{
    /* Gravitational force. Points in -z direction in car coordinate system!*/
    o_Fn = -i_m * p_g;
    /* Fn = Fz + FxMass + FyMass
     * tau:        angle between road and XY plane of the vehicle coordinate system
                   (Schnittwinkel Ebene und Ebene des Fahrzeugkoordinatensystems)
     * pitchAngle: angle between global x-y plane and vehicle x axis
     *             (Schnittwinkel zwischen x Koordinatenachse und Welt-xy-Ebene)
     * rollAngle:  angle between global x-y plane and vehicle y axis
     *             (Schnittwinkel zwischen y Koordinatenachse und Welt-xy-Ebene)
    */
    m_tau    = ::sim::atan( ::sim::sqrt( ::sim::pow( ::sim::tan( i_angleRollPitchYawSurface.Y() + i_angleRollPitchYawSuspension.Y()/*pitchAngleLocal*/ ), 2 ) 
                                        +::sim::pow( ::sim::tan( i_angleRollPitchYawSurface.X() + i_angleRollPitchYawSuspension.X() /*rollAngleLocal*/ ), 2 ) ) );

    m_Fz     =   o_Fn * ::sim::cos( m_tau );
    m_FxMass = - m_Fz * ::sim::tan( i_angleRollPitchYawSurface.Y() + i_angleRollPitchYawSuspension.Y() ); // pitchAngleLocal
    m_FyMass =   m_Fz * ::sim::tan( i_angleRollPitchYawSurface.X() + i_angleRollPitchYawSuspension.X() );  // rollAngleLocal

    /* wheel  front */
    transformWheelForce( m_FxFront, m_FyFront, i_FFrontWheelLongitudinal, i_FFrontWheelLateral, i_wheelAngleFront );
    transformWheelForce( m_RvFxFront, m_RvFyFront, i_RvFFrontWheelLongitudinal, i_RvFFrontWheelLateral, i_wheelAngleFront );

    /* wheel  rear */
    transformWheelForce( m_FxRear, m_FyRear, i_FRearWheelLongitudinal, i_FRearWheelLateral, i_wheelAngleRear );
    transformWheelForce( m_RvFxRear, m_RvFyRear, i_RvFRearWheelLongitudinal, i_RvFRearWheelLateral, i_wheelAngleRear );

    /* Torque calculation:
     *  (- define axis directions)
     *  - define force vectors and position vectors
     *  - calculate individual torques by force/position vector cross products and sum them up
     *
     *  Force calculation:
     *  - sum up force vectors
     */

    // force positions: include CoG height; neglect wheel radius and suspension height.
    //                  CoG is at z=0, road at z = -h
    m_pF.XYZ( i_xWheelFront,  i_yWheelFront,  -i_h );
    m_pR.XYZ( i_xWheelRear,   i_yWheelRear,   -i_h );

    // force vectors: constructive
    m_fF.XYZ( m_FxFront,  m_FyFront,  i_FzFrontSuspension );
    m_fR.XYZ( m_FxRear,   m_FyRear,   i_FzRearSuspension );
    m_fCoG.XYZ( m_FxMass,      m_FyMass,       m_Fz );

    // force vectors: destructive
    m_RvfF.XYZ( m_RvFxFront,  m_RvFyFront,  0 );
    m_RvfR.XYZ( m_RvFxRear,   m_RvFyRear,   0 );
    m_RvfCoG.XYZ( i_FairResistance * cos( i_beta ), 0, 0 );

    // total force
    o_FChassis   = m_fF + m_fR + m_fCoG;
    o_FChassis  += i_FxyzArticulation;
    o_FvRChassis = m_RvfF + m_RvfR + m_RvfCoG;

    // total torque
    o_MRollPitchYawChassis   = ::sim::crossProduct( m_crossProductF, m_pF, m_fF ) + ::sim::crossProduct( m_crossProductR, m_pR, m_fR );
    o_MRollPitchYawChassis  += ::sim::crossProduct( m_crossProductArticulation, i_xyzArticulation, i_FxyzArticulation );

    o_MvRRollPitchYawChassis = ::sim::crossProduct( m_crossProductF, m_pF, m_RvfF ) + ::sim::crossProduct( m_crossProductR, m_pR, m_RvfR );
}

void CStaticTwoWheeler::transformWheelForce( CFloat& f_Fx, CFloat& f_Fy, CFloat f_FWheelLongitudinal, CFloat f_FWheelLateral, CFloat f_wheelAngle )
{
    // ToDo: Consider roll angle of the motorbike:
    //       lateral forces (wheel/road) have a z component in bike coordinate system, if roll is not zero.
    f_Fx = + f_FWheelLongitudinal * ::sim::cos( f_wheelAngle )
           - f_FWheelLateral * ::sim::sin( f_wheelAngle ) ;
    f_Fy = + f_FWheelLongitudinal * ::sim::sin( f_wheelAngle )
           + f_FWheelLateral * ::sim::cos( f_wheelAngle ) ;
}
