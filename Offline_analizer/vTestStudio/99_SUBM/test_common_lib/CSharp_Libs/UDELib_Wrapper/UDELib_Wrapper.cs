using System;
using System.IO;
using System.Collections.ObjectModel;
using System.Linq;
using System.Text;
using System.Threading;
using System.Reflection;
using System.Diagnostics;
using Microsoft.Win32;

using Vector.Diagnostics;
using Vector.Tools;
using Vector.CANoe.Runtime;
using Vector.CANoe.Sockets;
using Vector.CANoe.Threading;
using Vector.CANoe.TFS;
using Vector.CANoe.VTS;

using FlashingLib;

[TestClass]
/**
 * @copyright  (C) 2019-2020 Robert Bosch GmbH.\n
 * The reproduction, distribution and utilization of this file as well as
 * the communication of its contents to others without express authorization
 * is prohibited.\n
 * Offenders will be held liable for the payment of damages.\n
 * All rights reserved in the event of the grant of a patent, utility model or design.
 *
 * @file         UDELib_Wrapper.cs
 *                                            
 * @author       Manfred Rast (CC-DA/EAD2)
 * @date         29.07.2020
 * @version      0.5
 *
 * @brief Wrapper class for the UDE API.
 *
 * @details Wrapper class for the UDE API.\n
 *          Functions of this class can be used directly in vTESTstudio.\n
 *          They are visible in the User Functions window.\n
 *          This file, FlashingLib dll and the UDE DLLs\
 *          - UDENetCOMLib.UDELauncher.dll
 *          - UDENetCOMLib.UDELib\n
 *          must be linked to the using test unit in vTESTstudio.\n
 *          Microsoft .NET Framework 4.0 or later must be installed to use this module.
 */
public class UDELib_Wrapper
{
  public enum ReturnCodes
  {
    TestStepPass              = 1,
    TestStepFail              = 2,
    TestStepErrorInTestSystem = 3
  }
  
  //!version of this class
  public static Version version = new Version(2020, 07, 29, 1);

  //! name of the tab of CANoe's write window where the output is written to
  static string tabName = "UDELib_Wrapper";
  
  //! class name for reporting the function calls
  static string className = MethodBase.GetCurrentMethod().DeclaringType.Name;


  /**
   * This function is used to log in the write window in case of info
   *
   * @param[in]	  msg The message to be logged
   */
  public static void logStepInfo(string msg){
    Output.WriteLine(msg,tabName);
  }
  
  /**
   * This function is used to log in the write window in case of passed step
   *
   * @param[in]	  msg The message to be logged
   */
  public static void logStepPass(string msg){
    Output.WriteLine(msg,tabName);
  }
  
    
   /**
   * This function is used to log in the write window in case of failed step
   *
   * @param[in]	  msg The message to be logged
   */
  public static void logStepFail(string msg){
    Output.WriteLine(msg,tabName);
  }
  
   /**
   * This function is used to log in the write window in case of error step
   *
   * @param[in]	  msg The message to be logged
   */
  public static void logStepError(string msg){
    Output.WriteLine(msg,tabName);
  }
  
  /**
   * This function is registering all the logger methods (pass, fail, error, log)
   */
  private static void registerLoggingMethodsToFlashingLib(){
    FlashingLib.Logging.registerInfoLoggingFunction(logStepInfo);
    FlashingLib.Logging.registerPassLoggingFunction(logStepPass);
    FlashingLib.Logging.registerFailLoggingFunction(logStepFail);
    FlashingLib.Logging.registerErrorLoggingFunction(logStepError);
  }
  
  /**
   * This function reports the result to the Report
   *
   * @param[in]	  rc return code
   * @param[in]	  methodName name of the logging method
   */
  private static void reportMethod(ReturnCodes rc, string methodName){
    switch (rc){
      case ReturnCodes.TestStepPass: 
        Report.TestStepPass(methodName + ": Passed!");
        break;
      case ReturnCodes.TestStepFail: 
        Report.TestStepFail(methodName + ": Failed!");
        break;
      case ReturnCodes.TestStepErrorInTestSystem: 
        Report.TestStepErrorInTestSystem(methodName + ": Error!");
        break;
      default: 
        Report.TestStepErrorInTestSystem(methodName + ": Invalid Return Code!");
        break;
    }
  }


