/*******************************************************************************
author Robert Erhart, ett2si (23.06.2005 - 00:00:00)
author (c) Copyright Robert Bosch GmbH 2005-2024. All rights reserved.
*******************************************************************************/

#include "CChassisCar.h"

/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CChassisCar::CChassisCar()
{
    /* Initialization messages */
    /***************************************************************************
     * Initialization of car parameter
     * car definition:
     *             leftFront    rightFront
     *                0-----------0
     *                      ^ x
     *                      |
     *                      |
     *              y <-----. Center of Gravity (h = height over the street)
     *                      |
     *                      |
     *                  o------------o
     *               leftRear     rightRear
     *
     **************************************************************************/
    addMessageParameter( p_wheelAngleRear, 0.0, CChassisCarDoc::p_wheelAngleRear );
    //wheel left front
    addMessageParameter( p_xWheelLeftFront, 1.292, CChassisCarDoc::p_xWheelLeftFront );
    addMessageParameter( p_yWheelLeftFront, 0.79106, CChassisCarDoc::p_yWheelLeftFront );
    addMessageParameter( p_myLeftFront, 1, CChassisCarDoc::p_myLeftFront );
    //wheel right front
    addMessageParameter( p_xWheelRightFront, 1.292, CChassisCarDoc::p_xWheelRightFront );
    addMessageParameter( p_yWheelRightFront, -0.79106, CChassisCarDoc::p_yWheelRightFront );
    addMessageParameter( p_myRightFront, 1, CChassisCarDoc::p_myRightFront );
    //wheel left rear
    addMessageParameter( p_xWheelLeftRear, -1.403, CChassisCarDoc::p_xWheelLeftRear );
    addMessageParameter( p_yWheelLeftRear, 0.79106, CChassisCarDoc::p_yWheelLeftRear );
    addMessageParameter( p_myLeftRear, 1, CChassisCarDoc::p_myLeftRear );
    //wheel right rear
    addMessageParameter( p_xWheelRightRear, -1.403, CChassisCarDoc::p_xWheelRightRear );
    addMessageParameter( p_yWheelRightRear, -0.79106, CChassisCarDoc::p_yWheelRightRear );
    addMessageParameter( p_myRightRear, 1, CChassisCarDoc::p_myRightRear );
    // CentreOfGravity
    addMessageParameter( p_h, 0.50, CChassisCarDoc::p_h );
    addMessageParameter( p_m, 1998, CChassisCarDoc::p_m );
    addMessageParameter( p_JRollPitchYaw, CFloatVectorXYZ( 3000, 3400, 3412 ), CChassisCarDoc::p_JRollPitchYaw );
    // articulation
    addMessageParameter( p_xyzArticulation, CFloatVectorXYZ( 1.0, 1.0, 1.0 ), CChassisCarDoc::p_xyzArticulation );

    //dummy only relevant for two wheeler
    p_setRollAngle.setInit( 0.0 );

    addMessageInput( i_wheelAngleFront, 0.0 );
    addMessageInput( i_MWheelLeftFront, 0.0 );
    addMessageInput( i_MWheelRightFront, 0.0 );
    addMessageInput( i_MWheelLeftRear, 0.0 );
    addMessageInput( i_MWheelRightRear, 0.0 );
    addMessageInput( i_RvMWheelLeftFront, 0.0 );
    addMessageInput( i_RvMWheelRightFront, 0.0 );
    addMessageInput( i_RvMWheelLeftRear, 0.0 );
    addMessageInput( i_RvMWheelRightRear, 0.0 );
    addMessageInput( i_angleRollPitchYawSurface, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_FxyzArticulation, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_staticSimulation, false );

    // input via internal modules
    addMessageInput( i_beta, 0.0 );
    addMessageInput( i_velocity, 0.0 );
    addMessageInput( i_vChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_rateRollPitchYawChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_nWheelRightFront, 0.0 );
    addMessageInput( i_nWheelLeftFront, 0.0 );
    addMessageInput( i_nWheelRightRear, 0.0 );
    addMessageInput( i_nWheelLeftRear, 0.0 );

    addMessageOutput( o_beta, 0.0, CChassisCarDoc::o_beta );
    addMessageOutput( o_velocity, 0.0, CChassisCarDoc::o_velocity );
    addMessageOutput( o_vChassis, CFloatVectorXYZ( 0.0, 0.0, 0.0 ), CChassisCarDoc::o_vChassis );
    addMessageOutput( o_yawRate, 0.0, CChassisCarDoc::o_yawRate );
    addMessageOutput( o_nWheelRightFront, 0.0, CChassisCarDoc::o_nWheelRightFront );
    addMessageOutput( o_nWheelLeftFront, 0.0, CChassisCarDoc::o_nWheelLeftFront );
    addMessageOutput( o_nWheelRightRear, 0.0, CChassisCarDoc::o_nWheelRightFront );
    addMessageOutput( o_nWheelLeftRear, 0.0, CChassisCarDoc::o_nWheelLeftFront );

    o_zero.setInit( 0.0 );
    addMessageOutput( o_zero, 0.0 );

}

