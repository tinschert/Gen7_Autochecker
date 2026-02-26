using System;
using System.IO;
using System.Collections.ObjectModel;
using System.Linq;
using System.Text;
using System.Threading;
using System.Reflection;
using System.Diagnostics;
using Microsoft.Win32;


namespace FlashingLib
{
    /**
     * @copyright  (C) 2019-2020 Robert Bosch GmbH.\n
     * The reproduction, distribution and utilization of this file as well as
     * the communication of its contents to others without express authorization
     * is prohibited.\n
     * Offenders will be held liable for the payment of damages.\n
     * All rights reserved in the event of the grant of a patent, utility model or design.
     *
     * @file         Flashing.cs
     *
     * @brief Abstract layer for flashing. Provides methods that can be called by the user. 
     *
     * @details Abstract layer for flashing. Provides methods that can be called by the user. 
     * According to the user choice, the proper low level function is called (PLS UDE / Miniwiggler / Lauterbach / ...etc)
     */
    public class Flashing
    {
        public enum DebuggerType
        {
            UDE = 1,
            Miniwiggler = 2,
            Lauterbach = 3
        };

        //! debugger type (UDE, Miniwiggler, Lauterbach, ...)
        static DebuggerType debuggerType = DebuggerType.UDE;
        
        //! class name for reporting the function calls
        static string className = MethodBase.GetCurrentMethod().DeclaringType.Name;

        /**
        * Chooses a debugger type (UDE, Miniwiggler, Lauterbach, ...)
        *
        * @param[in]	 type type of the use debugger (UDE, Miniwiggler, Lauterbach, ...)
        */
        public static void chooseDebugger(DebuggerType type)
        {
            debuggerType = type;
        }

        /**
        * Calls the suitable startAndOpenWorkspace method according to the choosen debugger in variable (debuggerType)
        *
        * @param[in]	 workspacePath Path of the workspace to open and start
        */
        public static Logging.ReturnCodes startAndOpenWorkspace(string workspacePath)
        {
            try
            {
                string methodName = getMethodName(new StackTrace());
                Logging.ReturnCodes rc;
                switch (debuggerType)
                {
                    case DebuggerType.UDE:
                        rc = FlashingUDE.FlashingUDE_StartAndOpenWorkspace(workspacePath);
                        break;
                    case DebuggerType.Miniwiggler:
                        Logging.printFail(methodName, "Not implemented for Miniwiggler");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    case DebuggerType.Lauterbach:
                        Logging.printFail(methodName, "Not implemented for Lauterbach");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    default:
                        Logging.printFail(methodName, "Unknown Debugger Type: " + debuggerType.ToString());
                        rc = Logging.ReturnCodes.Fail;
                        break;
                }
                return rc;
            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
                return Logging.ReturnCodes.Fail;
            }
        }

        /**
        * Calls the suitable stopAndCloseWorkspace method according to the choosen debugger in variable (debuggerType)
        */
        public static Logging.ReturnCodes stopAndCloseWorkspace()
        {
            try
            {
                string methodName = getMethodName(new StackTrace());
                Logging.ReturnCodes rc;
                switch (debuggerType)
                {
                    case DebuggerType.UDE:
                        rc = FlashingUDE.FlashingUDE_StopAndCloseWorkspace();
                        break;
                    case DebuggerType.Miniwiggler:
                        Logging.printFail(methodName, "Not implemented for Miniwiggler");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    case DebuggerType.Lauterbach:
                        Logging.printFail(methodName, "Not implemented for Lauterbach");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    default:
                        Logging.printFail(methodName, "Unknown Debugger Type: " + debuggerType.ToString());
                        rc = Logging.ReturnCodes.Fail;
                        break;
                }
                return rc;
            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
                return Logging.ReturnCodes.Fail;
            }
        }

