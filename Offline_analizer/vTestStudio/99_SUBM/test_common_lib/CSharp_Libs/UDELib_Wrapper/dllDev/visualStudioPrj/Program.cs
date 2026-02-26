using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace FlashingLib
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Calling UDE Flashing methods directly!");
            FlashingUDE.FlashingUDE_StartAndOpenWorkspace("D:\\GiTRepos\\test_common_libs\\CSharp_Libs\\UDELib_Wrapper\\CsLibDev\\Test\\UdeAutomation.wsx");
            //FlashingUDE.FlashingUDE_EnableFlashModule("DF1", 1);
            //FlashingUDE.FlashingUDE_EraseFlashModule("DF1");
            //FlashingUDE.FlashingUDE_FlashWithMemTool("D:\\GiTRepos\\test_common_libs\\CSharp_Libs\\UDELib_Wrapper\\CsLibDev\\Test\\STUB_F_DASy_Master_IDC5_FULL.hex");
            //FlashingUDE.FlashingUDE_StopAndCloseWorkspace();

            //Console.WriteLine("Trying the Go, break, breakpoint!");
            //FlashingUDE.FlashingUDE_StartAndOpenWorkspace("D:\\GiTRepos\\test_common_libs\\CSharp_Libs\\UDELib_Wrapper\\CsLibDev\\Test\\UdeAutomation.wsx");
            //FlashingUDE.FlashingUDE_Go();
            //FlashingUDE.FlashingUDE_Break();
            //FlashingUDE.FlashingUDE_Go();
            //FlashingUDE.FlashingUDE_Break();
            //FlashingUDE.FlashingUDE_Go();
            //FlashingUDE.FlashingUDE_Break();
            //FlashingUDE.FlashingUDE_Go();
            //FlashingUDE.FlashingUDE_Break();

            //Console.WriteLine("--------------------------------------------------------");
            //Console.WriteLine("Calling UDE Flashing through the abstract flahing!");
            //Flashing.chooseDebugger(Flashing.DebuggerType.UDE);
            //Flashing.startAndOpenWorkspace("D:\\GiTRepos\\test_common_libs\\CSharp_Libs\\UDELib_Wrapper\\CsLibDev\\Test\\UdeAutomation.wsx");
            //Flashing.enableFlashModule("DF1", 1);
            //Flashing.eraseFlashModule("DF1");
            //Flashing.flashFile("D:\\GiTRepos\\test_common_libs\\CSharp_Libs\\UDELib_Wrapper\\CsLibDev\\Test\\STUB_F_DASy_Master_IDC5_FULL.hex");
            //Flashing.stopAndCloseWorkspace();

            //Console.WriteLine("--------------------------------------------------------");
            //Console.WriteLine("Calling Miniwiggler Flashing through the abstract flahing!");
            //Flashing.chooseDebugger(Flashing.DebuggerType.Miniwiggler);
            //Flashing.startAndOpenWorkspace("D:\\GiTRepos\\test_common_libs\\CSharp_Libs\\UDELib_Wrapper\\CsLibDev\\Test\\UdeAutomation.wsx");
            //Flashing.enableFlashModule("DF1", 1);
            //Flashing.eraseFlashModule("DF1");
            //Flashing.flashFile("D:\\GiTRepos\\test_common_libs\\CSharp_Libs\\UDELib_Wrapper\\CsLibDev\\Test\\STUB_F_DASy_Master_IDC5_FULL.hex");
            //Flashing.stopAndCloseWorkspace();

            //Console.WriteLine("--------------------------------------------------------");
            //Console.WriteLine("Calling Lauterbach Flashing through the abstract flahing!");
            //Flashing.chooseDebugger(Flashing.DebuggerType.Lauterbach);
            //Flashing.startAndOpenWorkspace("D:\\GiTRepos\\test_common_libs\\CSharp_Libs\\UDELib_Wrapper\\CsLibDev\\Test\\UdeAutomation.wsx");
            //Flashing.enableFlashModule("DF1", 1);
            //Flashing.eraseFlashModule("DF1");
            //Flashing.flashFile("D:\\GiTRepos\\test_common_libs\\CSharp_Libs\\UDELib_Wrapper\\CsLibDev\\Test\\STUB_F_DASy_Master_IDC5_FULL.hex");
            //Flashing.stopAndCloseWorkspace();
        }
    }
}
