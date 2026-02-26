# Erstellt von Tim Nadolny
# Copyright Robert Bosch GMBH
# Datum: 13. Feb. 2025
# TC_Offline_Check_LGU_Radar_Communication.py
# CAN FD

import sys, os

# Fügen Sie verschiedene Pfade zu den Systempfaden hinzu, um Module aus diesen Verzeichnissen zu importieren
sys.path.append(r"..\..\..\Python_Testing_Framework\CANoePy\using_XIL_API")
sys.path.append(r"..\..\..\Python_Testing_Framework\ReportGen")
sys.path.append(r"..\..\..\..\adas_sim\Python_Testing_Framework\common_test_functions")
sys.path.append(r"..\..\..\Python_Testing_Framework\TraceParser")
sys.path.append(r"..\..\..\Python_Testing_Framework\ByteArrayParser")
sys.path.append(r"..\..\..\Python_Testing_Framework\CommonTestFunctions")
sys.path.append(r"..\..\..\Python_Testing_Framework\CANoePy\using_CANoe_COM")
sys.path.append(r"..\..\..\Platform\Python_Testing_Framework\ReportGen")
sys.path.append(r"..\common_test_functions")
sys.path.append(r"..\..\..\Platform\Python_Testing_Framework\TraceParser")
sys.path.append(r"..\..\..\Platform\Python_Testing_Framework\ByteArrayParser")
sys.path.append(r"..\..\..\Platform\Python_Testing_Framework\CommonTestFunctions")

# Ändern Sie das aktuelle Arbeitsverzeichnis auf das Verzeichnis, in dem sich diese Datei befindet
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Importieren Sie das HTML_Logger-Modul
import HTML_Logger

# Offline-Analyse-Importe
try:
    # Versuchen Sie, Module aus dem Plattformverzeichnis zu importieren
    sys.path.append(r"..\..\..")
    import Platform.Python_Testing_Framework.TraceParser.mdf_parser as mdf_parser
    from Platform.Python_Testing_Framework.CommonTestFunctions.offline_common_functions import CommonFunc, Condition
    from Platform.Python_Testing_Framework.ReportGen import plotter, plotter_dash
    import Platform.Python_Testing_Framework.TraceParser.asc_parser as asc_parser
    from Platform.Python_Testing_Framework.TraceParser.asc_parser import RADAR_ID
    from Platform.Python_Testing_Framework.TraceParser.args import get_args
except ImportError as e:
    # Falls der obige Import fehlschlägt, importieren Sie Module aus dem aktuellen Verzeichnis
    print(f"ImportError: {e}")
    import plotter, plotter_dash
    from offline_common_functions import CommonFunc, Condition
    import mdf_parser, asc_parser
    from asc_parser import RADAR_ID

test_args = get_args()  # Get parsed arguments

# Define a constant for log files, could be a single log or a directory
INPUT_LOG = test_args.log_file_path

# Definieren Sie eine Konstante für Logdateien, dies könnte eine einzelne Logdatei oder ein Verzeichnis sein
#INPUT_LOG = r"\\abtvdfs2.de.bosch.com\ismdfs\iad\verification\ODS\ADAS_HIL_concept\Measurements\offlineAnalyzerTraces\Vehicle_Model_Test_1_Config2_T001.mf4"

