/*!
********************************************************************************
@class CMessage
@ingroup framework
@brief template class basis of all message classes

@author Robert Erhart, ett2si (10.09.2004; 30.09.2011, 03.02.2015)
@copyright (c) Robert Bosch GmbH 2023. All rights reserved.
********************************************************************************
@remark
********************************************************************************
@param[in] <C>  valid class or type
********************************************************************************
*/
#ifndef CMESSAGE_H
#define CMESSAGE_H

#include <stdint.h>
#include "CFloat.h"
#include "CInt.h"
#include "CBool.h"
#include "CFloatVector.h"
#include "CBoolVector.h"
#include "CIntVector.h"
#include <valarray>
#include <iostream>
#include <string>


/*!
 * ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 * @class IMessageValue template
 * ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 */
template<typename Type> class IMessageValue
{
public:
    IMessageValue()
    {
        value = Type();
        time = -1;
    }

    IMessageValue( Type& f_value, CFloat f_time )
    {
        value = f_value;
        time = f_time;
    }

    IMessageValue( IMessageValue<Type>& f_message )
    {
        value = f_message.value;
        time = f_message.time;
    }

    virtual ~IMessageValue() {};

public:
    Type& getValue()
    {
        return value;
    };

    CFloat getTime()
    {
        return time;
    };

public: //ToDo switch to private to avoid misuse of output message content in foreign Modules: 1)refactoring setTypeInit to initWork and initCom
    Type value;
    CFloat time;
};

/*!
 * ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 * @class CMessageValue template + specialized type for CMessageValue without HistoryBuffer
 * ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 * @remark
 * The access to the buffer is multiprocess runtime save, but no read buffer consistent can be guaranteed.
 * The user must care about, that no new values are written in the buffer during a read process
 * ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 */
template<typename Type, uint32_t HistoryBufferLength = 0> class CMessageValue : public IMessageValue<Type>
{
public:
    CMessageValue()
    {
        value = 0;
        time = -1;
        clearBuffer();
    };

    CMessageValue( Type& f_value )
    {
        value = f_value;
        time = -1;
        clearBuffer();
    };

    virtual ~CMessageValue() {};

    void clearBuffer()
    {
        m_head = 0;
        m_tail = 0;
        m_contentSize = 0;
        for( uint32_t index = 0; index < HistoryBufferLength; index++ )
        {
            m_valueHist[index] = 0;
            m_timeHist[index] = -1;
        }
    };

    void set( const Type& f_value, CFloat f_time )
    {
        value = f_value;
        time  = f_time;
        append();
    }

    void set( const IMessageValue<Type>& f_value )
    {
        value = f_value.value;
        time  = f_value.time;
        append();
    }

    CMessageValue& operator=( const CMessageValue& f_other )
    {
        value = f_other.value;
        time  = f_other.time;
        //append();
        return *this;
    };

    CMessageValue& operator=( const IMessageValue<Type>& f_other )
    {
        value = f_other.value;
        time  = f_other.time;
        //append();
        return *this;
    };

    IMessageValue<Type> operator[]( int64_t f_index )
    {
        uint32_t l_index;
        if( f_index >= 0 ) //0 means oldest value
        {
            l_index = ( m_head + f_index ) % HistoryBufferLength;
        }
        else                 //-1: actual value; -2 k1 value, etc.
        {
            l_index = ( m_tail + f_index + HistoryBufferLength ) % HistoryBufferLength;
        }
        IMessageValue<Type> l_returnValue( m_valueHist[l_index], m_timeHist[l_index] );
        return l_returnValue;
    };

private:
    CMessageValue( const CMessageValue& );               // Prevent copy-construction

    void incHead()
    {
        m_contentSize--;
        m_head++;
        if( m_head == HistoryBufferLength )
        {
            m_head = 0;
        }
    };

    void incTail()
    {
        m_contentSize++;
        m_tail++;
        if( m_tail == HistoryBufferLength )
        {
            m_tail = 0;
        }
    };

    void append()
    {
        m_valueHist[m_tail] = value;
        m_timeHist[m_tail] = time;
        if( m_contentSize == HistoryBufferLength )
        {
            incHead();
        }
        incTail();
    };

public:
    using IMessageValue<Type>::value;
    using IMessageValue<Type>::time;

private:
    Type m_valueHist[HistoryBufferLength];
    CFloat m_timeHist[HistoryBufferLength];
    uint32_t m_head;
    uint32_t m_tail;
    uint32_t m_contentSize;
};