CChassisCar::~CChassisCar()
{}

/*------------------*/
/* public methods  */
/*------------------*/
void CChassisCar::init( IMessage<CFloat>& f_wheelAngleFront,
                        IMessage<CFloat>& f_MWheelLeftFront,
                        IMessage<CFloat>& f_RvMWheelLeftFront,
                        IMessage<CFloat>& f_MWheelRightFront,
                        IMessage<CFloat>& f_RvMWheelRightFront,
                        IMessage<CFloat>& f_MWheelLeftRear,
                        IMessage<CFloat>& f_RvMWheelLeftRear,
                        IMessage<CFloat>& f_MWheelRightRear,
                        IMessage<CFloat>& f_RvMWheelRightRear,
                        IMessage<CFloatVectorXYZ>& f_angleRollPitchYawSurface,
                        IMessage<CFloatVectorXYZ>& f_FxyzArticulation,
                        IMessage<CBool>& f_staticSimulation )
{
    /* Connect input with internal variables */
    i_wheelAngleFront.link( f_wheelAngleFront );
    i_MWheelLeftFront.link( f_MWheelLeftFront );
    i_RvMWheelLeftFront.link( f_RvMWheelLeftFront );
    i_MWheelRightFront.link( f_MWheelRightFront );
    i_RvMWheelRightFront.link( f_RvMWheelRightFront );
    i_MWheelLeftRear.link( f_MWheelLeftRear );
    i_RvMWheelLeftRear.link( f_RvMWheelLeftRear );
    i_MWheelRightRear.link( f_MWheelRightRear );
    i_RvMWheelRightRear.link( f_RvMWheelRightRear );
    i_angleRollPitchYawSurface.link( f_angleRollPitchYawSurface );
    i_FxyzArticulation.link( f_FxyzArticulation );
    i_staticSimulation.link( f_staticSimulation );

    // input via internal modules
    i_beta.link( dynamic.o_beta );
    i_velocity.link( dynamic.o_velocity );
    i_vChassis.link( dynamic.o_vChassis );
    i_rateRollPitchYawChassis.link( dynamic.o_rateRollPitchYawChassis );
    i_nWheelRightFront.link( wheelRightFront.o_nWheel );
    i_nWheelLeftFront.link( wheelLeftFront.o_nWheel );
    i_nWheelRightRear.link( wheelRightRear.o_nWheel );
    i_nWheelLeftRear.link( wheelLeftRear.o_nWheel );

    /* Initialization messages */
    initializationMessages();

    /* Initialization variable */

    /* Defines communication between objects */
    /**************************************************************************
     * KINETICS
     *************************************************************************/
    kineticsLeftFront.init( dynamic.o_vChassis,
                            dynamic.o_rateRollPitchYawChassis,
                            i_wheelAngleFront,
                            p_xWheelLeftFront,
                            p_yWheelLeftFront );

    kineticsRightFront.init( dynamic.o_vChassis,
                             dynamic.o_rateRollPitchYawChassis,
                             i_wheelAngleFront,
                             p_xWheelRightFront,
                             p_yWheelRightFront );

    kineticsLeftRear.init( dynamic.o_vChassis,
                           dynamic.o_rateRollPitchYawChassis,
                           p_wheelAngleRear,
                           p_xWheelLeftRear,
                           p_yWheelLeftRear );

    kineticsRightRear.init( dynamic.o_vChassis,
                            dynamic.o_rateRollPitchYawChassis,
                            p_wheelAngleRear,
                            p_xWheelRightRear,
                            p_yWheelRightRear );

    /**************************************************************************
     * WHEEL
     *************************************************************************/
    wheelLeftFront.init( kineticsLeftFront.o_alpha,
                         o_zero, // no wheel camber, roll angle only affects (suspended) chassis
                         suspensionLeftFront.o_FSuspensionWheel,
                         i_MWheelLeftFront,
                         i_RvMWheelLeftFront,
                         kineticsLeftFront.o_vXwheel,
                         kineticsLeftFront.o_vYwheel,
                         p_myLeftFront );

    wheelRightFront.init( kineticsRightFront.o_alpha,
                          o_zero, // no wheel camber, roll angle only affects (suspended) chassis
                          suspensionRightFront.o_FSuspensionWheel,
                          i_MWheelRightFront,
                          i_RvMWheelRightFront,
                          kineticsRightFront.o_vXwheel,
                          kineticsRightFront.o_vYwheel,
                          p_myRightFront );

    wheelLeftRear.init( kineticsLeftRear.o_alpha,
                        o_zero, // no wheel camber, roll angle only affects (suspended) chassis
                        suspensionLeftRear.o_FSuspensionWheel,
                        i_MWheelLeftRear,
                        i_RvMWheelLeftRear,
                        kineticsLeftRear.o_vXwheel,
                        kineticsLeftRear.o_vYwheel,
                        p_myLeftRear );

    wheelRightRear.init( kineticsRightRear.o_alpha,
                         o_zero, // no wheel camber, roll angle only affects (suspended) chassis
                         suspensionRightRear.o_FSuspensionWheel,
                         i_MWheelRightRear,
                         i_RvMWheelRightRear,
                         kineticsRightRear.o_vXwheel,
                         kineticsRightRear.o_vYwheel,
                         p_myRightRear );


    /**************************************************************************
     * AIR RESISTANCE
     *************************************************************************/
    airResistance.init( dynamic.o_velocity );

    /**************************************************************************
     * STATIC
     *************************************************************************/
    staticCar.init( suspensionLeftFront.o_FSuspensionChassis,
                    wheelLeftFront.o_FLateral,
                    wheelLeftFront.o_RvFLateral,
                    wheelLeftFront.o_FLongitudinal,
                    wheelLeftFront.o_RvFLongitudinal,
                    suspensionRightFront.o_FSuspensionChassis,
                    wheelRightFront.o_FLateral,
                    wheelRightFront.o_RvFLateral,
                    wheelRightFront.o_FLongitudinal,
                    wheelRightFront.o_RvFLongitudinal,
                    suspensionLeftRear.o_FSuspensionChassis,
                    wheelLeftRear.o_FLateral,
                    wheelLeftRear.o_RvFLateral,
                    wheelLeftRear.o_FLongitudinal,
                    wheelLeftRear.o_RvFLongitudinal,
                    suspensionRightRear.o_FSuspensionChassis,
                    wheelRightRear.o_FLateral,
                    wheelRightRear.o_RvFLateral,
                    wheelRightRear.o_FLongitudinal,
                    wheelRightRear.o_RvFLongitudinal,
                    airResistance.o_FairResistance,
                    i_wheelAngleFront,
                    p_wheelAngleRear,
                    dynamic.o_beta,
                    p_xWheelLeftFront,
                    p_yWheelLeftFront,
                    p_xWheelRightFront,
                    p_yWheelRightFront,
                    p_xWheelLeftRear,
                    p_yWheelLeftRear,
                    p_xWheelRightRear,
                    p_yWheelRightRear,
                    p_h,
                    p_m,
                    i_angleRollPitchYawSurface,
                    dynamic.o_angleRollPitchYawSuspension,
                    i_FxyzArticulation,
                    p_xyzArticulation );

    /**************************************************************************
     * DYNAMIC
     *************************************************************************/
    dynamic.init( staticCar.o_FChassis,
                  staticCar.o_FvRChassis,
                  staticCar.o_MRollPitchYawChassis,
                  staticCar.o_MvRRollPitchYawChassis,
                  p_m,
                  p_JRollPitchYaw,
                  p_setRollAngle,
                  i_staticSimulation );

    /**************************************************************************
     * vertical wheel KINETICSVERTICAL and SUSPENSION
     *************************************************************************/
    kineticsVerticalLeftFront.init( dynamic.o_angleRollPitchYawSuspension,
                                    dynamic.o_rateRollPitchYawChassis,
                                    dynamic.o_zChassis,
                                    dynamic.o_vChassis,
                                    p_xWheelLeftFront,
                                    p_yWheelLeftFront );

    kineticsVerticalRightFront.init( dynamic.o_angleRollPitchYawSuspension,
                                     dynamic.o_rateRollPitchYawChassis,
                                     dynamic.o_zChassis,
                                     dynamic.o_vChassis,
                                     p_xWheelRightFront,
                                     p_yWheelRightFront );

    kineticsVerticalLeftRear.init( dynamic.o_angleRollPitchYawSuspension,
                                   dynamic.o_rateRollPitchYawChassis,
                                   dynamic.o_zChassis,
                                   dynamic.o_vChassis,
                                   p_xWheelLeftRear,
                                   p_yWheelLeftRear );

    kineticsVerticalRightRear.init( dynamic.o_angleRollPitchYawSuspension,
                                    dynamic.o_rateRollPitchYawChassis,
                                    dynamic.o_zChassis,
                                    dynamic.o_vChassis,
                                    p_xWheelRightRear,
                                    p_yWheelRightRear );

    suspensionLeftFront.init( kineticsVerticalLeftFront.o_vZsuspension,
                              kineticsVerticalLeftFront.o_zSuspension );

    suspensionRightFront.init( kineticsVerticalRightFront.o_vZsuspension,
                               kineticsVerticalRightFront.o_zSuspension );

    suspensionLeftRear.init( kineticsVerticalLeftRear.o_vZsuspension,
                             kineticsVerticalLeftRear.o_zSuspension );

    suspensionRightRear.init( kineticsVerticalRightRear.o_vZsuspension,
                              kineticsVerticalRightRear.o_zSuspension );
}


