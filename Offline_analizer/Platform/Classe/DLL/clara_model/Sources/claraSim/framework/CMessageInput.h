/*!
********************************************************************************
@class CMessageInput
@ingroup framework
@brief template class basis of input message classes

@author Robert Erhart, ett2si (10.09.2004; 30.09.2011)
@copyright (c) Robert Bosch GmbH 2023. All rights reserved.
********************************************************************************
@remark
********************************************************************************
@param[in] <C>  valid class or type
********************************************************************************
*/
#ifndef CMESSAGEINPUT_H
#define CMESSAGEINPUT_H
#include "CMessage.h"
#include "CMessageOutput.h"
#include "CMessageParameter.h"
#include "CModuleVector.h"
#include <vector>

class CMessageInputInterface
{
public:
    CMessageInputInterface() {};
    virtual ~CMessageInputInterface() {};

    virtual void copyValueComToWork( CFloat f_dt, CFloat f_time ) = 0;
};

template < class Type, class ModuleClass = Type, class ModuleVector = Type > class CMessageInput : public CMessage<Type>, public CMessageInputInterface
{
public:
    CMessageInput()
    {
        m_comm_p = &m_comm;
    };

    CMessageInput( const CMessageInput& f_class_r )
    {
        //this->setTypeInit( m_initValue, f_class_r.m_initValue );
        this->setTypeInit( m_work, f_class_r.m_work );
        this->setTypeInit( m_comm, f_class_r.m_comm );
        if( f_class_r.m_comm_p == &( f_class_r.m_comm ) )
        {
            m_comm_p = &m_comm;
        }
        else
        {
            m_comm_p = f_class_r.m_comm_p;
        }
    };

    virtual ~CMessageInput()
    {};

    void link( IMessage<Type>& f_class_r )
    {
        m_comm_p = f_class_r.getLinkPointer();
        this->setTypeInit( m_work, *m_comm_p );
    };

    void setInit( const Type f_value )
    {
        ::std::cerr << "ERROR <CMessageInput:setInit>: no setInit Function valid" << ::std::endl;
    }

    void init( const Type& f_init )
    {
        //this->setTypeInit(m_initValue, f_init); //ToDo m_initValue not used
        this->setTypeInit( m_work, f_init );
        this->setTypeInit( m_comm, f_init );
    }

    Type get( long double* f_timestamp_p = NULL )
    {
        if( f_timestamp_p != NULL )
        {
            *f_timestamp_p = m_comm.time;
        }
        return m_comm_p->value;
    };

    void copyValueComToWork( CFloat f_dT, CFloat f_time )
    {
        m_work.value = m_comm_p->value;
    };

    IMessageValue<Type>* getLinkPointer( void )
    {
        return m_comm_p;
    };

    //Operator overload
    using CMessage<Type>::operator=; //operator= not automatically derived

private:
    //using CMessage<Type>::m_initValue;
    using CMessage<Type>::m_work;
    using CMessage<Type>::m_comm;
    IMessageValue<Type>* m_comm_p;
    void set( const Type f_value ) {}; // prevent use of set method
};


//specialization for CModuleVector
template<class Type, class ModuleClass>
class CMessageInput< Type, ModuleClass, CModuleVector<ModuleClass> > : public CMessageInputInterface
{
public:
    CMessageInput()
    {
        m_class_p = nullptr;
    };

    virtual ~CMessageInput()
    {};

    template<typename MESSAGETYPE> void link( CModuleVector<ModuleClass>& f_class_r, MESSAGETYPE ModuleClass::*f_member_p )
    {
        m_class_p = &f_class_r;
        m_message.clear();
        m_message.resize( f_class_r.size(), CMessageInput<Type>() ); //Type( (( *m_class_p )[0].*f_member_p ).size(), 0) );
        for( unsigned int index = 0; index < m_class_p->size(); index++ )
        {
            m_message[index].link( ( *m_class_p )[index].*f_member_p );
        }
    };

    void init()
    {
        m_message.clear();
    }

    void copyValueComToWork( CFloat f_dT, CFloat f_time )
    {
        for( unsigned int index = 0; index < m_class_p->size(); index++ )
        {
            m_message[index].copyValueComToWork( f_dT, f_time );
        }
    };

    IMessageValue< Type >* getLinkPointer( void )
    {
        throw;
        return nullptr;
    };

    CMessageInput<Type>& operator[]( size_t f_index )
    {
        return m_message[f_index];
    };

    size_t size()
    {
        return m_message.size();
    }

    /* Operator overload */
    operator Type() const
    {
        return static_cast<Type>( m_message );
    };  // cast operator

    /* Operator overload */
    operator Type& () const
    {
        return static_cast<Type&>( m_message );
    };  // cast operator


private:
    CMessageInput( const CMessageInput& f_class_r )
    {
        //disallow copy
        m_class_p = nullptr;  //only for removing gcc 4.7 warnings
    };

    ::std::vector< CMessageInput<Type> > m_message;
    CModuleVector<ModuleClass>* m_class_p;
    void set( const Type f_value ) {}; // prevent use of set method
};

#endif // CMESSAGEINPUT_H