        /**
        * Calls the suitable enableFlashModule method according to the choosen debugger in variable (debuggerType)
        *
        * @param[in]	 moduleName Name of the flash module to be enabled
        * @param[in]	 enable 1 to enable, 0 to disable
        */
        public static Logging.ReturnCodes enableFlashModule(string moduleName, int enable)
        {
            try {
                string methodName = getMethodName(new StackTrace());
                Logging.ReturnCodes rc;
                switch (debuggerType)
                {
                    case DebuggerType.UDE:
                        rc = FlashingUDE.FlashingUDE_EnableFlashModule(moduleName, enable);
                        break;
                    case DebuggerType.Miniwiggler:
                        Logging.printFail(methodName, "Not implemented for Miniwiggler");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    case DebuggerType.Lauterbach:
                        Logging.printFail(methodName, "Not implemented for Lauterbach");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    default:
                        Logging.printFail(methodName, "Unknown Debugger Type: " + debuggerType.ToString());
                        rc = Logging.ReturnCodes.Fail;
                        break;
                }
                return rc;
            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
                return Logging.ReturnCodes.Fail;
            }
        }

        /**
         * Erase Sector in the given flash module, e.g. DF1.
         *
         * @param[in] flashModName      name of the flash module to be enabled, e.g. DF1
         * @param[in] sectorIndex       zero-based sector index
         */
        public static Logging.ReturnCodes eraseSectorInFlashModule(string flashModName, string sectorIndex)
        {
            try
            {
                string methodName = getMethodName(new StackTrace());
                Logging.ReturnCodes rc;
                switch (debuggerType)
                {
                    case DebuggerType.UDE:
                        rc = FlashingUDE.FlashingUDE_EraseSectorInFlashModule(flashModName, sectorIndex);
                        break;
                    case DebuggerType.Miniwiggler:
                        Logging.printFail(methodName, "Not implemented for Miniwiggler");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    case DebuggerType.Lauterbach:
                        Logging.printFail(methodName, "Not implemented for Lauterbach");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    default:
                        Logging.printFail(methodName, "Unknown Debugger Type: " + debuggerType.ToString());
                        rc = Logging.ReturnCodes.Fail;
                        break;
                }
                return rc;
            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
                return Logging.ReturnCodes.Fail;
            }
        }

        /**
        * Calls the suitable eraseFlashModule method according to the choosen debugger in variable (debuggerType)
        *
        * @param[in]	 moduleName Name of the flash module to be erased
        */
        public static Logging.ReturnCodes eraseFlashModule(string moduleName)
        {
            try
            {
                string methodName = getMethodName(new StackTrace());
                Logging.ReturnCodes rc;
                switch (debuggerType)
                {
                    case DebuggerType.UDE:
                        rc = FlashingUDE.FlashingUDE_EraseFlashModule(moduleName);
                        break;
                    case DebuggerType.Miniwiggler:
                        Logging.printFail(methodName, "Not implemented for Miniwiggler");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    case DebuggerType.Lauterbach:
                        Logging.printFail(methodName, "Not implemented for Lauterbach");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    default:
                        Logging.printFail(methodName, "Unknown Debugger Type: " + debuggerType.ToString());
                        rc = Logging.ReturnCodes.Fail;
                        break;
                }
                return rc;
            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
                return Logging.ReturnCodes.Fail;
            }
        }

        /**
        * Calls the suitable flashing method  according to the choosen debugger in variable (debuggerType)
        *
        * @param[in]	 fileToFlash Path of the file to be flashed
        */
        public static Logging.ReturnCodes flashFile(string fileToFlash)
        {
            try
            {
                string methodName = getMethodName(new StackTrace());
                Logging.ReturnCodes rc;
                switch (debuggerType)
                {
                    case DebuggerType.UDE:
                        rc = FlashingUDE.FlashingUDE_FlashWithMemTool(fileToFlash);
                        break;
                    case DebuggerType.Miniwiggler:
                        Logging.printFail(methodName, "Not implemented for Miniwiggler");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    case DebuggerType.Lauterbach:
                        Logging.printFail(methodName, "Not implemented for Lauterbach");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    default:
                        Logging.printFail(methodName, "Unknown Debugger Type: " + debuggerType.ToString());
                        rc = Logging.ReturnCodes.Fail;
                        break;
                }
                return rc;
            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
                return Logging.ReturnCodes.Fail;
            }
        }

