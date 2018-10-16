from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import csv
import math
import getpass
import re
import os

timeNow = time.time()

user = getpass.getuser()

driver = webdriver.Chrome("C:\Users\%s\Desktop\chromedriver.exe" % user)

with open("C:\Users\%s\Desktop\patentqueries.txt" % user) as f:
    queries = f.readlines()

queries = [x.strip() for x in queries]

print queries

listResNumbers = []

resTitleStrings = []

overallCount = 0

queryNum = 0

for query in queries:

    resNames = []

    resLinks = []

    resPubInfo = []

    driver.get("https://worldwide.espacenet.com")

    searchForm = driver.find_element_by_xpath("//textarea[@name='query']")
    
    searchForm.send_keys(query)

    searchForm.submit()

    time.sleep(2)

    numResultsFoundMsg = driver.find_element_by_class_name("numResultsFoundMsg")

    print numResultsFoundMsg.text + " " + query

    for element in numResultsFoundMsg.text.split():
        if "," in element:
            element = element.replace(",", "")
        if element.isdigit():
            numResults = int(element)
            listResNumbers.insert(queryNum, numResults)
            print numResults

    # find out how many times to click "load more" button, rounded up
    timesToClickLoad = int((math.ceil(numResults / 25.0)) - 1)

    # need to load more links as only 25 are displayed initially
    if numResults > 25:
                
        print "Clicking LOAD-MORE button %i times" % timesToClickLoad

        publicationID = 1
        linkCount = 0
        
        for i in range(0, timesToClickLoad):
            
            # now save all the links to patents
            pubNames = driver.find_elements_by_class_name('publicationLinkClass')
            
            for name in pubNames:
                resNames.insert(linkCount, str(name.text))
                try:
                    publicationLink = driver.find_element_by_id('publicationId%d' % publicationID)
                    href = publicationLink.get_attribute('href')
                    resLinks.insert(linkCount, href)
                except:
                    print "COULDN'T FIND PUBLICATION %d" % publicationID

                try:
                    titleRow = driver.find_element_by_id('titleRow_%d' % publicationID)
                except:
                    print "COULDN'T FIND TITLE ROW %d" % publicationID

                try:
                    contentRow = driver.find_element_by_id('contentRow_%d' % publicationID)
                    contentRowSplit = re.sub("[^\w]", " ",  contentRow.text).split()
                    crIndex = contentRowSplit.index('info')
                    resPubInfo.insert(linkCount, contentRowSplit[crIndex+1])
                except:
                    print "COULDN'T FIND CONTENT ROW %d" % publicationID

                publicationID = publicationID + 1
                linkCount = linkCount + 1
            
            try:
                #try to click "load more results button"
                driver.find_element_by_id('nextPageLinkBottom').click()
            except:
                print "COULD NOT FIND ""NEXT"" BUTTON"
                break
            time.sleep(1)
            
    else:
        
        publicationID = 1
        linkCount = 0
        
        # now save all the links to patents
        pubNames = driver.find_elements_by_class_name('publicationLinkClass')
        
        for name in pubNames:
            resNames.insert(linkCount, str(name.text))
            try:
                publicationLink = driver.find_element_by_id('publicationId%d' % publicationID)
                href = publicationLink.get_attribute('href')
                resLinks.insert(linkCount, href)
            except:
                print "COULDN'T FIND PUBLICATION %d" % publicationID

            try:
                titleRow = driver.find_element_by_id('titleRow_%d' % publicationID)
            except:
                print "COULDN'T FIND TITLE ROW %d" % publicationID

            try:
                contentRow = driver.find_element_by_id('contentRow_%d' % publicationID)
                contentRowSplit = re.sub("[^\w]", " ",  contentRow.text).split()
                crIndex = contentRowSplit.index('info')
                resPubInfo.insert(linkCount, contentRowSplit[crIndex+1])
            except:
                print "COULDN'T FIND CONTENT ROW %d" % publicationID
                
            publicationID = publicationID + 1
            linkCount = linkCount + 1

    with open('C:/Users/%s/Desktop/PatentNumberResults.csv' % user, 'a') as file:
        fileWriter = csv.writer(file, lineterminator='\n')
        fileWriter.writerow([queries[queryNum], listResNumbers[queryNum]])
        j = 0
        for newName in resNames:
            boolSameName = False
            if len(resTitleStrings) != 0:
                for comparableName in resTitleStrings:
                    #now compare new patent title to already writen titles in document
                    if newName == comparableName:
                        boolSameName = True
                        print "PATENT ""%s"" ALREADY EXISTS IN DOCUMENT" % newName
                        break
            if boolSameName == False:
                resTitleStrings.insert(overallCount, newName)
                fileWriter.writerow(["", "", newName, resPubInfo[j], '=HYPERLINK("%s")' % resLinks[j]])
                j = j + 1
                overallCount = overallCount + 1

    queryNum = queryNum + 1

