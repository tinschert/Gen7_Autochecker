using System;
using System.IO;
using System.Collections.ObjectModel;
using System.Linq;
using System.Text;
using System.Threading;
using System.Reflection;
using System.Diagnostics;
using Microsoft.Win32;

using FlashingLib;

using UDELib;
using UDELauncherLib;

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
     * @file         FlashingUDE.cs
     *
     * @brief Class for Flashing using PLS UDE Debugger
     *
     * @details Class for Flashing using PLS UDE Debugger\n
     */
    public class FlashingUDE
    {

        //! class name for reporting the function calls
        static string className = MethodBase.GetCurrentMethod().DeclaringType.Name;

        //! path to the HEX file
        static string hexFilePath = "";
        //! path to the ELF file
        static string elfFilePath = "";

        //! launcher for starting the UDE workspace
        static UDELauncherLib.UDELauncher UDELauncher = null;
        //! the UDE debugger application
        static UDELib.IUDEApplication UDEApplication = null;
        //! the loaded workspace of the UDE application
        static UDELib.IUDEWorkspace UDEWorkspace = null;
        //! the UDE debugger
        static UDELib.IUDEDebuggerInterface UDEDebugger = null;

        static UDELib.DIUDEMemtool UDEMemToolAddin = null;

        //! operation result
        static int operationResult = 0;

        /** 
         * Constructor.\n
         * Initializes the member UDELauncher.\n
         * UDE 4.10 UDENetCOMLib.UDELauncher.dll must be copied from the\n
         *          UDE installation to Exec64 folder of the CANoe installation\n
         * UDE 5.0  copying this file is not necessary
         */
        static FlashingUDE()
        {
            UDELauncher = new UDELauncherLib.UDELauncher();
        }

        /**
         * Start the application "UDEVisualPlatform.exe" 
         * and load the given workspace.
         *
         * @param[in]	  WorkspacePath the path to the workspace file (*.wsx)
         */
        public static Logging.ReturnCodes FlashingUDE_StartAndOpenWorkspace(string WorkspacePath)
        {
            string methodName = getMethodName(new StackTrace());

            Logging.ReturnCodes rc;

            rc = _UDE_StartAndOpenWorkspace(WorkspacePath);

            switch (rc)
            {
                case Logging.ReturnCodes.Pass:
                    Logging.printPass(methodName, "UDE workspace opened");
                    break;
                case Logging.ReturnCodes.Error:
                    Logging.printError(methodName, "UDE workspace not opened");
                    break;
                case Logging.ReturnCodes.Fail:
                    Logging.printFail(methodName, "UDE workspace not opened");
                    break;
                default:
                    Logging.printFail(className, "No valid return code: " + rc.ToString());
                    break;
            }
            return rc;
        }



        /**
         * Start the application "UDEVisualPlatform.exe" 
         * and load the given workspace.
         *
         * @param[in]	  WorkspacePath the path to the workspace file (*.wsx)
         */
        private static Logging.ReturnCodes _UDE_StartAndOpenWorkspace(string WorkspacePath)
        {
            string methodName = getMethodName(new StackTrace());

            Logging.ReturnCodes rc = Logging.ReturnCodes.Fail;

            try
            {
                UDEApplication = (UDELib.IUDEApplication)UDELauncher.StartAndOpenWorkspace("UDEVisualPlatform.exe",
                                                                                            WorkspacePath,
                                                                                            "--dont-reload");

                UDEWorkspace = (UDELib.IUDEWorkspace)UDEApplication.Workspace;

                UDEDebugger = (UDELib.IUDEDebuggerInterface)UDEWorkspace.GetCoreDebugger(0);

                UDEMemToolAddin = (UDELib.DIUDEMemtool)UDEDebugger.GetMemtool();

                rc = Logging.ReturnCodes.Pass;
                Logging.printPass(methodName, "UDE workspace opened");
            }
            catch (Exception e)
            {
                rc = Logging.ReturnCodes.Fail;
                Logging.printFail(methodName, e.ToString());
            }

            return (rc);
        }

        /**
         * Stores the paths to the HEX and the ELF file for later use.
         *
         * @param[in]	  hexFile the path to the HEX file
         * @param[in]	  elfFile the path to the ELF file
         *
         */
        public static int FlashingUDE_StoreHexElfFiles(string hexFile, string elfFile)
        {
            hexFilePath = hexFile;
            elfFilePath = elfFile;

            return 1;
        }


        /**
         * Flash the given file with the Memtool Addin of the UDEDebugger.
         *
         * @param[in] hexFile path to the HEX file
         */
        public static Logging.ReturnCodes FlashingUDE_FlashWithMemTool(string hexFile)
        {
            string methodName = getMethodName(new StackTrace());
            Logging.ReturnCodes rc = Logging.ReturnCodes.Fail;
            bool hexFileLoaded;

            // Lock user interface
            UDEWorkspace.EnableUserInterface = false;
            UDEMemToolAddin.SetConfigParam("ScriptIsRunning", true);
            Logging.printInfo(methodName, "User interface locked...");

            UDELib.DIUDECfgProfile userProfile = (UDELib.DIUDECfgProfile)UDEWorkspace.UserProfile;
            userProfile.SetConfigParam("AutoLoadElf", "System", false);

            if (!File.Exists(hexFile))
            {
                Logging.printFail(methodName, String.Format("File not exists: {0}", hexFile));
                throw new FileNotFoundException(String.Format("UDE_FlashWithMemTool: File not exists: {0}", hexFile));
            }

            try
            {
                hexFileLoaded = UDEDebugger.LoadProgramFile(hexFile);
                if (hexFileLoaded)
                {
                    rc = Logging.ReturnCodes.Pass;

                    Logging.printInfo(methodName, String.Format("MemTool loaded HEX file: {0}", hexFile));

                    int index = 0;
                    for (index = 0; index < UDEMemToolAddin.NumOfFlashMods; index++)
                    {
                        Logging.printInfo(methodName, String.Format("Programming FlashMod[{0}] {1}", index, UDEMemToolAddin.FlashMod[index].Name));
                        UDEMemToolAddin.FlashMod[index].SetConfigParam("AutoErase", true);
                        UDEMemToolAddin.FlashMod[index].ProgramSections();
                    }

                    rc = Logging.ReturnCodes.Pass;
                    Logging.printPass(methodName, String.Format("DASy programmed with HEX file: {0}", hexFile));
                }
                else
                {
                    rc = Logging.ReturnCodes.Fail;
                    Logging.printFail(methodName, String.Format("MemTool could not load HEX file: {0}", hexFile));
                }
            }
            catch (Exception e)
            {
                //      Report.TestStepErrorInTestSystem(e.ToString());
                rc = Logging.ReturnCodes.Fail;
                Logging.printFail(methodName, e.ToString());
            }
            finally
            {
                // Unlock user interface
                userProfile.SetConfigParam("AutoLoadElf", "System", true);
                UDEMemToolAddin.SetConfigParam("ScriptIsRunning", false);
                UDEWorkspace.EnableUserInterface = true;
                Logging.printInfo(methodName, "User interface unlocked...");
            }

            return (rc);
        }

        /**
         * Flash the given file with the Memtool Addin of the UDE debugger.\n
         * The file to be flashed has to be loaded with the
         * function UDE_LoadHexElfFiles() before.
         *
         * There is also an overloaded function with the HEX file as a parameters. 
         */
        public static Logging.ReturnCodes FlashingUDE_FlashWithMemTool()
        {
            string methodName = getMethodName(new StackTrace());

            if (hexFilePath == "")
            {
                Logging.printFail(methodName, "UDE_FlashWithMemTool: No HEX file path stored. Hint: Use UDE_LoadHexElfFiles() before calling this function.");
                throw new Exception("UDE_FlashWithMemTool: No HEX file path stored. Hint: Use UDE_LoadHexElfFiles() before calling this function.");
            }

            try
            {
                FlashingUDE_FlashWithMemTool(hexFilePath);
            }
            catch (Exception e)
            {
                Logging.printFail(methodName, e.ToString());
            }

            return (Logging.ReturnCodes.Pass);
        }

        /**
         * Flash the given HEX file with the command line interface of MemtoolCli.exe.
         *
         * @param[in] hexFile       absolute path to the HEX file
         * @param[in] cfgFilePath   absolute path to the configuration file
         */
        public static Logging.ReturnCodes FlashingUDE_FlashWithMemToolCli(string hexFile, string cfgFilePath)
        {
            string methodName = (new StackTrace()).GetFrame(0).GetMethod().Name;
            methodName = className + "." + methodName;

            if (!File.Exists(hexFile))
            {
                Logging.printFail(methodName, String.Format("UDE_FlashWithMemToolCli: File not exists: {0}", hexFile));
                throw new FileNotFoundException(String.Format("UDE_FlashWithMemToolCli: File not exists: {0}", hexFile));
            }

            try
            {
                String MemtoolCliExePath = FlashingUDE_getMemtoolCliExePath();

                FlashingUDE_FlashWithMemToolCli(MemtoolCliExePath,
                                        hexFile,
                                        cfgFilePath);
            }
            catch (Exception e)
            {
                //      Report.TestStepErrorInTestSystem(e.ToString());
                Logging.printFail(methodName, e.ToString());
            }

            return Logging.ReturnCodes.Pass;
        }

        /**
         * Enables or disabled the given flash module, e.g. DF1.
         *
         * @param[in] flashModName      name of the flash module to be enabled, e.g. DF1
         * @param[in] enabled           1: enabled, 2: disabled
         */
        public static Logging.ReturnCodes FlashingUDE_EnableFlashModule(string flashModName, int enabled)
        {
            string methodName = getMethodName(new StackTrace());

            UDELib.DIUDETargetManager targetManager = (UDELib.DIUDETargetManager)UDEWorkspace.TargetManager;

            DIUDETargInfo targetInfo = (UDELib.DIUDETargInfo)UDEWorkspace.TargetInfo;
            Logging.printInfo(methodName, String.Format("Number of MCUs: {0}", targetInfo.NumOfMcus));

            UDELib.DIUDEMcuInfo mcuInfo = targetInfo.GetMcuInfo(0);
            Logging.printInfo(methodName, String.Format("MCU name: {0}", mcuInfo.Name));

            DIUDEFlashMod flashMod = UDEMemToolAddin.GetFlashMod(flashModName);
            flashMod.Enabled = enabled;
            if (flashMod.Enabled == enabled)
            {
                Logging.printPass(methodName, "Memory:" + flashMod.Name + " enable is changed to " + flashMod.Enabled);
            }
            else
            {
                Logging.printPass(methodName, "Memory:" + flashMod.Name + " enable is " + flashMod.Enabled);
            }


            return Logging.ReturnCodes.Pass;
        }

        /**
         * Erase Sector in the given flash module, e.g. DF1.
         *
         * @param[in] flashModName      name of the flash module to be enabled, e.g. DF1
         * @param[in] sectorIndex       zero-based sector index
         */
        public static Logging.ReturnCodes FlashingUDE_EraseSectorInFlashModule(string flashModName, string sectorIndex)
        {
            string methodName = getMethodName(new StackTrace());

            UDELib.DIUDETargetManager targetManager = (UDELib.DIUDETargetManager)UDEWorkspace.TargetManager;

            DIUDEFlashMod flashMod = UDEMemToolAddin.GetFlashMod(flashModName);
            var rc = flashMod.Erase(sectorIndex);
            if (rc)
            {
                Logging.printPass(methodName, "Memory:" + flashMod.Name + " | Sector: " + sectorIndex + " is erased successfully!");
                return Logging.ReturnCodes.Pass;
            }
            else
            {
                Logging.printFail(methodName, "Memory:" + flashMod.Name + " | failed to erase Sector: " + sectorIndex + " !");
                return Logging.ReturnCodes.Fail;
            }
        }

        /**
         * Erase the flash module given bei it's name.
         *
         * @param[in] flashModName    name of the flash module to be erased, e.g. DF1
         */
        public static Logging.ReturnCodes FlashingUDE_EraseFlashModule(string flashModName)
        {
            string methodName = getMethodName(new StackTrace());

            try
            {
                DIUDEFlashMod flashMod_DF1 = UDEMemToolAddin.GetFlashMod(flashModName);
                flashMod_DF1.Erase();
                Logging.printPass(methodName, String.Format("UDE_EraseFlashModule: Successfully erased flash module {0}", flashModName));
            }
            catch (Exception e)
            {
                Exception ex = new Exception(String.Format("UDE_EraseFlashModule: could not erase flash module {0}",
                                                           flashModName),
                                             e);
                //      Report.TestStepErrorInTestSystem(ex.ToString());
                Logging.printFail(methodName, ex.ToString());
            }

            return Logging.ReturnCodes.Pass;
        }

        /**
         * Release objects and close UDE instance.
         *
         */
        public static Logging.ReturnCodes FlashingUDE_StopAndCloseWorkspace()
        {
            string methodName = getMethodName(new StackTrace());

            UDELauncher.StopInstance(UDEApplication);
            Logging.printPass(methodName, "UDE workspace closed");

            return Logging.ReturnCodes.Pass;
        }

        /**
         * Execute a sleep call.
         *
         * @param[in] Milliseconds sleep period in ms
         *
         */
        public static int FlashingUDE_WorkspaceSleep(int Milliseconds)
        {
            UDEWorkspace.Sleep(Milliseconds);
            return (1);
        }

        /**
         * Start the target application.
         *
         */
        public static int FlashingUDE_StartApplication()
        {
            UDEDebugger.Go();

            return (1);
        }

        /**
         * Read the version information of the UDE debugger from the registry
         * and return the absolute path to MemtoolCli.exe.\n
         * The path is build in ths way:\n
         * String.Format("C:\\Program Files (x86)\\pls\\UDE {0}\\MemtoolCli.exe", udeVersion)
         *
         * @return absolute path to MemtoolCli.exe
         */
        public static String FlashingUDE_getMemtoolCliExePath()
        {
            // get UDE version from the registry
            String udeVersion = (String)Registry.GetValue("HKEY_CLASSES_ROOT\\UDEDebugger.Application\\CurVer", "", "");

            // udeVersion has this format: UDEDebugger.Application.4.10
            // extract the version number
            string[] udeVersionArr = udeVersion.Split('.');
            udeVersion = String.Format("{0}.{1}", udeVersionArr[2], udeVersionArr[3]);

            return String.Format("C:\\Program Files (x86)\\pls\\UDE {0}\\MemtoolCli.exe", udeVersion);
        }

        /**
         * Flash the given HEX file with the command line interface of MemtoolCli.exe.
         *
         * @param[in] memtoolPath     absolute path to MemtoolCli.exe
         * @param[in] hexFile         absolute path to the HEX file
         * @param[in] configFilePath  absolute path to the UDE debugger configuration file
         */
        public static void FlashingUDE_FlashWithMemToolCli(string memtoolPath, string hexFile, string configFilePath)
        {
            string methodName = getMethodName(new StackTrace());

            Logging.printInfo(methodName, "Flashing with MemtoolCli. This might take a while...");

            // build the arguments for MemtoolCli.exe
            string arguments = String.Format("PROGRAM \"{0}\" -c \"{1}\"", hexFile, configFilePath);

            Process process = new Process
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = memtoolPath,
                    Arguments = arguments,
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    CreateNoWindow = true
                }
            };
            process.Start();

            // Log the flashing process to CANoe's write window
            while (!process.StandardOutput.EndOfStream)
            {
                string line = process.StandardOutput.ReadLine();
                Logging.printInfo(methodName, line);
            }

            // Wait until the flashing process has finished
            if (!process.HasExited)
            {
                process.WaitForExit();
            }

            if (process.ExitCode != 0)
            {
                throw new Exception("UDE_FlashWithMemToolCli: Failed to flash the ECU. Check the write window for more details.");
            }

            Logging.printPass(methodName, "Finished flashing successfully");

        }


        /**
         * Read Register
         *
         * @param[in] registerName     name of the register
         */
        public static Logging.ReturnCodes FlashingUDE_ReadRegister(string registerName)
        {
            string methodName = getMethodName(new StackTrace());
            Logging.printInfo(methodName, "Reading Register " + registerName);

            operationResult = UDEDebugger.ReadRegister(registerName);
            Logging.printInfo(methodName, "Value is " + operationResult);
            return Logging.ReturnCodes.Pass;
        }

        /**
         * Write Register
         *
         * @param[in] registerName     name of the register
         * @param[in] newVal           new value
         */
        public static Logging.ReturnCodes FlashingUDE_WriteRegister(string registerName, int newVal)
        {
            string methodName = getMethodName(new StackTrace());
            Logging.printInfo(methodName, "Writing value " + newVal.ToString() + " to Register " + registerName);

            var val = UDEDebugger.WriteRegister(registerName, newVal);
            if (val == true)
            {
                Logging.printPass(methodName, "Write successful");
                return Logging.ReturnCodes.Pass;
            }
            else
            {
                Logging.printFail(methodName, "Write failed");
                return Logging.ReturnCodes.Fail;
            }
        }

        /**
         * Read Variable
         *
         * @param[in] varExpression     name of the memory variable or symbol based expression 
         */
        public static Logging.ReturnCodes FlashingUDE_ReadVariable(string variableName)
        {
            string methodName = getMethodName(new StackTrace());
            Logging.printInfo(methodName, "Reading Variable " + variableName);

            operationResult = UDEDebugger.ReadVariable(variableName);
            Logging.printInfo(methodName, "Value is " + operationResult);
            return Logging.ReturnCodes.Pass;
        }



        /**
         * Write Variable
         *
         * @param[in] varExpression    name of the variable or symbol based expression 
         * @param[in] newVal           new value
         */
        public static Logging.ReturnCodes FlashingUDE_WriteVariable(string varExpression, int newVal)
        {
            string methodName = getMethodName(new StackTrace());
            Logging.printInfo(methodName, "Writing value " + newVal.ToString() + " to Variable " + varExpression);

            var val = UDEDebugger.WriteVariable(varExpression, newVal);
            if (val == true)
            {
                Logging.printPass(methodName, "Write successful");
                return Logging.ReturnCodes.Pass;
            }
            else
            {
                Logging.printFail(methodName, "Write failed");
                return Logging.ReturnCodes.Fail;
            }
        }

        /**
         * FlashingUDE_AddBreakPoint
         *
         * @param[in] bpDescription    Textual description of breakpoint description 
         */
        public static Logging.ReturnCodes FlashingUDE_AddBreakPoint(string bpDescription)
        {
            string methodName = getMethodName(new StackTrace());
            Logging.printInfo(methodName, "Adding break point at " + bpDescription);

            int returnCode;
            returnCode = UDEDebugger.Breakpoints.AddAndGetResult(bpDescription);
            if (returnCode > 0)
            {
                Logging.printPass(methodName, "Break point is added successfully!");
                return Logging.ReturnCodes.Pass;
            }
            else if (returnCode == 0)
            {
                Logging.printFail(methodName, "Breakpoint description '" + bpDescription + "' cannot resolved");
                return Logging.ReturnCodes.Fail;
            }
            else if (returnCode == -2)
            {
                Logging.printFail(methodName, "Not enough breakpoints available to add " + bpDescription);
                return Logging.ReturnCodes.Fail;
            }
            else
            {
                Logging.printFail(methodName, "Unhandeled return code (" + returnCode.ToString() + ") from method: AddAndGetResult");
                return Logging.ReturnCodes.Fail;
            }
        }

        /**
         * FlashingUDE_EnableBreakPoint
         *
         * @param[in] bpDescription    Textual description of breakpoint description 
         */
        public static Logging.ReturnCodes FlashingUDE_EnableBreakPoint(string bpDescription)
        {
            string methodName = getMethodName(new StackTrace());
            Logging.printInfo(methodName, "Enabling break point at " + bpDescription);

            int returnCode;
            returnCode = UDEDebugger.Breakpoints.EnableAndGetResult(bpDescription);
            if (returnCode > 0)
            {
                Logging.printPass(methodName, "Break point is enabled successfully!");
                return Logging.ReturnCodes.Pass;
            }
            else if (returnCode == 0)
            {
                Logging.printFail(methodName, "Breakpoint description '" + bpDescription + "' cannot resolved");
                return Logging.ReturnCodes.Fail;
            }
            else if (returnCode == -1)
            {
                Logging.printFail(methodName, "Breakpoint '" + bpDescription + "' not found in collection to enable");
                return Logging.ReturnCodes.Fail;
            }
            else if (returnCode == -2)
            {
                Logging.printFail(methodName, "Not enough breakpoints available to enable " + bpDescription);
                return Logging.ReturnCodes.Fail;
            }
            else
            {
                Logging.printFail(methodName, "Unhandeled return code (" + returnCode.ToString() + ") from method: EnableAndGetResult");
                return Logging.ReturnCodes.Fail;
            }
        }

        /**
         * FlashingUDE_DisableBreakPoint
         *
         * @param[in] bpDescription    Textual description of breakpoint description 
         */
        public static Logging.ReturnCodes FlashingUDE_DisableBreakPoint(string bpDescription)
        {
            string methodName = getMethodName(new StackTrace());
            Logging.printInfo(methodName, "Disabling break point at " + bpDescription);

            int returnCode;
            returnCode = UDEDebugger.Breakpoints.DisableAndGetResult(bpDescription);
            if (returnCode > 0)
            {
                Logging.printPass(methodName, "Break point is disabled successfully!");
                return Logging.ReturnCodes.Pass;
            }
            else if (returnCode == 0)
            {
                Logging.printFail(methodName, "Breakpoint description '" + bpDescription + "' cannot resolved");
                return Logging.ReturnCodes.Fail;
            }
            else if (returnCode == -1)
            {
                Logging.printFail(methodName, "Breakpoint '" + bpDescription + "' not found in collection to disable");
                return Logging.ReturnCodes.Fail;
            }
            else
            {
                Logging.printFail(methodName, "Unhandeled return code (" + returnCode.ToString() + ") from method: DisableAndGetResult");
                return Logging.ReturnCodes.Fail;
            }
        }


        /**
         * FlashingUDE_RemoveBreakPoint
         *
         * @param[in] bpDescription    String, that describes breakpoint location 
         */
        public static Logging.ReturnCodes FlashingUDE_RemoveBreakPoint(string bpDescription)
        {
            string methodName = getMethodName(new StackTrace());
            Logging.printInfo(methodName, "Removing break point at " + bpDescription);

            int returnCode;
            returnCode = UDEDebugger.Breakpoints.RemoveAndGetResult(bpDescription);
            if (returnCode > 0)
            {
                Logging.printPass(methodName, "Break point is removed successfully!");
                return Logging.ReturnCodes.Pass;
            }
            else if (returnCode == 0)
            {
                Logging.printFail(methodName, "Breakpoint description '" + bpDescription + "' cannot resolved");
                return Logging.ReturnCodes.Fail;
            }
            else if (returnCode == -1)
            {
                Logging.printFail(methodName, "Breakpoint '" + bpDescription + "' not found in collection to remove");
                return Logging.ReturnCodes.Fail;
            }
            else
            {
                Logging.printFail(methodName, "Unhandeled return code (" + returnCode.ToString() + ") from method: RemoveAndGetResult");
                return Logging.ReturnCodes.Fail;
            }
        }

        /**
         * FlashingUDE_EnableAllBreakpoints
         */
        public static Logging.ReturnCodes FlashingUDE_EnableAllBreakpoints()
        {
            string methodName = getMethodName(new StackTrace());
            Logging.printInfo(methodName, "Enabling all breakpoints");

            UDEDebugger.Breakpoints.EnableAll();
            return Logging.ReturnCodes.Pass;
        }

        /**
         * FlashingUDE_DisableAllBreakpoints
         */
        public static Logging.ReturnCodes FlashingUDE_DisableAllBreakpoints()
        {
            string methodName = getMethodName(new StackTrace());
            Logging.printInfo(methodName, "Disabling all breakpoints");

            UDEDebugger.Breakpoints.DisableAll();
            return Logging.ReturnCodes.Pass;
        }


        /**
         * Go : Starts target program from current instruction pointer.
         */
        public static Logging.ReturnCodes FlashingUDE_Go()
        {
            string methodName = getMethodName(new StackTrace());
            Logging.printInfo(methodName, "Go: Start Target Program form current instruction pointer");

            UDEDebugger.Go();
            return Logging.ReturnCodes.Pass;
        }

        /**
         * Break : Breaks execution of currently running program.
         */
        public static Logging.ReturnCodes FlashingUDE_Break()
        {
            string methodName = getMethodName(new StackTrace());
            Logging.printInfo(methodName, "Break : Breaks execution of currently running program.");

            UDEDebugger.Break();
            return Logging.ReturnCodes.Pass;
        }

        /**
         * WaitForHalt : Wait until debugger is halted by debug event (e.g. breakpoint hit).
         */
        public static Logging.ReturnCodes FlashingUDE_WaitForHalt(int timeoutms)
        {
            string methodName = getMethodName(new StackTrace());
            Logging.printInfo(methodName, "WaitForHalt : Wait until debugger is halted by debug event (e.g. breakpoint hit).");

            bool isHalted = UDEDebugger.WaitForHalt(timeoutms);
            if (isHalted)
            {
                Logging.printPass(methodName, "Halted!");
                return Logging.ReturnCodes.Pass;
            }
            else
            {
                Logging.printFail(methodName, "not halted within wait time!");
                return Logging.ReturnCodes.Fail;
            }

        }

        /**
         * Reload Program : Forces reload of loaded target program. This function includes target reset and places actual instruction pointer on begin of startup code after reload is completed.
         */
        public static Logging.ReturnCodes FlashingUDE_ReloadProgram()
        {
            string methodName = getMethodName(new StackTrace());
            Logging.printInfo(methodName, "Reload Program : Forces reload of loaded target program. This function includes target reset and places actual instruction pointer on begin of startup code after reload is completed.");

            UDEDebugger.ReloadProgram();
            return Logging.ReturnCodes.Pass;
        }

        /**
         * Reset Target: Forces target system reset.
         */
        public static Logging.ReturnCodes FlashingUDE_ResetTarget()
        {
            string methodName = getMethodName(new StackTrace());
            Logging.printInfo(methodName, "Reset Target: Forces target system reset.");

            UDEDebugger.ResetTarget();
            return Logging.ReturnCodes.Pass;
        }

        /**
         * FlashingUDE_RemoveAllBreakpoints
         */
        public static Logging.ReturnCodes FlashingUDE_RemoveAllBreakpoints()
        {
            string methodName = getMethodName(new StackTrace());
            Logging.printInfo(methodName, "Removing all breakpoints");

            UDEDebugger.Breakpoints.RemoveAll();
            return Logging.ReturnCodes.Pass;
        }

        /**
         * Connects debugger to Target
         */
        public static Logging.ReturnCodes connect()
        {
            string methodName = getMethodName(new StackTrace());

            if (UDEWorkspace.CheckTargetConnected())
            {
                Logging.printPass(methodName, "Target was found already connected!");
                return Logging.ReturnCodes.Pass;
            }

            bool res;
            int timeout = 20000;
            res = UDEWorkspace.ConnectTarget(timeout);
            if (res)
            {
                Logging.printPass(methodName, "Target connected!");
                return Logging.ReturnCodes.Pass;
            }
            else
            {
                Logging.printFail(methodName, "Failed to connect to Target");
                return Logging.ReturnCodes.Fail;
            }
        }

        /**
        * Disonnects debugger to Target
        */
        public static Logging.ReturnCodes disconnect()
        {
            string methodName = getMethodName(new StackTrace());

            if (!UDEWorkspace.CheckTargetConnected())
            {
                Logging.printPass(methodName, "Target was found already disconnected!");
                return Logging.ReturnCodes.Pass;
            }

            bool res;
            int timeout = 20000;
            res = UDEWorkspace.DisonnectTarget(timeout);
            if (res)
            {
                Logging.printPass(methodName, "Target disconnected!");
                return Logging.ReturnCodes.Pass;
            }
            else
            {
                Logging.printFail(methodName, "Failed to disconnect to Target");
                return Logging.ReturnCodes.Fail;
            }
        }


        /**
        * get Result - shall be called directly after an operation that shall return a result. ex: readRegister
        *
        */
        public static int FlashingUDE_ReadLastOperationResult()
        {
            return operationResult;
        }

        private static string getMethodName(StackTrace trace)
        {
            string methodName = trace.GetFrame(0).GetMethod().Name;
            methodName = className + "." + methodName;
            return methodName;
        }
    }
}