        /**
        * get Result - shall be called directly after an operation that shall return a result. ex: readRegister
        *
        */
        public static int readLastOperationResult() {
            try
            {
                string methodName = getMethodName(new StackTrace());
                int result = 0;
                switch (debuggerType)
                {
                    case DebuggerType.UDE:
                        result = FlashingUDE.FlashingUDE_ReadLastOperationResult();
                        break;
                    case DebuggerType.Miniwiggler:
                        Logging.printFail(methodName, "Not implemented for Miniwiggler");
                        break;
                    case DebuggerType.Lauterbach:
                        Logging.printFail(methodName, "Not implemented for Lauterbach");
                        break;
                    default:
                        Logging.printFail(methodName, "Unknown Debugger Type: " + debuggerType.ToString());
                        break;
                }
                return result;
            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
                return 0;
            }
        }

        /**
        * Calls the suitable flashing method  according to the choosen debugger in variable (debuggerType)
        *
        * @param[in] registerName      name of the register
        */
        public static Logging.ReturnCodes readRegister(string registerName)
        {
            try
            {
                string methodName = getMethodName(new StackTrace());
                Logging.ReturnCodes rc;
                switch (debuggerType)
                {
                    case DebuggerType.UDE:
                        rc = FlashingUDE.FlashingUDE_ReadRegister(registerName);
                        break;
                    case DebuggerType.Miniwiggler:
                        Logging.printFail(methodName, "Not implemented for Miniwiggler");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    case DebuggerType.Lauterbach:
                        Logging.printFail(methodName, "Not implemented for Lauterbach");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    default:
                        Logging.printFail(methodName, "Unknown Debugger Type: " + debuggerType.ToString());
                        rc = Logging.ReturnCodes.Fail;
                        break;
                }
                return rc;
            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
                return Logging.ReturnCodes.Fail;
            }
        }

        /**
        * Calls the suitable flashing method  according to the choosen debugger in variable (debuggerType)
        *
        * @param[in] registerName     name of the register
        * @param[in] newVal           new value
        */
        public static Logging.ReturnCodes writeRegister(string registerName,  int newVal)
        {
            try
            {
                string methodName = getMethodName(new StackTrace());
                Logging.ReturnCodes rc;
                switch (debuggerType)
                {
                    case DebuggerType.UDE:
                        rc = FlashingUDE.FlashingUDE_WriteRegister(registerName, newVal);
                        break;
                    case DebuggerType.Miniwiggler:
                        Logging.printFail(methodName, "Not implemented for Miniwiggler");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    case DebuggerType.Lauterbach:
                        Logging.printFail(methodName, "Not implemented for Lauterbach");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    default:
                        Logging.printFail(methodName, "Unknown Debugger Type: " + debuggerType.ToString());
                        rc = Logging.ReturnCodes.Fail;
                        break;
                }
                return rc;
            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
                return Logging.ReturnCodes.Fail;
            }
        }

        /**
        * Calls the suitable flashing method  according to the choosen debugger in variable (debuggerType)
        *
        * @param[in] varExpression     name of the memory variable or symbol based expression 
        */
        public static Logging.ReturnCodes readVariable(string varExpression)
        {
            try
            {
                string methodName = getMethodName(new StackTrace());
                Logging.ReturnCodes rc;
                switch (debuggerType)
                {
                    case DebuggerType.UDE:
                        rc = FlashingUDE.FlashingUDE_ReadVariable(varExpression);
                        break;
                    case DebuggerType.Miniwiggler:
                        Logging.printFail(methodName, "Not implemented for Miniwiggler");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    case DebuggerType.Lauterbach:
                        Logging.printFail(methodName, "Not implemented for Lauterbach");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    default:
                        Logging.printFail(methodName, "Unknown Debugger Type: " + debuggerType.ToString());
                        rc = Logging.ReturnCodes.Fail;
                        break;
                }
                return rc;
            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
                return Logging.ReturnCodes.Fail;
            }
        }

