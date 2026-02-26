/*******************************************************************************
@author Robert Erhart, ett2si (12.10.2004 - 00:00:00)
@author Andreas Brunner, bnr2lr (2020)
@copyright (c) Robert Bosch GmbH 2004-2024. All rights reserved.
*******************************************************************************/

#include "CWheel.h"

/*------------------------*/
/* constructor/destructor */
/*------------------------*/
CWheel::CWheel():
    m_Fcombined( 0.0 ), m_wheelPlsCnt( 0.0 ), m_deltaOmega( 0.0 ), m_velocity( 0.0 )
{
    /* Initialization messages */
    addMessageParameter( p_rollResistCoefficent, 0.01, CWheelDoc::p_rollResistCoefficent );     // c_r value
    addMessageParameter( p_rWheel, 0.33, CWheelDoc::p_rWheel );
    addMessageParameter( p_B, 1.5, CWheelDoc::p_B );
    addMessageParameter( p_C, 100000, CWheelDoc::p_C );
    addMessageParameter( p_camberCoefficient, 0, CWheelDoc::p_camberCoefficient );
    addMessageParameter( p_wheelPlsTeeth, 64, CWheelDoc::p_wheelPlsTeeth );
    addMessageParameter( p_wheelPlsRangeMax, 255, CWheelDoc::p_wheelPlsRangeMax );
    addMessageParameter( p_wheelPlsRangeMin, 0, CWheelDoc::p_wheelPlsRangeMin );
    addMessageParameter( p_omegaAcceleration, 0, CWheelDoc::p_omegaAcceleration );

    addMessageInput( i_alpha, 0.0 );
    addMessageInput( i_camberAngle, 0.0 );
    addMessageInput( i_Fvertical, 0.0 );
    addMessageInput( i_MWheel, 0.0 );
    addMessageInput( i_RvMWheel, 0.0 );
    addMessageInput( i_vXwheel, 0.0 );
    addMessageInput( i_vYwheel, 0.0 );
    addMessageInput( i_my, 0.0 );

    addMessageOutput( o_FrollResistance, 0.0, CWheelDoc::o_FrollResistance );
    addMessageOutput( o_FLongitudinal, 0.0, CWheelDoc::o_FLongitudinal );
    addMessageOutput( o_RvFLongitudinal, 0.0, CWheelDoc::o_RvFLongitudinal );
    addMessageOutput( o_FLateral, 0.0, CWheelDoc::o_FLateral );
    addMessageOutput( o_RvFLateral, 0.0, CWheelDoc::o_RvFLateral );
    addMessageOutput( o_FmaxWheel, 0.0, CWheelDoc::o_FmaxWheel );
    addMessageOutput( o_nWheel, 0.0, CWheelDoc::o_nWheel );
    addMessageOutput( o_omega, 0.0, CWheelDoc::o_omega );
    addMessageOutput( o_wheelPlsCnt, 0, CWheelDoc::o_wheelPlsCnt );
}

CWheel::~CWheel()
{}

/*------------------*/
/* public methods  */
/*------------------*/
void CWheel::init( IMessage<CFloat>& f_alpha,
                   IMessage<CFloat>& f_camberAngle,
                   IMessage<CFloat>& f_Fvertical,
                   IMessage<CFloat>& f_MWheel,
                   IMessage<CFloat>& f_RvMWheel,
                   IMessage<CFloat>& f_vXwheel,
                   IMessage<CFloat>& f_vYwheel,
                   IMessage<CFloat>& f_my )
{
    /* Connect input with internal variables */
    i_alpha.link( f_alpha );
    i_camberAngle.link( f_camberAngle );
    i_Fvertical.link( f_Fvertical );
    i_MWheel.link( f_MWheel );
    i_RvMWheel.link( f_RvMWheel );
    i_vXwheel.link( f_vXwheel );
    i_vYwheel.link( f_vYwheel );
    i_my.link( f_my );

    /* Initialization messages */
    initializationMessages();

    /* Initialization variable */
    m_wheelPlsCnt = 0;
    m_deltaOmega = 0;
}