//specialized type for CMessageValue without HistoryBuffer
template<typename Type> class CMessageValue<Type, 0> : public IMessageValue<Type>
{
public:
    CMessageValue()
    {
        value = Type();
        time = -1;
    }

    CMessageValue( Type f_value )
    {
        value = f_value;
        time = -1;
    }

    virtual ~CMessageValue() {};

//    void clearBuffer()
//    {
//        //no historic buffer
//    };

    void set( const Type& f_value, CFloat f_time )
    {
        value = f_value;
        time  = f_time;
    }

    void set( const IMessageValue<Type>& f_value )
    {
        value = f_value.getValue();
        time  = f_value.getTime();
    }

    CMessageValue& operator=( const CMessageValue& f_other )
    {
        value = f_other.value;
        time  = f_other.time;
        return *this;
    };

    CMessageValue& operator=( const IMessageValue<Type>& f_other )
    {
        value = f_other.getValue();
        time  = f_other.getTime();
        return *this;
    };

public:
    using IMessageValue<Type>::value;
    using IMessageValue<Type>::time;

private:
    CMessageValue( const CMessageValue& );               // Prevent copy-construction
};


/*!
 * ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 * @class IMessage template for messageInterface
 * ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 * @remark
 * ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 */

class IMessageBase
{
public:
    IMessageBase():
        m_messageDescription()
    {};

    virtual ~IMessageBase() {};

    virtual size_t size() = 0;

    void setMessageDescription( const ::std::string& f_description )
    {
        m_messageDescription = f_description;
    };
    const ::std::string& getMessageDescription( void )
    {
        return m_messageDescription;
    };

private:
    ::std::string m_messageDescription;
};

template<class Type> class IMessage : public IMessageBase
{
public:
    IMessage() {};

    virtual ~IMessage() {};

    virtual IMessageValue<Type>* getLinkPointer( void ) = 0;
    virtual Type get( long double* f_timestamp_p = NULL ) = 0;
    virtual void setInit( const Type f_value ) = 0;
    virtual void set( const Type f_value ) = 0; //only valid for CMessageParameter; define in other messages as private
};


/*!
 * ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 * @class CMessageVar template for claraSim base types CInt, CBool, CFloat + specialization without buffer
 * ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 * @remark
 * ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 */