  [Export]
  /**
   * Start the application "UDEVisualPlatform.exe" 
   * and load the given workspace.
   *
   * Execution.WaitForTask() is called to avoid this error:
   * 01-0047 Measurement stopped due to real time event processing overrun at simulation time 
   *
   * @param[in]	  WorkspacePath the path to the workspace file (*.wsx)
   */
  public static void UDE_StartAndOpenWorkspace(string WorkspacePath)
  {    
    registerLoggingMethodsToFlashingLib();
    Flashing.chooseDebugger(Flashing.DebuggerType.UDE);
    ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int) Flashing.startAndOpenWorkspace(WorkspacePath));
    
    string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
    reportMethod(rc, methodName);
  }
  
  [Export]
  /**
   * Stores the paths to the HEX and the ELF file for later use.
   *
   * Execution.WaitForTask() is called to avoid this error:
   * 01-0047 Measurement stopped due to real time event processing overrun at simulation time 
   *
   * @param[in]	  hexFile the path to the HEX file
   * @param[in]	  elfFile the path to the ELF file
   *
   */
  public static void UDE_StoreHexElfFiles(string hexFile, string elfFile)
  {
    registerLoggingMethodsToFlashingLib();
    
    ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int)FlashingUDE.FlashingUDE_StoreHexElfFiles(hexFile, elfFile));
    
    string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
    reportMethod(rc, methodName);
  }

 
  
  [Export]
  /**
   * Flash the given file with the Memtool Addin of the UDEDebugger.
   *
   * Execution.WaitForTask() is called to avoid this error:
   * 01-0047 Measurement stopped due to real time event processing overrun at simulation time 
   *
   * @param[in] hexFile path to the HEX file
   */
  public static void UDE_FlashWithMemTool(string hexFile)
  {
    registerLoggingMethodsToFlashingLib();
    
    ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int) FlashingUDE.FlashingUDE_FlashWithMemTool(hexFile));
    
    string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
    reportMethod(rc, methodName);
  }



  [Export]
  /**
   * Flash the given file with the Memtool Addin of the UDE debugger.\n
   * The file to be flashed has to be loaded with the
   * function UDE_LoadHexElfFiles() before.
   *
   * Execution.WaitForTask() is called to avoid this error:
   * 01-0047 Measurement stopped due to real time event processing overrun at simulation time 
   *
   * There is also an overloaded function with the HEX file as a parameters. 
   */
  public static void UDE_FlashWithMemTool()
  {
    registerLoggingMethodsToFlashingLib();
    
    ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int) FlashingUDE.FlashingUDE_FlashWithMemTool()); 
    
    string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
    reportMethod(rc, methodName);
  }

 

  [Export]
  /**
   * Flash the given HEX file with the command line interface of MemtoolCli.exe.
   *
   * Execution.WaitForTask() is called to avoid this error:
   * 01-0047 Measurement stopped due to real time event processing overrun at simulation time 
   *
   * @param[in] hexFile       absolute path to the HEX file
   * @param[in] cfgFilePath   absolute path to the configuration file
   */
  public static void UDE_FlashWithMemToolCli(string hexFile, string cfgFilePath)
  {
    registerLoggingMethodsToFlashingLib();
    
    ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int)FlashingUDE.FlashingUDE_FlashWithMemToolCli(hexFile, cfgFilePath));
    
    string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
    reportMethod(rc, methodName);
  }

    [Export]
  /**
   * Enables or disabled the given flash module, e.g. DF1.
   *
   * Execution.WaitForTask() is called to avoid this error:
   * 01-0047 Measurement stopped due to real time event processing overrun at simulation time 
   *
   * @param[in] flashModName      name of the flash module to be enabled, e.g. DF1
   * @param[in] enabled           1: enabled, 2: disabled
   */
  public static void UDE_EnableFlashModule(string flashModName, int enabled)
  {
    registerLoggingMethodsToFlashingLib();
    Flashing.chooseDebugger(Flashing.DebuggerType.UDE);
    ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int)Flashing.enableFlashModule(flashModName, enabled));
    
    string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
    reportMethod(rc, methodName);
  }

  [Export]
  /**
   * Erase the flash module given bei it's name.
   *
   * Execution.WaitForTask() is called to avoid this error:
   * 01-0047 Measurement stopped due to real time event processing overrun at simulation time 
   *
   * @param[in] flashModName    name of the flash module to be erased, e.g. DF1
   */
  public static void UDE_EraseFlashModule(string flashModName)
  {
    registerLoggingMethodsToFlashingLib();
    Flashing.chooseDebugger(Flashing.DebuggerType.UDE);
    ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int)Flashing.eraseFlashModule(flashModName));
    
    string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
    reportMethod(rc, methodName);
  }

  [Export]
  /**
   * Release objects and close UDE instance.
   *
   * Execution.WaitForTask() is called to avoid this error:
   * 01-0047 Measurement stopped due to real time event processing overrun at simulation time 
   *
   */
  public static void UDE_StopAndCloseWorkspace()
  {
    registerLoggingMethodsToFlashingLib();
    Flashing.chooseDebugger(Flashing.DebuggerType.UDE);
    ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int)Flashing.stopAndCloseWorkspace());
    
    string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
    reportMethod(rc, methodName);
  }

  [Export]
  /**
   * Execute a sleep call.
   *
   * Execution.WaitForTask() is called to avoid this error:
   * 01-0047 Measurement stopped due to real time event processing overrun at simulation time 
   *
   * @param[in] Milliseconds sleep period in ms
   *
   */
  public static void UDE_WorkspaceSleep(int Milliseconds)
  {
    registerLoggingMethodsToFlashingLib();
    
    ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => FlashingUDE.FlashingUDE_WorkspaceSleep(Milliseconds));
    
    string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
    reportMethod(rc, methodName);
  }

  [Export]
  /**
   * Start the target application.
   *
   * Execution.WaitForTask() is called to avoid this error:
   * 01-0047 Measurement stopped due to real time event processing overrun at simulation time 
   *
   */
  public static void UDE_StartApplication()
  {
    registerLoggingMethodsToFlashingLib();
    
    ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => FlashingUDE.FlashingUDE_StartApplication());
    
    string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
    reportMethod(rc, methodName);
  }
  
  [Export]
  /**
   * Read the version information of the UDE debugger from the registry
   * and return the absolute path to MemtoolCli.exe.\n
   * The path is build in ths way:\n
   * String.Format("C:\\Program Files (x86)\\pls\\UDE {0}\\MemtoolCli.exe", udeVersion)
   *
   * @return absolute path to MemtoolCli.exe
   */
  public static String UDE_getMemtoolCliExePath()
  {
      
    registerLoggingMethodsToFlashingLib();
    
    return FlashingUDE.FlashingUDE_getMemtoolCliExePath();
  }

  [Export]
  /**
   * Flash the given HEX file with the command line interface of MemtoolCli.exe.
   *
   * @param[in] memtoolPath     absolute path to MemtoolCli.exe
   * @param[in] hexFile         absolute path to the HEX file
   * @param[in] configFilePath  absolute path to the UDE debugger configuration file
   */
  public static void UDE_FlashWithMemToolCli(string memtoolPath, string hexFile, string configFilePath)
  {
  	registerLoggingMethodsToFlashingLib();
    
    FlashingUDE.FlashingUDE_FlashWithMemToolCli(memtoolPath, hexFile, configFilePath);
  }
 
  [Export] 
		/**
    * Choose UDE debugger as debugger type
    *
    */
  public static void chooseUDEDebugger()
  {
    Flashing.chooseDebugger(Flashing.DebuggerType.UDE);
  }
  
			
  
  [Export] 
	/**
    * start And Open Workspace
    *
    * @param[in]	 workspacePath Path of the workspace to open and start
    */
    public static void startAndOpenWorkspace(string workspacePath)
		{    
			registerLoggingMethodsToFlashingLib();
			ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int) Flashing.startAndOpenWorkspace(workspacePath));
			
			string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
			reportMethod(rc, methodName);
		}


  [Export]
    /**
    * stop And Close Workspace
    */
    public static void stopAndCloseWorkspace()
		{    
			registerLoggingMethodsToFlashingLib();
			ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int) Flashing.stopAndCloseWorkspace());
			
			string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
			reportMethod(rc, methodName);
		}

  [Export]
    /**
    * enable Flash Module
    *
    * @param[in]	 moduleName Name of the flash module to be enabled
    * @param[in]	 enable 1 to enable, 0 to disable
    */
    public static void enableFlashModule(string moduleName, int enable)
		{    
			registerLoggingMethodsToFlashingLib();
			ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int) Flashing.enableFlashModule(moduleName, enable));
			
			string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
			reportMethod(rc, methodName);
		}

  [Export]
    /**
     * Erase Sector in the given flash module, e.g. DF1.
     *
     * @param[in] flashModName      name of the flash module to be enabled, e.g. DF1
     * @param[in] sectorIndex       zero-based sector index
     */
    public static void eraseSectorInFlashModule(string flashModName, string sectorIndex)
		{    
			registerLoggingMethodsToFlashingLib();
			ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int) Flashing.eraseSectorInFlashModule(flashModName, sectorIndex));
			
			string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
			reportMethod(rc, methodName);
		}
 
  [Export]
    /**
    * erase Flash Module
    *
    * @param[in]	 moduleName Name of the flash module to be erased
    */
    public static void eraseFlashModule(string moduleName)
		{    
			registerLoggingMethodsToFlashingLib();
			ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int) Flashing.eraseFlashModule(moduleName));
			
			string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
			reportMethod(rc, methodName);
		}

  [Export]
    /**
    * flash File
    *
    * @param[in]	 fileToFlash Path of the file to be flashed
    */
    public static void flashFile(string fileToFlash)
		{    
			registerLoggingMethodsToFlashingLib();
			ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int) Flashing.flashFile(fileToFlash));
			
			string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
			reportMethod(rc, methodName);
		}
 
  [Export]
    /**
    * read Register
    *
    * @param[in] registerName      name of the register
    * @param[out] value            reference to the variable that will carry the read value
    */
    public static int readRegister(string registerName)
		{    
			registerLoggingMethodsToFlashingLib();
			ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int) Flashing.readRegister(registerName));
      
			string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
			reportMethod(rc, methodName);
      
      return (int) Execution.WaitForTask((canceltoken) => (int) Flashing.readLastOperationResult());
		}

  [Export]
    /**
    * write Register
    *
    * @param[in] registerName     name of the register
    * @param[in] newVal           new value
    */
    public static void writeRegister(string registerName,  int newVal)
		{    
			registerLoggingMethodsToFlashingLib();
			ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int) Flashing.writeRegister(registerName,  newVal));
			
			string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
			reportMethod(rc, methodName);
		}

  [Export]
    /**
    * read Variable
    *
    * @param[in] varExpression     name of the memory variable or symbol based expression 
    */
    public static int readVariable(string varExpression)
		{    
			registerLoggingMethodsToFlashingLib();
			ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int) Flashing.readVariable(varExpression));
      
			string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
			reportMethod(rc, methodName);
      
      return (int) Execution.WaitForTask((canceltoken) => (int) Flashing.readLastOperationResult());
    }


  [Export]
    /**
    * write Variable
    *
    * @param[in] varExpression    name of the variable or symbol based expression 
    * @param[in] newVal           new value
    */
    public static void writeVariable(string varExpression, int newVal)
 		{    
			registerLoggingMethodsToFlashingLib();
			ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int) Flashing.writeVariable(varExpression, newVal));
			
			string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
			reportMethod(rc, methodName);
		}

  [Export]
    /**
     * add BreakPoint
     *
     * @param[in] bpDescription    Textual description of breakpoint description 
     */
    public static void addBreakPoint(string bpDescription)
		{    
			registerLoggingMethodsToFlashingLib();
			ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int) Flashing.addBreakPoint(bpDescription));
			
			string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
			reportMethod(rc, methodName);
		}
 
  [Export]
    /**
     * enable BreakPoint
     *
     * @param[in] bpDescription    Textual description of breakpoint description 
     */
    public static void enableBreakPoint(string bpDescription)
		{    
			registerLoggingMethodsToFlashingLib();
			ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int) Flashing.enableBreakPoint(bpDescription));
			
			string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
			reportMethod(rc, methodName);
		}

  [Export]
    /**
     * disable BreakPoint
     *
     * @param[in] bpDescription    Textual description of breakpoint description 
     */
    public static void disableBreakPoint(string bpDescription) 
		{    
			registerLoggingMethodsToFlashingLib();
			ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int) Flashing.disableBreakPoint(bpDescription));
			
			string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
			reportMethod(rc, methodName);
		}
		

  [Export]
    /**
     * remove BreakPoint
     *
     * @param[in] bpDescription    String, that describes breakpoint location 
     */
    public static void removeBreakPoint(string bpDescription)
 		{    
			registerLoggingMethodsToFlashingLib();
			ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int) Flashing.removeBreakPoint(bpDescription));
			
			string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
			reportMethod(rc, methodName);
		}
       

  [Export]
    /**
     * disable All Breakpoints
     */
    public static void disableAllBreakpoints()
 		{    
			registerLoggingMethodsToFlashingLib();
			ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int) Flashing.disableAllBreakpoints());
			
			string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
			reportMethod(rc, methodName);
		}
       

  [Export]
    /**
     * enable All Breakpoints
     */
    public static void enableAllBreakpoints()
		{    
			registerLoggingMethodsToFlashingLib();
			ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int) Flashing.enableAllBreakpoints());
			
			string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
			reportMethod(rc, methodName);
		}
        

  [Export]
    /**
     * remove All Breakpoints
     */
    public static void removeAllBreakpoints()
		{    
			registerLoggingMethodsToFlashingLib();
			ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int) Flashing.removeAllBreakpoints());
			
			string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
			reportMethod(rc, methodName);
		}
        

  [Export]
    /**
     * Go : Starts target program from current instruction pointer.
     */
    public static void go()
		{    
			registerLoggingMethodsToFlashingLib();
			ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int) Flashing.go());
			
			string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
			reportMethod(rc, methodName);
		}
        

  [Export]
    /**
     * Break : Breaks execution of currently running program.
     */
    public static void breakExecution()
		{    
			registerLoggingMethodsToFlashingLib();
			ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int) Flashing.breakExecution());
			
			string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
			reportMethod(rc, methodName);
		}
        

  [Export]
    /**
     * WaitForHalt : Wait until debugger is halted by debug event (e.g. breakpoint hit).
     */
    public static void waitForHalt(int timeoutms)
		{    
			registerLoggingMethodsToFlashingLib();
			ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int) Flashing.waitForHalt(timeoutms));
			
			string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
			reportMethod(rc, methodName);
		}
        

  [Export]
    /**
     * Reload Program : Forces reload of loaded target program. This function includes target reset and places actual instruction pointer on begin of startup code after reload is completed.
     */
    public static void reloadProgram()
		{    
			registerLoggingMethodsToFlashingLib();
			ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int) Flashing.reloadProgram());
			
			string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
			reportMethod(rc, methodName);
		}
        

  [Export]
    /**
     * Reset Target: Forces target system reset.
     */
    public static void resetTarget()
		{    
			registerLoggingMethodsToFlashingLib();
			ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int) Flashing.resetTarget());
			
			string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
			reportMethod(rc, methodName);
		}
  [Export]
    /**
     * Connect: Connect to target.
     */
    public static void connect()
		{    
			registerLoggingMethodsToFlashingLib();
			ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int) FlashingUDE.connect());
			
			string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
			reportMethod(rc, methodName);
		}

  [Export]
    /**
     * Connect: Disconnect from target.
     */
    public static void disconnect()
		{    
			registerLoggingMethodsToFlashingLib();
			ReturnCodes rc = (ReturnCodes) Execution.WaitForTask((canceltoken) => (int) FlashingUDE.disconnect());
			
			string methodName = className + "." + (new StackTrace()).GetFrame(0).GetMethod().Name;
			reportMethod(rc, methodName);
		}
  
  
}

