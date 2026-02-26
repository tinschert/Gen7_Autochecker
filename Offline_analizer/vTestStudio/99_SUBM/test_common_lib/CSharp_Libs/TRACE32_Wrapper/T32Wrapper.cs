using System;
using System.IO;
using System.Collections.ObjectModel;
using System.Linq;
using System.Text;
using System.Threading;

using Vector.Diagnostics;
//using Vector.Scripting.UI;
using Vector.Tools;
using Vector.CANoe.Runtime;
using Vector.CANoe.Sockets;
using Vector.CANoe.Threading;
using Vector.CANoe.TFS;
using Vector.CANoe.VTS;
//using NetworkDB;

using C_Sharp_DLL;

[TestClass]
public class MyTestClass
{
 public static Version version = new Version(2017, 08, 16, 0); //version of this module
 // public static Bdu3xx.BduState bduState = new Bdu3xx.BduState();
 //private static C_Sharp_DLL.program T32Api;//consider to implement singleton-class instead of static?
 static string tabName = "T32";

  [Export] 
  public static int Connect()
  {
    // Your implementation here...
	int error=999;
	
	error = program.T32_Config("NODE=","localhost") ;
	if(error!=0)
		 Output.WriteLine(tabName,"Connection error in config \"Node=localhost\" ,%d\n",error);
	else
		 Output.WriteLine("Config  Node OK ...",tabName);
	

	error = program.T32_Config("PORT=","20000") ;
	if(error!=0)
		 Output.WriteLine(tabName,"Connection error in config \"Port=20000\" ,{0}", error);
	else
		 Output.WriteLine("Config PORT OK ...",tabName);



	error = program.T32_Config("PACKLEN=","1024") ;
	if(error!=0)
		 Output.WriteLine(tabName,"Connection error in config \"PACKLIN=1024\" ,{0}",error);
	else
		 Output.WriteLine("Config PACKLEN OK ...",tabName);
    return error;
  }
  
  [Export] 
  public static int Init()
  {
    int error =999;
    //Execution.Wait(3000);
    if ((error = program.T32_Init())!=0) 
  	{
  		/* handle error */
  		Output.WriteLine(tabName,"Init Error {0}",error);
  	}
  		else
  		Output.WriteLine("Init OK ...",tabName);
   return error;
  }
  
  
  
  
  [Export] 
  public static int Attach()
  {
    int error=999;
    //Execution.Wait(3000);
    if ((error = program.T32_Attach(1)) != 0) 
  	{
  		/* handle error */
  		Output.WriteLine(tabName,"Attach Error {0}", error);
  	}	
  	else
  		Output.WriteLine("Attach OK ...",tabName);
    return error;
  }
  
  [Export]
  public static long ReadVariableIntValue(string variable_name)
  {
    int error =999;
    int a,b;
    a=b=-1;
    //Execution.Wait(3000);
    error= program.T32_ReadVariableValue(variable_name ,ref a ,ref b);
    if(error!=0)
    {
        		Output.WriteLine(tabName,"Read variable Error {0}", error);
            a=0;
            b=0;
    }
    else
    {
//            Output.WriteLine(tabName, "Read {0}" , variable_name );
            Output.WriteLine(tabName, "{0} = {1}" , variable_name,((b<<32)+a));
    }
    Report.TestCaseMeasuredValue(variable_name,((b<<32)+a));
    return ((b<<32)+a);
  }

  
  [Export]
  public static string ReadVariableStringValue(string VariableName,string VariableValue,int TargetLenth)
  //public static string ReadVariableStringValue(string VariableName,int TargetLenth)
  {
    int error =999;
    //Execution.Wait(3000);
    StringBuilder Variable_Str = new StringBuilder(TargetLenth); 
    error= program.T32_ReadVariableString(VariableName , Variable_Str ,TargetLenth);
    if(error!=0)
    {
        		Output.WriteLine(tabName,"Read variable Error {0}", error);
    }
    else
    {
//            Output.WriteLine(tabName, "Read {0}" , variable_name );
            //Output.WriteLine(tabName, "{0} = {1}" , variable_name,((b<<32)+a));
            Output.WriteLine(tabName, "{0} = {1}" , VariableName,Variable_Str);
            VariableValue=Variable_Str.ToString(); 
            Report.TestCaseComment(VariableValue);
    }
    Report.TestCaseMeasuredValue(VariableName,Variable_Str.ToString());    
    return Variable_Str.ToString(0,Variable_Str.Length) ;
  }
  
