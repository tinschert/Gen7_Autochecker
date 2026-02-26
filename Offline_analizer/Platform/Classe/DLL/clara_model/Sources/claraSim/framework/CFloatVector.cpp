/*******************************************************************************
author Robert Erhart, ett2si (18.10.2004 - 00:00:00)
author (c) Copyright Robert Bosch GmbH 2004, 2005.  All rights reserved.
*******************************************************************************/

#include "CFloatVector.h"
//#include <iostream>
//
///* Constructor */
//CFloatVector::CFloatVector()
//{}
//
///*--------------------------------*/
///* vector +                       */
///* vector3 = vector1 + vector2    */
///*--------------------------------*/
//CFloatVector CFloatVector::operator+ (const CFloatVector & v)
//{
//  /* Init */
//  CFloatVector temp;
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
//CFloatVector CFloatVector::operator* (const double value)
//{
//  /* Init */
//  CFloatVector temp;
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
//CFloatVector CFloatVector::operator/ (const double value)
//{
//  /* Init */
//  CFloatVector temp;
//
//  /* vector3 = vector1 * value */
//  for (unsigned int i = 0 ; i < this->size() ; i++)
//  {
//    temp.push_back( this->at(i) / value );
//  }
//
//  return temp;
//}
