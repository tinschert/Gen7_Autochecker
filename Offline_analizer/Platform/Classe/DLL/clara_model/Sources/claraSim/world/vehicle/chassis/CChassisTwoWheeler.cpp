/*******************************************************************************
author Robert Erhart, ett2si (23.06.2005 - 00:00:00)
author Andreas Brunner, bnr2lr (17.07.2019)
author (c) Copyright Robert Bosch GmbH 2019-2024. All rights reserved.
*******************************************************************************/

#include "CChassisTwoWheeler.h"

/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CChassisTwoWheeler::CChassisTwoWheeler()
{
    /* Initialization messages */
    /***************************************************************************
     * Initialization of bike parameter
     *
     * twowheeler definition:
     *       front
     *          0
     *          ^ x
     *          |
     *          |
     *  y <-----. Center of Gravity (h = height over the street)
     *          |
     *          |
     *          0
     *        rear
     *
     **************************************************************************/
    addMessageParameter( p_wheelAngleRear, 0.0, CChassisTwoWheelerDoc::p_wheelAngleRear );
    //wheel front
    addMessageParameter( p_xWheelFront, 0.85, CChassisTwoWheelerDoc::p_xWheelFront );
    addMessageParameter( p_yWheelFront, 0., CChassisTwoWheelerDoc::p_yWheelFront );
    addMessageParameter( p_myFront, 1, CChassisTwoWheelerDoc::p_myFront );
    //wheel rear
    addMessageParameter( p_xWheelRear, -0.75, CChassisTwoWheelerDoc::p_xWheelRear );
    addMessageParameter( p_yWheelRear, .0, CChassisTwoWheelerDoc::p_yWheelRear );
    addMessageParameter( p_myRear, 1, CChassisTwoWheelerDoc::p_myRear );
    // CentreOfGravity
    addMessageParameter( p_h, 0.50, CChassisTwoWheelerDoc::p_h );
    addMessageParameter( p_m, 324, CChassisTwoWheelerDoc::p_m );
    addMessageParameter( p_JRollPitchYaw, CFloatVectorXYZ( 50, 177, 177 ), CChassisTwoWheelerDoc::p_JRollPitchYaw );
    // articulation
    addMessageParameter( p_xyzArticulation, CFloatVectorXYZ( 0.0, 0.0, 1.0 ), CChassisTwoWheelerDoc::p_xyzArticulation );


    addMessageInput( i_wheelAngleFront, 0.0 );
    addMessageInput( i_MWheelFront, 0.0 );
    addMessageInput( i_MWheelRear, 0.0 );
    addMessageInput( i_RvMWheelFront, 0.0 );
    addMessageInput( i_RvMWheelRear, 0.0 );
    addMessageInput( i_angleRollPitchYawSurface, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_setRollAngle, 0.0 );
    addMessageInput( i_FxyzArticulation, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_staticSimulation, false );

    // input via internal modules
    addMessageInput( i_angleRollPitchYawSuspension, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_beta, 0.0 );
    addMessageInput( i_velocity, 0.0 );
    addMessageInput( i_vChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_rateRollPitchYawChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_nWheelFront, 0.0 );
    addMessageInput( i_nWheelRear, 0.0 );

    addMessageOutput( o_beta, 0.0, CChassisTwoWheelerDoc::o_beta );
    addMessageOutput( o_velocity, 0.0, CChassisTwoWheelerDoc::o_velocity );
    addMessageOutput( o_vChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ), CChassisTwoWheelerDoc::o_vChassis );
    addMessageOutput( o_yawRate, 0.0, CChassisTwoWheelerDoc::o_yawRate );
    addMessageOutput( o_nWheelFront, 0.0, CChassisTwoWheelerDoc::o_nWheelFront );
    addMessageOutput( o_camberAngle, 0.0, CChassisTwoWheelerDoc::o_camberAngle );

    p_xyzArticulation.setInit( CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );

    dynamic.p_forceRollAngle.setInit( true ); //switch to two wheeler mode
}

CChassisTwoWheeler::~CChassisTwoWheeler()
{}

