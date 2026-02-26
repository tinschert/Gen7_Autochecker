
import os
import sys
from bs4 import BeautifulSoup
from easygui import *
import pandas as pd
# Set the option to opt-in to the future behavior
try:
    pd.set_option('future.no_silent_downcasting', True)
except:
    pass
import shutil
import time
from pathlib import Path

rows_from_html_file=[]
rows_from_html_file.clear()
flag_indigo = 0
test_summary = []
test_summary.clear()

def Write_Out_HTML():
    output_html = soup.contents
    html = soup.prettify("utf-8")
    with open(output_file, "wb") as file:
        file.write(html)


#main function (program entry point)
def main():
    print('===========================================================')
    print('CANoe reports splitter by Ventsislav Negentsov, version 1.5')
    print('===========================================================')
    print('Argument list', sys.argv)
    try:
        input_file = sys.argv[1]
    except:
        input_file = fileopenbox("Select the HTML CANoe report file : ")

    input_file_name_only_list = input_file.split("\\")
    input_file_name_only_string = input_file_name_only_list[len(input_file_name_only_list) - 1]
    print("Chosen file : ", input_file_name_only_string)
    soup = BeautifulSoup(open(input_file, encoding="utf8"), "html.parser")
    soup2 = BeautifulSoup()
    soup2.clear()
    # extracts the head and formatting of HTML
    for el in soup('head'):
        soup2.append(el)
    ############################
    # extracts the OverView Table
    ############################
    soup = BeautifulSoup(open(input_file, encoding="utf8"), "html.parser")  # starts from beginning again
    for el in soup('table'):
        attributes_dict = el.attrs
        # print(attributes_dict)
        if "class" in attributes_dict.keys():
            # print(el["class"])
            if el["class"][0].find('OverviewTable') >= 0:
                soup2.append(el)
                # print("DEBUG 1")
    html2 = soup2.prettify("utf-8")
    with open("Overview_Table.html", "wb") as file:
        file.write(html2)

    ############################
    # removes the OverView Table
    ############################
    for el in soup('table'):
        attributes_dict = el.attrs
        # print(attributes_dict)
        if "class" in attributes_dict.keys():
            # print(el["class"])
            if el["class"][0].find('OverviewTable') >= 0:
                el.extract()
                # print("DEBUG 1")
    ############################
    # removes the OverallResultTable
    ############################
    for el in soup('table'):
        attributes_dict = el.attrs
        # print(attributes_dict)
        if "class" in attributes_dict.keys():
            # print(el["class"])
            if el["class"][0].find('OverallResultTable') >= 0:
                el.extract()
                # print("DEBUG 1")

    # creates a temporary file without the Overview table
    html = soup.prettify("utf-8")
    with open(input_file + "_tmp", "wb") as file:
        file.write(html)
    ################################################################################
    # open the temp HTML (the Overview Table is removed)
    f1 = open(input_file + "_tmp", "r")
    for x in f1:
        rows_from_html_file.append(x)
    f1.close()

    number_of_testcases_in_report = 0
    counter1 = -1
    for el in rows_from_html_file:
        counter1 = counter1 + 1
        # print(el)
        if (el.find(".text)") >= 0):
            # print(rows_from_html_file[counter1 + 10])
            if (rows_from_html_file[counter1 + 10].find("Passed") >= 0 or rows_from_html_file[counter1 + 10].find(
                    "Failed") >= 0):
                test_summary.append([rows_from_html_file[counter1 + 8], rows_from_html_file[counter1 + 10]])
                number_of_testcases_in_report = number_of_testcases_in_report + 1
    print("number_of_testcases_in_report = ", number_of_testcases_in_report)
    print("test_summary = ", test_summary)
    try:
        os.mkdir("Split_Reports_Output")
    except:
        print("Folder 'Split_Reports_Output' already exists !")
        pass
        # folder already exists

    for el in range(number_of_testcases_in_report):
        current_testcase = el + 1
        print("Currently processing testcase = ", current_testcase)
        flag_indigo = 1  # output is ON
        temp_str = test_summary[el][0]
        temp_str = temp_str.replace(":", "_")
        temp_str = temp_str.replace(" ", "_")
        temp_str = temp_str.replace("[", "_")
        temp_str = temp_str.replace("]", "_")
        temp_str = temp_str.replace("__", "_")
        temp_str = temp_str.replace("  ", " ")
        temp_str = temp_str.replace("\n", "")
        temp_str2 = test_summary[el][1]
        if (temp_str2.find("Passed") >= 0):
            temp_str = "TC_" + temp_str + "_PASSED"
        if (temp_str2.find("Failed") >= 0):
            temp_str = "TC_" + temp_str + "_FAILED"
        print(temp_str)
        new_file_name = "Split_Reports_Output\\" + input_file_name_only_string.replace(".html",
                                                                                       "") + "__" + temp_str + ".html"
        ts = time.time()
        print("timestamp = ", ts)
        my_file = Path(new_file_name)
        if my_file.is_file():
            print("File exists !!!")
            new_file_name = new_file_name.replace(".html", "") + str(ts) + ".html"
            print("new_file_name = ", new_file_name)
        else:
            #print("File does NOT exist !")
            pass
        output_file = open(new_file_name, "w+")

        cnt_separator = 0
        counter1 = -1
        for current_html_line in rows_from_html_file:
            counter1 = counter1 + 1
            if current_html_line.find('.text)') >= 0:
                if (rows_from_html_file[counter1 + 10].find("Passed") >= 0 or rows_from_html_file[counter1 + 10].find(
                        "Failed") >= 0):
                    cnt_separator = cnt_separator + 1
                    flag_indigo = 1  # output is ON
            if (cnt_separator >= 1):
                if (cnt_separator != current_testcase):
                    flag_indigo = 0  # output is OFF
                if (cnt_separator <= 0):
                    flag_indigo = 1  # output is ON
                if current_html_line.find('<td>Test case end:') >= 0:  # or current_html_line.find('End of ')>=0:
                    flag_indigo = 1  # output is ON
            if (flag_indigo == 1):
                output_file.write(current_html_line)
        output_file.close()

    try:
        shutil.move("Overview_Table.html", "Split_Reports_Output\\Overview_Table.html")
    except:
        print("The Overview Table HTML can not be moved (not existing ?!?)")

    # delete the temporary HTML file
    try:
        os.remove(input_file + "_tmp")
    except:
        print("Can not remove temp file : ", input_file + "_tmp")

    # export HTML to EXCEL
    table = pd.read_html("Split_Reports_Output\\Overview_Table.html")[0]
    table2 = pd.read_html("Split_Reports_Output\\Overview_Table.html")[1]
    # table=table.append(table2) #append method is deprecated
    table = pd.concat([table, table2], ignore_index=True)
    table.to_excel("Split_Reports_Output\\Overview_Table.xlsx")


if __name__ == "__main__":
    try:
        main()
        print("!!! Succeeded !!!")
    except:
        print("Failed to process HTML file !!!")