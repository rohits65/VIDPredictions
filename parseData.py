import os
from datetime import date, datetime, timedelta

from dateutil.parser import parse


def delete_line(original_file, line_number):
    """ Delete a line from a file at the given line number """
    is_skipped = False
    current_index = 0
    dummy_file = original_file + '.bak'
    # Open original file in read only mode and dummy file in write mode
    with open(original_file, 'r') as read_obj, open(dummy_file, 'w') as write_obj:
        # Line by line copy data from original file to dummy file
        for line in read_obj:
            # If current line number matches the given line number then skip copying
            if current_index != line_number:
                write_obj.write(line)
            else:
                is_skipped = True
            current_index += 1
 
    # If any line is skipped then rename dummy file as original file
    if is_skipped:
        os.remove(original_file)
        os.rename(dummy_file, original_file)
    else:
        os.remove(dummy_file)

def pullParameters(FILE, runTier):
    initData = {
        "COUNTY_NAME": None,
        "FIRST_CASE_DATE": None,
        "POPULATION_SIZE": None,
        "START_DATE": None
    }
    count = 0
    leave = True
    firstLine = True
    with open(FILE,"r") as fi:
        for ln in fi:
            if ln.startswith("# " + str(runTier)) ==  False and leave == True and firstLine:
                firstLine = False
                return None
                break
            elif firstLine:
                firstLine = False
                continue
            if ln.startswith("#") and ln.startswith("# 1") == False and ln.startswith("# 2") == False and ln.startswith("# 3") == False and ln.startswith("# 4") == False and ln.startswith("# 5") == False and ln.startswith("# 9") == False:
                newLn = ln.split("#",1)[1].strip(" ").strip("\n")
                
                data = newLn.split("=")
                try:
                    initData[data[0].strip(" ")] = int(data[1].strip(" "))
                except ValueError:
                    initData[data[0].strip(" ")] = data[1].strip(" ")
            else:
                try:
                    dataValue = int(ln)
                    count += 1
                except:
                    pass
            leave = False
        
        date = parse(initData["FIRST_CASE_DATE"]) + timedelta(days=(count-1))
        date = str(date.strftime('%m-%d-%Y'))#[0:-2])

        initData["START_DATE"] = date
        return initData
        


# delete_line("web/data/SanMateoNewCases.html", 12)
# pullParameters("main/Data/SantaClara.txt")
