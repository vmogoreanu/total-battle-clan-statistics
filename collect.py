import pyautogui
import pytesseract
import random
import time
import csv
from datetime import datetime, timedelta
import sys

chestsToCollect = 5000
if len(sys.argv) > 1 :
    chestsToCollect = int(sys.argv[1])

def clean(s):
    return s.strip(" ~\\/),.;|-=_'\"") 

accountDict = {}

def accountFix(s):
    s= clean(s)
    for k in accountDict.keys():
        s= s.replace(k, accountDict[k])
    return s

def loadAccountsDict():
    with open('accounts-dict.csv') as file: 
        heading = next(file) 
        reader = csv.reader(file) 

        for row in reader: 
            accountDict[row[0]]= row[1]


print("Started")
print("loading accounts dictionary")
loadAccountsDict()
print(accountDict)

print("Started collecting " + str(chestsToCollect) + " chests")
 
# writing the data into CSV file
with open("data.csv", 'a+', newline ='') as file:    
    writer = csv.writer(file)
    
    for x in range(chestsToCollect):
        print("Processing attempt #: {0}".format(x + 1))

        image= pyautogui.screenshot(region=[780, 410 ,450, 90])
        
        text = pytesseract.image_to_string(image)
        print('OCR result:\n' + text)
        lines = text.splitlines()
        if(len(lines) == 0):
            print("OCR didn't find info, waiting...")
            image.save("info.png")
            break
            time.sleep(30)
            continue
        
        i = 0
        chestType = clean(lines[i])
        i = i + 1
        
        if(lines[i].strip() == "") :
            i = i + 1
        account = accountFix(lines[i])
        i = i + 1
        
        if(lines[i].strip() == "") :
            i = i + 1
        source = clean(lines[i])

        if account.startswith("From"):
            account= account[5:].strip()
        else: 
            if account.startswith("rom"):
                account= account[4:].strip()
            else:
                print("From not found in " + account)
                image.save("info.png")
                break
    
        if "Source" in source or "source" in source:
            source= source[7:].strip()
        else:
            print("Source: not found")
            image.save("info.png")
            break                

        print("chestType: "+ chestType)
        print("account: "+ account)
        print("source: "+ source)

        buttonX = 1350
        buttonY = 490
        image= pyautogui.screenshot(region=[buttonX-20, buttonY-20 ,50, 30])
        buttonText = pytesseract.image_to_string(image).strip()

        print("button: "+ buttonText)
        if (buttonText == "Open") and (account != ""):
            print("writing to file")

            # get the current date and time
            now = datetime.now()
            writer.writerow([now.isoformat(), account, chestType, source])
            file.flush()

            buttonX = buttonX + random.randint(0,2)
            buttonY = buttonY + random.randint(0,2)
            print("click: {0}".format([buttonX, buttonY]))
            pyautogui.click(x=buttonX, y=buttonY) 
            time.sleep(.65 + random.randint(0,2)/10)
        else:
            print("Open button not found")
            image.save("button.png")
            break
        
print("End. next run before: " + (datetime.now() + timedelta(hours=19)).strftime("%Y-%m-%d %H:%M"))     


