using System;
using System.Collections.ObjectModel;
using Vector.Tools;
using Vector.CANoe.Runtime;
using Vector.CANoe.Threading;
using Vector.Diagnostics;
using Vector.Scripting.UI;
using Vector.CANoe.TFS;
using Vector.CANoe.VTS;

[TestClass]
public class MyTestClass
{
  [Export] 
  /**
  * Calls the suitable flashing method  according to the choosen debugger in variable (debuggerType)
  *
  * @param[in] varExpression     name of the memory variable or symbol based expression 
  * @param[out] value            reference to the variable that will carry the read value
  */
  public static void readVariable_Tester(string varExpression){
    int val = UDELib_Wrapper.readVariable(varExpression);
    UDELib_Wrapper.logStepInfo("Read Value of Variable " + varExpression + " is " + val.ToString() + "(0x" + val.ToString("X") + ")");
  }
  
  [Export] 
  /**
  * @param[in] registerName      name of the register
  * @param[out] value            reference to the variable that will carry the read value
  */
  public static void readRegister_Tester(string registerName){
    int val = UDELib_Wrapper.readRegister(registerName);
    UDELib_Wrapper.logStepInfo("Read Value of Register " + registerName + " is " + val.ToString() + "(0x" + val.ToString("X") + ")");
  }
}