/*------------------*/
/* public methods  */
/*------------------*/
void CChassisTwoWheeler::init( IMessage<CFloat>& f_wheelAngleFront,
                               IMessage<CFloat>& f_MWheelFront,
                               IMessage<CFloat>& f_RvMWheelFront,
                               IMessage<CFloat>& f_MWheelRear,
                               IMessage<CFloat>& f_RvMWheelRear,
                               IMessage<CFloatVectorXYZ>& f_angleRollPitchYawSurface,
                               IMessage<CFloat>& f_setRollAngle,
                               IMessage<CFloatVectorXYZ>& f_FxyzArticulation,
                               IMessage<CBool>& f_staticSimulation )
{
    /* Connect input with internal variables */
    i_wheelAngleFront.link( f_wheelAngleFront );
    i_MWheelFront.link( f_MWheelFront );
    i_RvMWheelFront.link( f_RvMWheelFront );
    i_MWheelRear.link( f_MWheelRear );
    i_RvMWheelRear.link( f_RvMWheelRear );
    i_angleRollPitchYawSurface.link( f_angleRollPitchYawSurface );
    i_setRollAngle.link( f_setRollAngle );
    i_FxyzArticulation.link( f_FxyzArticulation );
    i_staticSimulation.link( f_staticSimulation );

    // input via internal modules
    i_angleRollPitchYawSuspension.link( dynamic.o_angleRollPitchYawSuspension );
    i_beta.link( dynamic.o_beta );
    i_velocity.link( dynamic.o_velocity );
    i_vChassis.link( dynamic.o_vChassis );
    i_rateRollPitchYawChassis.link( dynamic.o_rateRollPitchYawChassis );
    i_nWheelFront.link( wheelFront.o_nWheel );
    i_nWheelRear.link( wheelRear.o_nWheel );

    /* Initialization messages */
    initializationMessages();

    /* Initialization variable */

    /* Defines communication between objects */
    /**************************************************************************
     * KINETICS
     *************************************************************************/
    kineticsFront.init( dynamic.o_vChassis,
                        dynamic.o_rateRollPitchYawChassis,
                        i_wheelAngleFront,
                        p_xWheelFront,
                        p_yWheelFront );

    kineticsRear.init( dynamic.o_vChassis,
                       dynamic.o_rateRollPitchYawChassis,
                       p_wheelAngleRear,
                       p_xWheelRear,
                       p_yWheelRear );

    /**************************************************************************
     * WHEEL
     *************************************************************************/
    wheelFront.init( kineticsFront.o_alpha,
                     o_camberAngle,
                     suspensionFront.o_FSuspensionWheel,
                     i_MWheelFront,
                     i_RvMWheelFront,
                     kineticsFront.o_vXwheel,
                     kineticsFront.o_vYwheel,
                     p_myFront );

    wheelRear.init( kineticsRear.o_alpha,
                    o_camberAngle,
                    suspensionRear.o_FSuspensionWheel,
                    i_MWheelRear,
                    i_RvMWheelRear,
                    kineticsRear.o_vXwheel,
                    kineticsRear.o_vYwheel,
                    p_myRear );

    /**************************************************************************
     * AIR RESISTANCE
     *************************************************************************/
    airResistance.init( dynamic.o_velocity );

    /**************************************************************************
     * STATIC
     *************************************************************************/
    staticTwoWheeler.init( suspensionFront.o_FSuspensionChassis,
                           wheelFront.o_FLateral,
                           wheelFront.o_RvFLateral,
                           wheelFront.o_FLongitudinal,
                           wheelFront.o_RvFLongitudinal,
                           suspensionRear.o_FSuspensionChassis,
                           wheelRear.o_FLateral,
                           wheelRear.o_RvFLateral,
                           wheelRear.o_FLongitudinal,
                           wheelRear.o_RvFLongitudinal,
                           airResistance.o_FairResistance,
                           i_wheelAngleFront,
                           p_wheelAngleRear,
                           dynamic.o_beta,
                           p_xWheelFront,
                           p_yWheelFront,
                           p_xWheelRear,
                           p_yWheelRear,
                           p_h,
                           p_m,
                           i_angleRollPitchYawSurface,
                           dynamic.o_angleRollPitchYawSuspension,
                           i_FxyzArticulation,
                           p_xyzArticulation );

    /**************************************************************************
     * DYNAMIC
     *************************************************************************/
    dynamic.init( staticTwoWheeler.o_FChassis,
                  staticTwoWheeler.o_FvRChassis,
                  staticTwoWheeler.o_MRollPitchYawChassis,
                  staticTwoWheeler.o_MvRRollPitchYawChassis,
                  p_m,
                  p_JRollPitchYaw,
                  i_setRollAngle,
                  i_staticSimulation );

    /**************************************************************************
     * vertical wheel KINETICSVERTICAL and SUSPENSION
     *************************************************************************/
    kineticsVerticalFront.init( dynamic.o_angleRollPitchYawSuspension,
                                dynamic.o_rateRollPitchYawChassis,
                                dynamic.o_zChassis,
                                dynamic.o_vChassis,
                                p_xWheelFront,
                                p_yWheelFront );

    kineticsVerticalRear.init( dynamic.o_angleRollPitchYawSuspension,
                               dynamic.o_rateRollPitchYawChassis,
                               dynamic.o_zChassis,
                               dynamic.o_vChassis,
                               p_xWheelRear,
                               p_yWheelRear );

    suspensionFront.init( kineticsVerticalFront.o_vZsuspension,
                          kineticsVerticalFront.o_zSuspension );

    suspensionRear.init( kineticsVerticalRear.o_vZsuspension,
                         kineticsVerticalRear.o_zSuspension );
}

/*------------------*/
/* private methods */
/*------------------*/
void CChassisTwoWheeler::calc( CFloat f_dT, CFloat f_time )
{
    /* calculate chassis components */
    kineticsFront.process( f_dT, f_time );
    kineticsRear.process( f_dT, f_time );
    airResistance.process( f_dT, f_time );
    staticTwoWheeler.process( f_dT, f_time );
    wheelFront.process( f_dT, f_time );
    wheelRear.process( f_dT, f_time );
    kineticsVerticalFront.process( f_dT, f_time );
    kineticsVerticalRear.process( f_dT, f_time );
    suspensionFront.process( f_dT, f_time );
    suspensionRear.process( f_dT, f_time );

    dynamic.process( f_dT, f_time );

    /* output */
    o_camberAngle = i_angleRollPitchYawSuspension.X();
    o_beta = i_beta;
    o_velocity = i_velocity;
    o_vChassis = i_vChassis;
    o_yawRate = i_rateRollPitchYawChassis.Z();
    o_nWheelFront   = i_nWheelFront;
    o_nWheelRear    = i_nWheelRear;
}