void CChassisCar::calcSuspensionSteadyState( CFloat f_integrationTime )
{
    CMessageOutput<CFloat>* l_messages[] =
    {
        &kineticsVerticalLeftFront.o_zSuspension,
        &kineticsVerticalLeftRear.o_zSuspension,
        &kineticsVerticalRightFront.o_zSuspension,
        &kineticsVerticalRightRear.o_zSuspension,

        &kineticsVerticalLeftFront.o_vZsuspension,
        &kineticsVerticalLeftRear.o_vZsuspension,
        &kineticsVerticalRightFront.o_vZsuspension,
        &kineticsVerticalRightRear.o_vZsuspension,

        &suspensionLeftFront.o_FSuspensionChassis,
        &suspensionRightFront.o_FSuspensionChassis,
        &suspensionLeftRear.o_FSuspensionChassis,
        &suspensionRightRear.o_FSuspensionChassis,

        &suspensionLeftFront.o_FSuspensionWheel,
        &suspensionRightFront.o_FSuspensionWheel,
        &suspensionLeftRear.o_FSuspensionWheel,
        &suspensionRightRear.o_FSuspensionWheel,

        &dynamic.o_zChassis
    };

    CFloat dt = 0.01; // integrate in 10 ms time steps
    CFloat t = 0;

    // integrate the model
    for( ; t < f_integrationTime; t += dt )
        process( dt, 0 );

    // update 'steady state' values (setInit call):
    for( auto& m : l_messages )
    {
        m->setInit( *m );
    }
}