  [Export]
    public static int ReadVariableStrStr(string VariableName,string SearchStr1,string SearchStr2,int TargetLenth)
  //public static string ReadVariableStringValue(string VariableName,int TargetLenth)
  {
    int error =999;
    string result="";
    //Execution.Wait(3000);
    StringBuilder Variable_Str = new StringBuilder(TargetLenth); 
    error= program.T32_ReadVariableString(VariableName , Variable_Str ,TargetLenth);
    if(error!=0)
    {
        		Output.WriteLine(tabName,"Read variable Error {0}", error);
    }
    else
    {  
//            Output.WriteLine(tabName, "Read {0}" , variable_name );
            //Output.WriteLine(tabName, "{0} = {1}" , variable_name,((b<<32)+a));
            Output.WriteLine(tabName, "{0} = {1}" , VariableName,Variable_Str);
            result=Variable_Str.ToString();
            Report.TestCaseComment(result);
            if(result.Contains("SearchStr1")&&result.Contains("SearchStr1"))
              error=0;
    }
    Report.TestCaseMeasuredValue(VariableName,Variable_Str.ToString());
    return error ;
  }
  
     //This Function is used for Comparing the string between ECU internal variable to release plan DID(Target Value)
    //Parameter:
    //name            --> variable name for getting from Lauterbarh
    //TargetString    --> Comparing target string
    //TargetLenth     --> Lenth of target string for confirm target string is correct
    [Export]
    public static int T32User_StringComparators(string name, string TargetString,int TargetLenth)
    {
      int Result ;
      int loop_i = 0;
      //string myString;
      StringBuilder Variable_Str = new StringBuilder(TargetLenth); 
      //Execution.Wait(3000);
      try
      {
        Result = program.T32_ReadVariableString(name,Variable_Str,TargetLenth );
      }
      catch(Exception e)
      {
        Output.WriteLine("Exeption in T32_ReadVariableString",tabName);
        Output.WriteLine(e.ToString(),tabName);
		    Result=0xFF;
      }
      if(Result<0)
      {
        Output.WriteLine("Read Variable String Communication Error ",tabName);
      }
   // the following else state is commented as a work arround for a bug in Lauterbach remote API, which sometimes returns value >0 while the readign is correct. 
      else if(Result>0)
      {
        Output.WriteLine("Read Variable String Access Error ",tabName);
      }
      else  //Result = 0 ==> Read operation done correctly
      {
		Result=0;
        if(TargetString.Length == /*TargetLenth*/ Variable_Str.Length)
        {
            //if (Variable_Str.Length < TargetString.Length)
            //{
            //    Result = 0;
            //}
            //else
            {
                //Variable_Str = T32.ReadVariable(name); not needed twice
                //Variable_Str.ToCharArray();
                string myString = Variable_Str.ToString();
                TargetString.ToCharArray();
                for (loop_i = 0; loop_i < TargetString.Length; loop_i++)
                {
                    //if (Variable_Str[loop_i] != TargetString[loop_i])
                    if (myString[loop_i] != TargetString[loop_i])
                    {
                        Result = 0xFF;
                        Output.WriteLine("Read Variable String value mismatch ",tabName);
                        Output.WriteLine(tabName,"Read Variable String Target value {0} ",TargetString);
                        Output.WriteLine(tabName,"Read Variable String value red    {0}",Variable_Str );
                        //Report.TestCaseMeasuredValue(name,Variable_Str.ToString());
                        //Output.WriteLine(tabName,"Read Variable String value red    {0}",myString );
                        //Output.WriteLine(tabName,"loop counter value {0}",loop_i);
                    }
                }
            }
            
        }
        else
        {
          Result = 0xFF;
          Output.WriteLine("Read Variable String Length mismatch ",tabName);
          Output.WriteLine(tabName,"TargetLenth = {0} , Variable_Str.Length = {1},TargetString.Length {2} ",TargetLenth,Variable_Str.Length,TargetString.Length);
          //Execution.Wait(300);
          
          Output.WriteLine(tabName,"Read Variable String Target value {0} ",TargetString);
          //Execution.Wait(300);

          Output.WriteLine(tabName,"Read Variable String value red    {0}",Variable_Str );
          //Execution.Wait(300);
          
          //Output.WriteLine(tabName,"Read Variable String value red    {0}",Variable_Str.ToString() );
          //Execution.Wait(300);

        }
      }      
      Report.TestCaseMeasuredValue(name,Variable_Str.ToString());
      return Result;
    }
    
    
            /// <summary>
        /// Disconnect TRACE32 to release connection. 
        /// Usually this shall be used in Cleanup state of a test unit
        /// </summary>
        /// <returns>When not 0 then an error is occured</returns>
        [Export]
        public static int DisconnectDebugger() 
        {
          return program.T32_Exit();
            /*Verdict result;
            TimeSpan time;
            int task_result, time_for_task;
            string txt;
            
            time_for_task = 20;//Lauterbach.tsv_TimeForTask.Value;
            txt = "Disconnect Step";
            time = Measurement.CurrentTime;
            
            Output.WriteLine(tabName, "{0:hh\\:mm\\:ss} Disconnect T32", time);
            //if(T32Api != null){                
                task_result = Execution.WaitForTask((canceltoken) => { return TDisconnect(canceltoken, time); }, maxTime: time_for_task);
                time = Measurement.CurrentTime;
                if(task_result == Execution.WAIT_TIMEOUT
                   || task_result == Execution.WAIT_EXCEPTION
                   || task_result == Execution.WAIT_ABORTED) 
                {
                    result = Verdict.ErrorInTestSystem;
                    txt = string.Format("Disconnect T32 failed: {0}", task_result);
                    Output.WriteLine(tabName, "{0:hh\\:mm\\:ss} {1}", time, txt);
                    Report.TestStepErrorInTestSystem(txt);
                } 
                  else if(task_result == Execution.WAIT_ILLEGAL_RESULTVALUE) 
                {
                    result = Verdict.ErrorInTestSystem;
                    txt = string.Format("task TDisconnect return illegal value: {0}", task_result);
                    Output.WriteLine(tabName, "{0:hh\\:mm\\:ss} {1}", time, txt);
                    Report.TestStepErrorInTestSystem(txt);
                } else 
                {
                    result = Verdict.Passed;
                    txt = "T32 disconnected";
                    Output.WriteLine(tabName, "{0:hh\\:mm\\:ss} {1}", time, txt);
                    Report.TestStepPass(txt);
                    T32Api = null;
                }
            //} else result = Verdict.Passed;//either already disconnected or it was not connected
            
            //Lauterbach.tsv_IsDebuggerConnected.Value = 0;

            return (int) result;
          */
        }

