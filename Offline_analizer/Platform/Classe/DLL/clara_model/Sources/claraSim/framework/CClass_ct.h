#ifndef CCLASS_CT_H
#define CCLASS_CT_H

#include "numericLib.h"

#ifndef print
/*!
 * Prints a number of arguments to std::cout. This is intended for debugging use.
 * The coding magic is achieved via template parameter pack voodoo and expansion.
 * C.f. https://riptutorial.com/cplusplus/example/3208/iterating-over-a-parameter-pack
 *
 * Example:
 *      std::cout << "Debug: val1=" << val1 << ", val2=" << val2 << std::endl;
 * becomes
 *      print("Debug: val1=", val1, ", val2=", val2);
 */
template <class... Ts>
void print( Ts const& ... args )
{
    using expander = int[];
    ( void )expander{0,
                     ( void( std::cout << args ), 0 )...
                    };
    std::cout << std::endl;
}
#endif


/*!
********************************************************************************
@class CDdtHeun
@ingroup framework
@brief Integration algorithm Heun

@author Robert Erhart, ett2si (18.10.2004 - 00:00:00)
@copyright (c) Robert Bosch GmbH 2023. All rights reserved.
********************************************************************************
@remark
- all equation of state classes inherit from CDdtHeun
- Heun Algorithm
   - y'(i) -> y(i+1) Prädiziert
   - n Korrekturschritte y(i+1) = y(i) + ( y'(i) + y'(i+1) ) f_dT/2
********************************************************************************
@param[in]  NumberOfStates             [CInt]   number of states
@param[in]  NumberOfIntegrationSteps   [CInt]   number of integration steps
********************************************************************************

********************************************************************************
*/

class CDdtHeun
{
public:
    CDdtHeun( uint8_t NumberOfStates, uint8_t NumberOfIntegrationSteps )
    {
        /* initialize CVector class */
        state.resize( NumberOfStates, 0 );
        ddtStateTemp.resize( NumberOfStates, 0 );
        statePredict.resize( NumberOfStates, 0 );
        ddtState.resize( NumberOfStates, 0 );
        m_numberOfIntegration = NumberOfIntegrationSteps;
    };
    virtual ~CDdtHeun() {};

    /* methods */
    CFloat getDtIntegration( void )
    {
        return m_dTintegrationStep;
    }
    /* variables */
    CFloatVector state ;
    CFloatVector ddtState;

protected:
    /* variables */
    // values for the Heun Algorithm
    CInt m_numberOfIntegration;
    CFloat m_dTintegrationStep;
    CFloatVector ddtStateTemp;
    CFloatVector statePredict;
    CInt m_stepCorr;
    CInt m_step;

    /* methods */
    virtual CFloatVector& ddt( CFloatVector& state ) = 0;           // abstract method, because the derivated class must overload this method
    inline void calcDdt( CFloat f_dT )
    {
        m_dTintegrationStep = f_dT / m_numberOfIntegration;
        for( m_step = 1; m_step <= m_numberOfIntegration; m_step++ )
        {
            /* Heun Algorithm                                                        */
            /*    ## -> y'(i) -> y(i+1) Prädiziert                                    */
            /*    ## -> n Korrekturschritte y(i+1) = y(i) + ( y'(i) + y'(i+1) ) f_dT/2  */
            ddtStateTemp = ddt( state );
            statePredict = state + ddtStateTemp * m_dTintegrationStep ;
            for( m_stepCorr = 1; m_stepCorr <= 3; m_stepCorr++ )
            {
                statePredict = state + ( ddtStateTemp + ddt( statePredict ) ) * ( m_dTintegrationStep / 2.0 ) ;
            }
            state = statePredict ;
        }
    };
};

/*!
********************************************************************************
@class CClass_ct
@ingroup framework
@brief Template base class of all claraSim artifacts

@author Robert Erhart, ett2si (18.10.2004 - 00:00:00)
@copyright (c) Robert Bosch GmbH 2023. All rights reserved.
********************************************************************************
@remark
- all equation of state classes inherit from CDdtHeun
- Heun Algorithm
   - y'(i) -> y(i+1) Prädiziert
   - n Korrekturschritte y(i+1) = y(i) + ( y'(i) + y'(i+1) ) f_dT/2
********************************************************************************
@param[in]  NumberOfStates             [CInt]   number of states
@param[in]  NumberOfIntegrationSteps   [CInt]   number of integration steps
********************************************************************************
*/
//Interface class of CClass_ct
class CClass_ctInterface
{
public:
    CClass_ctInterface() {};
    virtual ~CClass_ctInterface() {};

    virtual void process( CFloat f_dT, CFloat f_time ) = 0;
};

template < uint16_t NumberOfStates = 0, uint16_t NumberOfIntegrationSteps = 2, class IntegrationMethod = CDdtHeun >
class CClass_ct : public IntegrationMethod, public CClass_ctInterface
{
public:
    CClass_ct(): IntegrationMethod( NumberOfStates, NumberOfIntegrationSteps ) {}; //::std::cout << "NumberOfState = "<< NumberOfStates << ::std::endl;};
    virtual ~CClass_ct() {};

    virtual void init( void ) {};

    virtual void process( CFloat f_dT, CFloat f_time )
    {
        calcPre( f_dT, f_time );
        calc( f_dT, f_time );
        IntegrationMethod::calcDdt( f_dT );
        calcPost( f_dT, f_time );
    };

protected:
    /* methods */
    virtual void calcPre( CFloat f_dT, CFloat f_time ) {};                     // "virtual" because the derivated class can overload this methode
    virtual void calc( CFloat f_dT, CFloat f_time ) {};
    virtual CFloatVector& ddt( CFloatVector& state ) = 0;     // abstract method, because the derivated class must overload this methode
    virtual void calcPost( CFloat f_dT, CFloat f_time ) {};                    // "virtual" because the derivated class can overload this methode

    //virtual void calcDdt( CFloat f_dT );                      // abstract method, because the derivated class must overload this methode
};

//partial template specialization, without integration method
template<>
class CClass_ct<0> : public CClass_ctInterface
{
public:
    CClass_ct() {}; //::std::cout << "special NumberOfState = 0" << ::std::endl;};
    virtual ~CClass_ct() {};

    virtual void init( void ) {};

    virtual void process( CFloat f_dT, CFloat f_time )
    {
        calcPre( f_dT, f_time );
        calc( f_dT, f_time );
        calcPost( f_dT, f_time );
    };

protected:
    /* methods */
    virtual void calcPre( CFloat f_dT, CFloat f_time ) {};                   // "virtual" because the derivated class can overload this methode
    virtual void calc( CFloat f_dT, CFloat f_time ) = 0;                   // abstract method, because the derivated class must overload this methode
    virtual void calcPost( CFloat f_dT, CFloat f_time ) {};                  // "virtual" because the derivated class can overload this methode
};


#endif // CCLASS_CT_H
