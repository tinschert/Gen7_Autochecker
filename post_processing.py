import json
import os
import shutil
import datetime
import base64
import html
import re
import pathlib

def read_json(config_json):
    with open(config_json, 'r') as f:
        config = json.load(f)
    path_to_check = config.get("path_to_check", "")
    rtps_checks = 1 if config.get("RTPS_Checks") == 1 else 0
    mal_checks = 1 if config.get("MAL_Checks") == 1 else 0
    return path_to_check, rtps_checks, mal_checks

def create_test_results_folder(base_path):
    date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    folder_name = f"{date_str}_test_results"
    new_folder_path = os.path.join(base_path, folder_name)
    os.makedirs(new_folder_path, exist_ok=True)
    return new_folder_path

def move_files_with_prefix(source_folder, destination_folder, prefix):
    files_folder = os.path.join(destination_folder, "Files")
    os.makedirs(files_folder, exist_ok=True)
    for filename in os.listdir(source_folder):
        if filename.startswith(prefix):
            source_file = os.path.join(source_folder, filename)
            destination_file = os.path.join(files_folder, filename)
            shutil.move(source_file, destination_file)
    return files_folder

def image_to_data_uri(image_path):
    """Converts an image file to a data URI."""
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()
        base64_encoded = base64.b64encode(image_data).decode('utf-8')
        mime_type = 'image/png'  # Adjust the MIME type based on the image format
        return f'data:{mime_type};base64,{base64_encoded}'
    
def path_to_results_html(test_results_path, prefix):
    """
    Returns the full path to the .html file in test_results_path that starts with the given prefix.
    Assumes there is only one such file.
    """
    for filename in os.listdir(test_results_path):
        if filename.startswith(prefix) and filename.lower().endswith('.html'):
            return os.path.join(test_results_path, filename)
    return None

def create_Gen7_test_summery_html(bosch_stripe, bosch_logo, test_type, results_folder):
    """
    Create an HTML file with Gen7 test summery for review.

    Args:
        bosch_stripe (str): Path to the Bosch stripe image file.
        bosch_logo (str): Path to the Bosch logo image file.

    Returns:
        str: The full path of the created HTML file.
    """
    cwd = os.getcwd()
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    file_path = os.path.join(results_folder, f"{current_date}_{datetime.datetime.now().strftime('%H%M%S')}_Gen7_test_summery_{test_type}.html")
    with open(file_path, 'w', encoding='utf-8') as html_file:
        html_file.write("<!DOCTYPE html>\n<html>\n<head>\n<title>Gen 7 Test summery report</title>\n</head>\n<body>\n")
        # Write the Bosch stripe image
        image_data_uri = image_to_data_uri(bosch_stripe)
        html_file.write(f'<img src="{image_data_uri}" alt="Bosch_Stripe"><br>\n')
        image_data_uri = image_to_data_uri(bosch_logo)
        html_file.write(f'<img src="{image_data_uri}" alt="Bosch_Logo"><br>\n')
        html_file.write("</body>\n</html>")

        html_file.write(f"<h1>Gen 7 {test_type} Test Summery Report </h1>\n")
    
    return file_path

def simple_fix_xml(directory: str, overwrite: bool = False):
    """
    Replaces all occurrences of '&#9135;' with '-' in .xml files.

    Args:
        directory (str): Path to the folder containing .xml files.
        overwrite (bool): If True, overwrites the original files.
                          If False, creates '_cleaned.xml' versions.
    """
    for filename in os.listdir(directory):
        if filename.lower().endswith(".xml"):
            path = os.path.join(directory, filename)

            # Read file
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            # Simple replacement
            cleaned = content.replace("&#9135;", "-")

            # Define output
            if overwrite:
                out_path = path
            else:
                name, ext = os.path.splitext(filename)
                out_path = os.path.join(directory, f"{name}_cleaned{ext}")

            # Write back
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(cleaned)


def find_measurements_in_xml(XML_Path, prefix, measurement_regex):
    """
    Scans XML files in XML_Path with the given prefix and extracts all matches of measurement_rege
    Args:
        XML_Path (str): Directory containing XML files.
        prefix (str): Prefix that XML files must start with.
        measurement_regex (str): Regular expression pattern to search fo
    Returns:
        List[str]: List of all regex matches found in the files.
    """
    matches = []
    pattern = re.compile(measurement_regex)
    for filename in os.listdir(XML_Path):
        if filename.lower().endswith('.xml') and filename.startswith(prefix):
            file_path = os.path.join(XML_Path, filename)
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                found = pattern.findall(content)
                matches.extend(found)
    return matches