        [Export]
        public static int T32User_ArrComparators(String name, string Target_Arr, int Target_Lenth)
        {
          int Result = 1;
          int i;
          //string Variable_Str;
          string txt;
          
          string[] sArray = Target_Arr.Split(',');
          byte[] TargetArr = new byte[Target_Lenth];
          StringBuilder Variable_Str = new StringBuilder(Target_Lenth); 
          Result=program.T32_ReadVariableString(name,Variable_Str,Target_Lenth );
          //Variable_Str.ToCharArray();
          if(Result<0)
          {
            Output.WriteLine(tabName,"Read Variable String Communication Error ");
            Result=0;
          }
          else if(Result>0)
          {
            Output.WriteLine(tabName,"Read Variable String Access Error ");
            Result=0;
          }
          else  //Result = 0
          {

            for(i = 0;i < Target_Lenth;i ++)
            {
              TargetArr[i] = Convert.ToByte(sArray[i], 16);
              txt = String.Format("TargetValue[{0}] is: {1:X000}; ResultValue is {2:X000}", i, TargetArr[i],(Byte)Variable_Str[i]);
              if(Variable_Str[i] != TargetArr[i])
              {
                Result = 0;
                Report.TestStepFail(txt);
              }
              else
              {
                Report.TestStepPass(txt);
              }
            }
          }
          return Result;
        }

