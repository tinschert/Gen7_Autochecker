# -*- coding: utf-8 -*-
# @file StbmOverCan.py
# @author ADAS_HIL_TEAM
# @date 10-04-2022

##################################################################
# C O P Y R I G H T S
# ----------------------------------------------------------------
# Copyright (c) 2022-2023 by Robert Bosch GmbH. All rights reserved.

# The reproduction, distribution and utilization of this file as
# well as the communication of its contents to others without express
# authorization is prohibited. Offenders will be held liable for the
# payment of damages. All rights reserved in the event of the grant
# of a patent, utility model or design.

##################################################################


node=[]#Gobal variable

sysvar_xml ='''<?xml version="1.0" encoding="utf-8"?>
<systemvariables version="4">
  <namespace name="" comment="" interface="">
    <namespace name="STBM" comment="" interface="">
      <struct name="struct_STBM_Over_CAN" isUnion="False" definedBinaryLayout="True" comment="">
        <structMember relativeOffset="0" byteOrder="0" isOptional="False" isHidden="False" name="Sync_Trigger" comment="" bitcount="32" isSigned="true" encoding="65001" type="int" startValue="0" minValue="0" minValuePhys="0" maxValue="1" maxValuePhys="1" />
        <structMember relativeOffset="0" byteOrder="0" isOptional="False" isHidden="False" name="Sync_CycleTime" comment="" bitcount="32" isSigned="true" encoding="65001" type="int" startValue="460" />
        <structMember relativeOffset="0" byteOrder="0" isOptional="False" isHidden="False" name="FUP_Trigger" comment="" bitcount="32" isSigned="true" encoding="65001" type="int" startValue="0" minValue="0" minValuePhys="0" maxValue="1" maxValuePhys="1" />
        <structMember relativeOffset="0" byteOrder="0" isOptional="False" isHidden="False" name="FUP_CycleTime" comment="" bitcount="32" isSigned="true" encoding="65001" type="int" startValue="40" />
        <structMember relativeOffset="0" byteOrder="0" isOptional="False" isHidden="False" name="UNIX_Time" comment="" bitcount="64" isSigned="false" encoding="65001" type="longlong" startValue="0" minValue="0" minValuePhys="0" />
      </struct>
	  <variable anlyzLocal="2" readOnly="false" valueSequence="false" unit="" name="STBM_Over_CAN" comment="" bitcount="32" isSigned="true" encoding="65001" type="struct" structDefinition="STBM::struct_STBM_Over_CAN" />
    </namespace>
  </namespace>
</systemvariables>
'''