        /**
        * Calls the suitable flashing method  according to the choosen debugger in variable (debuggerType)
        *
        * @param[in] varExpression    name of the variable or symbol based expression 
        * @param[in] newVal           new value
        */
        public static Logging.ReturnCodes writeVariable(string varExpression, int newVal)
        {
            try
            {
                string methodName = getMethodName(new StackTrace());
                Logging.ReturnCodes rc;
                switch (debuggerType)
                {
                    case DebuggerType.UDE:
                        rc = FlashingUDE.FlashingUDE_WriteVariable(varExpression, newVal);
                        break;
                    case DebuggerType.Miniwiggler:
                        Logging.printFail(methodName, "Not implemented for Miniwiggler");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    case DebuggerType.Lauterbach:
                        Logging.printFail(methodName, "Not implemented for Lauterbach");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    default:
                        Logging.printFail(methodName, "Unknown Debugger Type: " + debuggerType.ToString());
                        rc = Logging.ReturnCodes.Fail;
                        break;
                }
                return rc;
            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
                return Logging.ReturnCodes.Fail;
            }
}

        /**
         * FlashingUDE_AddBreakPoint
         *
         * @param[in] bpDescription    Textual description of breakpoint description 
         */
        public static Logging.ReturnCodes addBreakPoint(string bpDescription)
        {
            try
            {
                string methodName = getMethodName(new StackTrace());
                Logging.ReturnCodes rc;
                switch (debuggerType)
                {
                    case DebuggerType.UDE:
                        rc = FlashingUDE.FlashingUDE_AddBreakPoint(bpDescription);
                        break;
                    case DebuggerType.Miniwiggler:
                        Logging.printFail(methodName, "Not implemented for Miniwiggler");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    case DebuggerType.Lauterbach:
                        Logging.printFail(methodName, "Not implemented for Lauterbach");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    default:
                        Logging.printFail(methodName, "Unknown Debugger Type: " + debuggerType.ToString());
                        rc = Logging.ReturnCodes.Fail;
                        break;
                }
                return rc;
            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
                return Logging.ReturnCodes.Fail;
            }
        }

        /**
         * enableBreakPoint
         *
         * @param[in] bpDescription    Textual description of breakpoint description 
         */
        public static Logging.ReturnCodes enableBreakPoint(string bpDescription)
        {
            try
            {
                string methodName = getMethodName(new StackTrace());
                Logging.ReturnCodes rc;
                switch (debuggerType)
                {
                    case DebuggerType.UDE:
                        rc = FlashingUDE.FlashingUDE_EnableBreakPoint(bpDescription);
                        break;
                    case DebuggerType.Miniwiggler:
                        Logging.printFail(methodName, "Not implemented for Miniwiggler");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    case DebuggerType.Lauterbach:
                        Logging.printFail(methodName, "Not implemented for Lauterbach");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    default:
                        Logging.printFail(methodName, "Unknown Debugger Type: " + debuggerType.ToString());
                        rc = Logging.ReturnCodes.Fail;
                        break;
                }
                return rc;
            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
                return Logging.ReturnCodes.Fail;
            }
        }

        /**
         * disableBreakPoint
         *
         * @param[in] bpDescription    Textual description of breakpoint description 
         */
        public static Logging.ReturnCodes disableBreakPoint(string bpDescription) {
            try
            {
                string methodName = getMethodName(new StackTrace());
                Logging.ReturnCodes rc;
                switch (debuggerType)
                {
                    case DebuggerType.UDE:
                        rc = FlashingUDE.FlashingUDE_DisableBreakPoint(bpDescription);
                        break;
                    case DebuggerType.Miniwiggler:
                        Logging.printFail(methodName, "Not implemented for Miniwiggler");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    case DebuggerType.Lauterbach:
                        Logging.printFail(methodName, "Not implemented for Lauterbach");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    default:
                        Logging.printFail(methodName, "Unknown Debugger Type: " + debuggerType.ToString());
                        rc = Logging.ReturnCodes.Fail;
                        break;
                }
                return rc;
            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
                return Logging.ReturnCodes.Fail;
            }
        }

