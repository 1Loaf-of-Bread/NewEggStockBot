from colorama import Fore, init
import requests
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

init()

def get_page_html(url):
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"}
    page = requests.get(url, headers=headers)
    return page.content


def check_item_in_stock(page_html):
    global totalPrice
    global totalInv
    global totalName

    soup = BeautifulSoup(page_html, 'html.parser')

    divProductPrice = soup.find("li", {"class": "price-current"})
    priceSoup = BeautifulSoup(str(divProductPrice), 'html.parser')
    priceText = [*priceSoup.stripped_strings]
    totalPrice = ": "
    for i in priceText:
        totalPrice = str(totalPrice) + i

    divProductInv = soup.find("div", {"class": "product-inventory"}).find("strong")
    invSoup = BeautifulSoup(str(divProductInv), 'html.parser')
    invText = [*invSoup.stripped_strings]
    totalInv = ": "
    for i in invText:
        totalInv = i

    divProductName = soup.find("h1", {"class": "product-title"})
    nameSoup = BeautifulSoup(str(divProductName), 'html.parser')
    nameText = [*nameSoup.stripped_strings]
    totalName = ": "
    for i in nameText:
        totalName = i


def check_inventory():
    page_html = get_page_html(url)
    check_item_in_stock(page_html)

    if totalInv=="OUT OF STOCK.":
        now = datetime.now()
        currentTime = now.strftime("%d/%m/%Y %H:%M:%S")
        print(str(currentTime) + ": Out of stock")
        itemStock = False
        
    if totalInv=="In stock.":
        itemStock = True

    if itemStock==True:
        emailSubject = "Item In Stock!!"
        soundAlarm(emailSubject)

    if itemStock==False:
        now = datetime.now()
        currentTime = now.strftime("%d/%m/%Y %H:%M:%S")
        print(str(currentTime) + ": Re-Checking in 30 minutes.")
        sleep(1800)
        check_inventory()

    else:
        print(Fore.RED + "Critical Error: " + Fore.WHITE + "Item Stock Not Found.")
        print(Fore.RESET)
        input("Press ENTER to Exit...")
        exit()


def soundAlarm(emailSubject):
    now = datetime.now()
    currentTime = now.strftime("%d/%m/%Y %H:%M:%S")
    print()
    print(str(currentTime) + ": Item is in stock!")
    print("Sending Email...")
    sendEmail(emailSubject)


def sendEmail(emailSubject):
    message = MIMEMultipart("alternative")
    message["Subject"] = emailSubject
    message["From"] = senderEmail
    message["To"] = receiverEmail

    text = f"""\
    Hello,
    The Iten you Requested is in Stock!

    Name: {totalName}
    URL: {url}
    Price: {totalPrice}"""

    emailText = MIMEText(text, "plain")
    message.attach(emailText)
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(senderEmail, senderEmailPassword)
        server.sendmail(
            senderEmail, receiverEmail, message.as_string()
        )

    print()
    print("Email Sent!")
    print()
    print()
    input("Press ENTER to Exit...")
    exit()
    


senderEmail = input("Sender Email: ")
senderEmailPassword = input("Password: ")
receiverEmail = input("Reciever Email: ")
url = input("URL: ")
print()
check_inventory()