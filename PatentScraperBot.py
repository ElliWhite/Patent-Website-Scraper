from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import csv
import math
import getpass
import re

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

                contentRow = driver.find_element_by_id('contentRow_%d' % publicationID)
                contentRowSplit = re.sub("[^\w]", " ",  contentRow.text).split()
                crIndex = contentRowSplit.index('info')
                resPubInfo.insert(linkCount, contentRowSplit[crIndex+1])

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

            contentRow = driver.find_element_by_id('contentRow_%d' % publicationID)
            contentRowSplit = re.sub("[^\w]", " ",  contentRow.text).split()
            crIndex = contentRowSplit.index('info')
            resPubInfo.insert(linkCount, contentRowSplit[crIndex+1])
                
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

print "TIME TAKEN IN SECS = %d" % totalTime
print "TIME TAKEN IN MIN = %d" % (totalTime / 60)

driver.quit();
