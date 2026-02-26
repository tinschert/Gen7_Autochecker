/*!
********************************************************************************
@class CMessageParameter
@ingroup framework
@brief template class basis of parameter message classes

@author Robert Erhart, ett2si (10.09.2004; 30.09.2011)
@copyright (c) Robert Bosch GmbH 2023. All rights reserved.
********************************************************************************
@remark
********************************************************************************
@param[in] <C>  valid class or type
********************************************************************************
*/
#ifndef CMESSAGEPARAMETER_H
#define CMESSAGEPARAMETER_H
#include "CMessage.h"
//#include "CFloat.h"

class CMessageParameterInterface
{
public:
    CMessageParameterInterface() {};
    virtual ~CMessageParameterInterface() {};

    virtual void copyValueInit() = 0;
    virtual void copyValueWorkToCom( CFloat f_time ) = 0;
    virtual void copyValueComToWork( CFloat f_dt, CFloat f_time ) = 0;
};

template<typename Type, uint32_t HistoryBufferLength = 0> class CMessageParameter : public CMessage<Type, HistoryBufferLength>, public CMessageParameterInterface
{
public:
    CMessageParameter();
    CMessageParameter( const CMessageParameter& );
    virtual ~CMessageParameter();

    void copyValueInit();
    void init( const Type& f_value );
    void setInit( const Type f_value );
    void copyValueWorkToCom( CFloat f_time );
    void set( const Type );
    void setRampStartValue( const Type f_start );
    void setRampTargetValue( const Type f_target );
    void setRampRateValue( const Type f_rate );
    void startRampCalc( CBool f_startCalcRamp );

    void calcRamp( CFloat f_dT, CFloat f_time );
    long double getSetTimeStamp( void );
    void setTime( CFloat f_time );
    void setTimeValue( const Type );
    Type get( long double* f_timestamp_p = NULL );
    void copyValueComToWork( CFloat f_dt, CFloat f_time );
    IMessageValue<Type>* getLinkPointer( void );
    //virtual void buildCaliMeasVectors( ::std::string f_label );

    //Operator overload
    using CMessage<Type, HistoryBufferLength>::operator=; //operator= not automatically derived

private:
    using CMessage<Type, HistoryBufferLength>::m_init;
    using CMessage<Type, HistoryBufferLength>::m_work;
    using CMessage<Type, HistoryBufferLength>::m_comm;
    Type m_commInput;
    Type m_timeValue;
    Type m_start;
    Type m_target;
    CBool m_startCalcRamp;
    CFloat m_rate;
    CFloat m_timeModification;
    CFloat m_dt;
    CBool m_commInputChanged;
};

//**************
//implementation
//**************
template<typename Type, uint32_t HistoryBufferLength> CMessageParameter<Type, HistoryBufferLength>::CMessageParameter()
{
    m_timeModification = 0.0;
    m_dt = 0.0;
    m_commInputChanged  = false;
    m_startCalcRamp = false;
}

template<typename Type, uint32_t HistoryBufferLength> CMessageParameter<Type, HistoryBufferLength>::CMessageParameter( const CMessageParameter<Type, HistoryBufferLength>& f_class_r )
{
    this->setTypeInit( m_init, f_class_r.m_init );
    this->setTypeInit( m_work, f_class_r.m_work );
    this->setTypeInit( m_comm, f_class_r.m_comm );
    this->setTypeInit( m_commInput, f_class_r.m_commInput );
    this->setTypeInit( m_timeValue, f_class_r.m_timeValue );
    this->setTypeInit( m_start, f_class_r.m_start );
    this->setTypeInit( m_target, f_class_r.m_target );
    m_timeModification = f_class_r.m_timeModification;
    m_dt = f_class_r.m_dt;
    m_commInputChanged = f_class_r.m_commInputChanged;
}

template<typename Type, uint32_t HistoryBufferLength> CMessageParameter<Type, HistoryBufferLength>::~CMessageParameter()
{}

template<typename Type, uint32_t HistoryBufferLength> void CMessageParameter<Type, HistoryBufferLength>::copyValueInit()
{
    this->setTypeInit( m_work, m_init );
    this->setTypeInit( m_comm, m_init );
    this->setTypeInit( m_commInput, m_init );
    this->setTypeInit( m_timeValue, m_init );
    m_timeModification = 0.0;
}

template<typename Type, uint32_t HistoryBufferLength> void CMessageParameter<Type, HistoryBufferLength>::init( const Type& f_init )
{
    this->setTypeInit( m_init, f_init );
    this->setTypeInit( m_work, f_init );
    this->setTypeInit( m_comm, f_init );
    this->setTypeInit( m_commInput, f_init );
    this->setTypeInit( m_timeValue, f_init );
    m_timeModification = 0.0;
}