panel_xvp ='''<?xml version="1.0"?>
<Panel Type="Vector.CANalyzer.Panels.PanelSerializer, Vector.CANalyzer.Panels.Serializer, Version=15.1.1.0, Culture=neutral, PublicKeyToken=null">
  <Object Type="Vector.CANalyzer.Panels.Runtime.Panel, Vector.CANalyzer.Panels.Common, Version=15.1.1.0, Culture=neutral, PublicKeyToken=null" Name="Panel" Children="Controls" ControlName="STBM_On_CAN">
    <Object Type="Vector.CANalyzer.Panels.Design.GroupBoxControl, Vector.CANalyzer.Panels.CommonControls, Version=15.1.1.0, Culture=neutral, PublicKeyToken=null" Name="GroupBoxControl7" Children="Controls" ControlName="CAN_IL_States">
      <Object Type="Vector.CANalyzer.Panels.Design.GroupBoxControl, Vector.CANalyzer.Panels.CommonControls, Version=15.1.1.0, Culture=neutral, PublicKeyToken=null" Name="GroupBoxControl4" Children="Controls" ControlName="Group Box">
        <Object Type="Vector.CANalyzer.Panels.Design.TextBoxControl, Vector.CANalyzer.Panels.CommonControls, Version=15.1.1.0, Culture=neutral, PublicKeyToken=null" Name="TextBoxControl2" Children="Controls" ControlName="Input/Output Box">
          <Property Name="Name">TextBoxControl2</Property>
          <Property Name="Size">162, 20</Property>
          <Property Name="Location">6, 11</Property>
          <Property Name="AlarmUpperTextColor">WindowText</Property>
          <Property Name="ValueDecimalPlaces">0</Property>
          <Property Name="AlarmLowerBkgColor">Salmon</Property>
          <Property Name="ValueDisplay">Decimal</Property>
          <Property Name="AlarmUpperBkgColor">IndianRed</Property>
          <Property Name="AlarmLowerTextColor">WindowText</Property>
          <Property Name="AlarmGeneralSettings">1;0;0;0</Property>
          <Property Name="DisplayLabel">Left</Property>
          <Property Name="DescriptionText">UNIX time</Property>
          <Property Name="DescriptionSize">56, 20</Property>
          <Property Name="SymbolConfiguration">6;128;STBM;;STBM_Over_CAN;UNIX_Time;1;;;-1;;;;</Property>
          <Property Name="TabIndex">3</Property>
        </Object>
        <Object Type="Vector.CANalyzer.Panels.Design.StaticTextControl, Vector.CANalyzer.Panels.CommonControls, Version=15.1.1.0, Culture=neutral, PublicKeyToken=null" Name="StaticTextControl1" Children="Controls" ControlName="ElemST">
          <Property Name="Name">StaticTextControl1</Property>
          <Property Name="Size">112, 14</Property>
          <Property Name="Location">56, 37</Property>
          <Property Name="BackColor">LightGoldenrodYellow</Property>
          <Property Name="Font">Courier New, 8.25pt</Property>
          <Property Name="Text">Time in Seconds</Property>
          <Property Name="ForeColor">Black</Property>
        </Object>
        <Property Name="Name">GroupBoxControl4</Property>
        <Property Name="Size">176, 59</Property>
        <Property Name="Location">3, 152</Property>
        <Property Name="Text">
        </Property>
        <Property Name="TabIndex">12</Property>
      </Object>
      <Object Type="Vector.CANalyzer.Panels.Design.GroupBoxControl, Vector.CANalyzer.Panels.CommonControls, Version=15.1.1.0, Culture=neutral, PublicKeyToken=null" Name="GroupBoxControl3" Children="Controls" ControlName="Group Box">
        <Object Type="Vector.CANalyzer.Panels.Design.GroupBoxControl, Vector.CANalyzer.Panels.CommonControls, Version=15.1.1.0, Culture=neutral, PublicKeyToken=null" Name="GroupBoxControl2" Children="Controls" ControlName="Group Box">
          <Object Type="Vector.CANalyzer.Panels.Design.TextBoxControl, Vector.CANalyzer.Panels.CommonControls, Version=15.1.1.0, Culture=neutral, PublicKeyToken=null" Name="TextBoxControl1" Children="Controls" ControlName="Input/Output Box">
            <Property Name="Name">TextBoxControl1</Property>
            <Property Name="Size">127, 20</Property>
            <Property Name="Location">35, 19</Property>
            <Property Name="AlarmUpperTextColor">WindowText</Property>
            <Property Name="ValueDecimalPlaces">0</Property>
            <Property Name="AlarmLowerBkgColor">Salmon</Property>
            <Property Name="ValueDisplay">Decimal</Property>
            <Property Name="AlarmUpperBkgColor">IndianRed</Property>
            <Property Name="AlarmLowerTextColor">WindowText</Property>
            <Property Name="AlarmGeneralSettings">1;0;0;0</Property>
            <Property Name="DisplayLabel">Left</Property>
            <Property Name="DescriptionText">Cycle Time</Property>
            <Property Name="DescriptionSize">61, 20</Property>
            <Property Name="SymbolConfiguration">6;128;STBM;;STBM_Over_CAN;FUP_CycleTime;1;;;-1;;;;</Property>
            <Property Name="TabIndex">10</Property>
          </Object>
          <Object Type="Vector.CANalyzer.Panels.Design.SwitchControl, Vector.CANalyzer.Panels.CommonControls, Version=15.1.1.0, Culture=neutral, PublicKeyToken=null" Name="SwitchControl2" ControlName="SwitchControl_STBM">
            <Property Name="Name">SwitchControl2</Property>
            <Property Name="Size">23, 30</Property>
            <Property Name="Location">6, 17</Property>
            <Property Name="StateCnt">2</Property>
            <Property Name="Activation">Left</Property>
            <Property Name="SwitchValues">1;2;0;1</Property>
            <Property Name="SwitchValuesRx">1;2;0;1</Property>
            <Property Name="SwitchValuesVT">1;2;0/Lower/0;1/Lower/1</Property>
            <Property Name="SwitchValuesVTXml">&lt;Version&gt;2&lt;/Version&gt;&lt;Count&gt;2&lt;/Count&gt;&lt;RxValue&gt;0&lt;/RxValue&gt;&lt;LowerUpper&gt;Lower&lt;/LowerUpper&gt;&lt;TxValue&gt;0&lt;/TxValue&gt;&lt;RxValue&gt;1&lt;/RxValue&gt;&lt;LowerUpper&gt;Lower&lt;/LowerUpper&gt;&lt;TxValue&gt;1&lt;/TxValue&gt;</Property>
            <Property Name="SymbolConfiguration">6;128;STBM;;STBM_Over_CAN;FUP_Trigger;1;;;-1;;;;</Property>
            <Property Name="TabIndex">0</Property>
          </Object>
          <Property Name="Name">GroupBoxControl2</Property>
          <Property Name="Size">166, 53</Property>
          <Property Name="Location">6, 66</Property>
          <Property Name="Text">Fup</Property>
          <Property Name="TabIndex">11</Property>
        </Object>
        <Object Type="Vector.CANalyzer.Panels.Design.GroupBoxControl, Vector.CANalyzer.Panels.CommonControls, Version=15.1.1.0, Culture=neutral, PublicKeyToken=null" Name="GroupBoxControl1" Children="Controls" ControlName="Group Box">
          <Object Type="Vector.CANalyzer.Panels.Design.TextBoxControl, Vector.CANalyzer.Panels.CommonControls, Version=15.1.1.0, Culture=neutral, PublicKeyToken=null" Name="TextBoxControl4" Children="Controls" ControlName="Input/Output Box">
            <Property Name="Name">TextBoxControl4</Property>
            <Property Name="Size">127, 20</Property>
            <Property Name="Location">35, 19</Property>
            <Property Name="AlarmUpperTextColor">WindowText</Property>
            <Property Name="ValueDecimalPlaces">0</Property>
            <Property Name="AlarmLowerBkgColor">Salmon</Property>
            <Property Name="ValueDisplay">Decimal</Property>
            <Property Name="AlarmUpperBkgColor">IndianRed</Property>
            <Property Name="AlarmLowerTextColor">WindowText</Property>
            <Property Name="AlarmGeneralSettings">1;0;0;0</Property>
            <Property Name="DisplayLabel">Left</Property>
            <Property Name="DescriptionText">Cycle Time</Property>
            <Property Name="DescriptionSize">61, 20</Property>
            <Property Name="SymbolConfiguration">6;128;STBM;;STBM_Over_CAN;Sync_CycleTime;1;;;-1;;;;</Property>
            <Property Name="TabIndex">10</Property>
          </Object>
          <Object Type="Vector.CANalyzer.Panels.Design.SwitchControl, Vector.CANalyzer.Panels.CommonControls, Version=15.1.1.0, Culture=neutral, PublicKeyToken=null" Name="SwitchControl1" ControlName="SwitchControl_STBM">
            <Property Name="Name">SwitchControl1</Property>
            <Property Name="Size">23, 30</Property>
            <Property Name="Location">6, 17</Property>
            <Property Name="StateCnt">2</Property>
            <Property Name="Activation">Left</Property>
            <Property Name="SwitchValues">1;2;0;1</Property>
            <Property Name="SwitchValuesRx">1;2;0;1</Property>
            <Property Name="SwitchValuesVT">1;2;0/Lower/0;1/Lower/1</Property>
            <Property Name="SwitchValuesVTXml">&lt;Version&gt;2&lt;/Version&gt;&lt;Count&gt;2&lt;/Count&gt;&lt;RxValue&gt;0&lt;/RxValue&gt;&lt;LowerUpper&gt;Lower&lt;/LowerUpper&gt;&lt;TxValue&gt;0&lt;/TxValue&gt;&lt;RxValue&gt;1&lt;/RxValue&gt;&lt;LowerUpper&gt;Lower&lt;/LowerUpper&gt;&lt;TxValue&gt;1&lt;/TxValue&gt;</Property>
            <Property Name="SymbolConfiguration">6;128;STBM;;STBM_Over_CAN;Sync_Trigger;1;;;-1;;;;</Property>
            <Property Name="TabIndex">0</Property>
          </Object>
          <Property Name="Name">GroupBoxControl1</Property>
          <Property Name="Size">166, 53</Property>
          <Property Name="Location">6, 9</Property>
          <Property Name="Text">Sync</Property>
          <Property Name="TabIndex">7</Property>
        </Object>
        <Object Type="Vector.CANalyzer.Panels.Design.StaticTextControl, Vector.CANalyzer.Panels.CommonControls, Version=15.1.1.0, Culture=neutral, PublicKeyToken=null" Name="StaticTextControl39" Children="Controls" ControlName="ElemST">
          <Property Name="Name">StaticTextControl39</Property>
          <Property Name="Size">140, 14</Property>
          <Property Name="Location">28, 122</Property>
          <Property Name="BackColor">LightGoldenrodYellow</Property>
          <Property Name="Font">Courier New, 8.25pt</Property>
          <Property Name="Text">Time in Millisecond</Property>
          <Property Name="ForeColor">Black</Property>
        </Object>
        <Property Name="Name">GroupBoxControl3</Property>
        <Property Name="Size">176, 140</Property>
        <Property Name="Location">3, 13</Property>
        <Property Name="Text">
        </Property>
        <Property Name="TabIndex">9</Property>
      </Object>
      <Property Name="Name">GroupBoxControl7</Property>
      <Property Name="Size">184, 216</Property>
      <Property Name="Location">3, 3</Property>
      <Property Name="BackColor">White</Property>
      <Property Name="Text">STBM</Property>
      <Property Name="ForeColor">Black</Property>
      <Property Name="UseWindowsStyle">False</Property>
      <Property Name="TabIndex">3</Property>
    </Object>
    <Property Name="Name">Panel</Property>
    <Property Name="Size">190, 222</Property>
    <Property Name="BackColor">White</Property>
  </Object>
</Panel>
'''

