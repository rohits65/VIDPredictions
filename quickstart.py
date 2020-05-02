from __future__ import print_function
from pprint import pprint
import datetime
import os
import pickle
# from datetime import timedelta

import numpy as np
import pandas as pd
from googleapiclient.discovery import build
import pygsheets as pg


class SpreadsheetOperations(object):
    def __init__(self, service):
        self.service = service

    def create(self, title):
        service = self.service
        # [START sheets_create]
        spreadsheet = {
            'properties': {
                'title': title
            }
        }
        spreadsheet = service.spreadsheets().create(body=spreadsheet,
                                                    fields='spreadsheetId').execute()
        print('Spreadsheet ID: {0}'.format(spreadsheet.get('spreadsheetId')))
        # [END sheets_create]
        return spreadsheet.get('spreadsheetId')

    def batch_update(self, spreadsheet_id, title, find, replacement):
        service = self.service
        # [START sheets_batch_update]
        requests = []
        # Change the spreadsheet's title.
        requests.append({
            'updateSpreadsheetProperties': {
                'properties': {
                    'title': title
                },
                'fields': 'title'
            }
        })
        # Find and replace text
        requests.append({
            'findReplace': {
                'find': find,
                'replacement': replacement,
                'allSheets': True
            }
        })
        # Add additional requests (operations) ...

        body = {
            'requests': requests
        }
        response = service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=body).execute()
        find_replace_response = response.get('replies')[1].get('findReplace')
        print('{0} replacements made.'.format(
            find_replace_response.get('occurrencesChanged')))
        # [END sheets_batch_update]
        return response

    def get_values(self, spreadsheet_id, range_name):
        service = self.service
        # [START sheets_get_values]
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=range_name).execute()
        rows = result.get('values', [])
        print('{0} rows retrieved.'.format(len(rows)))
        # [END sheets_get_values]
        return result

    def batch_get_values(self, spreadsheet_id, _range_names):
        service = self.service
        # [START sheets_batch_get_values]
        range_names = [
            # Range names ...
        ]
        # [START_EXCLUDE silent]
        range_names = _range_names
        # [END_EXCLUDE]
        result = service.spreadsheets().values().batchGet(
            spreadsheetId=spreadsheet_id, ranges=range_names).execute()
        ranges = result.get('valueRanges', [])
        print('{0} ranges retrieved.'.format(len(ranges)))
        # [END sheets_batch_get_values]
        return result

    def update_values(self, spreadsheet_id, range_name, value_input_option,
                      _values):
        service = self.service
        # [START sheets_update_values]
        values = [
            [
                # Cell values ...
            ],
            # Additional rows ...
        ]
        # [START_EXCLUDE silent]
        values = _values
        # [END_EXCLUDE]
        body = {
            'values': values
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption=value_input_option, body=body).execute()
        print('{0} cells updated.'.format(result.get('updatedCells')))
        # [END sheets_update_values]
        return result

    def batch_update_values(self, spreadsheet_id, range_name,
                            value_input_option, _values):
        service = self.service
        # [START sheets_batch_update_values]
        values = [
            [
                # Cell values ...
            ],
            # Additional rows
        ]
        # [START_EXCLUDE silent]
        values = _values
        # [END_EXCLUDE]
        data = [
            {
                'range': range_name,
                'values': values
            },
            # Additional ranges to update ...
        ]
        body = {
            'valueInputOption': value_input_option,
            'data': data
        }
        result = service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id, body=body).execute()
        print('{0} cells updated.'.format(result.get('totalUpdatedCells')))
        # [END sheets_batch_update_values]
        return result

    def append_values(self, spreadsheet_id, range_name, value_input_option,
                      _values):
        service = self.service
        # [START sheets_append_values]
        values = [
            [
                # Cell values ...
            ],
            # Additional rows ...
        ]
        # [START_EXCLUDE silent]
        values = _values
        # [END_EXCLUDE]
        body = {
            'values': values
        }
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption=value_input_option, body=body).execute()
        print('{0} cells appended.'.format(result
                                           .get('updates')
                                           .get('updatedCells')))
        # [END sheets_append_values]
        return result

    def pivot_tables(self, spreadsheet_id):
        service = self.service
        # Create two sheets for our pivot table.
        body = {
            'requests': [{
                'addSheet': {}
            }, {
                'addSheet': {}
            }]
        }
        batch_update_response = service.spreadsheets() \
            .batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
        source_sheet_id = batch_update_response.get('replies')[0] \
            .get('addSheet').get('properties').get('sheetId')
        target_sheet_id = batch_update_response.get('replies')[1] \
            .get('addSheet').get('properties').get('sheetId')
        requests = []
        # [START sheets_pivot_tables]
        requests.append({
            'updateCells': {
                'rows': {
                    'values': [
                        {
                            'pivotTable': {
                                'source': {
                                    'sheetId': source_sheet_id,
                                    'startRowIndex': 0,
                                    'startColumnIndex': 0,
                                    'endRowIndex': 20,
                                    'endColumnIndex': 7
                                },
                                'rows': [
                                    {
                                        'sourceColumnOffset': 1,
                                        'showTotals': True,
                                        'sortOrder': 'ASCENDING',

                                    },

                                ],
                                'columns': [
                                    {
                                        'sourceColumnOffset': 4,
                                        'sortOrder': 'ASCENDING',
                                        'showTotals': True,

                                    }
                                ],
                                'values': [
                                    {
                                        'summarizeFunction': 'COUNTA',
                                        'sourceColumnOffset': 4
                                    }
                                ],
                                'valueLayout': 'HORIZONTAL'
                            }
                        }
                    ]
                },
                'start': {
                    'sheetId': target_sheet_id,
                    'rowIndex': 0,
                    'columnIndex': 0
                },
                'fields': 'pivotTable'
            }
        })
        body = {
            'requests': requests
        }
        response = service.spreadsheets() \
            .batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
        # [END sheets_pivot_tables]
        return response

    def conditional_formatting(self, spreadsheet_id):
        service = self.service

        # [START sheets_conditional_formatting]
        my_range = {
            'sheetId': 0,
            'startRowIndex': 1,
            'endRowIndex': 11,
            'startColumnIndex': 0,
            'endColumnIndex': 4,
        }
        requests = [{
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [my_range],
                    'booleanRule': {
                        'condition': {
                            'type': 'CUSTOM_FORMULA',
                            'values': [{
                                'userEnteredValue':
                                    '=GT($D2,median($D$2:$D$11))'
                            }]
                        },
                        'format': {
                            'textFormat': {
                                'foregroundColor': {'red': 0.8}
                            }
                        }
                    }
                },
                'index': 0
            }
        }, {
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [my_range],
                    'booleanRule': {
                        'condition': {
                            'type': 'CUSTOM_FORMULA',
                            'values': [{
                                'userEnteredValue':
                                    '=LT($D2,median($D$2:$D$11))'
                            }]
                        },
                        'format': {
                            'backgroundColor': {
                                'red': 1,
                                'green': 0.4,
                                'blue': 0.4
                            }
                        }
                    }
                },
                'index': 0
            }
        }]
        body = {
            'requests': requests
        }
        response = service.spreadsheets() \
            .batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
        print('{0} cells updated.'.format(len(response.get('replies'))))
        # [END sheets_conditional_formatting]
        return response

    def filter_views(self, spreadsheet_id):
        service = self.service

        # [START sheets_filter_views]
        my_range = {
            'sheetId': 0,
            'startRowIndex': 0,
            'startColumnIndex': 0,
        }
        addFilterViewRequest = {
            'addFilterView': {
                'filter': {
                    'title': 'Sample Filter',
                    'range': my_range,
                    'sortSpecs': [{
                        'dimensionIndex': 3,
                        'sortOrder': 'DESCENDING'
                    }],
                    'criteria': {
                        0: {
                            'hiddenValues': ['Panel']
                        },
                        6: {
                            'condition': {
                                'type': 'DATE_BEFORE',
                                'values': {
                                    'userEnteredValue': '4/30/2016'
                                }
                            }
                        }
                    }
                }
            }
        }

        body = {'requests': [addFilterViewRequest]}
        addFilterViewResponse = service.spreadsheets() \
            .batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()

        duplicateFilterViewRequest = {
            'duplicateFilterView': {
                'filterId':
                addFilterViewResponse['replies'][0]['addFilterView']['filter']
                ['filterViewId']
            }
        }

        body = {'requests': [duplicateFilterViewRequest]}
        duplicateFilterViewResponse = service.spreadsheets() \
            .batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()

        updateFilterViewRequest = {
            'updateFilterView': {
                'filter': {
                    'filterViewId': duplicateFilterViewResponse['replies'][0]
                    ['duplicateFilterView']['filter']['filterViewId'],
                    'title': 'Updated Filter',
                    'criteria': {
                        0: {},
                        3: {
                            'condition': {
                                'type': 'NUMBER_GREATER',
                                'values': {
                                    'userEnteredValue': '5'
                                }
                            }
                        }
                    }
                },
                'fields': {
                    'paths': ['criteria', 'title']
                }
            }
        }

        body = {'requests': [updateFilterViewRequest]}
        updateFilterViewResponse = service.spreadsheets() \
            .batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
        # [END sheets_filter_views]

    def empty_rows(self, spreadsheet_id, range_):
        service = self.service
        clear_values_request_body = {
            # TODO: Add desired entries to the request body.
        }

        request = service.spreadsheets().values().clear(spreadsheetId=spreadsheet_id,
                                                        range=range_, body=clear_values_request_body)
        response = request.execute()

        # pprint(response)