        /// <summary>
        /// Use this to execute TRACE32 commands, timeout in msec (default 2000)
        /// </summary>
        /// <param name="cmd">any TRACE32 commands as described in C:\T32\pdf\commandlist.pdf</param>
        /// <returns>0 (Verdict.Passed) when Trace32.Cmd(cmd) returns without errors, 
        /// 4 (Verdict.ErrorInTestSystem) otherways</returns>
        [Export]
        public static int ExecuteCommand(string cmd, int timeout)
        {
            Verdict result;
            string txt = string.Format("Execute TRACE32 command: {0}", cmd);
            Report.TestStep(txt);
            Output.WriteLine(tabName, "{0:hh\\:mm\\:ss} {1}", Measurement.CurrentTime, txt);
            int task_result = Execution.WaitForTask((canceltoken) => {return TCommand(canceltoken, cmd);}, maxTime: timeout); //Lauterbach.tsv_TimeForTask.Value);
            if( (task_result != 1) && (cmd != "quit") ) 
            {
                Report.TestStepErrorInTestSystem(string.Format("TRACE32 failed to execute command: {0}", cmd));
                OutputTaskResult("ExecuteCommand", task_result);
                result = Verdict.ErrorInTestSystem;
            } else 
            {
                result = Verdict.Passed;
            }
            Output.WriteLine(tabName, "{0:hh\\:mm\\:ss} {1}", Measurement.CurrentTime, string.Format("TRACE32 command executed: {0}", cmd));
            return (int) result;
        }
        
        
        [Export]
        public static int check_bit(long value, int bit)
        {
          int i;
          long[] bin = new long[32];
          
          if (value == -2147483648)
            return 1;
      
          for(i = 0; value > 0; i++)
          {
            bin[i] = value % 2;
            value = value / 2;
          }
      
          if (bin[bit] == 1)
              return 1;
      
          return 0;
        }

        
/*      internal static int TDisconnect(TaskCancelToken token, TimeSpan time) 
        {
            int result;
            string taskname = System.Reflection.MethodBase.GetCurrentMethod().Name;
            int t32_result = program.T32_Exit();
            if(0 == t32_result) 
            {
                result = 1;
            } else 
            {
                result = 2;
                Output.WriteLine(taskname +" error occured: "+ t32_result);
            }
            T32Api = null;
            return result;
        }
*/

        
        internal static int TCommand(TaskCancelToken token, String cmd)
        {
            int result;
            string taskname = System.Reflection.MethodBase.GetCurrentMethod().Name;
            int t32_result = program.T32_Cmd(cmd);
            if((0 == t32_result) || (cmd == "quit"))
            {
                result = 1;
            } 
            else
            {
                result = 2;
                Output.WriteLine(tabName,taskname +" error occured: "+ t32_result);
            }
            
            return result;
        }