def write_measurements_to_html(html_file_path, measurements):
    """Appends a list of measurements to an existing HTML file.

    Args:
        html_file_path (str): Path to the HTML file.
        measurements (List[str]): List of measurement strings to append.
    """
    with open(html_file_path, 'a', encoding='utf-8') as html_file:
        html_file.write('Tested Measurements\n')
        html_file.write('<ul>\n')
        for measurement in measurements:
            escaped_measurement = html.escape(measurement)
            html_file.write(f'  <li>{escaped_measurement}</li>\n')
        html_file.write('</ul>\n')

def write_line(html_file, text):
    html_file.write(f'<p style="margin-bottom:10px;">{text}</p>\n')

def check_results(path_xml, String_to_check, lines_to_skip):
    """
    Scans all XML files in path_xml for String_to_check, skips lines_to_skip lines,
    and collects the result. Returns 'PASSED' if all results are 'PASSED', else 'FAILED'.
    """
    results = []
    for filename in os.listdir(path_xml):
        if filename.lower().endswith('.xml'):
            file_path = os.path.join(path_xml, filename)
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
                for idx, line in enumerate(lines):
                    if String_to_check in line:
                        result_idx = idx + lines_to_skip
                        if result_idx < len(lines):
                            result_line = lines[result_idx].strip()
                            results.append(result_line)
    # If any result contains 'Warning', return all such warnings
    warnings = [res for res in results if 'Warning' in res]
    if warnings:
        return warnings
    # Check if all results are 'PASSED'
    if results and all(res == "PASSED" for res in results):
        return "PASSED"
    else:
        return "FAILED"
    

def make_file_href(path_str: str) -> str:
    """
    Turn a Windows/UNC path into something usable in an <a href="...">.
    - For UNC paths (\\server\share\...), create file://///server/share/... URL.
    - For normal local paths (C:\...), use pathlib's as_uri().
    """
    path = pathlib.Path(path_str).absolute()
    abs_str = str(path)

    # UNC path: \\server\share\dir\file.html
    if abs_str.startswith(r'\\'):
        # strip leading backslashes, then convert to / and prepend file://///
        # UNC \\server\share -> file://///server/share
        unc = abs_str.lstrip('\\')
        return 'file://///' + unc.replace('\\', '/')
    else:
        # Local drive path -> file:///C:/...
        return path.as_uri()


def write_rqm_step_result(
    test_summary_html,
    rqm_testcase_string,
    rqm_result,
    pass_comment,
    fail_comment,
    results_html,
    pass_warning,
    check_mark,
    fail_mark,
    warning_mark
):
    """Writes an RQM step result section into the summary HTML file."""
    with open(test_summary_html, 'a', encoding='utf-8') as html_file:
        write_line(html_file, f'<strong>{html.escape(rqm_testcase_string)}</strong>')
        write_line(html_file, f'Result: <strong>{html.escape(rqm_result)}</strong>')
        
        # Choose the correct image based on result
        if rqm_result == "PASSED":
            image_data_uri = image_to_data_uri(check_mark)
            comment_block = pass_comment
        else:
            image_data_uri = image_to_data_uri(fail_mark)
            comment_block = fail_comment

        html_file.write(
            f'<img src="{image_data_uri}" alt="Result Mark" '
            f'style="height:64px;vertical-align:middle;">\n'
        )

        # Standard copy block
        write_line(html_file, '-------------------------------------------Start Copy Here-------------------------------------------')
        for line in comment_block.split('\n'):
            write_line(html_file, html.escape(line))
        write_line(html_file, 'For more details please check the following document:')

        # Build href that works better with UNC paths
        file_href = make_file_href(results_html)

        # You can keep the long path as label or shorten it
        link_label = html.escape(results_html)  # or something like "Open Results HTML"

        write_line(html_file, f' Results HTML: <a href="{file_href}">{link_label}</a>')
        write_line(html_file, '---------------------------------------------End Copy Here---------------------------------------------')

        # If pass_warning is a non-empty list, show warnings
        if pass_warning and isinstance(pass_warning, list):
            for warning in pass_warning:
                warning_data_uri = image_to_data_uri(warning_mark)
                html_file.write(
                    f'<img src="{warning_data_uri}" alt="Warning Mark" '
                    f'style="height:64px;vertical-align:middle;">\n'
                )
                write_line(html_file, f' {html.escape(warning)}')

def find_html_file_relative(folder_path):
    """
    Searches for the first .html file in the given folder and returns its relative path.
    Returns None if no .html file is found.
    """
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.html'):
            return os.path.relpath(os.path.join(folder_path, filename))
    return None