/*------------------*/
/* private methods */
/*------------------*/
void CWheel::calc( CFloat f_dT, CFloat f_time )
{
    /***************************************************************************
     * Rolling resistance calculation (reverse force!):
     * F = p_rollResistCoefficent * i_Fz
     ***************************************************************************/
    m_velocity = i_vXwheel; //sqrt( pow( i_vXwheel, 2 ) + pow( i_vYwheel, 2 ) );
    o_FrollResistance = ::sim::sign_of( m_velocity ) * i_Fvertical * p_rollResistCoefficent;

    /***************************************************************************
     * Maximum wheel force: Fvert should be <0, else loss of road contact.
     **************************************************************************/
    o_FmaxWheel = ( i_Fvertical < 0 ) ? ( i_my * -i_Fvertical ) : 0;

    /***************************************************************************
     * Longitudinal force
     * Simplification: longitudinal force is active force
     *                  (wheel dynamics much faster than vehicle dynamics)
     * Vereinfachung: Laengskraft als eingepraegte Kraft,
     *                  da Raddynamik >> Fahrzeugdynamik (m_Rad << m_Fahrzeug)
     **************************************************************************/
    o_FLongitudinal = i_MWheel / p_rWheel;
    o_RvFLongitudinal = i_RvMWheel / p_rWheel + o_FrollResistance;

    /***************************************************************************
     * lateral force
     * type 1: linear model:
     *       o_RvFLateral = p_C * i_alpha
     * type 2: Pacejka model:
     *       o_RvFLateral = A * sin( B * atan(C*alpha) )
     *       A = my * Fvertical
     * ************************************************************************/
    o_FLateral  = 0;
    // ToDo: change sideslip coefficient to more general load-dependent value.
    m_Fsideslip = p_C * i_alpha;
    m_Fcamber   = p_camberCoefficient * ( -i_camberAngle ) * ( -i_Fvertical );

    // Fvertical should be negative, if >0: loss of road contact. In this case, FmaxWheel = 0 will null all forces anyway.
    o_RvFLateral = m_Fsideslip + m_Fcamber;

    // ---- Pacejka model:  UNUSED ---- //
    // Pacejka Flateral = m_Fmax * sin( B  * atan(C * alpha) );

    /**************************************************************************
     * Circle of Forces (Kammscher Kreis):
     * superposition of lateral and longitudinal force
     *          F^2 = Flateral^2 + Flongitudinal^2
     * and their limitation to F_maxWheel
     * --> scale the forces by theorem of intersecting lines
     **************************************************************************/
    CFloat l_FLongitudinal = ::sim::limit( o_FLongitudinal + o_RvFLongitudinal, -o_FmaxWheel, o_FmaxWheel );
    CFloat l_FLateral = ::sim::limit( o_FLateral + o_RvFLateral, -o_FmaxWheel, o_FmaxWheel );

    m_Fcombined = ::sim::sqrt( ::sim::pow( l_FLongitudinal, 2 ) + ::sim::pow( l_FLateral, 2 ) );
    if( m_Fcombined > o_FmaxWheel )
    {
        //theorem of intersecting lines (Strahlensatz)
        l_FLongitudinal = l_FLongitudinal * o_FmaxWheel / m_Fcombined;
        l_FLateral = l_FLateral * o_FmaxWheel / m_Fcombined;
    }
    CFloat l_FLongitudinalSum = o_FLongitudinal + o_RvFLongitudinal;
    if( ::sim::abs( l_FLongitudinal ) <  ::sim::abs( l_FLongitudinalSum ) )
    {
        o_FLongitudinal = o_FLongitudinal * l_FLongitudinal / l_FLongitudinalSum;
        o_RvFLongitudinal = o_RvFLongitudinal * l_FLongitudinal / l_FLongitudinalSum;
    }
    CFloat l_FLateralSum = o_FLateral + o_RvFLateral;
    if( ::sim::abs( l_FLateral ) <  ::sim::abs( l_FLateralSum ) )
    {
        o_FLateral = o_FLateral * l_FLateral / l_FLateralSum;
        o_RvFLateral = o_RvFLateral * l_FLateral / l_FLateralSum;
    }
    /***************************************************************************
        * wheel rpm
        **************************************************************************/
    if( p_omegaAcceleration != 0 )
    {
        m_deltaOmega += p_omegaAcceleration * f_dT;
    }
    else
    {
        m_deltaOmega = 0;
    }

    o_omega = i_vXwheel / p_rWheel + m_deltaOmega;

    o_nWheel = o_omega * 60 / ( 2 * M_PI );
    /**************************************************************************
     * Pulse counter p_wheelPlsRangeMin..p_wheelPlsRange
     * wheelPlsCnt += nWheel * f_dT * wheelPlsTeeth
     **************************************************************************/
    m_wheelPlsCnt += ::sim::abs( o_nWheel ) / 60 * f_dT * p_wheelPlsTeeth;
    if( m_wheelPlsCnt > p_wheelPlsRangeMax ) m_wheelPlsCnt = m_wheelPlsCnt - p_wheelPlsRangeMax + p_wheelPlsRangeMin - 1;
    o_wheelPlsCnt = ( ( CInt ) m_wheelPlsCnt ) ;
}