timeEnd = time.time()

totalTime = timeEnd - timeNow

#print "TIME TAKEN IN SECS = %d" % totalTime
print "TIME TAKEN TO SEARCH ESPACE.NET IN MIN = %d" % (totalTime / 60)

queryNum = 0

for query in queries:

    driver.get("https://patents.google.com")

    searchTextBox = driver.find_element_by_xpath("//input[@name='q']")

    searchTextBox.send_keys(query)

    driver.find_element_by_id('searchButton').click()

    time.sleep(2)

    downloadButton = driver.find_element_by_xpath("//a[@class='style-scope search-results']")

    downloadLink = downloadButton.get_attribute('href')

    driver.get(downloadLink)

    time.sleep(2)

    #this is the line used for university PCs
    #fileList = os.listdir(r"C:\Users\%s\Downloads" % user)

    #this is the line used for Elliott's PC ONLY
    fileList = os.listdir(r"D:\Downloads")

    matching = [s for s in fileList if "gp-search" in s]
        
    x = len(matching)

    print matching[x-1]

    #uncomment this next line and comment out the 2nd line for use on university PCs
    #with open('C:\Users\%s\Downloads\%s' % (user, matching[x-1]), 'r') as file:
    with open('D:\Downloads\%s' % matching[x-1], 'r') as downloadedFile:
        downloadedFileReader = csv.reader(downloadedFile, delimiter=' ', quotechar='|')
        rowCounter =  1
        newAppNumList = []
        for row in downloadedFileReader:
            if rowCounter > 2:
                appNum = row[0].split(",")
                appNum = appNum[0]
                appNum = appNum.split("-")
                appNum = appNum[0] + appNum[1]
                newAppNumList.append(appNum)
            rowCounter = rowCounter + 1
        print rowCounter
        rowCounter = rowCounter - 3
        with open('C:/Users/%s/Desktop/PatentNumberResults.csv' % user, 'r') as fileRead:
            fileReader = csv.reader(fileRead, lineterminator='\n')
            #need to iterate over rows in PatentNumberResults.csv and build up a list of the application numbers
            appNumList = []
            for row in fileReader:
                try:
                    if len(row[3]) != 0:
                        appNumList.append(row[3])
                except:
                    print "row[3] is empty in PatentNumberResults.csv"
            with open('C:/Users/%s/Desktop/PatentNumberResults.csv' % user, 'a') as fileWrite:
                fileWriter = csv.writer(fileWrite, lineterminator='\n')
                fileWriter.writerow([queries[queryNum], rowCounter])
                for applicationNumber in newAppNumList:
                    boolSameName = False
                    for existingAppNum in appNumList:
                        if applicationNumber == existingAppNum:
                            boolSameName = True
                            print "PATENT ""%s"" ALREADY EXISTS IN DOCUMENT" % applicationNumber
                            break
                    #now need to write info into file
                    #currently only writes application number
                    if boolSameName == False:
                        print "WRITING %d TO FILE" % applicationNumber
                        fileWriter.writerow(["","","",applicationNumber])

                    #time.sleep(2)

            
    
    queryNum = queryNum + 1



    

driver.quit();