/*------------------*/
/* private methods */
/*------------------*/
void CChassisCar::calc( CFloat f_dT, CFloat f_time )
{

    /* calculate chassis components */
    kineticsLeftFront.process( f_dT, f_time );
    kineticsRightFront.process( f_dT, f_time );
    kineticsLeftRear.process( f_dT, f_time );
    kineticsRightRear.process( f_dT, f_time );
    airResistance.process( f_dT, f_time );
    staticCar.process( f_dT, f_time );
    wheelLeftFront.process( f_dT, f_time );
    wheelRightFront.process( f_dT, f_time );
    wheelLeftRear.process( f_dT, f_time );
    wheelRightRear.process( f_dT, f_time );
    kineticsVerticalLeftFront.process( f_dT, f_time );
    kineticsVerticalRightFront.process( f_dT, f_time );
    kineticsVerticalLeftRear.process( f_dT, f_time );
    kineticsVerticalRightRear.process( f_dT, f_time );
    suspensionLeftFront.process( f_dT, f_time );
    suspensionRightFront.process( f_dT, f_time );
    suspensionLeftRear.process( f_dT, f_time );
    suspensionRightRear.process( f_dT, f_time );

    dynamic.process( f_dT, f_time );

    /* output */
    o_beta = i_beta;
    o_velocity = i_velocity;
    o_vChassis = i_vChassis;
    o_yawRate = i_rateRollPitchYawChassis.Z();
    o_nWheelRightFront  = i_nWheelRightFront;
    o_nWheelLeftFront   = i_nWheelLeftFront;
    o_nWheelRightRear   = i_nWheelRightRear;
    o_nWheelLeftRear    = i_nWheelLeftRear;
}

