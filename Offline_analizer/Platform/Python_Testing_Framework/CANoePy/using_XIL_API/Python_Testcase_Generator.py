#created by Ventsislav Negentsov
#copyright Robert Bosch GMBH
#date : 11.Dec.2024

class PythonScriptGenerator:
    """
    A class to generate a Python script file based on a user-defined template.

    Attributes:
    - template: str
        The template string that will be used to create the Python script.
    """

    def __init__(self):
        """
        Initializes the PythonScriptGenerator with a predefined template.

        The template contains a placeholder "<testcase_name>" which will be replaced
        by the user's input when generating the script.
        """
        self.template = """#created by CANoePy testcase generator tool
#copyright Robert Bosch GMBH
#date : <current_date>

import sys
sys.path.append(r"..\\..\\..\\Python_Testing_Framework\\CANoePy\\using_XIL_API")
sys.path.append(r"..\\..\\..\\Python_Testing_Framework\\ReportGen")
sys.path.append(r"..\\..\\..\\..\\adas_sim\\Python_Testing_Framework\\common_test_functions")

import HTML_Logger
import CAPL_Wrapper_Functions_XIL_API as capl
import Test_Functions_XIL_API as tf

def <testcase_name>():
    
    capl.Testcase_Start(__file__, "CANoePy Testcase", filename=HTML_Logger.generate_report_name()) #create the HTML report
    HTML_Logger.TestReportHeader("Tester : Ventsislav Negentsov")
    HTML_Logger.TestReportHeader("TestCaseID : <testcase_name>")
    HTML_Logger.TestReportHeader("DefectID : None")
    HTML_Logger.TestReportHeader("Requirement_ID : 1234")
    HTML_Logger.TestReportHeader("RQM_ID : 1234")

    #===========================================================================================================================================================================
    #TEST STARTS HERE:
    #capl.StartMeasurement()
    capl.SetSignal("hil_ctrl", "configuration_od", 2) #set configuration = 7 (1V1D)
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("hil_ctrl", "hil_mode", 4)  # set HIL mode to CarMaker
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("Customer_specific", "cm_scenario", r"<scenario_name>")  # fill the scenario name
    capl.TestWaitForTimeout(1000)
    capl.AwaitValueMatch("hil_ctrl", "init_cm_done", 1, 80)  # wait green LED
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("Customer_specific", "load_scenario", 1)  # press the LOAD SCENARIO button
    #capl.TestWaitForTimeout(500)
    capl.AwaitValueMatch("hil_ctrl", "cm_ready_to_start", 1, 80)  # wait green LED
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("hil_ctrl", "scenario_start", 1)  # press the START SCENARIO button
    capl.TestWaitForTimeout(500)
    capl.TestWaitForTimeout(1000)
    capl.AwaitValueMatch("CarMaker/SC", "State", 8, 70)

    tf.Set_Ego_Vehicle_Velocity(<ego_velocity>)  # set ego to <ego_velocity>kph
    tf.Set_Drv_gear(3)  # set Drive gear
    capl.SetSignal_Array("", "Classe_Obj_Sim/obj_ctrl.obj_target_v_long", [<target_velocity>, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])   #set target object velocity to <target_velocity>

    capl.TestWaitForTimeout(10000)

    capl.SetSignal("Customer_specific", "cm_stopsim", 1)  # press the STOP SIM button to END scenario/test

    # opens the HTML report in Browser  (using the default OS configured browser)
    if capl.GetSignal("","hil_ctrl/jenkins_control") == 0:HTML_Logger.Show_HTML_Report()     #opens the HTML report in Browser  (using the default OS configured browser)

    return capl.Testcase_End()

if __name__ == "__main__":
    <testcase_name>()
"""

    def generate_script(self, testcase_name: str, ego_velocity: str, target_velocity: str, scenario_name : str):
        """
        Generates a Python script file with the specified test case name.

        Parameters:
        - testcase_name: str
            The name of the test case that will replace the placeholder in the template.

        Raises:
        - ValueError:
            If the testcase_name is empty or contains invalid characters.
        """
        # Validating the testcase_name to ensure it is not empty and contains valid characters
        if not testcase_name or not testcase_name.isidentifier():
            raise ValueError("Invalid testcase name. It must be a non-empty identifier.")

        # Replacing the placeholder in the template with the actual testcase name
        temp_str=self.template.replace("<testcase_name>", testcase_name)
        temp_str=temp_str.replace("<ego_velocity>", ego_velocity)
        temp_str = temp_str.replace("<target_velocity>", target_velocity)
        temp_str = temp_str.replace("<scenario_name>", scenario_name)
        script_content = temp_str

        # Writing the generated script to a .py file
        filename = f"{testcase_name}.py"
        with open(filename, 'w') as script_file:
            script_file.write(script_content)

        print(f"Script '{filename}' has been generated successfully.")

# Example usage of the PythonScriptGenerator class
if __name__ == "__main__":
    # Creating an instance of the script generator
    generator = PythonScriptGenerator()

    # Asking the user for the testcase name
    user_testcase_name = input("Enter the test case name: ")
    user_ego_velocity = input("Enter the ego velocity: ")
    user_target_velocity = input("Enter the target object velocity: ")
    user_scenario_name = input("Enter the CarMaker scenario name (press <ENTER> for default 'ACC_CountryRoad_Test'): ")
    if (user_scenario_name==""):
        user_scenario_name = "ACC_CountryRoad_Test"
    # Generating the script based on user input
    try:
        generator.generate_script(user_testcase_name, user_ego_velocity, user_target_velocity, user_scenario_name)
    except ValueError as e:
        print(f"Error: {e}")