class COVIDSpreadsheetOperations(SpreadsheetOperations):
    def __init__(self, service):
        super().__init__(service)
        self.states = {
            'AK': 'Alaska',
            'AL': 'Alabama',
            'AR': 'Arkansas',
            'AS': 'American Samoa',
            'AZ': 'Arizona',
            'CA': 'California',
            'CO': 'Colorado',
            'CT': 'Connecticut',
            'DC': 'District of Columbia',
            'DE': 'Delaware',
            'FL': 'Florida',
            'GA': 'Georgia',
            'GU': 'Guam',
            'HI': 'Hawaii',
            'IA': 'Iowa',
            'ID': 'Idaho',
            'IL': 'Illinois',
            'IN': 'Indiana',
            'KS': 'Kansas',
            'KY': 'Kentucky',
            'LA': 'Louisiana',
            'MA': 'Massachusetts',
            'MD': 'Maryland',
            'ME': 'Maine',
            'MI': 'Michigan',
            'MN': 'Minnesota',
            'MO': 'Missouri',
            'MP': 'Northern Mariana Islands',
            'MS': 'Mississippi',
            'MT': 'Montana',
            'NA': 'National',
            'NC': 'North Carolina',
            'ND': 'North Dakota',
            'NE': 'Nebraska',
            'NH': 'New Hampshire',
            'NJ': 'New Jersey',
            'NM': 'New Mexico',
            'NV': 'Nevada',
            'NY': 'New York',
            'OH': 'Ohio',
            'OK': 'Oklahoma',
            'OR': 'Oregon',
            'PA': 'Pennsylvania',
            'PR': 'Puerto Rico',
            'RI': 'Rhode Island',
            'SC': 'South Carolina',
            'SD': 'South Dakota',
            'TN': 'Tennessee',
            'TX': 'Texas',
            'UT': 'Utah',
            'VA': 'Virginia',
            'VI': 'Virgin Islands',
            'VT': 'Vermont',
            'WA': 'Washington',
            'WI': 'Wisconsin',
            'WV': 'West Virginia',
            'WY': 'Wyoming'
        }
        self.dfPopulation = pd.read_csv(
            'https://query.data.world/s/lfpwfjlgqzuabq56ekn4h7dyeigebh').to_numpy()
        self.dfCases = pd.read_csv(
            'https://query.data.world/s/ca2vuivlwqit5vmybbnckbzyf3mtoq').to_numpy()
        self.dfDeaths = pd.read_csv(
            'https://query.data.world/s/v447mfteuni64epqv52rc2fiecbg3j').to_numpy()

    def isTimeBetween(self, begin_time, end_time, check_time=None):
        # If check time is not given, default to current UTC time
        check_time = check_time or datetime.datetime.utcnow().time()
        if begin_time < end_time:
            return check_time >= begin_time and check_time <= end_time
        else:  # crosses midnight
            return check_time >= begin_time or check_time <= end_time

    def get_raw_data(self, spreadsheet_id, county, state, maxOut='', useCases=True):
        dates = SpreadsheetOperations.get_values(
            self, spreadsheet_id, county+"!A2:A"+maxOut)
        dates = np.array(dates['values'])
        dates = dates.flatten()
        maxLength = len(dates)
        firstCaseDate = datetime.datetime.strptime(
            dates[0], "%Y-%m-%d").strftime('%m-%d-%Y')
        if useCases:
            newCases = SpreadsheetOperations.get_values(
                self, spreadsheet_id, county+"!E2:E"+maxOut)
        else:
            newCases = SpreadsheetOperations.get_values(
                self, spreadsheet_id, county+"!F2:F"+maxOut)
        newCases = np.array(newCases['values'])
        newCases = newCases.flatten()
        newCases = newCases[0:maxLength]
        # print(newCases)
        for i in range(len(newCases)):
            newCases[i] = newCases[i].replace(',', '')
        newCases = [int(i) for i in newCases]

        params = SpreadsheetOperations.get_values(
            self, spreadsheet_id, county+"!G2:G3")
        params = np.array(params['values'])
        params = params.flatten()
        params = [int(i) for i in params]

        if useCases != True:
            params[0] = round(0.05658764045*params[0])

        return (firstCaseDate, newCases, params)

    def createFileData(self, file, tier, county, firstCaseDate, populationSize, data):
        try:
            os.remove(file)
        except:
            pass
        finally:
            f = open(file, "a")

        f.write("# " + str(tier) + "\n")
        f.write("# COUNTY_NAME = " + county+"\n")
        f.write("# FIRST_CASE_DATE = " + firstCaseDate+"\n")
        f.write("# POPULATION_SIZE = " + str(populationSize) + "\n\n")
        for point in data:
            f.write(str(point) + "\n")
        f.close()

    def getSheets(self, spreadsheet_id):
        sheet_metadata = self.service.spreadsheets().get(
            spreadsheetId=spreadsheet_id).execute()
        sheets = sheet_metadata.get('sheets', '')
        titles = []
        for i in range(1, len(sheets)):
            titles.append(sheets[i].get(
                "properties", {}).get("title", "Sheet1"))

        return titles

    def createFile(self, spreadsheet_id, file, county, state, maxOut, useCases=True):
        fileInformation = self.get_raw_data(
            spreadsheet_id, county, state, maxOut, useCases)
        self.createFileData(
            file, fileInformation[2][1], county, fileInformation[0], fileInformation[2][0], fileInformation[1])

    def fetchCountyIds(self, state):
        beginID = None
        endId = None
        for i in range(len(self.dfCases)):
            if self.dfCases[i][2] == state:
                if beginID == None or beginID == 0:
                    beginID = i
                else:
                    endId = i
        # GPC removal
        if state == "CA":
            beginID += 1

        return list(range(beginID+1, endId+1))
        # return dfCases["County Name"][beginID+1:endId+1]

    def fetchCountyId(self, state, county):
        '''
        County --> format: 'Santa Clara'
        State --> format: 'CA'
        '''
        for i in range(len(self.dfCases)):
            if self.dfCases[i][2] == state and self.dfCases[i][1] == county + " County":
                return i

    def getCountyData(self, countyID, state, singleCounty=True):
        countyData = self.dfCases[countyID]
        county = countyData[1].replace(" County", "")
        totalCases = countyData[4:]

        countyData = self.dfDeaths[countyID]
        totalDeaths = countyData[4:]

        startDate = datetime.datetime.strptime("2020-01-22", "%Y-%m-%d")
        # endDate = startDate+datetime.timedelta(days=len(newCases))

        datelist = pd.date_range(startDate, periods=len(totalCases)).tolist()
        datelist = [datetime.datetime.strftime(datelist[i], "%Y-%m-%d") for i in range(len(datelist))]

        population = 0
        tier = 0

        for i in range(len(self.dfPopulation)):
            # print(self.dfPopulation[i][1])
            if self.dfPopulation[i][1] == self.states[state] and self.dfPopulation[i][2] == county:
                population = int(self.dfPopulation[i][8])
                if singleCounty:
                    if population <= 100000:
                        raise Exception("Population too small")
                    elif population <= 1000000:
                        tier = 1
                    elif population <= 5000000:
                        tier = 2
                    elif population <= 10000000:
                        tier = 3
                    else:
                        tier = 4
                break

        if singleCounty:
            if totalCases[-1] < 200:
                raise Exception("Too few cases")

        params = (population, tier)

        return (datelist, totalCases, totalDeaths, params)

    def getCountiesState(self, state):
        counties = []
        for i in range(len(self.dfPopulation)):
            if self.dfPopulation[i][1] == self.states[state]:
                counties.append(self.dfPopulation[i][2])
        return counties

    def rewriteSheet(self, county, state, sheet, countyData):
        '''
        county <-- format: 'SantaClara'
        state <-- format: 'CA'
        sheet <-- pygsheets obj
        countyDate <-- returns from getCountyData()
        '''
        county = county.replace(" ", "")
        try:
            worksheet = sheet.worksheet_by_title(state+county)
        except:
            srcWorksheet = sheet.worksheet_by_title("Template")
            sheet.add_worksheet(state+county, rows=1000,
                                cols=26, src_worksheet=srcWorksheet)
            worksheet = sheet.worksheet_by_title(state+county)

        # Date reset
        worksheet.clear(start="A2", end="A1000")
        worksheet.update_col(1, list(countyData[0]), row_offset=1)

        # Case reset
        worksheet.clear(start="C2", end="C1000")
        worksheet.update_col(3, list(countyData[1]), row_offset=1)

        # Deaths reset
        worksheet.clear(start="D2", end="D1000")
        worksheet.update_col(4, list(countyData[2]), row_offset=1)

        # Params reset
        worksheet.clear(start="G2", end="G1000")
        worksheet.update_col(7, list(countyData[3]), row_offset=1)

    def updateData(self, county, state, sheet, spreadsheet_id):
        '''
        state <-- format: "CA"
        '''
        date = None
        newCasesUp = 0
        newDeaths = 0
        for i in range(len(self.dfPopulation)):
            if self.dfPopulation[i][1] == self.states[state] and self.dfPopulation[i][2] == county:
                newCasesUp = self.dfPopulation[i][9]
                newDeaths = self.dfPopulation[i][11]

        county = county.replace(" ", "")

        dates = SpreadsheetOperations.get_values(
            self, spreadsheet_id, state+county+"!A2:A")
        dates = np.array(dates['values'])
        dates = dates.flatten()
        date = datetime.datetime.strptime(dates[-1], "%Y-%m-%d")
        date += datetime.timedelta(days=1)
        date = datetime.datetime.strftime(date, "%Y-%m-%d")

        newCases = SpreadsheetOperations.get_values(
            self, spreadsheet_id, state+county+"!E2:E")
        newCases = np.array(newCases['values'])
        newCases = newCases.flatten()
        newCases = newCases[0:len(dates)]

        if newCases[-1] != newCasesUp:

            worksheet = sheet.worksheet_by_title(state+county)

            worksheet.update_col(1, [date], row_offset=len(dates)+1)
            worksheet.update_col(3, [newCasesUp], row_offset=len(dates)+1)
            worksheet.update_col(4, [newDeaths], row_offset=len(dates)+1)

    def getLastFive(self, county, state, spreadsheet_id, number):
        '''
        county <-- "CASantaClara"
        '''
        dates = SpreadsheetOperations.get_values(
            self, spreadsheet_id, county+"!A2:A")
        dates = np.array(dates['values'])
        dates = dates.flatten()
        maxLength = len(dates)
        return range(maxLength-(number-2), maxLength+1)

    def updateStateData(self, state, sheet, spreadsheet_id):
        # Specific module to update state level data with the most recent data

        # Check if current time is within time range for CA updates (PT)
        if self.isTimeBetween(datetime.time(19, 00), datetime.time(10, 00)):
            # Initialize data to append
            date = None
            newCasesUp = 0
            newDeaths = 0

            for i in range(len(self.dfPopulation)):
                if self.dfPopulation[i][1] == self.states[state]:
                    newCasesUp += self.dfPopulation[i][9]
                    newDeaths += self.dfPopulation[i][11]

            dates = SpreadsheetOperations.get_values(
                self, spreadsheet_id, state+state+"!A2:A")
            dates = np.array(dates['values'])
            dates = dates.flatten()
            date = datetime.datetime.strptime(dates[-1], "%Y-%m-%d")
            date += datetime.timedelta(days=1)
            date = datetime.datetime.strftime(date, "%Y-%m-%d")

            newCases = SpreadsheetOperations.get_values(
                self, spreadsheet_id, state+state+"!E2:E")
            newCases = np.array(newCases['values'])
            newCases = newCases.flatten()
            newCases = newCases[0:len(dates)]

            worksheet = sheet.worksheet_by_title(state+state)

            worksheet.update_col(1, [date], row_offset=len(dates)+1)
            worksheet.update_col(3, [newCasesUp], row_offset=len(dates)+1)
            worksheet.update_col(4, [newDeaths], row_offset=len(dates)+1)

    def fetchStateData(self, state):
        # init
        countyIds = self.fetchCountyIds(state)

        population = 0

        # run once to init data
        countyDates, countyCases, countyDeaths, countyParams = self.getCountyData(
            countyIds[0], state, singleCounty=False)

        # update data
        casesArray = countyCases
        deathsArray = countyDeaths
        population = countyParams[0]

        # turn countyIds into iterable to iterate through
        countyIds = iter(countyIds)

        # skip first element in countyIds
        next(countyIds)

        # loop through all remaining counties in state
        for countyId in countyIds:
            # fetch data
            countyDates, countyCases, countyDeaths, countyParams = self.getCountyData(
                countyId, state, singleCounty=False)

            # add data
            casesArray = np.add(casesArray, countyCases)
            deathsArray = np.add(deathsArray, countyDeaths)
            population += countyParams[0]

        # if COVIDSpreadsheetOperations.isTimeBetween(datetime.time(22,00), datetime.time(10,00)):
            # Update the sheet with more recent data
        return (countyDates, casesArray, deathsArray, (population, 0))


