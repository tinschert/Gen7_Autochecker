/*!
********************************************************************************
@class CFifo
@ingroup framework

@author tsh9fe, 09.01.2015
@copyright (c) Robert Bosch GmbH 2023. All rights reserved.
********************************************************************************
@remark
********************************************************************************
*/

#ifndef CFIFO_H_
#define CFIFO_H_

#include <queue>

template <typename Type> class CFifo
{
public:

    inline void init( int size, Type value )
    {
        clear();
        for( int i = 0; i < size; i++ ) Queue.push( value );
    }

    inline void push( Type value )
    {
        Queue.push( value );
    }

    inline Type pop( void )
    {
        Type front = Queue.front();
        Queue.pop();
        return front;
    }

    inline void clear()
    {
        while( !Queue.empty() ) Queue.pop();
    }

private:
    ::std::queue<Type> Queue;
};

#endif /* CFIFO_H_ */