template<typename Type, uint32_t HistoryBufferLength = 0> class CMessageVar : public IMessage<Type>
{
public:
    CMessageVar()
    {
        m_init = 0;
        m_work = 0;
        m_sampleRateHistBuffer = 1;
        m_sampleRateHistBufferInit = 1;
    };

    virtual ~CMessageVar() {};

    virtual size_t size()
    {
        return 1;
    };

    virtual void init( const Type& f_value ) = 0;

    /*!
     * clear the history com buffer
     * @param[in] dummy [bool] dummy variable for ClaraServer
     */
    void clearHistBuffer( bool dummy = 0 )
    {
        m_comm.clearBuffer();
    };

    /*!
     * set the output sample rate of the history com buffer
     * @param[in] f_sampleRate [uint32_t] sample rate (must be >0!)
     * @remark: if used in claraServer interface, this must be called in the singleCali block (dynamic memory allocation!!)
     */
    void setHistComSampleRateInit( uint32_t f_sampleRate )
    {
        if( f_sampleRate > 0 and f_sampleRate < HistoryBufferLength )
        {
            m_sampleRateHistBufferInit = f_sampleRate;
        }
        else
        {
            ::std::cerr << "ERROR <CMessage:setHistComSampleRate>: invalid sample rate <=0 or >=HistoryBufferLength" << ::std::endl;
        }
    }

    ::std::valarray<Type> getHistComValues( long double* f_timestamp_p = nullptr )
    {
        uint32_t l_bufferSize = static_cast<uint32_t>( HistoryBufferLength / m_sampleRateHistBuffer );
        ::std::valarray<Type> l_returnValue( l_bufferSize );
        for( uint32_t l_index = 0; l_index < l_bufferSize; l_index++ )
        {
            //IMessageValue<Type> t_messageValue(m_comm[l_index]);
            l_returnValue[l_index] = m_comm[l_index * m_sampleRateHistBuffer].value;
            if( f_timestamp_p != nullptr )
            {
                f_timestamp_p[l_index] = m_comm[l_index * m_sampleRateHistBuffer].time;
            }
        }
        return l_returnValue;
    };

//    ::std::valarray<CFloat> getHistComTime()
//    {
//        uint32_t l_bufferSize = static_cast<uint32_t>( HistoryBufferLength / m_sampleRateHistBuffer );
//        ::std::valarray<CFloat> l_returnValue( l_bufferSize );
//        for( uint32_t l_index = 0; l_index < l_bufferSize; l_index++ )
//        {
//            //IMessageValue<CFloat> t_messageValue(m_comm[l_index]);
//            l_returnValue[l_index] = m_comm[l_index * m_sampleRateHistBuffer].time;
//        }
//        return l_returnValue;
//    };

    /* Operator overload */
    operator Type() const
    {
        return static_cast<Type>( m_work.value );
    };  // cast operator

    CMessageVar& operator=( const Type& f_other )
    {
        m_work = f_other;
        return *this;
    };

    CMessageVar& operator=( const CMessageVar<Type>& f_other )
    {
        m_work = f_other.m_work;
        return *this;
    };
    //ToDo //friend class CModuleInterface

protected:
    CMessageValue<Type> m_init;
    CMessageValue<Type> m_work;
    CMessageValue<Type, HistoryBufferLength> m_comm;

    inline void setTypeInit( CMessageValue<Type, HistoryBufferLength>& f_value, const Type& f_init )
    {
        //::std::cout << "Et99: setTypeInit1:" << ::std::endl;
        f_value.value = f_init;
        f_value.time = -1;
        f_value.clearBuffer();
        m_sampleRateHistBuffer = m_sampleRateHistBufferInit;
    }

    inline void setTypeInit( CMessageValue<Type, HistoryBufferLength>& f_value, const IMessageValue<Type>& f_init )
    {
        //::std::cout << "Et99: setTypeInit2:" << ::std::endl;
        f_value.value = f_init.value;
        f_value.time = -1;
        f_value.clearBuffer();
        m_sampleRateHistBuffer = m_sampleRateHistBufferInit;
    }

    inline void setTypeInit( Type& f_value, const Type& f_init )
    {
        f_value = f_init;
    }

    inline void setTypeInit( IMessageValue<Type>& f_value, const Type& f_init )
    {
        f_value.value = f_init;
        f_value.time = -1;
    }

    inline void setTypeInit( Type& f_value, const IMessageValue<Type>& f_init )
    {
        f_value = f_init.value;
    }

    inline void setTypeInit( IMessageValue<Type>& f_value, const IMessageValue<Type>& f_init )
    {
        f_value.value = f_init.value;
        f_value.time = -1;
    }

private:
    CMessageVar( const CMessageVar<Type>& );

    uint32_t m_sampleRateHistBuffer;
    uint32_t m_sampleRateHistBufferInit;
};

//specialized type for CMessageVar without HistoryBuffer
template<typename Type> class CMessageVar<Type, 0> : public IMessage<Type>
{
public:
    CMessageVar()
    {
        m_init = 0;
        m_work = 0;
    };

    virtual ~CMessageVar() {};

    virtual size_t size()
    {
        return 1;
    };

    virtual void init( const Type& f_value ) = 0;

    /* Operator overload */
    operator Type() const
    {
        return static_cast<Type>( m_work.value );
    };  // cast operator

    operator Type& ()
    {
        return static_cast<Type&>( m_work.value );
    };  // cast operator


    CMessageVar& operator=( const Type& f_other )
    {
        m_work = f_other;
        return *this;
    };

    CMessageVar& operator=( const CMessageVar<Type>& f_other )
    {
        m_work = f_other.m_work;
        return *this;
    };
    //ToDo //friend class CModuleInterface

protected:
    CMessageValue<Type> m_init;
    CMessageValue<Type> m_work;
    CMessageValue<Type> m_comm;

    inline void setTypeInit( Type& f_value, const Type& f_init )
    {
        f_value = f_init;
    }

    inline void setTypeInit( IMessageValue<Type>& f_value, const Type& f_init )
    {
        f_value.value = f_init;
        f_value.time = -1;
    }

    inline void setTypeInit( Type& f_value, const IMessageValue<Type>& f_init )
    {
        f_value = f_init.value;
    }

    inline void setTypeInit( IMessageValue<Type>& f_value, const IMessageValue<Type>& f_init )
    {
        f_value.value = f_init.value;
        f_value.time = -1;
    }

private:
    CMessageVar( const CMessageVar<Type>& );

};

