import os
import sys
from bs4 import BeautifulSoup
import shutil

rows_from_html_file=[]
rows_from_html_file.clear()
flag_indigo = 0

def Write_Out_HTML():
    output_html = soup.contents
    html = soup.prettify("utf-8")
    with open(output_file, "wb") as file:
        file.write(html)

def HTML_Scrapper():
    # removes the OverView Table
    for el in soup('table'):
        attributes_dict = el.attrs
        # print(attributes_dict)
        if "class" in attributes_dict.keys():
            # print(el["class"])
            if el["class"][0].find('OverviewTable') >= 0:
                el.extract()
                print("DEBUG 1")
            # if ("OverviewTable" in el["class"].keys()):
            #   print(el["class"]["OverviewTable"])
            # el.extract()
            # el.decompose()

    #<table class="GroupHeadingTable">
    cnt = 0
    for el in soup('table'):
        attributes_dict = el.attrs
        # print(attributes_dict)
        if "class" in attributes_dict.keys():
            # print(el["class"])
            if el["class"][0].find('GroupHeadingTable') >= 0:
                el.extract()
                print("DEBUG 1")
                # print(el)
                cnt = cnt + 1
                if (cnt == 3):
                    print("removed")
                    el.extract()
                if (cnt == 4):
                    print("removed")
                    el.extract()

    # removes the 1.2.x Table
    for el in soup('table'):
        attributes_dict = el.attrs
        # print(attributes_dict)
        if "id" in attributes_dict.keys():
            # print( el["id"])
            if (el["id"].find("tbl_1.2") >= 0):
                # print("removed elements : ", el["id"])
                # el.extract()
                pass

    for el in soup('tr'):
        if el.find(string='not executed'):
            # print(el)
            # el.extract()
            # el.decompose()
            pass
    for el in soup('tr'):
        if el.find(string='1.2') or el.find(string='1.2.1') or el.find(string='1.2.2') or el.find(
                string='1.2.3') or el.find(string='1.2.4'):
            # print(el)
            # el.extract()
            # el.decompose()
            pass
    for el in soup('td'):
        if el.find(string='1.2') or el.find(string='1.2.1') or el.find(string='1.2.2') or el.find(
                string='1.2.3') or el.find(string='1.2.4'):
            # print(el)
            # el.extract()
            # el.decompose()
            pass


def Generate_List_Of_Files(folder):
    listOfFile = os.listdir(folder)
    allFiles = list()
    for entry in listOfFile:
        fullPath = os.path.join(folder, entry)
        if os.path.isdir(fullPath):
            allFiles = allFiles + Generate_List_Of_Files(fullPath)
        else:
            if fullPath.find(".blf")>=0: #add only blf files
                allFiles.append(fullPath)
    return allFiles

def main():
    print('===========================================================')
    print('CANoe reports splitter by Ventsislav Negentsov, version 1.1')
    print('===========================================================')
    print('argument list', sys.argv)
    input_file = sys.argv[1]

    soup = BeautifulSoup(open(input_file, encoding="utf8"), "html.parser")

    ############################
    # removes the OverView Table
    ############################
    for el in soup('table'):
        attributes_dict=el.attrs
        #print(attributes_dict)
        if "class" in attributes_dict.keys():
            #print(el["class"])
            if el["class"][0].find('OverviewTable')>=0:
                el.extract()
                #print("DEBUG 1")
    html = soup.prettify("utf-8")
    with open(input_file+"_tmp", "wb") as file:
        file.write(html)
################################################################################
# open the HTML
    f1 = open(input_file+"_tmp", "r")
    for x in f1:
        rows_from_html_file.append(x)
    f1.close()

    number_of_testcases_in_report=-1
    for el in rows_from_html_file:
        if el.find('<table class="GroupHeadingTable">')>=0:
            number_of_testcases_in_report=number_of_testcases_in_report+1
    print("number_of_testcases_in_report = ",number_of_testcases_in_report)

    try:
        os.mkdir("Split_Reports_Output")
    except:
        pass
        #folder already exists

    for el in range(number_of_testcases_in_report):
        current_testcase=el+1
        print ("Currently processing testcase = ",current_testcase)
        flag_indigo = 1 #output is ON
        output_file = open("Split_Reports_Output\\"+str(current_testcase)+"_split_"+sys.argv[1], "w+")
        cnt_separator = -1
        for current_html_line in rows_from_html_file:
            if current_html_line.find('<table class="GroupHeadingTable">')>=0:
                cnt_separator=cnt_separator+1
                flag_indigo = 1  # output is ON
            if (cnt_separator>=1):
                if (cnt_separator!=current_testcase):
                    flag_indigo=0   #output is OFF
                if (cnt_separator <= 0):
                    flag_indigo = 1  # output is ON
                if current_html_line.find('<td>End of Test Fixture:')>=0:
                    flag_indigo=1   #output is ON
            if (flag_indigo==1):
                output_file.write(current_html_line)
        output_file.close()



if __name__ == "__main__":
    main()