        /**
         * removeBreakPoint
         *
         * @param[in] bpDescription    String, that describes breakpoint location 
         */
        public static Logging.ReturnCodes removeBreakPoint(string bpDescription)
        {
            try
            {
                string methodName = getMethodName(new StackTrace());
                Logging.ReturnCodes rc;
                switch (debuggerType)
                {
                    case DebuggerType.UDE:
                        rc = FlashingUDE.FlashingUDE_RemoveBreakPoint(bpDescription);
                        break;
                    case DebuggerType.Miniwiggler:
                        Logging.printFail(methodName, "Not implemented for Miniwiggler");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    case DebuggerType.Lauterbach:
                        Logging.printFail(methodName, "Not implemented for Lauterbach");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    default:
                        Logging.printFail(methodName, "Unknown Debugger Type: " + debuggerType.ToString());
                        rc = Logging.ReturnCodes.Fail;
                        break;
                }
                return rc;
            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
                return Logging.ReturnCodes.Fail;
            }
}

        /**
         * disableAllBreakpoints
         */
        public static Logging.ReturnCodes disableAllBreakpoints()
        {
            try
            {
                string methodName = getMethodName(new StackTrace());
                Logging.ReturnCodes rc;
                switch (debuggerType)
                {
                    case DebuggerType.UDE:
                        rc = FlashingUDE.FlashingUDE_DisableAllBreakpoints();
                        break;
                    case DebuggerType.Miniwiggler:
                        Logging.printFail(methodName, "Not implemented for Miniwiggler");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    case DebuggerType.Lauterbach:
                        Logging.printFail(methodName, "Not implemented for Lauterbach");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    default:
                        Logging.printFail(methodName, "Unknown Debugger Type: " + debuggerType.ToString());
                        rc = Logging.ReturnCodes.Fail;
                        break;
                }
                return rc;
            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
                return Logging.ReturnCodes.Fail;
            }
        }

        /**
         * enableAllBreakpoints
         */
        public static Logging.ReturnCodes enableAllBreakpoints()
        {
            try
            {
                string methodName = getMethodName(new StackTrace());
                Logging.ReturnCodes rc;
                switch (debuggerType)
                {
                    case DebuggerType.UDE:
                        rc = FlashingUDE.FlashingUDE_EnableAllBreakpoints();
                        break;
                    case DebuggerType.Miniwiggler:
                        Logging.printFail(methodName, "Not implemented for Miniwiggler");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    case DebuggerType.Lauterbach:
                        Logging.printFail(methodName, "Not implemented for Lauterbach");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    default:
                        Logging.printFail(methodName, "Unknown Debugger Type: " + debuggerType.ToString());
                        rc = Logging.ReturnCodes.Fail;
                        break;
                }
                return rc;
            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
                return Logging.ReturnCodes.Fail;
            }
        }

        /**
         * removeAllBreakpoints
         */
        public static Logging.ReturnCodes removeAllBreakpoints()
        {
            try
            {
                string methodName = getMethodName(new StackTrace());
                Logging.ReturnCodes rc;
                switch (debuggerType)
                {
                    case DebuggerType.UDE:
                        rc = FlashingUDE.FlashingUDE_RemoveAllBreakpoints();
                        break;
                    case DebuggerType.Miniwiggler:
                        Logging.printFail(methodName, "Not implemented for Miniwiggler");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    case DebuggerType.Lauterbach:
                        Logging.printFail(methodName, "Not implemented for Lauterbach");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    default:
                        Logging.printFail(methodName, "Unknown Debugger Type: " + debuggerType.ToString());
                        rc = Logging.ReturnCodes.Fail;
                        break;
                }
                return rc;
            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
                return Logging.ReturnCodes.Fail;
            }
        }

        /**
         * Go : Starts target program from current instruction pointer.
         */
        public static Logging.ReturnCodes go()
        {
            try
            {
                string methodName = getMethodName(new StackTrace());
                Logging.ReturnCodes rc;
                switch (debuggerType)
                {
                    case DebuggerType.UDE:
                        rc = FlashingUDE.FlashingUDE_Go();
                        break;
                    case DebuggerType.Miniwiggler:
                        Logging.printFail(methodName, "Not implemented for Miniwiggler");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    case DebuggerType.Lauterbach:
                        Logging.printFail(methodName, "Not implemented for Lauterbach");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    default:
                        Logging.printFail(methodName, "Unknown Debugger Type: " + debuggerType.ToString());
                        rc = Logging.ReturnCodes.Fail;
                        break;
                }
                return rc;
            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
                return Logging.ReturnCodes.Fail;
            }
        }