/*!
 * ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 * @class CMessageVector template for claraSim vector types CIntVector, CBoolVector, CFloatVector, CFloatVectorXYZ
 */
//template<class Type> class CMessageVector : public IMessage< ::std::valarray<Type> >
template<class TypeVector, typename TypeValue> class CMessageVector : public IMessage< TypeVector >
{
public:
    CMessageVector() {};

    virtual ~CMessageVector() {};

    virtual size_t size()
    {
        return m_work.value.size();
    };

    virtual void init( const TypeVector& f_value ) = 0;

    virtual void resizeInit( const unsigned long f_numberOfElements ) //only for parameter for ClaraServer
    {
        /* resize only m_init.value                                 */
        /* use methode init() to set m_comm and m_work to new size, */
        /* until then methode size() will return OLD size           */
        m_init.value.resize( f_numberOfElements );
    }

    /* Operator overload */
    operator TypeVector() const
    {
        return static_cast< TypeVector >( m_work.value );
    };  // cast operator

    operator TypeVector& ()
    {
        return static_cast< TypeVector& >( m_work.value );
    };  // cast operator


    CMessageVector& operator=( const TypeVector& f_other )
    {
        m_work = f_other;
        return *this;
    };

    CMessageVector& operator=( const CMessageVector<TypeVector, TypeValue>& f_other )
    {
        m_work = f_other.m_work;
        return *this;
    };

    /* Unary arithmetic operator overloads are defined here.
     * This allows operations between same type MessageVectors (e.g. CFloatVector & CFloatVector)
     * and acts element-wise. Exception handling done by 'valarray' arithmetics.
     */
    CMessageVector& operator+=( const TypeVector& f_other )
    {
        m_work.value += f_other;
        return *this;
    };

    CMessageVector& operator+=( const CMessageVector<TypeVector, TypeValue>& f_other )
    {
        m_work.value += f_other.m_work.value;
        return *this;
    };

    friend TypeVector operator+ ( TypeVector& f_left,
                                  TypeVector& f_right )
    {
        TypeVector l_sum;
        l_sum = f_left + f_right;
        return l_sum;
    };

    CMessageVector& operator-=( const TypeVector& f_other )
    {
        m_work.value -= f_other;
        return *this;
    };

    CMessageVector& operator-=( const CMessageVector<TypeVector, TypeValue>& f_other )
    {
        m_work.value -= f_other.m_work.value;
        return *this;
    };

    friend TypeVector operator- ( TypeVector& f_left,
                                  TypeVector& f_right )
    {
        TypeVector l_diff;
        l_diff = f_left - f_right;
        return l_diff;
    };


    CMessageVector& operator*=( const TypeVector& f_other )
    {
        m_work.value *= f_other;
        return *this;
    };

    CMessageVector& operator*=( const CMessageVector<TypeVector, TypeValue>& f_other )
    {
        m_work.value *= f_other.m_work.value;
        return *this;
    };


    friend TypeVector operator* ( TypeVector& f_left,
                                  TypeVector& f_right )
    {
        TypeVector l_prod;
        l_prod = f_left * f_right;
        return l_prod;
    };

    CMessageVector& operator/=( const TypeVector& f_other )
    {
        m_work.value /= f_other;
        return *this;
    };

    CMessageVector& operator/=( const CMessageVector<TypeVector, TypeValue>& f_other )
    {
        m_work.value /= f_other.m_work.value;
        return *this;
    };

    friend TypeVector operator/ ( TypeVector& f_left,
                                  TypeVector& f_right )
    {
        TypeVector l_div;
        l_div = f_left / f_right;
        return l_div;
    };


    TypeValue& operator[]( size_t f_index )
    {
        return m_work.value[f_index];
    };

protected:
    CMessageValue< TypeVector > m_init;
    CMessageValue< TypeVector > m_work;
    CMessageValue< TypeVector > m_comm;

    inline void setTypeInit( TypeVector& f_value, const TypeVector& f_init )
    {
        f_value.resize( f_init.size() ); //potentielles problem
        f_value = f_init;
    }

    inline void setTypeInit( IMessageValue< TypeVector >& f_value, const TypeVector& f_init )
    {
        f_value.value.resize( f_init.size() ); //potentielles problem
        f_value.value = f_init;
        f_value.time = -1;
    }

    inline void setTypeInit( TypeVector& f_value, const IMessageValue< TypeVector >& f_init )
    {
        f_value.resize( f_init.value.size() ); //potentielles problem
        f_value = f_init.value;
    }

    inline void setTypeInit( IMessageValue< TypeVector >& f_value, const IMessageValue< TypeVector >& f_init )
    {
        f_value.value.resize( f_init.value.size() ); //potentielles problem
        f_value.value = f_init.value;
        f_value.time = -1;
    }

private:
    CMessageVector( const CMessageVector<TypeVector, TypeValue>& );
};