def main():
    results_path = r".\Offline_analizer\Platform\TestCases\InfraTests\Python_Tests\Reports"
    config_json = r".\Gen7_config.json"
    cwd = os.getcwd()
    path_to_check, rtps_checks, mal_checks = read_json(config_json)
    test_results_folder = create_test_results_folder(cwd)
    bosch_stripe = r".\Resource\Bosch_Stripe.png"
    bosch_logo = r".\Resource\Bosch_Logo.png"
    check_mark = r".\Resource\Check.png"
    fail_mark = r".\Resource\Fail.png"
    warning_mark = r".\Resource\Warning.png"
    measurement_regex = "RA7_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}_\d{3}.MF4"


    if rtps_checks == 0 and mal_checks == 0:
        with open(test_summery_html, 'a', encoding='utf-8') as html_file:
            html_file.write('<p style="color:red;"><strong>Warning: No checks selected, please check the configuration file "config.json".</strong></p>\n')
        # Terminate the script after this point
        exit()

    print("Transfering results")
    rtps_prefix = "TC_Gen7_Checks___"
    # Write RTPS header to HTML

    files_folder = move_files_with_prefix(results_path, test_results_folder, rtps_prefix)
    measurement_list = find_measurements_in_xml(files_folder, rtps_prefix, measurement_regex)
    simple_fix_xml(files_folder, overwrite=True)
    
    if rtps_checks == 1:
        test_summery_html = create_Gen7_test_summery_html(bosch_stripe, bosch_logo, "RTPS", test_results_folder)    
        with open(test_summery_html, 'a', encoding='utf-8') as html_file:
            html_file.write(f'<h2>561318: SYS_INT_IOC_RPTS_xGU_RadarPerformanceAndHealth</h2>\n')
        write_measurements_to_html(test_summery_html, measurement_list)
        results_html_relative = find_html_file_relative(files_folder)

        rqm_step_1_result = check_results(files_folder , "---- RQM test step 1 and 2:  RPTS Performance & Health Check", 5)

        write_rqm_step_result(
            test_summary_html=test_summery_html,
            rqm_testcase_string="RQM Step 1: RPTS Performance & Health Check",
            rqm_result = rqm_step_1_result,
            pass_comment="Pre-Conditions for RTPS Passed.",
            fail_comment="Pre-Conditions for RTPS Failed. Please check the RTPS results for more details.",
            pass_warning=None,
            results_html=results_html_relative,
            check_mark=check_mark,
            fail_mark=fail_mark,
            warning_mark=warning_mark
        )

        rqm_step_2_result_1 = check_results(files_folder, "No consecutive AliveCounter repetitions found in the log file for g_ConfigurationData.m_misc.m_cycleCounter.", 2)
        rqm_step_2_result_2 = check_results(files_folder, "AliveCounter is received for every timestamp in the log file for g_ConfigurationData.m_misc.m_cycleCounter.", 2)
        rqm_step_2_result = "PASSED" if rqm_step_2_result_1 == "PASSED" and rqm_step_2_result_2 == "PASSED" else "FAILED"

        write_rqm_step_result(
            test_summary_html=test_summery_html,
            rqm_testcase_string="RQM Step 2: CycleStatus and Counters Check",
            rqm_result = rqm_step_2_result,
            pass_comment="EOK, and Counters are working as expected.",
            fail_comment="EOK, and Counters are not working as expected, test failed",
            pass_warning=None,
            results_html=results_html_relative,
            check_mark=check_mark,
            fail_mark=fail_mark,
            warning_mark=warning_mark
        )

        rqm_step_3_result = check_results(files_folder, "---- RQM test step 3:  DmpID Check", 4)
        rqm_step_3_warning = check_results(files_folder, "---- RQM test step 3:  DmpID Check", 6)

        write_rqm_step_result(
            test_summary_html=test_summery_html,
            rqm_testcase_string="RQM Step 3: Check the range of the MOD_ID with this ranges:",
            rqm_result = rqm_step_3_result,
            pass_comment="MOD_ID is within the expected range",
            fail_comment="MOD_ID is not within the expected range, test failed.",
            pass_warning = rqm_step_3_warning,
            results_html=results_html_relative,
            check_mark=check_mark,
            fail_mark=fail_mark,
            warning_mark=warning_mark,
        )

        rqm_step_4_result = check_results(files_folder, "---- RQM test step 4:  ModID Check", 4)
        rqm_step_4_warning = check_results(files_folder, "---- RQM test step 4:  ModID Check", 6)   

        write_rqm_step_result(
            test_summary_html=test_summery_html,
            rqm_testcase_string="RQM Step 4: Check MOD_ID with the different ranges:",
            rqm_result = rqm_step_4_result,
            pass_comment="DMP_ID is within the expected value.",
            fail_comment="DMP_ID is not within the expected value, test failed.",
            pass_warning = rqm_step_4_warning,
            results_html=results_html_relative,
            check_mark=check_mark,
            fail_mark=fail_mark,
            warning_mark=warning_mark
        )

        rqm_step_5_result = check_results(files_folder, "---- RQM test step 5:  Radio Astronomy Protection Check", 4)

        write_rqm_step_result(
            test_summary_html=test_summery_html,
            rqm_testcase_string="RQM Step 5: Radio Astronomy Protection check",
            rqm_result = rqm_step_5_result,
            pass_comment="Radio Astronomy Protection is working as expected.",
            fail_comment="Radio Astronomy Protection is not working as expected, test failed.",
            pass_warning=None,
            results_html=results_html_relative,
            check_mark=check_mark,
            fail_mark=fail_mark,
            warning_mark=warning_mark
        )

        print(f"RTPS Test summery HTML created at: {test_summery_html}")

    if mal_checks == 1:
        print("Transfering MAL results")
        test_summery_html = create_Gen7_test_summery_html(bosch_stripe, bosch_logo, "MAL", test_results_folder)
        with open(test_summery_html, 'a', encoding='utf-8') as html_file:
            html_file.write(f'<h2>561319: SYS_INT_VC_MAL_xGU_OnlineMisalignment</h2>\n')
        write_measurements_to_html(test_summery_html, measurement_list)
        results_html_relative = find_html_file_relative(files_folder)
        rqm_step_1_result_az = check_results(files_folder , "Expected Constant Value: Azimuth_OSS_Text_Check == Pass", 3)
        rqm_step_1_result_el = check_results(files_folder , "Expected Constant Value: Elevation_OSS_Text_Check == Pass", 3)

        write_rqm_step_result(
            test_summary_html=test_summery_html,
            rqm_testcase_string="RQM Step 1: Azimuth and Elevation OSS Text Check",
            rqm_result = "PASSED" if rqm_step_1_result_az == "PASSED" and rqm_step_1_result_el == "PASSED" else "FAILED",
            pass_comment="Azimuth and Elevation OSS Text Check passed.",
            fail_comment="Azimuth and/or Elevation OSS Text Check failed.",
            pass_warning=None,
            results_html=results_html_relative,
            check_mark=check_mark,
            fail_mark=fail_mark,
            warning_mark=warning_mark
        )

        rqm_step_2_result_az = check_results(files_folder , "Azimuth_MAL_function_check == Pass", 3)
        rqm_step_2_result_el = check_results(files_folder , "Elevation_MAL_function_check == Pass", 3)
        write_rqm_step_result(
            test_summary_html=test_summery_html,
            rqm_testcase_string="RQM Step 2: Azimuth and Elevation MAL Function Check",
            rqm_result = "PASSED" if rqm_step_2_result_az == "PASSED" and rqm_step_2_result_el == "PASSED" else "FAILED",
            pass_comment="Azimuth and Elevation MAL Function Check passed.",
            fail_comment="Azimuth and/or Elevation MAL Function Check failed.",
            pass_warning=None,
            results_html=results_html_relative,
            check_mark=check_mark,
            fail_mark=fail_mark,
            warning_mark=warning_mark
        )

        rqm_step_3_result_az = check_results(files_folder , "Expected Constant Value: Azimuth_Orientation_check == Pass", 3)
        rqm_step_3_result_el = check_results(files_folder , "Expected Constant Value: Elevation_Orientation_check == Pass", 3)
        write_rqm_step_result(
            test_summary_html=test_summery_html,
            rqm_testcase_string="RQM Step 3: Azimuth and Elevation Orientation Check",
            rqm_result = "PASSED" if rqm_step_3_result_az == "PASSED" and rqm_step_3_result_el == "PASSED" else "FAILED",
            pass_comment="Azimuth and Elevation Orientation Check passed.",
            fail_comment="Azimuth and/or Elevation Orientation Check failed.",
            pass_warning=None,
            results_html=results_html_relative,
            check_mark=check_mark,
            fail_mark=fail_mark,
            warning_mark=warning_mark
        )
        print(f"MAL Test summery HTML created at: {test_summery_html}") 


if __name__ == "__main__":
    main()