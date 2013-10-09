from bs4 import BeautifulSoup
import urllib
import MySQLdb
import unicodedata
import argparse
import logging
import logging.handlers
import datetime
logger = logging.getLogger()

class Craiglist:
    def __init__(self):
        parser = argparse.ArgumentParser(description="Toronto_cell_table", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument("-v", "--verbosity", action="count", default=0, help="increase output verbosity")
        args = parser.parse_args()
        self._setup_logging()
        if args.verbosity >= 2:
            logger.setLevel(logging.DEBUG)
        elif args.verbosity >= 1:
            logger.setLevel(logging.INFO)
        else:
            logger.setLevel(logging.WARNING)
        logger.debug("Finish Setting Logger")
        self.cityLink = {"/tor":"City of Toronto", "/drh": "Durham", "/yrk": "York", "/bra":"Brampton", "/mss":"Mississauga","/oak":"Oakville"}
        self.headerLink = "http://toronto.en.craigslist.ca/search/moa"
        self.footerLink = "?zoomToPosting=&query=&srchType=A&minAsk=100&maxAsk=1000"
        self.companyID = "craiglist"
        self.itemLeft = 1
        self.fullList = []
        self.resultList = []
        self.getFullList()
        self.parsePosterGeneralInfo()
        self.parseEachPosterLink()
        self.parseEachTitleContent()
        self.saveData()
    def _setup_logging(self):
        """Setup general global script logger(log)."""
        logger.setLevel(logging.WARNING)
        
        # create console handler and set level to DEBUG
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        
        # create file logger and set level to DEBUG
        filePath = '/Users/samuelchien821/MyFolder/Emart/ParseLog/' + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M.log")
        hdlr = logging.FileHandler(filePath)
        hdlr.setLevel(logging.DEBUG)
        
        # create syslog handler and set level to DEBUG (default)
        sl  = logging.handlers.SysLogHandler()
        sl.setLevel(logging.DEBUG)
        
        # create formatter for console log
        ch_formatter = logging.Formatter('%(asctime)s [%(levelname)-8s] %(message)s')
        ch.setFormatter(ch_formatter)
        
        # create hdlr formatter for file logging
        hdlr_formatter = logging.Formatter('%(asctime)s [%(levelname)-8s] %(message)s')
        hdlr.setFormatter(ch_formatter)
        
        # create formatter for sys log
        sl_formatter = logging.Formatter('%(filename)s: %(message)s')
        sl.setFormatter(sl_formatter)
        
        # add all handler to log
        logger.addHandler(ch)
        logger.addHandler(hdlr)
        logger.addHandler(sl)
    def getFullList(self):
        logger.debug("getFullList is called")
        for key in self.cityLink:
            Location = self.cityLink[key]
            nextLink = self.headerLink + key + self.footerLink
    
            while (nextLink):
                f = urllib.urlopen(nextLink)
                soup = BeautifulSoup(f.read())
                description = soup.findAll("p", {"class":"row"})
                self.fullList.append([description, Location])
                nextLink = None
                if(soup.find("span", {"class":"nplink next"}).a):
                    nextLink = soup.find("span", {"class":"nplink next"}).a["href"]

    def parsePosterGeneralInfo(self):
        logger.debug("parsePosterGeneralInfo is called")
        for listing in self.fullList:
            description = listing[0]
            Location = listing[1]
            for posterBlob in description:
                #Image URL
                try:
                    imageURL = "N/A"
                    if (posterBlob.find("a",{"class":"i"}).has_attr("data-id")):
                        imageLink = posterBlob.find("a",{"class":"i"})["data-id"]
                        imageURL = "http://images.craigslist.org/" + imageLink
                except:
                    imageURL = "N/A"
                    logger.warning("WARNING: FAIL TO PARSE IMAGE URL")
                #Poster URL
                try:
                    posterLink = posterBlob.find("a",{"class":"i"})["href"]
                    PosterURL = "http://toronto.en.craigslist.ca" + posterLink
                except:
                    PosterURL = "N/A"
                    logger.warning("WARNING: FAIL TO PARSE POSTER URL")
                #Title
                try:
                    listingTitle = posterBlob.findAll("a",{"href":posterLink})[1].string
                except:
                    listingTitle = "N/A"
                    logger.warning("WARNING: FAIL TO PARSE TITLE")
                #Price
                try:
                    price = posterBlob.find("span",{"class":"price"}).string
                    price = price.split("$")[1]
                except:
                    price = "N/A"
                    logger.warning("WARNING: FAIL TO PARSE PRICE")
    
                self.resultList.append([imageURL, PosterURL, listingTitle, price, Location])
    
    def parseEachPosterLink(self):
        logger.debug("parseEachPosterLink is called")
        for posterInfo in self.resultList:
            imageURL = posterInfo[0]
            PosterURL = posterInfo[1]
            listingTitle = posterInfo[2]
            price = posterInfo[3]
            Location = posterInfo[4]


            f = urllib.urlopen(PosterURL)
            urlPosterString = f.read()
            soup = BeautifulSoup(urlPosterString)
        
            # PosterDetail
            try:
                rawStringResult = soup.find("section", {"id": "postingbody"}).get_text().strip()
                finalPosterResult = ""
                for sentence in rawStringResult.split("\n"):
                    finalPosterResult = finalPosterResult + sentence + " "
            except:
                logger.warning("Warning: FAIL TO PARSE POSTER DETAIL")
                finalPosterResult = "N/A"
        
            # Date
            try:
                date = soup.findAll("date")[0].contents[0]
            except:
                date = "N/A"
                logger.warning("WARNING: FAIL TO PARSE DATE SOUP VARIABLE")
                    
            #email
            try:
                email = urlPosterString.split("displayEmail = \"")[1].split("\"")[0]
            except:
                email = "N/A"
        
            try:
                d = datetime.datetime.strptime(date,  '%Y-%m-%d,  %I:%M%p EDT')
                dateTimeString = d.strftime('%Y-%m-%d %H:%M')
                dateTimeInteger = d.toordinal()
            except:
                dateTimeString = "N/A"
                dateTimeInteger = "N/A"
                logger.warning("WARNING: FAIL TO PARSE DATE: " + date )
        
        
            posterInfo.extend((dateTimeString, dateTimeInteger, finalPosterResult, email))
                
    def parseEachTitleContent(self):
        logger.debug("parseEachTitleContent is called")
        for posterInfo in self.resultList:
            listingTitle = posterInfo[2]
            finalPosterResult = posterInfo[7]
                
            company = "N/A"
            phoneType = "N/A"
            version = "N/A"
            size = "N/A"
            color = "N/A"
            phoneNumber = "N/A"
                    
            baseInfoArray = [company, phoneType, version, size, color, phoneNumber, self.changeTypeToString(listingTitle)]
            baseInfoArray = self.get_List_Info_By_Text(baseInfoArray)
            
            
            listingTitle = baseInfoArray[6]
            posterInfo[2] = listingTitle
            
            baseInfoArray[6] = self.changeTypeToString(finalPosterResult)
            baseInfoArray = self.get_List_Info_By_Text(baseInfoArray)
                    
                    
            company = baseInfoArray[0]
            phoneType = baseInfoArray[1]
            version = baseInfoArray[2]
            size = baseInfoArray[3]
            color = baseInfoArray[4]
            phoneNumber = baseInfoArray[5]
            bodyString = baseInfoArray[6]
            posterInfo[7] = bodyString

            posterInfo.extend((company, phoneType, version, size, color, phoneNumber))




    def changeTypeToString(self, s):
        logger.debug("changeTypeToString is called")
        if (s == None):
            return "N/A"
        if isinstance(s, str):
            return s
        elif isinstance(s, unicode):
            return unicodedata.normalize('NFKD', s).encode('ascii','ignore')
        else:
            return str(s)

    def get_List_Info_By_Text(self, baseInfoArray):
        logger.debug("get_List_Info_By_Text is called")
    
        company = baseInfoArray[0]
        phoneType = baseInfoArray[1]
        version = baseInfoArray[2]
        size = baseInfoArray[3]
        color = baseInfoArray[4]
        phoneNumber = baseInfoArray[5]
        finalPosterResult = baseInfoArray[6]
    
    
    
        finalPosterResultParsing = ""
        for subString in finalPosterResult.split("\""):
            finalPosterResultParsing = finalPosterResultParsing + subString + " "

        finalPosterResult = ""
        for subString in finalPosterResultParsing.split("\'"):
            finalPosterResult = finalPosterResult + subString + " "    

        companyList = ["rogers", "telus", "bell", "koodo", "fido", "unlocked"]
        phoneTypeAndVersionList = {"iphone":["5", "4s", "4", "3gs"], "blackberry":["9300","9780", "9900", "q10", "9700", "z10", "9810"], "galaxy":["discover","nexus", "s3", "s4", "s2", "note"], "htc":["one", "sensation", "wildfire"], "nokia":["x2", "lumia", "x7"], "lg":["optimus"]}
        sizeList = ["16gb", "32gb", "64gb", "16g", "32g", "64g", "16", "32", "64"]
        colorList = ["blue", "black", "white"]
        numberList = ["647", "416", "705"]

        finalPosterResultList =  finalPosterResult.split(" ")

        highlightString = ""
        for word in finalPosterResultList:
            if word.lower() in companyList:
                if company == "N/A":
                    company = word.title()
                highlightString += "<strong>"
                highlightString += word
                highlightString += "</strong> "
        
            elif word.lower() in phoneTypeAndVersionList:
                if phoneType == "N/A":
                    phoneType = word.title()
                    if phoneType == "Iphone":
                        phoneType = "iPhone"
                    elif phoneType == "Htc":
                        phoneType = "HTC"
                    elif phoneType == "Lg":
                        phoneType = "LG"
                highlightString += "<strong>"
                highlightString += word
                highlightString += "</strong> "
    
            elif word.lower() == "i":
                if phoneType == "N/A":
                    phoneType = "iPhone"
                highlightString += "<strong>"
                highlightString += "iPhone"
                highlightString += "</strong> "

                    
    
            elif word.lower() in sizeList:
                if size == "N/A":
                    size = word.upper()
                highlightString += "<strong>"
                highlightString += word
                highlightString += "</strong> "
        
            elif word.lower() in colorList:
                if color == "N/A":
                    color = word.title()
                highlightString += "<strong>"
                highlightString += word 
                highlightString += "</strong> "
    
        
            elif phoneType != "N/A" and word.lower() in phoneTypeAndVersionList[phoneType.lower()]:
                if version == "N/A":
                    version = word.title()
                highlightString += "<strong>"
                highlightString += word
                highlightString += "</strong> "

            elif word[0:3] in numberList:
                if phoneNumber == "N/A":
                    phoneNumber = word
                highlightString += "<strong>"
                highlightString += word
                if (len(word) >= 10):
                    highlightString += "</strong> "

            elif phoneNumber != "N/A" and len(phoneNumber) < 10:
                phoneNumber += word
                highlightString += word
                if (len(word) >= 10):
                    highlightString += "</strong> "

            else:
                highlightString = highlightString +  word + " "




        return [company, phoneType, version, size, color, phoneNumber, highlightString]

    
    def saveData(self):
        logger.debug("Save Data is called")
        database = MySQLdb.connect(host="localhost",user="root",passwd="",db="mydata")
        cursor = database.cursor()
        queryString = "SELECT PosterID FROM cellphone_Toronto"
        cursor.execute(queryString)
        posterCount = cursor.rowcount
        
        for posterInfo in self.resultList:
            imageURL = self.changeTypeToString(posterInfo[0])
            PosterURL = self.changeTypeToString(posterInfo[1])
            listingTitle = self.changeTypeToString(posterInfo[2])
            price = self.changeTypeToString(posterInfo[3])
            Location = self.changeTypeToString(posterInfo[4])
            dateTimeString = self.changeTypeToString(posterInfo[5])
            dateTimeInteger = self.changeTypeToString(posterInfo[6])
            bodyString = self.changeTypeToString(posterInfo[7])
            email = self.changeTypeToString(posterInfo[8])
            company = self.changeTypeToString(posterInfo[9])
            phoneType = self.changeTypeToString(posterInfo[10])
            version = self.changeTypeToString(posterInfo[11])
            size = self.changeTypeToString(posterInfo[12])
            color = self.changeTypeToString(posterInfo[13])
            phoneNumber = self.changeTypeToString(posterInfo[14])
            posterID = self.changeTypeToString(posterCount)
            itemLeft = self.changeTypeToString(self.itemLeft)
            companyID = self.changeTypeToString(self.companyID)
            
            
            logger.info( "_______________________________________________________")
            logger.info(imageURL)
            logger.info(PosterURL)
            logger.info(listingTitle)
            logger.info(price)
            logger.info(Location)
            logger.info(dateTimeString)
            logger.info(dateTimeInteger)
            logger.info(bodyString)
            logger.info(email)
            logger.info(company)
            logger.info(phoneType)
            logger.info(version)
            logger.info(size)
            logger.info(color)
            logger.info(phoneNumber)
            logger.info(posterID)
            logger.info(itemLeft)
            logger.info(companyID)
        
        

            
            try:
                queryString = "INSERT INTO cellphone_Toronto (PosterID, companyID , title, dateTimeString, dateTimeInteger, location, imageLink, posterLink, posterDetail, email, minPrice, dreamPrice, lockedCompany, phoneType, version, size, color, phoneNumber, itemLeft) VALUES " + "(\"" + posterID + "\", \"" + companyID + "\", \"" + listingTitle + "\", \"" + dateTimeString + "\", \"" + dateTimeInteger + "\", \"" + Location + "\", \"" + imageURL + "\", \"" + PosterURL + "\", \"" + bodyString + "\", \"" + email + "\", \"" + price + "\", \"" + price + "\", \"" + company + "\", \"" + phoneType + "\", \"" + version + "\", \"" + size + "\", \"" + color  + "\", \"" + phoneNumber + "\", \"" + itemLeft + "\")"
                db1 = MySQLdb.connect(host="localhost",user="root",passwd="",db="mydata")
                cursor = db1.cursor()
                cursor.execute (queryString)
                db1.commit()
                posterCount += 1
            except:
                logger.warning("WARNING: FAIL TO SAVE DATA")
                continue


x = Craiglist()



















