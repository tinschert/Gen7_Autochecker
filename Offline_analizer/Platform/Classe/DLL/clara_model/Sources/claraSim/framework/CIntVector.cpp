/*******************************************************************************
author Robert Erhart, ett2si (18.10.2004 - 00:00:00)
author (c) Copyright Robert Bosch GmbH 2004, 2005.  All rights reserved.
*******************************************************************************/

#include "CIntVector.h"
//#include <iostream>
//
///* Constructor */
//CIntVector::CIntVector()
//{}
//
///*--------------------------------*/
///* vector +                       */
///* vector3 = vector1 + vector2    */
///*--------------------------------*/
//CIntVector CIntVector::operator+ (const CIntVector & v)
//{
//  /* Init */
//  CIntVector temp;
//
//  /* check if vector have the same size */
//  if(this->size()!= v.size())
//  {
//   exit(0);
//  }
//
//  /* vector3 = vector1 + vector2 */
//  for (unsigned int i = 0 ; i < this->size() ; i++)
//  {
//    temp.push_back( this->at(i) + v.at(i) );
//  }
//
//  return temp;
//}
//
///*------------------------------*/
///* vector *                     */
///* vector3 = vector1 * double   */
///*------------------------------*/
//CIntVector CIntVector::operator* (const double value)
//{
//  /* Init */
//  CIntVector temp;
//
//  /* vector3 = vector1 * value */
//  for (unsigned int i = 0 ; i < this->size() ; i++)
//  {
//    temp.push_back( this->at(i) * value );
//  }
//
//  return temp;
//}
//
///*------------------------------*/
///* vector /                     */
///* vector3 = vector1 / double   */
///*------------------------------*/
//CIntVector CIntVector::operator/ (const double value)
//{
//  /* Init */
//  CIntVector temp;
//
//  /* vector3 = vector1 * value */
//  for (unsigned int i = 0 ; i < this->size() ; i++)
//  {
//    temp.push_back( this->at(i) / value );
//  }
//
//  return temp;
//}