if __name__ == "__main__":
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    service = build('sheets', 'v4', credentials=creds)
    gSheets = SpreadsheetOperations(service)
    spreadsheet_id = "1w_67qHjxVyYtegiQLapKlk7NIlbUMvsL6Ucak-EL_Eg"
    gSheetsCOVID = COVIDSpreadsheetOperations(service)
    gc = pg.authorize()
    sh = gc.open('covidProbabilityModels')
    # gSheets.update_values(spreadsheet_id, "SantaClara!A1:A", 0,0)
    '''
    counties = gSheetsCOVID.getCountiesState("CA")

    for county in counties:
        try:
            countyData = gSheetsCOVID.getCountyData(gSheetsCOVID.fetchCountyId("CA", county), "CA")
            gSheetsCOVID.rewriteSheet(county, "CA", sh, countyData)
        except:
            pass
    # gSheetsCOVID.updateData("Santa Clara", "CA", sh)
    '''

    gSheetsCOVID.rewriteSheet(
        "CA", "CA", sh, gSheetsCOVID.fetchStateData("CA"))
    gSheetsCOVID.updateStateData("CA", sh, spreadsheet_id)


    '''
    gSheetsCOVID = COVIDSpreadsheetOperations(service)
    
    gSheetsCOVID.createFile(spreadsheet_id, "main/Data/SantaClara.txt", "SantaClara")
    print(gSheetsCOVID.getSheets(spreadsheet_id))
    # print(gSheets.get_values("1w_67qHjxVyYtegiQLapKlk7NIlbUMvsL6Ucak-EL_Eg", "SantaClara!A2:A"))
    # print(gSheets.get_values("1w_67qHjxVyYtegiQLapKlk7NIlbUMvsL6Ucak-EL_Eg", "SantaClara!E2:E"))
    '''
