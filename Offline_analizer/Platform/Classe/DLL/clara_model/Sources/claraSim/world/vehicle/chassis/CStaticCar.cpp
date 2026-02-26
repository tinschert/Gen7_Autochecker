/*******************************************************************************
author Robert Erhart, ett2si (20.12.2004 - 00:00:00)
author (c) Copyright Robert Bosch GmbH 2004-2024. All rights reserved.
*******************************************************************************/

#include "CStaticCar.h"

/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CStaticCar::CStaticCar():
    m_FxLeftFront( 0.0 ), m_FxRightFront( 0.0 ),  m_FxLeftRear( 0.0 ),  m_FxRightRear( 0.0 ),
    m_FyLeftFront( 0.0 ), m_FyRightFront( 0.0 ), m_FyLeftRear( 0.0 ), m_FyRightRear( 0.0 ),
    m_RvFxLeftFront( 0.0 ), m_RvFxRightFront( 0.0 ), m_RvFxLeftRear( 0.0 ),  m_RvFxRightRear( 0.0 ),
    m_RvFyLeftFront( 0.0 ), m_RvFyRightFront( 0.0 ), m_RvFyLeftRear( 0.0 ), m_RvFyRightRear( 0.0 ),
    m_Fz( 0.0 ),  m_FxMass( 0.0 ), m_FyMass( 0.0 ), m_tau( 0.0 ),
    m_pLF(), m_pLR(), m_pRF(), m_pRR(),
    m_fLF(), m_fLR(), m_fRF(), m_fRR(), m_fCoG(),
    m_RvfLF(), m_RvfLR(), m_RvfRF(), m_RvfRR(), m_RvfCoG(),
    m_crossProductLF(), m_crossProductLR(), m_crossProductRF(), m_crossProductRR(), m_crossProductArticulation()
{

    addMessageParameter( p_g, 9.81, CStaticCarDoc::p_g );

    addMessageInput( i_FzLeftFrontSuspension, 0.0 );
    addMessageInput( i_FLeftFrontWheelLateral, 0.0 );
    addMessageInput( i_RvFLeftFrontWheelLateral, 0.0 );
    addMessageInput( i_FLeftFrontWheelLongitudinal, 0.0 );
    addMessageInput( i_RvFLeftFrontWheelLongitudinal, 0.0 );
    addMessageInput( i_FzRightFrontSuspension, 0.0 );
    addMessageInput( i_FRightFrontWheelLateral, 0.0 );
    addMessageInput( i_RvFRightFrontWheelLateral, 0.0 );
    addMessageInput( i_FRightFrontWheelLongitudinal, 0.0 );
    addMessageInput( i_RvFRightFrontWheelLongitudinal, 0.0 );
    addMessageInput( i_FzLeftRearSuspension, 0.0 );
    addMessageInput( i_FLeftRearWheelLateral, 0.0 );
    addMessageInput( i_RvFLeftRearWheelLateral, 0.0 );
    addMessageInput( i_FLeftRearWheelLongitudinal, 0.0 );
    addMessageInput( i_RvFLeftRearWheelLongitudinal, 0.0 );
    addMessageInput( i_FzRightRearSuspension, 0.0 );
    addMessageInput( i_FRightRearWheelLateral, 0.0 );
    addMessageInput( i_RvFRightRearWheelLateral, 0.0 );
    addMessageInput( i_FRightRearWheelLongitudinal, 0.0 );
    addMessageInput( i_RvFRightRearWheelLongitudinal, 0.0 );
    addMessageInput( i_FairResistance, 0.0 );
    addMessageInput( i_wheelAngleFront, 0.0 );
    addMessageInput( i_wheelAngleRear, 0.0 );
    addMessageInput( i_beta, 0.0 );
    addMessageInput( i_xWheelLeftFront, 0.0 );
    addMessageInput( i_yWheelLeftFront, 0.0 );
    addMessageInput( i_xWheelRightFront, 0.0 );
    addMessageInput( i_yWheelRightFront, 0.0 );
    addMessageInput( i_xWheelLeftRear, 0.0 );
    addMessageInput( i_yWheelLeftRear, 0.0 );
    addMessageInput( i_xWheelRightRear, 0.0 );
    addMessageInput( i_yWheelRightRear, 0.0 );
    addMessageInput( i_h, 0.0 );
    addMessageInput( i_m, 0.0 );
    addMessageInput( i_angleRollPitchYawSurface, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_angleRollPitchYawSuspension, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_FxyzArticulation, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_xyzArticulation, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );

    addMessageOutput( o_FChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ), CStaticCarDoc::o_FChassis );
    addMessageOutput( o_FvRChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ), CStaticCarDoc::o_FvRChassis );
    addMessageOutput( o_Fn, 0.0, CStaticCarDoc::o_Fn );
    addMessageOutput( o_MRollPitchYawChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ), CStaticCarDoc::o_MRollPitchYawChassis );
    addMessageOutput( o_MvRRollPitchYawChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ), CStaticCarDoc::o_MvRRollPitchYawChassis );
}

