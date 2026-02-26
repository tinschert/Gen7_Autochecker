/*******************************************************************************
author Andreas Brunner, bnr2lr (29.05.2019)
author (c) Copyright Robert Bosch GmbH 2019-2024.  All rights reserved.
*******************************************************************************/

#include "CArticulation.h"


/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CArticulation::CArticulation():
    m_dT0( 1e-3 ), m_dT1( 1e-3 ), m_dT2( 1e-3 ),
    m_Fxyz( {0., 0., 0.,} ), m_zeroVector( {0, 0, 0} ),
        m_angleRollPitchYawFirst( {0., 0., 0.} ), m_angleRollPitchYawSecond( {0., 0., 0.} ),
        m_xyzArtFirst( {0., 0., 0.} ), m_xyzArtSecond( {0., 0., 0.} ),
        m_deltaxyzArt0( {0., 0., 0.} ), m_deltaxyzArt1( {0., 0., 0.} ),
        m_deltaxyzVel0( {0., 0., 0.} ), m_deltaxyzVel1( {0., 0., 0.} ),
        m_deltaxyzAcc0( {0., 0., 0.} ),
        m_deltaxyzIntegrated( {0., 0., 0.} )

{
    /* Initialization messages */
    /***************************************************************************
     * Coordinate transform between two vehicles
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



    /* input messages */
    addMessageInput( i_angleRollPitchYawFirstVehicle, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_angleRollPitchYawSecondVehicle, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_xyzFirstVehicle, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_xyzSecondVehicle, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_xyzArticulationFirstVehicle, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_xyzArticulationSecondVehicle, CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    addMessageInput( i_detach, true );
    i_detach.setInit( true );

    /* parameter messages */

    // standard feedback constants are heuristically optimized for truck/trailer with ~7500 kg on standard track
    addMessageParameter( p_Kacceleration, CFloatVectorXYZ( 0.0, 0.0, 0.0 ), CArticulationDoc::p_Kacceleration );
    addMessageParameter( p_Kvelocity, CFloatVector( 25e3, 3 ), CArticulationDoc::p_Kvelocity );
    addMessageParameter( p_Kdistance, CFloatVector( 300e3, 3 ), CArticulationDoc::p_Kdistance );
    addMessageParameter( p_Kintegrated, CFloatVectorXYZ( 0.0, 0.0, 0.0 ), CArticulationDoc::p_Kintegrated );

    /* output messages */
    addMessageOutput( o_FxyzFirstVehicle, CFloatVectorXYZ( 0.0, 0.0, 0.0 ), CArticulationDoc::o_FxyzFirstVehicle );
    addMessageOutput( o_FxyzSecondVehicle, CFloatVectorXYZ( 0.0, 0.0, 0.0 ), CArticulationDoc::o_FxyzSecondVehicle );

    o_FxyzFirstVehicle.setInit( CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );
    o_FxyzSecondVehicle.setInit( CFloatVectorXYZ( 0.0, 0.0, 0.0 ) );


}

CArticulation::~CArticulation()
{}

/*------------------*/
/* public methods  */
/*------------------*/


void CArticulation::init( IMessage<CFloatVectorXYZ>& f_angleRollPitchYawFirstVehicle,
                          IMessage<CFloatVectorXYZ>& f_angleRollPitchYawSecondVehicle,
                          IMessage<CFloatVectorXYZ>& f_xyzFirstVehicle,
                          IMessage<CFloatVectorXYZ>& f_xyzSecondVehicle,
                          IMessage<CFloatVectorXYZ>& f_xyzArticulationFirstVehicle,
                          IMessage<CFloatVectorXYZ>& f_xyzArticulationSecondVehicle,
                          IMessage<CBool>& f_detach )
{
    /* Connect input with internal variables */
    i_angleRollPitchYawFirstVehicle.link( f_angleRollPitchYawFirstVehicle );
    i_angleRollPitchYawSecondVehicle.link( f_angleRollPitchYawSecondVehicle );
    i_xyzFirstVehicle.link( f_xyzFirstVehicle );
    i_xyzSecondVehicle.link( f_xyzSecondVehicle );
    i_xyzArticulationFirstVehicle.link( f_xyzArticulationFirstVehicle );
    i_xyzArticulationSecondVehicle.link( f_xyzArticulationSecondVehicle );
    i_detach.link( f_detach );

    /* Initialization messages */
    initializationMessages();

    // initalize outgoing forces and helper variables to zero to "reset memory" during Sim Init
    o_FxyzFirstVehicle  = m_zeroVector;
    o_FxyzSecondVehicle = m_zeroVector;

    m_dT0 = 1e-3, m_dT1 = 1e-3, m_dT2 = 1e-3;
    m_Fxyz = CFloatVectorXYZ( 0.0, 0.0, 0.0 ), m_zeroVector = CFloatVectorXYZ( 0.0, 0.0, 0.0 );
    m_angleRollPitchYawFirst = CFloatVectorXYZ( 0.0, 0.0, 0.0 ), m_angleRollPitchYawSecond = CFloatVectorXYZ( 0.0, 0.0, 0.0 );
    m_xyzArtFirst = CFloatVectorXYZ( 0.0, 0.0, 0.0 ), m_xyzArtSecond = CFloatVectorXYZ( 0.0, 0.0, 0.0 );
    m_deltaxyzArt0 = CFloatVectorXYZ( 0.0, 0.0, 0.0 ), m_deltaxyzArt1 = CFloatVectorXYZ( 0.0, 0.0, 0.0 );
    m_deltaxyzVel0 = CFloatVectorXYZ( 0.0, 0.0, 0.0 ), m_deltaxyzVel1 = CFloatVectorXYZ( 0.0, 0.0, 0.0 );
    m_deltaxyzAcc0 = CFloatVectorXYZ( 0.0, 0.0, 0.0 );
    m_deltaxyzIntegrated = CFloatVectorXYZ( 0.0, 0.0, 0.0 );

}

/*------------------*/
/* private methods */
/*------------------*/
void CArticulation::calc( CFloat f_dT, CFloat f_time )
{
    /* Calculate reaction forces */
    if( i_detach ) // detached --> output zero "reaction force" vectors
    {
        o_FxyzFirstVehicle      = m_zeroVector;
        o_FxyzSecondVehicle     = m_zeroVector;
    }
    else
    {
        // Calculate global articulation (x,y,z) positions of truck and trailer.
        m_angleRollPitchYawFirst  = i_angleRollPitchYawFirstVehicle;
        m_angleRollPitchYawSecond = i_angleRollPitchYawSecondVehicle;

        ::sim::coordinateRotation( m_angleRollPitchYawFirst,
                            i_xyzArticulationFirstVehicle,
                            m_xyzArtFirst );

        m_xyzArtFirst = m_xyzArtFirst + i_xyzFirstVehicle;

        ::sim::coordinateRotation( m_angleRollPitchYawSecond,
                            i_xyzArticulationSecondVehicle,
                            m_xyzArtSecond );

        m_xyzArtSecond = m_xyzArtSecond + i_xyzSecondVehicle;

        // Calculate current xyz delta, delta velocity, delta acceleration, and integrated delta.
        // Sign chosen s.th. a pulling first vehicle (x_first increasing) will lead to positive delta_x.
        m_deltaxyzArt0 =  m_xyzArtFirst - m_xyzArtSecond;

        // Articulation delta position, velocity, acceleration, and integrated position
        // For velocity/acceleration: catch division by zero (dT == 0)
        m_deltaxyzVel0  = ( m_dT1 == 0 ) ? m_zeroVector : ( m_deltaxyzArt0 - m_deltaxyzArt1 ) * ( 1 / m_dT1 );
        m_deltaxyzAcc0  = ( m_dT2 == 0 ) ? m_zeroVector : ( m_deltaxyzVel0 - m_deltaxyzVel1 ) * ( 1 / m_dT2 ); // theoretically, (dT1+dT2)/2 would be expected. heuristically, dT2 gives smooth results
        m_deltaxyzIntegrated += m_deltaxyzArt0 * m_dT1;
        m_dT0           = f_dT;

        // Add forces, each component limited to 200 kN to suppress "numerical singularities".
        // Under stable driving conditions, this is effectively not a limit for a 30 ton trailer.
        CFloat Fmin = -2e5, Fmax = 2e5;

        m_Fxyz  = ::sim::limit( p_Kacceleration * m_deltaxyzAcc0,  Fmin,  Fmax );
        m_Fxyz += ::sim::limit( p_Kvelocity     * m_deltaxyzVel0,  Fmin,  Fmax );
        m_Fxyz += ::sim::limit( p_Kdistance     * m_deltaxyzArt0,  Fmin,  Fmax );
        // m_Fxyz += limit(p_Kintegrated * m_deltaxyzIntegrated,   Fmin, Fmax );

        // Transform force from global coordinates to the vehicles' coordinate systems.
        //  -> Minus sign for reaction force on first vehicle, since its positive acceleration leads to positive delta_xyz.
        //  -> Plus sign for input angles in coordinate rotation to go from global to vehicle coordinates.

        /* original */
        ::sim::coordinateRotationInv( m_angleRollPitchYawSecond,
                               m_Fxyz,
                               o_FxyzSecondVehicle );

        m_Fxyz = m_Fxyz * ( -1.0L );
        ::sim::coordinateRotationInv( m_angleRollPitchYawFirst,
                               m_Fxyz,
                               o_FxyzFirstVehicle );

        // Update variable history
        m_dT2          = m_dT1;
        m_dT1          = m_dT0;

        m_deltaxyzArt1 = m_deltaxyzArt0;
        m_deltaxyzVel1 = m_deltaxyzVel0;
    }
}