COPYRIGHT='''/*@!Encoding:1252*/

/*******************************************************************************
	MODULEFILE_DESCRIPTION:stbm over CAN
	COPYRIGHT:
	Robert Bosch GmbH reserves all rights even in the event of industrial
	property. We reserve all rights of disposal such as copying and passing
	on to third parties.
	COPYRIGHT_END:

	PROJECT:		  Implements STBM functionality as a Master Node
	FILENAME:		  stbm_over_can.cin

	DESCRIPTION:		  CAPL-Program for STBM master over CAN simulation.

	HISTORY:
        Version1: 14.02.2019 ; DUE1KOR ; Initial Version 

*****************************************************************************/
'''

Variables='''
variables{
  message FDP1_SYNC_FRADAR_358 GTB_Msg;//STBM over CAN PDU
  
  mstimer GTBTimer1;//Syn Timer
  mstimer GTBTimer2;//Fup Timer
  
  dword timestamp;//Second
  dword timestamp_nanosecond_portion;//Nanosecond
  
  dword T_diff;
  dword time_raw_ns;
  dword total_nanosecond;
  dword Overflow_to_second;
  dword nanosecond_FUP;
  dword time_raw_10us_precision;
  dword nanosecond_rollover = 1000000000;

  int Sync_Cnt = 0;
  int cycle_time = 0;
  byte Sync_transmitted = 0;
}
'''
on_envVar_STBM_on_CAN_SYNC='''
on sysvar STBM::STBM_Over_CAN.Sync_Trigger{
  if(@STBM::STBM_Over_CAN.Sync_Trigger==1)
  {
    setTimer(GTBTimer1,0); 
  }else{
    canceltimer(GTBTimer1);
    canceltimer(GTBTimer2);
    @STBM::STBM_Over_CAN.FUP_Trigger=0;
  }
}
'''
on_envVar_STBM_on_CAN_FUP='''
on sysvar STBM::STBM_Over_CAN.FUP_Trigger{
  if(@STBM::STBM_Over_CAN.FUP_Trigger==0)
  {
    canceltimer(GTBTimer2);
  }
}
'''
#Map Sync parameter to signal  based on requiremet
on_timer_GTBTimer1='''
on timer GTBTimer1
{
    dword OffSet_timestamp;

    //get number of tick, one tick is 10us
    //In CAPL, to get the current system time, the timeNow() function is used.
    //When a measurement starts, the system clock initialises, and it’s incremented in 10us units (for example, timestamp = 12345 ticks = 123.45ms)
    //Note: time_raw_10us_precision is overflow after around 12hours (due to 32bit, each bit 10us)
  
    time_raw_10us_precision = timeNow();
    //debugging purpose
    //write("time_raw_10us_precision: %d",time_raw_10us_precision);

    //Retrive second portion from time raw value (10us precision) that is returned from timeNow()
    //Note: timestamp is overflow depends on overflow of time_raw_10us_precision
  
    timestamp = (time_raw_10us_precision)/100000;
    //debugging purpose
    write("Before:OffSet:timestamp: %X",timestamp);
  
    //Retrive nanosecond portion from time raw value (10us precision) that is returned from timeNow()
    //Note:timestamp_nanosecond_portion is overflow depends on overflow of time_raw_10us_precision 
  
    timestamp_nanosecond_portion = (dword)((((double)(time_raw_10us_precision)/(double)100000) - (double)(timestamp))*(double)(1000000000));
    //debugging purpose
    //write("timestamp_nanosecond_portion: %d", timestamp_nanosecond_portion);
  
    OffSet_timestamp=timestamp + @STBM::STBM_Over_CAN.UNIX_Time;
    //debugging purpose
    write("After:OffSet:timestamp: %X",OffSet_timestamp); 
  
  /*
    GTB_Msg.byte(0) = 0x10;//Type: 0x10 means SYNC PDU
    GTB_Msg.byte(1) = 0x00;//user byte 1: default value is 0
    GTB_Msg.byte(2) = 0x10 | Sync_Cnt;//time domain (bit7 -> bit4) is 1, sequence counter: bit 3 -> 0
    GTB_Msg.byte(3) = 0x00;//user byte 0: default value is 0
  
    GTB_Msg.byte(4) = (OffSet_timestamp)>>24;
    //write("After:GTB_Msg.byte(4): %X", GTB_Msg.byte(4));
    GTB_Msg.byte(5) = (OffSet_timestamp)>>16;
    //write("After:GTB_Msg.byte(5): %X",GTB_Msg.byte(5));
    GTB_Msg.byte(6) = (OffSet_timestamp)>>8;
    //write("After:GTB_Msg.byte(6): %X",GTB_Msg.byte(6));
    GTB_Msg.byte(7) = OffSet_timestamp;
   // write("After:GTB_Msg.byte(7): %X",GTB_Msg.byte(7));
    
  */
    //To indicate that Sync message is transmitted, it shall be reset after transmitting corresponding follow up message
    Sync_transmitted = 1;
  
    GTB_Msg.SYNC_TYPE=0x10;//Type: 0x10 means SYNC PDU
    GTB_Msg.SYNC_TIME_DOMAIN =0x1;//default value is 1
  
    GTB_Msg.SYNC_TIMESEC=OffSet_timestamp;
    GTB_Msg.SYNC_SEQUENCE_COUNTER = Sync_Cnt;
  
  
    //trigger the transmission of Sync message
    write("SYNC");
  
    output(GTB_Msg);
    
    //Increment sequence counter for Sync message for the next transmission
    Sync_Cnt++;
    //If Sequence counter of Sync message reaches maximum value, then reset to 0
    Sync_Cnt%=16;
    
    
    //Time Offset for corresponding Follow Up message is 40ms
    if(@STBM::STBM_Over_CAN.FUP_Trigger==1)
    {
      cycle_time = @STBM::STBM_Over_CAN.FUP_CycleTime;
      setTimer(GTBTimer2,cycle_time);
    }else{
      cycle_time = @STBM::STBM_Over_CAN.FUP_CycleTime + @STBM::STBM_Over_CAN.Sync_CycleTime ;
      setTimer(GTBTimer1,cycle_time);
    }
 }
'''
#Map FUP parameter to signal  based on requiremet
on_timer_GTBTimer2='''
on timer GTBTimer2
{
 
  if (@STBM::STBM_Over_CAN.FUP_Trigger == 1)
  {
    /*
    
    GTB_Msg.byte(0) = 0x18;
    GTB_Msg.byte(1) = 0x00;//user byte 2: default value is 0
    GTB_Msg.byte(3) = 0x00;//SGW is always 0 as it's synchronized with Global Time Master
    GTB_Msg.byte(4) = nanosecond_FUP>>24;
    GTB_Msg.byte(5) = nanosecond_FUP>>16;
    GTB_Msg.byte(6) = nanosecond_FUP>>8;
    GTB_Msg.byte(7) = nanosecond_FUP;
    
    */
    GTB_Msg.SYNC_TYPE=0x18; //FUP     
    GTB_Msg.SYNC_TIME_DOMAIN=1;  //Default value
    
    GTB_Msg.SYNC_TIMESEC=0;
     
    GTB_Msg.FUP_TIMENSEC=nanosecond_FUP;
    
    //Reset Sync transmitted flag here, it shall be set in next transmission of Sync msg
    Sync_transmitted = 0;
    
    //trigger to transmit
    write("FUP");
    output(GTB_Msg);
    
    //TxPeriod of Sync message is 460ms Default
    cycle_time = @STBM::STBM_Over_CAN.Sync_CycleTime;
  }
    setTimer(GTBTimer1,cycle_time);

}
'''
#On message or PDU change according to requirement
on_PDU='''
on message FDP1_SYNC_FRADAR_358
{
  //Tx confirmation for Sync message
  if (Sync_transmitted == 1)
  {
    //Retrieve the time difference in ns between t0 (time value to be transmitted)and t1 (time triggered by Tx confirmation mechanism)

    T_diff = (timeNow() - time_raw_10us_precision)*10000;
    
    //Calculate total nanosecond portion that need to be attached to transmit in FUP message
    total_nanosecond = T_diff + timestamp_nanosecond_portion;
    
    //Check overflow due to the maximum of nanosecond portion is 10^9
    Overflow_to_second = total_nanosecond/nanosecond_rollover;
    
    //Final nanosecond shall be attached after overflow checked
    nanosecond_FUP = total_nanosecond - (Overflow_to_second*nanosecond_rollover);
    
    //debugging purpose
    //write("nanosecond_FUP: %d", nanosecond_FUP);
    
    //debugging purpose
    //write("T_diff: %d", T_diff);
  }
}
'''

