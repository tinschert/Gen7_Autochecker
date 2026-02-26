/*!
********************************************************************************
@class CMessageOutput
@ingroup framework
@brief template class basis of output message classes

@author Robert Erhart, ett2si (10.09.2004; 30.09.2011)
@copyright (c) Robert Bosch GmbH 2023. All rights reserved.
********************************************************************************
@remark
*   the "get"-method for message vectors
*   could lead to a switch to secondary mode in realtime context
*   reason: copy constructor of valarray call malloc
********************************************************************************
@param[in] <C>  valid class or type
********************************************************************************
*/
#ifndef CMESSAGEOUTPUT_H
#define CMESSAGEOUTPUT_H
#include "CMessage.h"

class CMessageOutputInterface
{
public:
    CMessageOutputInterface() {};
    virtual ~CMessageOutputInterface() {};

    virtual void copyValueInit() = 0;
    virtual void copyValueWorkToCom( CFloat f_time ) = 0;
};

template<class Type, uint32_t HistoryBufferLength = 0> class CMessageOutput : public CMessage<Type, HistoryBufferLength>, public CMessageOutputInterface
{
public:
    CMessageOutput();
    CMessageOutput( const CMessageOutput& );
    virtual ~CMessageOutput();

    void copyValueInit();
    void init( const Type& f_init );
    void setInit( const Type f_value );
    void copyValueWorkToCom( CFloat f_time );
    Type get( long double* f_timestamp_p = NULL );
    IMessageValue<Type>* getLinkPointer( void );

    //Operator overload
    using CMessage<Type, HistoryBufferLength>::operator=; //operator= not automatically derived

private:
    using CMessage<Type, HistoryBufferLength>::m_init;
    using CMessage<Type, HistoryBufferLength>::m_work;
    using CMessage<Type, HistoryBufferLength>::m_comm;
    void set( const Type f_value ) {}; // prevent use of set method of IMessage class
};

//**************
//implementation
//**************
template<class Type, uint32_t HistoryBufferLength> CMessageOutput<Type, HistoryBufferLength>::CMessageOutput()
{}

template<class Type, uint32_t HistoryBufferLength> CMessageOutput<Type, HistoryBufferLength>::CMessageOutput( const CMessageOutput<Type, HistoryBufferLength>& f_class_r )
{
    this->setTypeInit( m_init, f_class_r.m_init );
    this->setTypeInit( m_work, f_class_r.m_work );
    this->setTypeInit( m_comm, f_class_r.m_comm );
}

template<class Type, uint32_t HistoryBufferLength> CMessageOutput<Type, HistoryBufferLength>::~CMessageOutput()
{}

template<class Type, uint32_t HistoryBufferLength> void CMessageOutput<Type, HistoryBufferLength>::copyValueInit()
{
    this->setTypeInit( m_work, m_init );
    this->setTypeInit( m_comm, m_init );
}

template<class Type, uint32_t HistoryBufferLength> void CMessageOutput<Type, HistoryBufferLength>::init( const Type& f_init )
{
    this->setTypeInit( m_init, f_init );
    this->setTypeInit( m_work, f_init );
    this->setTypeInit( m_comm, f_init );
}

template<class Type, uint32_t HistoryBufferLength> void CMessageOutput<Type, HistoryBufferLength>::setInit( const Type f_value )
{
    m_init.value = f_value;
    m_init.time = -1;
};

template<class Type, uint32_t HistoryBufferLength> void CMessageOutput<Type, HistoryBufferLength>::copyValueWorkToCom( CFloat f_time )
{
    m_comm.set( m_work.value, f_time );
    //m_comm.value = m_work.value;
    //m_comm.time = f_time;
}

template<class Type, uint32_t HistoryBufferLength> Type CMessageOutput<Type, HistoryBufferLength>::get( long double* f_timestamp_p )
{
    if( f_timestamp_p != NULL )
    {
        *f_timestamp_p = m_comm.time;
    }
    return m_comm.value;
}

template<class Type, uint32_t HistoryBufferLength> IMessageValue<Type>* CMessageOutput<Type, HistoryBufferLength>::getLinkPointer( void )
{
    return &m_comm;
}

//template<typename Type> void CMessageOutput<Type, HistoryBufferLength>::buildCaliMeasVectors( ::std::string f_label ) {
//
//}

#endif // CMESSAGEOUTPUT_H
