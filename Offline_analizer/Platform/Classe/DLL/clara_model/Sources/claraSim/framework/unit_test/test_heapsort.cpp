//============================================================================
// Name        : test_CAutosarTP.cpp
// Author      :
// Version     :
// Copyright   : Your copyright notice
// Description : Hello World in C++, Ansi-style
//============================================================================

#include <iostream>
#include "../CFloatVector.h"
#include "../CIntVector.h"
using namespace std;


void heapSortWithComparsionCriterion( CIntVector& f_indexVector_r, const CFloatVector& f_prioVector_r )
{
    /* sort f_indexVector_r array into descending order, use f_prioVector_r as comparison criterion
     * sort index array with inverse Heapsort (invented by J.W.J. Williams) implementation
     * and special comparison criterion */
    unsigned long n = f_indexVector_r.size();
    if( n > 1 )
    {
        unsigned long indexI, indexR, indexJ, indexL;
        unsigned long sortValueTemp = 0;
        indexL = ( n >> 1 ) + 1;
        indexR = n;
        while( true )
        {
            if( indexL > 1 )
            {
                // hiring phase
                indexL--;
                sortValueTemp = f_indexVector_r[indexL - 1];
            }
            else
            {
                // retirement-and-promotion phase
                sortValueTemp = f_indexVector_r[indexR - 1];
                f_indexVector_r[indexR - 1] = f_indexVector_r[0];
                indexR--;
                if( indexR == 1 )
                {
                    f_indexVector_r[0] = sortValueTemp;
                    break;
                }
            }
            indexI = indexL;
            indexJ = indexL + indexL;
            while( indexJ <= indexR )
            {
                if( indexJ < indexR &&
                    f_prioVector_r[ f_indexVector_r[indexJ - 1] ] > f_prioVector_r[ f_indexVector_r[indexJ] ] )
                {
                    indexJ++;
                }
                if( f_prioVector_r[ sortValueTemp ] > f_prioVector_r[ f_indexVector_r[indexJ - 1] ] )
                {
                    f_indexVector_r[indexI - 1] = f_indexVector_r[indexJ - 1];
                    indexI = indexJ;
                    indexJ = indexJ << 1;
                }
                else
                {
                    indexJ = indexR + 1;
                }
            }
            f_indexVector_r[indexI - 1] = sortValueTemp;
        }
    }
}

int main()
{
    CIntVector indexVector( 10 );
    for( long int index = 0; index < indexVector.size(); index++ )
    {
        indexVector[index] = index;
    }
    CFloatVector prioVector( 10 );

    for( long int index = 0; index < prioVector.size(); index++ )
    {
        prioVector[index] = 0.0;
    }
    prioVector[4] = 0.1;
    prioVector[6] = 0.5;
    prioVector[7] = 0.2;

    ::std::cout << "0++++" << ::std::endl;
    heapSortWithComparsionCriterion( indexVector, prioVector );

    for( long int index = 0; index < indexVector.size(); index++ )
    {
        ::std::cout << " index: " << index << " indexVector: " << indexVector[index] << " prio: " << prioVector[indexVector[index]] << ::std::endl;
    }

    ::std::cout << "1++++" << ::std::endl;
    heapSortWithComparsionCriterion( indexVector, prioVector );

    for( long int index = 0; index < indexVector.size(); index++ )
    {
        ::std::cout << " index: " << index << " indexVector: " << indexVector[index] << " prio: " << prioVector[indexVector[index]] << ::std::endl;
    }

    ::std::cout << "2++++" << ::std::endl;
    heapSortWithComparsionCriterion( indexVector, prioVector );

    for( long int index = 0; index < indexVector.size(); index++ )
    {
        ::std::cout << " index: " << index << " indexVector: " << indexVector[index] << " prio: " << prioVector[indexVector[index]] << ::std::endl;
    }

    return 0;
}