/*!
********************************************************************************
@class CMessage
@brief template base class  of all INPUT-, OUTPUT- and PARAMETERmessage classes
//only allow defined/specialized types => constructor private!!!
 *
 */
template<class Type, uint32_t HistoryBufferLength = 0> class CMessage
{
private:
    CMessage() {};
    virtual ~CMessage() {};
};

template<uint32_t HistoryBufferLength> class CMessage<CInt, HistoryBufferLength> : public CMessageVar<CInt, HistoryBufferLength>
{
public:
    CMessage() {};
    virtual ~CMessage() {};

    //Operator overload
    using CMessageVar<CInt, HistoryBufferLength>::operator=; //operator= not automatically derived

private:
    CMessage( const CMessage<CInt>& );
};

template<uint32_t HistoryBufferLength> class CMessage<CBool, HistoryBufferLength> : public CMessageVar<CBool, HistoryBufferLength>
{
public:
    CMessage() {};
    virtual ~CMessage() {};

    //Operator overload
    using CMessageVar<CBool, HistoryBufferLength>::operator=; //operator= not automatically derived

private:
    CMessage( const CMessage<CBool>& );
};


template<uint32_t HistoryBufferLength> class CMessage<CFloat, HistoryBufferLength> : public CMessageVar<CFloat, HistoryBufferLength>
{
public:
    CMessage() {};
    virtual ~CMessage() {};

    //Operator overload
    using CMessageVar<CFloat, HistoryBufferLength>::operator=; //operator= not automatically derived

private:
    CMessage( const CMessage<CFloat>& );
};


template<> class CMessage<CIntVector, 0> : public CMessageVector<CIntVector, CInt>
{
public:
    CMessage() {};
    virtual ~CMessage() {};

    //Operator overload
    using CMessageVector<CIntVector, CInt>::operator=; //operator= not automatically derived

private:
    CMessage( const CMessage<CIntVector>& );
};

template<> class CMessage<CBoolVector, 0> : public CMessageVector<CBoolVector, CBool>
{
public:
    CMessage() {};
    virtual ~CMessage() {};

    //Operator overload
    using CMessageVector<CBoolVector, CBool>::operator=; //operator= not automatically derived

private:
    CMessage( const CMessage<CBoolVector>& );
};

template<> class CMessage<CFloatVector, 0> : public CMessageVector<CFloatVector, CFloat>
{
public:
    CMessage() {};
    virtual ~CMessage() {};

    //Operator overload
    using CMessageVector<CFloatVector, CFloat>::operator=; //operator= not automatically derived

private:
    CMessage( const CMessage<CFloatVector>& );
};

template<> class CMessage<CFloatVectorXYZ, 0> : public CMessageVector<CFloatVectorXYZ, CFloat>
{
public:
    CMessage() {};
    virtual ~CMessage() {};

    //Operator overload
    using CMessageVector<CFloatVectorXYZ, CFloat>::operator=; //operator= not automatically derived

    CFloat X()
    {
        return m_work.value[0];
    };

    CFloat Y()
    {
        return m_work.value[1];
    };

    CFloat Z()
    {
        return m_work.value[2];
    };

    CFloat X( CFloat x )
    {
        m_work.value[0] = x;
        return m_work.value[0];
    };

    CFloat Y( CFloat y )
    {
        m_work.value[1] = y;
        return m_work.value[1];
    };

    CFloat Z( CFloat z )
    {
        m_work.value[2] = z;
        return m_work.value[2];
    };

    CFloatVectorXYZ& XYZ( CFloat x, CFloat y, CFloat z )
    {
        m_work.value = {x, y, z};
        return m_work.value;
    }

private:
    CMessage( const CMessage<CFloatVectorXYZ>& );
};


#endif // CMESSAGE_H
