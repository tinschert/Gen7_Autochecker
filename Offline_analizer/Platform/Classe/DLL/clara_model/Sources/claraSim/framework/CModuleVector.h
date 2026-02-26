/*!
********************************************************************************
@class CModuleVector
@ingroup framework
@brief Basis class for implementation for all multitask safe modules

@author Robert Erhart, ett2si (06.10.2011)
@copyright (c) Robert Bosch GmbH 2023. All rights reserved.
********************************************************************************
@remark
********************************************************************************
*/
#ifndef CModuleVector_CT_H
#define CModuleVector_CT_H

//#include "CModule.h"

#include <vector>
#include "CFloat.h"

template < class T>
class CModuleVector// : CModuleInterface
{
public:
    CModuleVector( size_t f_numberOfElements, void* f_pointer_p )
    {
        m_vector.clear();
        for( unsigned int index = 0; index < f_numberOfElements; index++ )
        {
            m_vector.push_back( new T( f_pointer_p ) );
        }
    };

    CModuleVector( size_t f_numberOfElements )
    {
        m_vector.clear();
        for( unsigned int index = 0; index < f_numberOfElements; index++ )
        {
            m_vector.push_back( new T() );
        }
    };

    virtual ~CModuleVector()
    {
        clear();
    };

    void clear()
    {
        for( size_t index = 0; index < m_vector.size(); index++ )
        {
            delete m_vector[index];
        }
        m_vector.clear();
    };

    void process( CFloat f_dT, CFloat f_time )
    {
        for( size_t index = 0; index < m_vector.size(); index++ )
        {
            m_vector[index]->process( f_dT, f_time );
        }
    }

    T& at( size_t f_index )
    {
        if( f_index >= m_vector.size() )
        {
            //ToDO raise exception
            exit( 0 );
        }
        return *m_vector[f_index];
    }

    //! Support python-type negative indexing: [+1] yields second element, [-1] yields last element.
    //  Caution: No vector size / index boundary handling included.
    T& operator[]( int64_t f_index )
    {
        int64_t l_index;
        if( f_index >= 0 ) // and (f_index < m_vector.size()))
        {
            l_index = f_index;
        }
        else if( f_index < 0 ) // and f_index > -m_vector.size() )
        {
            l_index = m_vector.size() + f_index;
        }

        return *m_vector[l_index];
    };




//only static modulesVector allowed. Reason: ClaraServer and GUI
//    void resize( uint32_t f_numberOfElements)
//    {
//        clear();
//        for( unsigned int index = 0; index < f_numberOfElements; index++ )
//        {
//            m_vector.push_back( new T() );
//        }
//    };

    size_t size()
    {
        return m_vector.size();
    };

private:
    ::std::vector<T*> m_vector;

private:
    CModuleVector( const CModuleVector<T>& f_module ) = delete;
    CModuleVector& operator=( const CModuleVector<T>& f_other ) = delete;
};

#endif // CModuleVector_CT_H
