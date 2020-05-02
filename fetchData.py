import pygsheets
gc = pygsheets.authorize() # This will create a link to authorize 

#  Open spreadsheet  

# # 1. Open spreadsheet by name 
sh = gc.open('covidProbabilityModels') # open spreadsheet

# # 2. Open spreadsheet by key
# sh = gc.open_by_key('spreadsheet_key')

# 3. Open spredhseet by link
# sh = gc.open_by_link('https://docs.google.com/spreadsheets/d/1w_67qHjxVyYtegiQLapKlk7NIlbUMvsL6Ucak-EL_Eg/edit#gid=721977854')

# Open worksheet

# wk1 = sh[0] #Open first worksheet of spreadsheet
# Or 
wk1 = sh.worksheet_by_title("Orange") # sheet1 is name of first worksheet
print(sh.worksheets)
wk1.clear(start="A2", end="A1000")
wk1.update_col(1, [2,3,4], row_offset=1)

""" First worksheet has index 0, second has index 1, so on. 
Instead of index, you can use worksheet name. 
"""