        /**
         * Break : Breaks execution of currently running program.
         */
        public static Logging.ReturnCodes breakExecution()
        {
            try
            {
                string methodName = getMethodName(new StackTrace());
                Logging.ReturnCodes rc;
                switch (debuggerType)
                {
                    case DebuggerType.UDE:
                        rc = FlashingUDE.FlashingUDE_Break();
                        break;
                    case DebuggerType.Miniwiggler:
                        Logging.printFail(methodName, "Not implemented for Miniwiggler");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    case DebuggerType.Lauterbach:
                        Logging.printFail(methodName, "Not implemented for Lauterbach");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    default:
                        Logging.printFail(methodName, "Unknown Debugger Type: " + debuggerType.ToString());
                        rc = Logging.ReturnCodes.Fail;
                        break;
                }
                return rc;
            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
                return Logging.ReturnCodes.Fail;
            }
        }

        /**
         * WaitForHalt : Wait until debugger is halted by debug event (e.g. breakpoint hit).
         */
        public static Logging.ReturnCodes waitForHalt(int timeoutms)
        {
            try
            {
                string methodName = getMethodName(new StackTrace());
                Logging.ReturnCodes rc;
                switch (debuggerType)
                {
                    case DebuggerType.UDE:
                        rc = FlashingUDE.FlashingUDE_WaitForHalt(timeoutms);
                        break;
                    case DebuggerType.Miniwiggler:
                        Logging.printFail(methodName, "Not implemented for Miniwiggler");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    case DebuggerType.Lauterbach:
                        Logging.printFail(methodName, "Not implemented for Lauterbach");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    default:
                        Logging.printFail(methodName, "Unknown Debugger Type: " + debuggerType.ToString());
                        rc = Logging.ReturnCodes.Fail;
                        break;
                }
                return rc;
            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
                return Logging.ReturnCodes.Fail;
            }
        }

        /**
         * Reload Program : Forces reload of loaded target program. This function includes target reset and places actual instruction pointer on begin of startup code after reload is completed.
         */
        public static Logging.ReturnCodes reloadProgram()
        {
            try
            {
                string methodName = getMethodName(new StackTrace());
                Logging.ReturnCodes rc;
                switch (debuggerType)
                {
                    case DebuggerType.UDE:
                        rc = FlashingUDE.FlashingUDE_ReloadProgram();
                        break;
                    case DebuggerType.Miniwiggler:
                        Logging.printFail(methodName, "Not implemented for Miniwiggler");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    case DebuggerType.Lauterbach:
                        Logging.printFail(methodName, "Not implemented for Lauterbach");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    default:
                        Logging.printFail(methodName, "Unknown Debugger Type: " + debuggerType.ToString());
                        rc = Logging.ReturnCodes.Fail;
                        break;
                }
                return rc;
            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
                return Logging.ReturnCodes.Fail;
            }
        }

        /**
         * Reset Target: Forces target system reset.
         */
        public static Logging.ReturnCodes resetTarget()
        {
            try
            {
                string methodName = getMethodName(new StackTrace());
                Logging.ReturnCodes rc;
                switch (debuggerType)
                {
                    case DebuggerType.UDE:
                        rc = FlashingUDE.FlashingUDE_ResetTarget();
                        break;
                    case DebuggerType.Miniwiggler:
                        Logging.printFail(methodName, "Not implemented for Miniwiggler");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    case DebuggerType.Lauterbach:
                        Logging.printFail(methodName, "Not implemented for Lauterbach");
                        rc = Logging.ReturnCodes.Fail;
                        break;
                    default:
                        Logging.printFail(methodName, "Unknown Debugger Type: " + debuggerType.ToString());
                        rc = Logging.ReturnCodes.Fail;
                        break;
                }
                return rc;
            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
                return Logging.ReturnCodes.Fail;
            }
        }

        private static string getMethodName(StackTrace trace)
        {
            string methodName = trace.GetFrame(0).GetMethod().Name;
            methodName = className + "." + methodName;
            return methodName;
        }
    }
}

