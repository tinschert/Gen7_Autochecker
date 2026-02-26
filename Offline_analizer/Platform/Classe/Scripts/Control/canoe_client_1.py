# -*- coding: utf-8 -*-
# @file canoe_client_1.py
# @author ADAS_HIL_TEAM
# @date 08-21-2023

##################################################################
# C O P Y R I G H T S
# ----------------------------------------------------------------
# Copyright (c) 2023 by Robert Bosch GmbH. All rights reserved.

# The reproduction, distribution and utilization of this file as
# well as the communication of its contents to others without express
# authorization is prohibited. Offenders will be held liable for the
# payment of damages. All rights reserved in the event of the grant
# of a patent, utility model or design.

##################################################################


"""
@authorIDs :: PEP3SF4
@authorNAMEs :: Plamen Petkov
"""

import win32com.client as win32

try:
    import canoe_event_handler
except:
    from Control import canoe_event_handler
import pythoncom
import time
import os
import subprocess

try:
    from logging_config import logger
except:
    from Control.logging_config import logger


class CANoeClient:
    """A COM client used to remote control CANoe."""

    def __init__(self):
        self.CANoe = win32.Dispatch("CANoe.Application")

        logger.info(f"Loaded CANoe version --> {self.CANoe.Version.FullName}")
        time.sleep(10)  # Sometimes CANoe needs some time after it is ready to execute other com commands

    def startMeasurement(self, nrOfTests=1):
        """
        Starts a measurement in CANoe.

        Args:
          nrOfTests:  (Default value = 1)

        Returns:

        """

        logger.info("Starting CanOE measurement")
        measurement = self.CANoe.Measurement

        if measurement.Running is False:
            measurement.Start()
            time.sleep(90) #wait 30sec by default
            waitCycles = 0
            maxWaitCycles = 30 * nrOfTests
            while not measurement.Running and (waitCycles < maxWaitCycles):
                waitCycles = waitCycles + 1
                time.sleep(1)
                pythoncom.PumpWaitingMessages()

            if waitCycles >= maxWaitCycles:
                logger.error("The measurement start operation timed out")
                raise Exception("The measurement start operation timed out. Please check CANoe write window")
        else:
            logger.warning("Measurement already running!!!")

    def stopMeasurement(self):
        """Stops a measurement in CANoe."""

        measurement = self.CANoe.Measurement

        if measurement.Running is True:
            measurement.StopEx()
            waitCycles = 0
            maxWaitCycles = 1000

            while measurement.Running and waitCycles < maxWaitCycles:
                waitCycles = waitCycles + 1
                time.sleep(0.1)
                pythoncom.PumpWaitingMessages()
            logger.info("CanOE measurement stopped")

            if waitCycles >= maxWaitCycles:
                logger.error("The measurement stop operation timed out")
                raise Exception("The measurement stop operation timed out")
        else:
            logger.warning("Measurement already Stopped!!!")

    def openConfiguration(self, configurationFilePath, skip_cfg_check=False):
        """
        Switches the loaded configuration in CANoe.

        Args:
          configurationFilePath: Path to Project .can file

        Returns:

        """

        if skip_cfg_check or f'{self.CANoe.Configuration.Path}\\{self.CANoe.Configuration.Name}.cfg' != configurationFilePath:
            self.CANoe.Open(configurationFilePath)

        """Check if the configuration file was opened successfully"""

        checkConfigResult = self.CANoe.Configuration.OpenConfigurationResult.result

        # result == 0 (success)

        if checkConfigResult != 0:
            logger.error("The configuration could not be opened due to an error")
            raise Exception("The configuration could not be opened due to an error. Please check CANoe write window")
        else:
            logger.info(f"Loaded CANoe configuration --> {self.CANoe.Configuration.Name}")

    def addXCPConfiguration(self, xcpConfigurationFilePath):
        """
        Adds xcp configuration files to CANoe

        Args:
          xcpConfigurationFilePath: XCP configuration file to load

        Returns:

        """

        xcpConfigurationFilePath = os.path.abspath(xcpConfigurationFilePath)
        self.CANoe.Configuration.GeneralSetup.XCPSetup.ECUs.AddConfiguration(xcpConfigurationFilePath)

        if self.CANoe.Configuration.GeneralSetup.XCPSetup.ECUs.Count == 0:
            logger.error("The XCP configuration could not loaded")
            raise Exception("The XCP configuration could not loaded")
        else:
            logger.info(f"XCP configuration {xcpConfigurationFilePath} loaded")

    def removeAllXCPDevices(self):
        """Remove all xcp devices(ecus) from the loaded CANoe configuration"""

        ecus = self.CANoe.Configuration.GeneralSetup.XCPSetup.ECUs
        while ecus.Count > 0:
            ecus.Remove(1)

    def getSysVariable(self, namespace, name):
        """
        Gets a system variable.

        Args:
          namespace: Namespace of the variable
          name: Name of the variable

        Returns:
        variable
        """

        nameSpaces = self.CANoe.System.Namespaces
        for nameSpace in nameSpaces:
            if nameSpace.Name == namespace:
                variables = nameSpace.Variables
                for variable in variables:
                    if variable.Name == name:
                        return variable

    def getSysVarValue(self, namespace, name):
        """
        Sets the value of a system variable.

        Args:
          namespace: Namespace of the variable
          name: Name of the variable

        Returns:
        Sysvar value
        """

        namespaces = self.CANoe.System.Namespaces
        desired_namespace = namespaces(namespace)
        desired_value = desired_namespace.variables(name)
        return desired_value.Value

    def setSysVarValue(self, namespace, name, value):
        """
        Sets the value of a system variable.

        Args:
          namespace: Namespace of the variable
          name: Name of the variable
          value: Value to be set

        Returns:
        """

        namespaces = self.CANoe.System.Namespaces
        desired_namespace = namespaces(namespace)
        desired_value = desired_namespace.variables(name)
        desired_value.Value = value

    def setVariableToValue(self, namespace, name, value):
        """
        Sets the value of a system variable.

        Args:
          namespace: Namespace of the variable
          name: Name of the variable
          value: Value to set

        Returns:

        """

        variable = self.getSysVariable(namespace, name)
        if variable is None:
            logger.error(f"System variable {namespace}::{name} NOT found.")
            raise AttributeError(f"System variable {namespace}::{name} NOT found.")
        else:
            variable.Value = value
            logger.info(f"Set {namespace}::{name}={value}")
        time.sleep(1)
        if variable.Value != value:
            logger.error(f"System variable '{name}' = {value} could not be set")
            raise Exception(f"System variable '{name}' = {value} could not be set")

    def check_fdx_connection(self):
        """ Check FDX connection"""
        wait_cycles = 0
        max_wait_cycles = 180
        while wait_cycles < max_wait_cycles:
            variable = self.getSysVariable("hil_ctrl", "trace_logging_start_mf4")
            if variable.Value == 1.0:
                logger.info("FDX connection established")
                break
            else:
                wait_cycles = wait_cycles + 1
                time.sleep(1)
                pythoncom.PumpWaitingMessages()

        if wait_cycles >= max_wait_cycles:
            logger.error("FDX connection could not be established for timeout of 180 seconds")
            raise Exception("FDX connection could not be established for timeout of 180 seconds")

    def quitCanoe(self, save_cfg):
        """
        Quits canoe CANoe.

        Args:
          save_cfg: Canoe cfg to save

        Returns:

        """

        measurement = self.CANoe.Measurement

        wait_sec = 5
        while measurement.Running:
            time.sleep(1)
            wait_sec -= 1

            try:
                self.stopMeasurement()
            except:
                logger.warning(f"Measurement Couldn't be stopped waiting -> {wait_sec}s")

            pythoncom.PumpWaitingMessages()

            if wait_sec == 0:
                logger.warning(f"Tried many times couldn't stop measurement, force quiting canoe")
                break

        logger.info("CanOE measurement stopped")
        time.sleep(5)
        if save_cfg:
            self.CANoe.Configuration.Modified = True
            logger.info("Save configuration changes")
        else:
            self.CANoe.Configuration.Modified = False
            logger.info("Discarding configuration changes")
        try:
            self.CANoe.Application.Quit()
            logger.info("CanOE application quit")
        except Exception as e:
            logger.warning(f"Control script was unable to quit CanOE app due to {e}")

        time.sleep(10)
        # make sure the CANoe is close properly, otherwise enforce taskkill
        output = subprocess.check_output('tasklist', shell=True)

        if "CANoe64.exe" in str(output):
            logger.info(f"Executing taskkill canoe")
            os.system("taskkill /im CANoe64.exe /f 2>nul >nul")
        if "CANoeTBE.exe" in str(output):
            logger.info(f"Executing taskkill canoe")
            os.system("taskkill /im CANoeTBE.exe /f 2>nul >nul")

    def checkEvent(self, sysvar):
        """
        Checks for system variable events in CANoe.

        Args:
          sysvar: Name of the sysvar

        Returns:

        """

        measurement = self.CANoe.Measurement
        variable = self.getSysVariable("hil_ctrl", sysvar)

        if measurement.Running is True:
            eventHandler = win32.WithEvents(variable, canoe_event_handler.SystemVariablesHandler)

            while not eventHandler.Changed:
                time.sleep(1)
                pythoncom.PumpWaitingMessages()
                if measurement.Running is False:
                    break
            return int(self.getSysVariable("hil_ctrl", sysvar))
        else:
            logger.warning("Measurement already Stopped!!!")

    def executeTestsInTestConfiguration(self, test_suite, customer, path_platform, sw_variant=None):
        """
        Executes all enabled tests in a test configuration.

        Args:
          test_suite: Test group to execute
          sw_variant: (Default value = None)

        Returns:
        """

        enabled_tc_count = 0
        failed_tc_count = 0
        passed_tc_count = 0
        other_tc_count = 0

        tests = test_suite.split(",")
        tests = [i.strip() for i in tests]

        test_units = self.CANoe.Configuration.TestConfigurations.Count
        failed_test_units = []

        for test_unit in range(1, test_units + 1):
            test_unit_name = self.CANoe.Configuration.TestConfigurations.Item(test_unit).Name
            if test_unit_name in tests:
                testConfiguration = self.CANoe.Configuration.TestConfigurations.Item(test_unit)
                testConfiguration = win32.CastTo(testConfiguration, "ITestConfiguration8")

                if sw_variant:
                    available_profiles_list = []
                    variant_profiles = testConfiguration.ListAllVariantProfiles()
                    for prof_count in range(1, variant_profiles.Count + 1):
                        available_profiles_list.append(variant_profiles.Item(prof_count))
                    if sw_variant in available_profiles_list:
                        time.sleep(1)
                        testConfiguration.SetVariantProfileAsync(sw_variant)
                        time.sleep(10)
                        logger.info(f"Changed {test_unit_name} profile variant to -> {sw_variant}")

                #eventHandler = win32.WithEvents(testConfiguration, canoe_event_handler.TestConfigurationEventHandler)

                testConfiguration.Start()

                waitCycles = 0
                maxWaitCycles = 1000
                while not testConfiguration.Running and waitCycles < maxWaitCycles:
                    waitCycles = waitCycles + 1
                    time.sleep(0.1)
                    pythoncom.PumpWaitingMessages()

                if waitCycles >= maxWaitCycles:
                    raise Exception("The test configuration start operation timed out :CANOE CRASH")
                logger.info(f"Test configuration {test_unit_name} started running...")
                waitCycles = 0
                maxWaitCycles = 8000
                self.CANoe.UI.Write.Clear()

                while testConfiguration.Running and waitCycles < maxWaitCycles:
                    if (len(self.CANoe.UI.Write.Text) > 3):
                        self.CANoe.UI.Write.Clear()
                    waitCycles = waitCycles + 1
                    time.sleep(1)
                    pythoncom.PumpWaitingMessages()

                if waitCycles >= maxWaitCycles:
                    logger.error(f"The test configuration {test_unit_name} run timed out :CANOE CRASH")
                    raise Exception(f"The test configuration {test_unit_name} run timed out :CANOE CRASH")
                logger.info(f"Test configuration {test_unit_name} finished running.")

                errors_code = {0: "VerdictNotAvailable", 1: "PASSED", 2: "FAILED", 3: "NONE", 4: "INCONCLUSIVE", 5: "ERROR IN TEST SYSTEM"}

                if testConfiguration.Verdict == 1:
                    logger.info(f"{test_unit_name} -> Tests ended with result PASSED.")
                    elem = testConfiguration.Elements
                    for el in elem:
                        for sub_tree in el.Elements:
                            for test in sub_tree.Elements:
                                if test.Elements.Count!=0:
                                    for tst in test.Elements:
                                        if (tst.Enabled):
                                            logger.info(
                                                f"ENABLED_TC_VTEST#:#{el.Caption} --> {sub_tree.Caption} --> {test.Caption} --> {tst.Caption}#:#")
                                            enabled_tc_count += 1
                                            if tst.Verdict == 1:
                                                passed_tc_count += 1
                                            elif tst.Verdict in errors_code.keys():
                                                other_tc_count += 1
                                                logger.error(
                                                    f"TC_ERROR#::#{el.Caption} --> {sub_tree.Caption} --> {test.Caption} --> {tst.Caption} = {errors_code[tst.Verdict]} #::#")
                                            else:
                                                continue
                                else:
                                    if (test.Enabled):
                                        logger.info(
                                            f"ENABLED_TC_VTEST#:#{el.Caption} --> {sub_tree.Caption} --> {test.Caption}#:#")
                                        enabled_tc_count += 1
                                        if test.Verdict == 1:
                                            passed_tc_count += 1
                                        elif test.Verdict in errors_code.keys():
                                            other_tc_count += 1
                                            logger.error(
                                                f"TC_ERROR#::#{el.Caption} --> {sub_tree.Caption} --> {test.Caption} = {errors_code[test.Verdict]} #::#")
                                        else:
                                            continue
                else:
                    logger.error("#" * 10 + f"Stop at exception -> LIST FAILED TEST CASES in {test_suite} " + "#" * 10)
                    elem = testConfiguration.Elements
                    if sw_variant!=None and "default" not in sw_variant.lower():
                        logger.error(f"TC_ERROR#::#<b>{test_unit_name}-{sw_variant}:</b>#::#")  # pattern #::#
                    else:
                        logger.error(f"TC_ERROR#::#<b>{test_unit_name}:</b>#::#")  # pattern #::#
                    for el in elem:
                        for sub_tree in el.Elements:
                            for test in sub_tree.Elements:
                                if test.Elements.Count!=0:
                                    for tst in test.Elements:
                                        if (tst.Enabled):
                                            logger.info(
                                                f"ENABLED_TC_VTEST#:#{el.Caption} --> {sub_tree.Caption} --> {test.Caption} --> {tst.Caption}#:#")
                                            enabled_tc_count += 1
                                            if tst.Verdict == 1:
                                                passed_tc_count += 1
                                            elif tst.Verdict == 2:
                                                failed_tc_count += 1
                                                logger.error(
                                                    f"TC_ERROR#::#{el.Caption} --> {sub_tree.Caption} --> {test.Caption}  --> {tst.Caption}= FAILED #::#")  # pattern #::#
                                            else:
                                                other_tc_count += 1
                                                errors_code = {0: "VerdictNotAvailable", 1: "PASSED", 2: "FAILED", 3: "NONE", 4: "INCONCLUSIVE",
                                                               5: "ERROR IN TEST SYSTEM"}
                                                if tst.Verdict in errors_code.keys():
                                                    logger.error(
                                                        f"TC_ERROR#::#{el.Caption} --> {sub_tree.Caption} --> {test.Caption} --> {tst.Caption} = {errors_code[tst.Verdict]} #::#")
                                                else:
                                                    logger.error(
                                                        f"TC_ERROR#::#{el.Caption} --> {sub_tree.Caption} --> {test.Caption}  --> {tst.Caption}= VerdictNotAvailable #::#")
                                else:
                                    if (test.Enabled):
                                        logger.info(
                                            f"ENABLED_TC_VTEST#:#{el.Caption} --> {sub_tree.Caption} --> {test.Caption}#:#")
                                        enabled_tc_count += 1
                                        if test.Verdict == 1:
                                            passed_tc_count += 1
                                        elif test.Verdict == 2:
                                            failed_tc_count += 1
                                            logger.error(
                                                f"TC_ERROR#::#{el.Caption} --> {sub_tree.Caption} --> {test.Caption} = FAILED #::#")  # pattern #::#
                                        else:
                                            other_tc_count += 1
                                            errors_code = {0: "VerdictNotAvailable", 1: "PASSED", 2: "FAILED", 3: "NONE", 4: "INCONCLUSIVE",
                                                           5: "ERROR IN TEST SYSTEM"}
                                            if test.Verdict in errors_code.keys():
                                                logger.error(
                                                    f"TC_ERROR#::#{el.Caption} --> {sub_tree.Caption} --> {test.Caption} = {errors_code[test.Verdict]} #::#")
                                            else:
                                                logger.error(
                                                    f"TC_ERROR#::#{el.Caption} --> {sub_tree.Caption} --> {test.Caption} = VerdictNotAvailable #::#")

                    if sw_variant:
                        failed_test_units.append(test_unit_name + "::" + sw_variant)
                    else:
                        failed_test_units.append(test_unit_name)
        # pattern #:#
        logger.info(f"TC_INFO#:#<b>vTESTstudio tcs: {test_suite}, variant: {sw_variant}</b>#:#")
        logger.info(f"TC_INFO#:#Total Enabled tc = {enabled_tc_count} #:#")
        logger.info(f"TC_INFO#:#Total Executed tc = {passed_tc_count + failed_tc_count + other_tc_count} #:#")
        logger.info(f"TC_INFO#:#   -Passed tc = {passed_tc_count} #:#")
        logger.info(f"TC_INFO#:#   -Failed tc = {failed_tc_count} #:#")
        logger.info(f"TC_INFO#:#   -Other tc = {other_tc_count} #:#")

        if customer == "OD":
            test_report_file_path = path_platform + r"\Report_SystemIntegration_CM.vtestreport"
            if os.path.exists(test_report_file_path):
                new_test_report_file_path = path_platform + rf"\{sw_variant}_Report_SystemIntegration_CM.vtestreport"
                os.rename(test_report_file_path, new_test_report_file_path)
                logger.info(f"Report file name renamed old : {test_report_file_path} new : {new_test_report_file_path}")

        return failed_test_units

    def executeTestModules(self, test_envs):
        """
        Run test modules if they are enabled in the given test environment

        Args:
          test_envs: Test Environment to execute

        Returns:

        """
        enabled_tc_count = 0
        failed_tc_count = 0
        passed_tc_count = 0
        other_tc_count = 0

        verdict_manual = {0: "NotAvailable", 1: "Passed", 2: "Failed", 3: "None", 4: "Inconclusive", 5: "ErrorInTestSystem"}
        rq_test_envs_list = test_envs.split(",")
        rq_test_envs_list = [env.strip() for env in rq_test_envs_list]

        verdict_dict = {}

        for testenv in self.CANoe.Configuration.TestSetup.TestEnvironments:
            testenv = win32.CastTo(testenv, "ITestEnvironment2")

            if testenv.Name not in rq_test_envs_list:
                continue

            test_modules = []
            self.TraverseTestItem(testenv, lambda tm: test_modules.append(tm))
            for test_module in test_modules:
                if not (test_module.Enabled):
                    continue
                enabled_tc_count += 1
                logger.info(f"ENABLED_TC_CAPL#:#{testenv.Name} --> {test_module.Name}#:#")

                testModule_event = win32.WithEvents(test_module, canoe_event_handler.ModuleEventHandler)
                test_module.Start()
                # start timeout 100 secs
                waitCycles = 0
                maxWaitCycles = 1000
                while (not testModule_event.testModuleStarted) and (waitCycles < maxWaitCycles):
                    waitCycles = waitCycles + 1
                    time.sleep(0.1)
                    pythoncom.PumpWaitingMessages()

                if waitCycles >= maxWaitCycles:
                    logger.error(f"The test Module {test_module.Name} start timed out ")
                    raise Exception(f"The test Module {test_module.Name} start timed out ")

                # stop timeout 600 secs
                waitCycles = 0
                maxWaitCycles = 5000
                if "_endurance" in test_module.Name.lower():
                    maxWaitCycles = 72000  # 120mins
                while (not testModule_event.testModuleStopped) and (waitCycles < maxWaitCycles):
                    waitCycles = waitCycles + 1
                    time.sleep(1)
                    pythoncom.PumpWaitingMessages()

                if waitCycles >= maxWaitCycles:
                    logger.error(f"The test Module {test_module.Name} run timed out ")
                    raise Exception(f"The test Module {test_module.Name} run timed out ")

                logger.info(f"Finished, verdict -> {verdict_manual[test_module.Verdict]}")

                if verdict_manual[test_module.Verdict] == "Passed":
                    passed_tc_count += 1
                elif verdict_manual[test_module.Verdict] == "Failed":
                    verdict_dict[testenv.Name + " --> " + test_module.Name] = verdict_manual[test_module.Verdict]
                    failed_tc_count += 1
                else:
                    verdict_dict[testenv.Name + " --> " + test_module.Name] = verdict_manual[test_module.Verdict]
                    other_tc_count += 1
            try:
                test_env_report = testenv.Report
                if test_env_report.Enabled:
                    test_env_report.GenerateReportAsync()
            except Exception as e:
                logger.error(f"Error occured while geenrating test env report for {testenv.Name} -> {e}")
            
        if verdict_dict:
            logger.error("#" * 10 + f"Stop at exception -> LIST FAILED TEST CASES : capl/xml " + "#" * 10)
            logger.error(f"TC_ERROR#::#<b>CAPL/XML tcs:</b>#::#")  # pattern #::#
            for tm, verdict in verdict_dict.items():
                logger.error(f"TC_ERROR#::#{tm} = {verdict} #::#")  # pattern #::#

        # pattern #:#
        logger.info(f"TC_INFO#:#<b>CAPL/XML tcs:</b>#:#")
        logger.info(f"TC_INFO#:#Total Enabled test module = {enabled_tc_count} #:#")
        logger.info(f"TC_INFO#:#Total Executed test module = {passed_tc_count + failed_tc_count + other_tc_count} #:#")
        logger.info(f"TC_INFO#:#   -Passed test module = {passed_tc_count} #:#")
        logger.info(f"TC_INFO#:#   -Failed test module = {failed_tc_count} #:#")
        logger.info(f"TC_INFO#:#   -Other test module = {other_tc_count} #:#")

        return verdict_dict

    def TraverseTestItem(self, parent, testfunc):
        """
        Finds test unit in test module

        Args:
          parent: TestModule
          testfunc: Test Function to search

        Returns:

        """
        for test in parent.TestModules:
            testfunc(test)
        for folder in parent.Folders:
            found = self.TraverseTestItem(folder, testfunc)

    def executeTestsInTestModules(self, testModule_names, kpi_run=False):
        """
        searches the given test module name and executes

        Args:
          testModule_names: Name of the test module
          kpi_run:  (Default value = False)

        Returns:

        """
        verdict_manual = {0: "NotAvailable", 1: "Passed", 2: "Failed", 3: "None", 4: "Inconclusive", 5: "ErrorInTestSystem"}
        verdict = "NotAvailable"

        failed_tc_count = 0
        passed_tc_count = 0
        other_tc_count = 0

        verdict_dict = {}

        testModule_names_list = testModule_names.split(",")
        testModule_names_list = [modl.strip() for modl in testModule_names_list]

        test_modules = self.CANoe.Configuration.TestSetup.TestEnvironments.Item(1).Items
        module_count = test_modules.Count

        for testenv in self.CANoe.Configuration.TestSetup.TestEnvironments:
            testenv = win32.CastTo(testenv, "ITestEnvironment2")

            test_modules = []
            self.TraverseTestItem(testenv, lambda tm: test_modules.append(tm))
            for test_module in test_modules:
                if test_module.Name not in testModule_names_list:
                    continue
                logger.info(f"Starting -> {test_module.Name}")
                testModule_event = win32.WithEvents(test_module, canoe_event_handler.ModuleEventHandler)
                test_module.Start()
                time.sleep(3)
                # start timeout 100 secs
                waitCycles = 0
                maxWaitCycles = 1000
                while (not testModule_event.testModuleStarted) and (waitCycles < maxWaitCycles):
                    waitCycles = waitCycles + 1
                    time.sleep(0.1)
                    pythoncom.PumpWaitingMessages()

                if waitCycles >= maxWaitCycles:
                    logger.error(f"The test Module {test_module.Name} start timed out :CANOE CRASH")
                    raise Exception(f"The test Module {test_module.Name} start timed out :CANOE CRASH")

                time.sleep(3)
                # stop timeout 600 secs
                waitCycles = 0
                maxWaitCycles = 5000
                if "_endurance" in test_module.Name.lower():
                    maxWaitCycles = 72000  # 120mins
                while (not testModule_event.testModuleStopped) and (waitCycles < maxWaitCycles):
                    waitCycles = waitCycles + 1
                    time.sleep(1)
                    pythoncom.PumpWaitingMessages()

                if waitCycles >= maxWaitCycles:
                    logger.error(f"The test Module {test_module.Name} run timed out ")
                    raise Exception(f"The test Module {test_module.Name} run timed out ")

                time.sleep(4)
                verdict = verdict_manual[test_module.Verdict]

                logger.info(f"Finished, verdict -> {verdict}")

                if verdict == "Passed":
                    passed_tc_count += 1
                elif verdict == "Failed":
                    verdict_dict[testenv.Name + " --> " + test_module.Name] = verdict
                    failed_tc_count += 1
                else:
                    verdict_dict[testenv.Name + " --> " + test_module.Name] = verdict
                    other_tc_count += 1

        if not (kpi_run):
            if verdict_dict:
                logger.error("#" * 10 + f"Stop at exception -> LIST FAILED TEST CASES : capl/xml " + "#" * 10)
                logger.error(f"TC_ERROR#::#<b>CAPL/XML tcs:</b>#::#")  # pattern #::#
                for tm, verdict in verdict_dict.items():
                    logger.error(f"TC_ERROR#::#{tm} = {verdict} #::#")  # pattern #::#

            # pattern #:#
            logger.info(f"TC_INFO#:#<b>CAPL/XML tcs:</b>#:#")
            logger.info(f"TC_INFO#:#Total Given test module = {len(testModule_names_list)} #:#")
            logger.info(
                f"TC_INFO#:#Total Executed test module = {passed_tc_count + failed_tc_count + other_tc_count} #:#")
            logger.info(f"TC_INFO#:#   -Passed test module = {passed_tc_count} #:#")
            logger.info(f"TC_INFO#:#   -Failed test module = {failed_tc_count} #:#")
            logger.info(f"TC_INFO#:#   -Other test module = {other_tc_count} #:#")

        return verdict_dict

    def enableTestEnvironments(self, test_envs):
        """
        activates the given test environments
        test_envs (str): test envs separated by ,

        Args:
          test_envs: Test environment

        Returns:

        """
        rq_test_envs_list = test_envs.split(",")
        rq_test_envs_list = [env.strip() for env in rq_test_envs_list]

        for testenv in self.CANoe.Configuration.TestSetup.TestEnvironments:
            testenv = win32.CastTo(testenv, "ITestEnvironment2")

            if testenv.Name not in rq_test_envs_list:
                continue
            testenv.Enabled = True
            logger.info(f"Enabled test env -> {testenv.Name}")

    def enableTestsModules(self, testModule_names):
        """
        activates the given test modules
        testModule_names (str): test modules separated by ,

        Args:
          testModule_names: Test module name

        Returns:

        """
        testModule_names_list = testModule_names.split(",")
        testModule_names_list = [modl.strip() for modl in testModule_names_list]

        for testenv in self.CANoe.Configuration.TestSetup.TestEnvironments:
            testenv = win32.CastTo(testenv, "ITestEnvironment2")

            test_modules = []
            self.TraverseTestItem(testenv, lambda tm: test_modules.append(tm))
            for test_module in test_modules:
                if test_module.Name not in testModule_names_list:
                    continue
                test_module.Enabled = True
                logger.info(f"Enabled test module -> {test_module.Name}")

    def activate_network(self, network_name):
        """activates given can/eth network_name OR network_names list"""
        Buses = self.CANoe.Configuration.SimulationSetup.Buses

        if type(network_name) == list and network_name:
            for i in range(1, Buses.Count + 1):
                if Buses.Item(i).Name in network_name:
                    Buses.Item(i).Active = True
                    logger.info(f"Activated Network -> {Buses.Item(i).Name}")

        else:
            for i in range(1, Buses.Count + 1):
                if Buses.Item(i).Name == network_name:
                    Buses.Item(i).Active = True
                    logger.info(f"Activated Network -> {Buses.Item(i).Name}")
                    return

    def deactivate_network(self, network_name):
        """deactivates given can/eth network_name OR network_names list"""
        Buses = self.CANoe.Configuration.SimulationSetup.Buses

        if type(network_name) == list and network_name:
            for i in range(1, Buses.Count + 1):
                if Buses.Item(i).Name in network_name:
                    Buses.Item(i).Active = False
                    logger.info(f"Deactivated Network -> {Buses.Item(i).Name}")

        else:
            for i in range(1, Buses.Count + 1):
                if Buses.Item(i).Name == network_name:
                    Buses.Item(i).Active = False
                    logger.info(f"Deactivated Network -> {Buses.Item(i).Name}")
                    return

    def deactivate_node(self, node_name):
        """deactivates given can/eth node_name OR node_names list"""
        Nodes = self.CANoe.Configuration.SimulationSetup.Nodes

        if type(node_name) == list and node_name:
            for i in range(1, Nodes.Count + 1):
                canoe_node_name = Nodes.Item(i).FullName.split("\\")[-1].split(".")[0]
                if canoe_node_name in node_name:
                    Nodes.Item(i).Active = False
                    logger.info(f"Deactivated Node -> {canoe_node_name}")

        else:
            for i in range(1, Nodes.Count + 1):
                canoe_node_name = Nodes.Item(i).FullName.split("\\")[-1].split(".")[0]
                if canoe_node_name == node_name:
                    Nodes.Item(i).Active = False
                    logger.info(f"Deactivated Node -> {canoe_node_name}")
                    return

    def activate_node(self, node_name):
        """deactivates given can/eth node_name OR node_names list"""
        Nodes = self.CANoe.Configuration.SimulationSetup.Nodes

        if type(node_name) == list and node_name:

            for i in range(1, Nodes.Count + 1):
                canoe_node_name = Nodes.Item(i).FullName.split("\\")[-1].split(".")[0]
                if canoe_node_name in node_name:
                    Nodes.Item(i).Active = True
                    logger.info(f"Activated Node -> {canoe_node_name}")

        else:
            for i in range(1, Nodes.Count + 1):
                canoe_node_name = Nodes.Item(i).FullName.split("\\")[-1].split(".")[0]
                if canoe_node_name == node_name:
                    Nodes.Item(i).Active = True
                    logger.info(f"Activated Node -> {canoe_node_name}")
                    return

    def activate_measurementSetup_block(self, name):
        """
        to activate a blck in measurement setup.
        name: name of the block

        Args:
          name: Name of the block

        Returns:

        """
        try:
            measurement_setup = self.CANoe.Configuration.OnlineSetup
            measurement_setup.ActivateEndBlock(name, True)
            logger.info(f"{name} --> activated in measurement_setup")
        except Exception as e:
            logger.error(f"Unable to activate {name} in measurement_setup --> {e}")

    def deactivate_measurementSetup_block(self, name):
        """
        to deactivate a blck in measurement setup.
        name: name of the block

        Args:
          name: Name of the block

        Returns:

        """
        try:
            measurement_setup = self.CANoe.Configuration.OnlineSetup
            measurement_setup.ActivateEndBlock(name, False)
            logger.info(f"{name} --> deactivated in measurement_setup")
        except Exception as e:
            logger.error(f"Unable to deactivate {name} in measurement_setup --> {e}")

    def set_logging_path(self, log_path):
        """
        used to set logging path, also defines type of file format to be logged

        Args:
          log_path: Path to the log file

        Returns:

        """
        try:
            log = self.CANoe.Configuration.OnlineSetup.LoggingCollection(1)
            log.FullName = log_path
            logger.info(f"Logging path changed to {log.FullName}")
            return log.FullName
        except Exception as e:
            logger.error(f"Unable to change the logs default path. Failure --> {e}")

    def enable_logging_filter(self, enable_filter_list):
        """
        used for applying filter for required data to be logged
        enable_filter_list: list of filter index
        com reference: file:///C:/Program%20Files/Vector%20CANoe%2016/Help01/CANoeCANalyzerHTML5/CANoeCANalyzer.htm#Topics/COMInterface/Objects/COMObjectLoggingFilter.htm

        Args:
          enable_filter_list: Filter list

        Returns:
        """
        try:
            log = self.CANoe.Configuration.OnlineSetup.LoggingCollection(1)
            logging = win32.CastTo(log, 'ILogging5')
            logging.Filter.Disable(0)
            for filter_index in enable_filter_list:
                logging.Filter.Enable(filter_index)
            logger.info(f"Logging filter applied --> {enable_filter_list}")
        except Exception as e:
            logger.error(f"Unable to apply logging filter: --> {e}")
        
    
    def convert_logged_file(self,destination_file,source_file="", filter_symbols_patterns=[]):
        """
        converts logging file formats. provide source file path if the source file is not the current logged file
        (measurement should be stopped)

        Args:
          destination_file: Destination of the log file
          source_file:  (Default value = "")
          filter_symbols_patterns (list): list of required message/signal/variable name/name pattern

        Returns:

        """
        try:
            logger.info(f"-------Started Logged file conversion------")
            log = self.CANoe.Configuration.OnlineSetup.LoggingCollection(1)
            logging = win32.CastTo(log, 'ILogging3')
            exporter = logging.Exporter
            if source_file != "":
                exporter.Sources.Clear()
                exporter.Sources.Add(source_file)

            exporter.Load()

            #check if filter is needed
            if filter_symbols_patterns:
                exporter_pass_filter = exporter.Filter
                for symbol in exporter.Symbols:
                    if any(pattern in symbol.FullName for pattern in filter_symbols_patterns):
                        exporter_pass_filter.Add(symbol.FullName)
                exporter_pass_filter.Enabled = True
                logger.info(f"Applied pass filter for patterns -> {filter_symbols_patterns}")

            exporter.Destinations.Clear()
            exporter.Destinations.Add(destination_file)
            exporter.Save(True)
            logger.info(f"Logged Source File -> {exporter.Sources.Item(1)}")
            logger.info(f"Logging file converted to {destination_file}")
            logger.info(f"-------Finished Logged file conversion------")
            return True
        except Exception as e:
            logger.error(f"Unable export log file. Failure --> {e}")
            return False

    def changeFileOfNode(self, node_name, new_file_path):
        """
        changes the file for the given node
        Args:
            node_name (str): name of node
            new_file_path (str): complete path for new file

        Returns:
        """
        try:
            Nodes = self.CANoe.Configuration.SimulationSetup.Nodes
            for i in range(1, Nodes.Count + 1):
                if node_name == Nodes.Item(i).Name:
                    Nodes.Item(i).FullName = new_file_path
                    logger.info(f"Changed file for node -> {node_name} to -> {new_file_path}")
                    break
        except Exception as e:
            logger.error(f"Error occured while changing file for node->{node_name} --> {e}")
            return False

    def getUserFilesList(self):
        """
        gets user files list
        Returns (list): list of added user files full_name

        """
        try:
            files_list = []
            userfiles = self.CANoe.Configuration.UserFiles
            files_count = userfiles.Count
            for i in range(1, files_count + 1):
                fullname = userfiles.Item(i).FullName
                files_list.append(fullname)
            logger.info(f"Found {len(files_list)} files ")
            return userfiles
        except Exception as e:
            logger.error(f"Error occured while getting userfiles list --> {e}")
            return False

    def addUserFile(self, files):
        """
        adds user file with path to canoe userfiles
        Args:
            files: can be list of files or a str with single file, need complete path of file

        Returns:

        """
        try:
            userfiles = self.CANoe.Configuration.UserFiles
            if type(files) != list:
                files = [files]
            for file in files:
                userfiles.Add(file)
                logger.info(f"Added userfile -> {file}")
        except Exception as e:
            logger.error(f"Error occured while adding userfiles --> {e}")
            return False

    def removeUserFile(self, files):
        """
        removes user file to canoe
        Args:
            files: can be list of files or a str with single file, only filename or complete path of file both works

        Returns:

        """
        try:
            if type(files) != list:
                files = [files]
            for file in files:
                time.sleep(0.2)
                userfiles = self.CANoe.Configuration.UserFiles
                files_count = userfiles.Count
                # while files_count>0:
                #     name = userfiles.Item(i).Name
                #     if name in file:
                #         userfiles.Remove(i)
                #         files_count=-1
                #         logger.info(f"Removed userfile -> {file}")
                #     files_count=-1
                for i in range(1, files_count + 1):
                    name = userfiles.Item(i).Name
                    if name in file:
                        userfiles.Remove(i)
                        logger.info(f"Removed userfile -> {file}")
                        break
        except Exception as e:
            logger.error(f"Error occured while removing userfiles --> {e}")
            return False

    def save_cfg(self, file_path=""):
        """saves the current cfg file"""
        try:
            if file_path:
                self.CANoe.Configuration.Save(file_path)
            else:
                self.CANoe.Configuration.Save()
            logger.info(f"Configuration saved -> {file_path}")
        except Exception as e:
            logger.error(f"Error while saving CFG-{file_path} -> {e}")
            raise Exception(f"Error while saving CFG-{file_path} -> {e}")

    def write_to_output_window(self, text):
        """
        Write to Canoe Write window

        Args:
          text: Text to be written

        Returns:

        """
        self.CANoe.UI.Write.Output(text)

    def enable_write_window_log(self, path):
        """
        Enable write window

        Args:
          path: Path to the write window

        Returns:
        """
        self.CANoe.UI.Write.EnableOutputFile(path)

# Examples -->
# canoeClient = CANoeClient()
# canoeClient.openConfiguration(r'D:\ADAS_Develop\RBS_OD.cfg')
# canoeClient.set_logging_path()

# canoeClient.addXCPConfiguration(r'D:\test_canoe_multiecu_hil_Test\Functions\XCP\XCP_PSA_FrontRadar.xcpcfg')
# canoeClient.startMeasurement()
# canoeClient.executeTestsInTestConfiguration("SystemIntegration")
# canoeClient.setVariableToValue("hil_ctrl","hil_mode",2)
# canoeClient.setVariableToValue("hil_ctrl","brada",1)
# canoeClient.stopMeasurement()