# Definieren Sie die Testfallfunktion
def TC_Offline_Check_LGU_Radar_Communication(input_log):


    ################# Initialisierung ###########################################################################
    # Richten Sie den HTML-Bericht ein
    HTML_Logger.setup(__file__, "CANoePy Testcase", filename=HTML_Logger.generate_report_name())
    # Fügen Sie Kopfzeilen zum HTML-Bericht hinzu
    HTML_Logger.TestReportHeader("Tester : XXX")
    HTML_Logger.TestReportHeader("TestCaseName : TC_Offline_Check_LGU_Radar_Communication")
    HTML_Logger.TestReportHeader("DefectID : None")
    HTML_Logger.TestReportHeader("RQM_ID : 3226019")
    HTML_Logger.TestReportHeader(f"Eingabedatei -> {INPUT_LOG}")
    trace = CommonFunc()  # Erstellen Sie ein Testfunktionen-Objekt, das einmal pro Test instanziiert werden soll

    output = mdf_parser.ChannelFinder(input_log) # Parse passed mdf file
    # input from jenkins a trace or folder and from the online analyzer *** 
    output.list_channels() # If needed user can check all available channels objects
    channels = output.get_channels(["RFC_LocHdr_SensorOriginPointX","RFC_LocHdr_SensorOriginPointY","RFC_LocHdr_SensorOriginPointZ","RFC_LocHdr_NumValidDetections","RFC_LocHdr_TimeStamp","RFC_LocHdr_TimeStampStatus","RFC_LocHdrA_ProtBlockCtr","RFC_LocHdrA_AliveCtr","RFC_LocHdrA_CRC"]) # Provide channels of interest as a string list. Functions will return mdf channel objects
    # function needed to get all channels defined in the python file ***
    ################################################################################################################

    ################ TESTSCHRITTE Abschnitt ########################################################################
    
    #Teststep 1 - Radar General interface info - Mounting position

    HTML_Logger.ReportTestStepStart()
    HTML_Logger.ReportWhiteMessage(f"--------------- Testschritt 1 Check Radar Mounting Positions--------------------")
    HTML_Logger.ReportTestStepEnd()
    # RFC Radar General interface info - Mounting position

    # Check RFC X Mounting position
    HTML_Logger.ReportTestStepStart()
    HTML_Logger.ReportWhiteMessage(f"--------------- RFC X Mounting position --------------------")
    data = trace.get_signal_value(channels["RFC_LocHdr_SensorOriginPointX"], 0, 0) # 0,0 - all range, x,0 - from x:end, 0,x - beginning:x , x,x - defined range
    trace.check_signal_update(data, Condition.EQUALS, 3.84)
    HTML_Logger.ReportTestStepEnd()

    # Check RFC Y Mounting position
    HTML_Logger.ReportTestStepStart()
    HTML_Logger.ReportWhiteMessage(f"--------------- RFC Y Mounting position --------------------")
    data = trace.get_signal_value(channels["RFC_LocHdr_SensorOriginPointY"], 0, 0) # 0,0 - all range, x,0 - from x:end, 0,x - beginning:x , x,x - defined range
    trace.check_signal_update(data, Condition.EQUALS, 0.0)
    HTML_Logger.ReportTestStepEnd()

    # Check RFC Z Mounting position
    HTML_Logger.ReportTestStepStart()
    HTML_Logger.ReportWhiteMessage(f"--------------- RFC Z Mounting position --------------------")
    data = trace.get_signal_value(channels["RFC_LocHdr_SensorOriginPointZ"], 0, 0) # 0,0 - all range, x,0 - from x:end, 0,x - beginning:x , x,x - defined range
    trace.check_signal_update(data, Condition.EQUALS, 0.3)
    HTML_Logger.ReportTestStepEnd()

    HTML_Logger.ReportTestStepStart()
    HTML_Logger.ReportWhiteMessage(f"--------------- Testschritt 2 Communication RFC existence--------------------")
    HTML_Logger.ReportTestStepEnd()
    
    HTML_Logger.ReportTestStepStart()
    HTML_Logger.ReportWhiteMessage(f"--------------- Check RFC_LocHdr_NumValidDetections unequal 0 --------------------")
    
    data = trace.get_signal_value(channels["RFC_LocHdr_NumValidDetections"], 0, 0)
    trace.check_signal_update(data, Condition.NOT_EQUALS, 0)
    HTML_Logger.ReportWhiteMessage(f"Signalwert: {data}, Erwarteter Wert: ist ungleich Null, Ergebnis: ")
    HTML_Logger.ReportTestStepEnd()
 
    HTML_Logger.ReportTestStepStart()
    HTML_Logger.ReportWhiteMessage(f"--------------- Testschritt 3  Data timing--------------------")
    HTML_Logger.ReportTestStepEnd()
    HTML_Logger.ReportTestStepStart()
    HTML_Logger.ReportWhiteMessage(f"--------------- Check Timestamp values RFC_LocHdr_TimeStamp increase with each cycle --------------------")
    data = trace.get_signal_value(channels["RFC_LocHdr_TimeStamp"], 0, 0)
    trace.check_incrementing(data, 67108863)
    HTML_Logger.ReportTestStepEnd()

    # Check RFC_LocHdr_TimeStampStatus ==8
    HTML_Logger.ReportTestStepStart()
    HTML_Logger.ReportWhiteMessage(f"--------------- RFC_LocHdr_TimeStampStatus --------------------")
    data = trace.get_signal_value(channels["RFC_LocHdr_TimeStampStatus"], 0, 0) # 0,0 - all range, x,0 - from x:end, 0,x - beginning:x , x,x - defined range
    trace.check_signal_update(data, Condition.CONSTANT, 8)
    HTML_Logger.ReportTestStepEnd()


    HTML_Logger.ReportTestStepStart()
    HTML_Logger.ReportWhiteMessage(f"--------------- Testschritt 4  Data Data integrity--------------------")
    HTML_Logger.ReportTestStepEnd()

    HTML_Logger.ReportTestStepStart()
    HTML_Logger.ReportWhiteMessage(f"--------------- Check ProtBlockCounter messsage increase with each cycle --------------------")
    data = trace.get_signal_value(channels["RFC_LocHdrA_ProtBlockCtr"], 0, 0)
    trace.check_incrementing(data, 15)
    HTML_Logger.ReportTestStepEnd()

    HTML_Logger.ReportTestStepStart()
    HTML_Logger.ReportWhiteMessage(f"--------------- Check AliveCounter message increase with each cycle --------------------")
    data = trace.get_signal_value(channels["RFC_LocHdrA_AliveCtr"], 0, 0)
    trace.check_incrementing(data, 255)
    HTML_Logger.ReportTestStepEnd()

    HTML_Logger.ReportTestStepStart()
    HTML_Logger.ReportWhiteMessage(f"--------------- Check availability of E2E protection --------------------")
    data = trace.get_signal_value(channels["RFC_LocHdrA_CRC"], 0, 0)
    trace.check_incrementing(data, 65535)
    HTML_Logger.ReportTestStepEnd()

    HTML_Logger.ReportTestStepStart()
    HTML_Logger.ReportWhiteMessage(f"--------------- Testschritt 5 General interface info - field of view signals--------------------")
    HTML_Logger.ReportTestStepEnd()

    HTML_Logger.ReportTestStepStart()
    HTML_Logger.ReportWhiteMessage(f"--------------- Check azimuth message  --------------------")
    HTML_Logger.ReportWhiteMessage(f"Check azimuth signal values RXX_LocXYZ_Azimuth")
    Regex_channels = output.get_channels_regex([r'^RF[A-Z]{1}_Loc\d{3}_Azimuth$'])  # Provide channels of interest as a string list. Functions will return mdf channel objects
    # Analysis
    trace.check_dataframes_for_zero(Regex_channels, 80)
    HTML_Logger.ReportTestStepEnd()

    HTML_Logger.ReportTestStepStart()
    HTML_Logger.ReportWhiteMessage(f"--------------- Check elevation message  --------------------")
    HTML_Logger.ReportWhiteMessage(f"Check elevation signal values RXX_LocXYZ_Elevation")
    Regex_channels = output.get_channels_regex([r'^RF[A-Z]{1}_Loc\d{3}_Elevation$'])  # Provide channels of interest as a string list. Functions will return mdf channel objects
    # Analysis
    trace.check_dataframes_for_zero(Regex_channels, 80)
    HTML_Logger.ReportTestStepEnd()

    HTML_Logger.ReportTestStepStart()
    HTML_Logger.ReportWhiteMessage(f"--------------- Testschritt 6 Post-drive analyzis--------------------")
    HTML_Logger.ReportTestStepEnd()

    HTML_Logger.ReportTestStepStart()
    HTML_Logger.ReportWhiteMessage(f"--------------- Check that 99% of network frames are transmitted within 46ms and 86ms --------------------")
    trace.check_cycle_time(output.mdf,["RadarFrontCenter"])
    HTML_Logger.ReportTestStepEnd()


    HTML_Logger.ReportFinalVerdict()
    HTML_Logger.Show_HTML_Report()




if __name__ == "__main__":
    # Überprüfen Sie, ob der Pfad ein Verzeichnis ist
    if os.path.isdir(INPUT_LOG):
        logs = list(CommonFunc.find_mf4_files(INPUT_LOG))
        for log in logs:
            TC_Offline_Check_LGU_Radar_Communication(log)
    else:
        TC_Offline_Check_LGU_Radar_Communication(INPUT_LOG)