template<typename Type, uint32_t HistoryBufferLength> void CMessageParameter<Type, HistoryBufferLength>::copyValueWorkToCom( CFloat f_time )
{
    m_comm.set( m_work.value, f_time );
    //m_comm.value = m_work.value;
    //m_comm.time = f_time;
}

template<typename Type, uint32_t HistoryBufferLength> void CMessageParameter<Type, HistoryBufferLength>::set( const Type f_value )
{
    m_commInput = f_value;
    m_commInputChanged = true;
}
template<typename Type, uint32_t HistoryBufferLength> void CMessageParameter<Type, HistoryBufferLength>::setRampStartValue( const Type f_start )
{
    m_start = f_start;
    ::std::cout << "m_start " << m_start << ::std::endl;
}
template<typename Type, uint32_t HistoryBufferLength> void CMessageParameter<Type, HistoryBufferLength>::setRampTargetValue( const Type f_target )
{
    m_target = f_target;
    ::std::cout << "Ramp m_target " << m_target << ::std::endl;
}
template<typename Type, uint32_t HistoryBufferLength> void CMessageParameter<Type, HistoryBufferLength>::setRampRateValue( const Type f_rate )
{
    m_rate = f_rate;
    ::std::cout << "Ramp m_rate " << m_rate << ::std::endl;
}

template<typename Type, uint32_t HistoryBufferLength> void CMessageParameter<Type, HistoryBufferLength>::startRampCalc( CBool f_startCalcRamp )
{
    if( m_target  !=  m_start )
    {
        m_startCalcRamp = f_startCalcRamp;
    }
}
template<typename Type, uint32_t HistoryBufferLength> void CMessageParameter<Type, HistoryBufferLength>::calcRamp( CFloat f_dT, CFloat f_time )
{
    if( m_startCalcRamp )
    {
        if( m_start < m_target )
        {
            if( ( m_target - m_start ) > ( m_rate * f_dT ) )
            {
                m_start =  m_start + m_rate * f_dT;
                this->set( m_start );
            }
            else
            {
                this->set( m_target );
            }
        }
        else if( m_start > m_target )
        {
            if( ( m_start - m_target ) > ( m_rate * f_dT ) )
            {
                m_start = m_start - m_rate * f_dT;
                this->set( m_start );
            }
            else
            {
                this->set( m_target );
            }
        }
    }
}
template<typename Type, uint32_t HistoryBufferLength> long double CMessageParameter<Type, HistoryBufferLength>::getSetTimeStamp( void )
{
    return m_work.time;
}

template<typename Type, uint32_t HistoryBufferLength> void CMessageParameter<Type, HistoryBufferLength>::setInit( const Type f_value )
{
    m_init.value = f_value;
};

template<typename Type, uint32_t HistoryBufferLength> void CMessageParameter<Type, HistoryBufferLength>::setTime( CFloat f_time )
{
    m_timeModification = f_time;
    m_commInputChanged = true;
}

template<typename Type, uint32_t HistoryBufferLength> void CMessageParameter<Type, HistoryBufferLength>::setTimeValue( const Type f_value )
{
    m_timeValue = f_value;
}

template<typename Type, uint32_t HistoryBufferLength> Type CMessageParameter<Type, HistoryBufferLength>::get( long double* f_timestamp_p )
{
    if( f_timestamp_p != NULL )
    {
        *f_timestamp_p = m_comm.time;
    }
    return m_comm.value;
}

template<typename Type, uint32_t HistoryBufferLength> void CMessageParameter<Type, HistoryBufferLength>::copyValueComToWork( CFloat f_dt, CFloat f_time )
{
    if( m_timeModification <= 0.0 )
    {
        m_work.value = m_commInput;
    }
    else
    {
        m_work.value = m_timeValue;
        m_timeModification = m_timeModification - f_dt;
    }

    if( m_commInputChanged == true )
    {
        m_work.time = f_time;
        m_commInputChanged = false;
    }
}

template<typename Type, uint32_t HistoryBufferLength> IMessageValue<Type>* CMessageParameter<Type, HistoryBufferLength>::getLinkPointer( void )
{
    return &m_comm;
}

//template<typename Type, uint32_t HistoryBufferLength> void CMessageParameter<Type, HistoryBufferLength>::buildCaliMeasVectors( ::std::string f_label ) {
//
//}

#endif // CMESSAGEPARAMETER_H