CStaticCar::~CStaticCar()
{}

/*------------------*/
/* public methods  */
/*------------------*/
void CStaticCar::init( IMessage<CFloat>& f_FzLeftFrontSuspension,
                       IMessage<CFloat>& f_FLeftFrontWheelLateral,
                       IMessage<CFloat>& f_RvFLeftFrontWheelLateral,
                       IMessage<CFloat>& f_FLeftFrontWheelLongitudinal,
                       IMessage<CFloat>& f_RvFLeftFrontWheelLongitudinal,
                       IMessage<CFloat>& f_FzRightFrontSuspension,
                       IMessage<CFloat>& f_FRightFrontWheelLateral,
                       IMessage<CFloat>& f_RvFRightFrontWheelLateral,
                       IMessage<CFloat>& f_FRightFrontWheelLongitudinal,
                       IMessage<CFloat>& f_RvFRightFrontWheelLongitudinal,
                       IMessage<CFloat>& f_FzLeftRearSuspension,
                       IMessage<CFloat>& f_FLeftRearWheelLateral,
                       IMessage<CFloat>& f_RvFLeftRearWheelLateral,
                       IMessage<CFloat>& f_FLeftRearWheelLongitudinal,
                       IMessage<CFloat>& f_RvFLeftRearWheelLongitudinal,
                       IMessage<CFloat>& f_FzRightRearSuspension,
                       IMessage<CFloat>& f_FRightRearWheelLateral,
                       IMessage<CFloat>& f_RvFRightRearWheelLateral,
                       IMessage<CFloat>& f_FRightRearWheelLongitudinal,
                       IMessage<CFloat>& f_RvFRightRearWheelLongitudinal,
                       IMessage<CFloat>& f_FairResistance,
                       IMessage<CFloat>& f_wheelAngleFront,
                       IMessage<CFloat>& f_wheelAngleRear,
                       IMessage<CFloat>& f_beta,
                       IMessage<CFloat>& f_xWheelLeftFront,
                       IMessage<CFloat>& f_yWheelLeftFront,
                       IMessage<CFloat>& f_xWheelRightFront,
                       IMessage<CFloat>& f_yWheelRightFront,
                       IMessage<CFloat>& f_xWheelLeftRear,
                       IMessage<CFloat>& f_yWheelLeftRear,
                       IMessage<CFloat>& f_xWheelRightRear,
                       IMessage<CFloat>& f_yWheelRightRear,
                       IMessage<CFloat>& f_h,
                       IMessage<CFloat>& f_m,
                       IMessage<CFloatVectorXYZ>& f_angleRollPitchYawSurface,
                       IMessage<CFloatVectorXYZ>& f_angleRollPitchYawSuspension,
                       IMessage<CFloatVectorXYZ>& f_FxyzArticulation,
                       IMessage<CFloatVectorXYZ>& f_xyzArticulation )
{
    /* Connect input with internal variables */
    i_FzLeftFrontSuspension.link( f_FzLeftFrontSuspension );
    i_FLeftFrontWheelLateral.link( f_FLeftFrontWheelLateral );
    i_RvFLeftFrontWheelLateral.link( f_RvFLeftFrontWheelLateral );
    i_FLeftFrontWheelLongitudinal.link( f_FLeftFrontWheelLongitudinal );
    i_RvFLeftFrontWheelLongitudinal.link( f_RvFLeftFrontWheelLongitudinal );
    i_FRightFrontWheelLateral.link( f_FRightFrontWheelLateral );
    i_FzRightFrontSuspension.link( f_FzRightFrontSuspension );
    i_RvFRightFrontWheelLateral.link( f_RvFRightFrontWheelLateral );
    i_FRightFrontWheelLongitudinal.link( f_FRightFrontWheelLongitudinal );
    i_RvFRightFrontWheelLongitudinal.link( f_RvFRightFrontWheelLongitudinal );
    i_FzLeftRearSuspension.link( f_FzLeftRearSuspension );
    i_FLeftRearWheelLateral.link( f_FLeftRearWheelLateral );
    i_RvFLeftRearWheelLateral.link( f_RvFLeftRearWheelLateral );
    i_FLeftRearWheelLongitudinal.link( f_FLeftRearWheelLongitudinal );
    i_RvFLeftRearWheelLongitudinal.link( f_RvFLeftRearWheelLongitudinal );
    i_FRightRearWheelLateral.link( f_FRightRearWheelLateral );
    i_FzRightRearSuspension.link( f_FzRightRearSuspension );
    i_RvFRightRearWheelLateral.link( f_RvFRightRearWheelLateral );
    i_FRightRearWheelLongitudinal.link( f_FRightRearWheelLongitudinal );
    i_RvFRightRearWheelLongitudinal.link( f_RvFRightRearWheelLongitudinal );
    i_FairResistance.link( f_FairResistance );
    i_wheelAngleFront.link( f_wheelAngleFront );
    i_wheelAngleRear.link( f_wheelAngleRear );
    i_beta.link( f_beta );
    i_xWheelLeftFront.link( f_xWheelLeftFront );
    i_yWheelLeftFront.link( f_yWheelLeftFront );
    i_xWheelRightFront.link( f_xWheelRightFront );
    i_yWheelRightFront.link( f_yWheelRightFront );
    i_xWheelLeftRear.link( f_xWheelLeftRear );
    i_yWheelLeftRear.link( f_yWheelLeftRear );
    i_xWheelRightRear.link( f_xWheelRightRear );
    i_yWheelRightRear.link( f_yWheelRightRear );
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
void CStaticCar::calc( CFloat f_dT, CFloat f_time )
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

    /* wheel left front */
    transformWheelForce( m_FxLeftFront, m_FyLeftFront, i_FLeftFrontWheelLongitudinal, i_FLeftFrontWheelLateral, i_wheelAngleFront );
    transformWheelForce( m_RvFxLeftFront, m_RvFyLeftFront, i_RvFLeftFrontWheelLongitudinal, i_RvFLeftFrontWheelLateral, i_wheelAngleFront );

    /* wheel right front */
    transformWheelForce( m_FxRightFront, m_FyRightFront, i_FRightFrontWheelLongitudinal, i_FRightFrontWheelLateral, i_wheelAngleFront );
    transformWheelForce( m_RvFxRightFront, m_RvFyRightFront, i_RvFRightFrontWheelLongitudinal, i_RvFRightFrontWheelLateral, i_wheelAngleFront );

    /* wheel left rear */
    transformWheelForce( m_FxLeftRear, m_FyLeftRear, i_FLeftRearWheelLongitudinal, i_FLeftRearWheelLateral, i_wheelAngleRear );
    transformWheelForce( m_RvFxLeftRear, m_RvFyLeftRear, i_RvFLeftRearWheelLongitudinal, i_RvFLeftRearWheelLateral, i_wheelAngleRear );

    /* wheel right rear */
    transformWheelForce( m_FxRightRear, m_FyRightRear, i_FRightRearWheelLongitudinal, i_FRightRearWheelLateral, i_wheelAngleRear );
    transformWheelForce( m_RvFxRightRear, m_RvFyRightRear, i_RvFRightRearWheelLongitudinal, i_RvFRightRearWheelLateral, i_wheelAngleRear );

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
    m_pLF.XYZ( i_xWheelLeftFront,  i_yWheelLeftFront,  -i_h );
    m_pLR.XYZ( i_xWheelLeftRear,   i_yWheelLeftRear,   -i_h );
    m_pRF.XYZ( i_xWheelRightFront, i_yWheelRightFront, -i_h );
    m_pRR.XYZ( i_xWheelRightRear,  i_yWheelRightRear, -i_h );

    // force vectors: constructive
    m_fLF.XYZ( m_FxLeftFront,  m_FyLeftFront,  i_FzLeftFrontSuspension );
    m_fLR.XYZ( m_FxLeftRear,   m_FyLeftRear,   i_FzLeftRearSuspension );
    m_fRF.XYZ( m_FxRightFront, m_FyRightFront, i_FzRightFrontSuspension );
    m_fRR.XYZ( m_FxRightRear,  m_FyRightRear,  i_FzRightRearSuspension );
    m_fCoG.XYZ( m_FxMass,      m_FyMass,       m_Fz );

    // force vectors: destructive
    m_RvfLF.XYZ( m_RvFxLeftFront,  m_RvFyLeftFront,  0 );
    m_RvfLR.XYZ( m_RvFxLeftRear,   m_RvFyLeftRear,   0 );
    m_RvfRF.XYZ( m_RvFxRightFront, m_RvFyRightFront, 0 );
    m_RvfRR.XYZ( m_RvFxRightRear,  m_RvFyRightRear,  0 );
    m_RvfCoG.XYZ( i_FairResistance * ::sim::cos( i_beta ), 0, 0 );

    // total force
    o_FChassis   = m_fLF + m_fLR + m_fRF + m_fRR + m_fCoG;
    o_FChassis  += i_FxyzArticulation;
    o_FvRChassis = m_RvfLF + m_RvfLR + m_RvfRF + m_RvfRR + m_RvfCoG;

    // total torque
    o_MRollPitchYawChassis   = ( ::sim::crossProduct( m_crossProductLF, m_pLF, m_fLF )   + ::sim::crossProduct( m_crossProductRF, m_pRF, m_fRF )
                                 + ::sim::crossProduct( m_crossProductLR, m_pLR, m_fLR )   + ::sim::crossProduct( m_crossProductRR, m_pRR, m_fRR ) );
    o_MRollPitchYawChassis  +=  ::sim::crossProduct( m_crossProductArticulation, i_xyzArticulation, i_FxyzArticulation );

    o_MvRRollPitchYawChassis = ( ::sim::crossProduct( m_crossProductLF, m_pLF, m_RvfLF ) + ::sim::crossProduct( m_crossProductRF, m_pRF, m_RvfRF )
                                 + ::sim::crossProduct( m_crossProductLR, m_pLR, m_RvfLR ) + ::sim::crossProduct( m_crossProductRR, m_pRR, m_RvfRR ) );
}

void CStaticCar::transformWheelForce( CFloat& f_Fx, CFloat& f_Fy, CFloat f_FWheelLongitudinal, CFloat f_FWheelLateral, CFloat f_wheelAngle )
{
    f_Fx = + f_FWheelLongitudinal * ::sim::cos( f_wheelAngle )
           - f_FWheelLateral * ::sim::sin( f_wheelAngle ) ;
    f_Fy = + f_FWheelLongitudinal * ::sim::sin( f_wheelAngle )
           + f_FWheelLateral * ::sim::cos( f_wheelAngle ) ;
}