def generate_copyright():
    """ """
    # Release documentation + copyright 
    node.append(COPYRIGHT)
    print("\tCOPYRIGHT: generated Release documentation")
    
def generate_variables():
    """ """
    # Case create node variables
    node.append(Variables)
    print("\tVariables: generated for Stbm over CAN")

def generate_functions():
    """ """
    node.append('')
    node.append(on_envVar_STBM_on_CAN_SYNC)
    node.append('')
    node.append(on_envVar_STBM_on_CAN_FUP)
    node.append('')
    print("\tfunctions: on envVar generated for Stbm over CAN ")
    node.append(on_timer_GTBTimer1)
    node.append('')
    node.append(on_timer_GTBTimer2)
    node.append('')
    print("\tfunctions: on timer generated for Stbm over CAN ")
    node.append(on_PDU)
    node.append('')
    print("\tfunctions: on PDU for Stbm over CAN ")
    
def save_sysvar_xml(file_name):#SysVar for STBM over can
    """
    

    Args:
      file_name: 

    Returns:

    """
    sysvar_node=[]
    sysvar_node.append(sysvar_xml)
    file = ('../TimeSync/Databases/SysVarDef_{0}.xml'.format(file_name))
    save_file(file,sysvar_node)
    
def save_panel_xvp(file_name):#Panel for STBM over can
    """
    

    Args:
      file_name: 

    Returns:

    """
    panel_node=[]
    panel_node.append(panel_xvp)
    file = ('../TimeSync/Panels/{0}.xvp'.format(file_name))
    save_file(file,panel_node)
    
def save_can(file_name):#CAPL for STBM over can
    """
    

    Args:
      file_name: 

    Returns:

    """
    file = ('../TimeSync/Node/{0}.can'.format(file_name))
    save_file(file,node)

def save_file(file,data):
    """
    

    Args:
      file: 
      data: 

    Returns:

    """
    # Open and save file
    with open(file, 'w') as outfile:
        outfile.write("\n".join(str(item) for item in data))
    print(file + " updated successfully")

# main function to create CAPL
def create_stbm_capl():
    """ """
    file_name="StbmOverCan"
    print("\nCreating {0}.can ".format(file_name))
    try:
        generate_copyright()
        generate_variables()
        generate_functions()
        save_can(file_name)
        save_sysvar_xml(file_name)
        save_panel_xvp(file_name)
    except Exception as exp:
        print("\nFailed to create {0}.can ".format(file_name))
        print("Error:", exp)
        return False


if __name__ == "__main__":
    # load excel and create dataframes. Data only means not copy the formula.
    create_stbm_capl()