        internal static void OutputTaskResult(string task_name, int task_result) 
        {
            Output.WriteLine(tabName, "{0}. Task result: {1}", task_name, task_result);
            if(task_result <= 0) 
            {//Vector predefined errors
                Output.WriteLine(tabName, "Vector.CANoe.Threading.Execution defined task results:{0} {1} = {2};{3} {4} = {5};{6} {7} = {8};{9} {10} = {11};",
                    Environment.NewLine, Execution.WAIT_ABORTED, "WAIT_ABORTED",
                    Environment.NewLine, Execution.WAIT_EXCEPTION, "WAIT_EXCEPTION",
                    Environment.NewLine, Execution.WAIT_ILLEGAL_RESULTVALUE, "WAIT_ILLEGAL_RESULTVALUE",
                    Environment.NewLine, Execution.WAIT_TIMEOUT, "WAIT_TIMEOUT");
            } 
            else 
            {
                Output.WriteLine(tabName, "{0}. Check T32.cs when task result bigger then 1", task_name, task_result);
            }
        }
        [Export]
        public static int CheckFile(string name) {
            Verdict result;
            int task_result;
            TimeSpan time;
            string txt;
            
            txt = string.Format("Try to find file:{0}", name);
            Output.WriteLine(tabName, "{0:hh\\:mm\\:ss} {1}", Measurement.CurrentTime, txt);
            
            time = Measurement.CurrentTime;              
            task_result = Execution.WaitForTask((canceltoken) => { return TCheckFile(canceltoken, name); });
          
            if(task_result == 1) {
                result = Verdict.Passed;
                txt = string.Format("File exists: {0}", name);
                Report.TestStepPass(txt);
            } else {// failed
                result = Verdict.ErrorInTestSystem;
                txt = string.Format("File not found: {0}", name);
                Report.TestStepFail(txt);
            }
            Output.WriteLine(tabName, "{0:hh\\:mm\\:ss} {1}", Measurement.CurrentTime, txt);
            return (int) result;
        }

        [Export]
        public static int CheckFlashErrorFile(string path) {
            Verdict result;
            int task_result;
            TimeSpan time;
            string txt;
            string filename = "errorlog.txt";
          
            txt = string.Format("Try to find file:{0} in path:{1}", filename, path);
            Output.WriteLine(tabName, "{0:hh\\:mm\\:ss} {1}", Measurement.CurrentTime, txt);
            
            time = Measurement.CurrentTime;  
            Directory.SetCurrentDirectory(path);
            task_result = Execution.WaitForTask((canceltoken) => { return TCheckFile(canceltoken, filename); });
          
            if(task_result != 1) {
                result = Verdict.Passed;
                txt = string.Format("File {0} is not present", filename);
                Report.TestStepPass(txt);
            } else {// failed
                result = Verdict.ErrorInTestSystem;
                txt = string.Format("Flashing failed, see file: {0}", filename);
                Report.TestStepErrorInTestSystem(txt);
            }
            Output.WriteLine(tabName, "{0:hh\\:mm\\:ss} {1}", Measurement.CurrentTime, txt);
            return (int) result;
        }
        
        [Export]
        public static int CheckFileNoFail(string name) {
//            Verdict result;
            int task_result;
            TimeSpan time;
            string txt;
            
            txt = string.Format("Try to find file:{0}", name);
            //Output.WriteLine(tabName, "{0:hh\\:mm\\:ss} {1}", Measurement.CurrentTime, txt);
            
            time = Measurement.CurrentTime;              
            task_result = Execution.WaitForTask((canceltoken) => { return TCheckFileNoWrite(canceltoken, name); });
          
            if(task_result == 1) {
                //result = Verdict.Passed;
                txt = string.Format("File exists: {0}", name);
                //Report.TestStepPass(txt);
            } else {// failed
                //result = Verdict.ErrorInTestSystem;
                txt = string.Format("File not found: {0}", name);
                //Report.TestStepFail(txt);
            }
            //Output.WriteLine(tabName, "{0:hh\\:mm\\:ss} {1}", Measurement.CurrentTime, txt);
            return (int) task_result;
        }
        
        internal static int TCheckFile(TaskCancelToken token, String name) {
            int result;
          
          //check file
            if(File.Exists(name)){
                result = 1;
            } else {
                result = 2;
                Output.WriteLine(string.Format("TCheckFile... file not found {0}", name));
            }
            return result;
        }
        
         internal static int TCheckFileNoWrite(TaskCancelToken token, String name) {
            int result;
          
          //check file
            if(File.Exists(name)){
                result = 1;
            } else {
                result = 2;
                //Output.WriteLine(string.Format("TCheckFile... file not found {0}", name));
            }
            return result;
        }

}

