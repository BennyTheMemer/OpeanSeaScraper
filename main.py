from bs4 import BeautifulSoup as bs
from selenium import webdriver
from datetime import datetime
import gspread
import time
import pandas as pd
import re
from urllib.parse import urlparse
import undetected_chromedriver as uc


f = open("keys.json", 'r')
pd.set_option('display.max_columns', None)

#Init google sheets

gc = gspread.service_account(filename="keys.json")
sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1D7F-38GMfyJDVI9pmiQiiau5qHcHekLcMXN2qxkGjkI/edit#gid=0").sheet1
sh2 = gc.open_by_url("https://docs.google.com/spreadsheets/d/1D7F-38GMfyJDVI9pmiQiiau5qHcHekLcMXN2qxkGjkI/edit#gid=0").worksheet("Folha2")
options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
driver = uc.Chrome(options=options)

#Init dictionary to later impo


def urlsFiller(urls):
    with open("URLs") as file:
        for line in file:
            urls.append(line.strip())
    return urls

def parseLinks(link):
    availableLinks = ["www.twitter.com", "discord.gg", "t.me"]
    domain = urlparse(link).netloc
    if domain in availableLinks:
        if domain == "www.twitter.com":
            return (1,link)
        else:
            return (1, "")
    else:
        return (0, "")


def main():

    #Init sheet
    if sh.get_all_records() == {}:
        dict = {
            "Project Site": [],
            "Marketplace": [],
            "Owners": [],
            "Twitter": [],
            "Floor" + " " + datetime.today().strftime('%d-%m'): [],
            "Discord Members" + " " + datetime.today().strftime('%d-%m'): [],
            "Twitter Followers" + " " + datetime.today().strftime('%d-%m'): [],
            "Telegram Members" + " " + datetime.today().strftime('%d-%m'): [],
        }
        urls = []
        #fill urls
        urls = urlsFiller(urls)
        print(urls)
        for url in urls:
            driver.get(url)

            soup = bs(driver.page_source, 'html.parser')
            owners = soup.find_all("h3",{"class":"Blockreact__Block-sc-1xf18x6-0 Textreact__Text-sc-1w94ul3-0 iKSQyx kscHgv"})[1].find("div", {"class":"Overflowreact__OverflowContainer-sc-10mm0lu-0 fqMVjm"}).contents[0]
            marketplace = driver.current_url
            try:
                floorPrice = soup.find("div",{"class":"Blockreact__Block-sc-1xf18x6-0 InfoItemreact__BlockContainer-sc-gubhmc-0 ctiaqU ipynZW"}).find("div", {"class":"Overflowreact__OverflowContainer-sc-10mm0lu-0 fqMVjm"}).contents[0]
            except:
                floorPrice = ""
            project = soup.find("h2", {"class":"Blockreact__Block-sc-1xf18x6-0 Textreact__Text-sc-1w94ul3-0 cnMxgB dgOUEe"}).contents[0]
            website = soup.find("div", {"class":"Blockreact__Block-sc-1xf18x6-0 Flexreact__Flex-sc-1twd32i-0 ButtonGroupreact__StyledButtonGroup-sc-1skvztv-1 ctiaqU jYqxGr daKevg"}).find_all("a", {"class":"styles__StyledLink-sc-l6elh8-0 cnTbOd Blockreact__Block-sc-1xf18x6-0 Buttonreact__StyledButton-sc-glfma3-0 ctiaqU efDGWe ButtonGroupreact__StyledButton-sc-1skvztv-0 dBcbvG"})[1]["href"]
            dict["Project Site"].append(website)
            dict["Marketplace"].append(marketplace)
            dict["Floor" + " " + datetime.today().strftime('%d-%m')].append(floorPrice)
            dict["Owners"].append(owners)

            projectLinks = soup.find("div", {"class":"Blockreact__Block-sc-1xf18x6-0 Flexreact__Flex-sc-1twd32i-0 ButtonGroupreact__StyledButtonGroup-sc-1skvztv-1 ctiaqU jYqxGr daKevg"}).find_all("a")

            for links in projectLinks:
                link = links["href"]
                (bool, twitterHref) = parseLinks(link)
                if twitterHref != "":
                    dict["Twitter"].append(twitterHref)
                if bool:
                    try:
                        driver.get(link)
                        time.sleep(2)
                        soup = bs(driver.page_source, 'html.parser')
                        followers = soup.find("div", {"class": "css-1dbjc4n r-1ifxtd0 r-ymttw5 r-ttdzmv"}).find("div", {
                            "class": "css-1dbjc4n r-13awgt0 r-18u37iz r-1w6e6rj"}).find_all("span", {
                            "class": "css-901oao css-16my406 r-poiln3 r-bcqeeo r-qvutc0"})[2].contents[0]
                        try:
                            followers.index("mil")
                            followers = ''.join(followers.split())
                            print(followers)
                            followers = followers.replace("mil", "K").replace(",",".")
                        except:
                            print("entrei")
                            followers = int(followers.replace(".", ""))
                            followers = str(round(followers/1000, 1)) + "K"

                        dict["Twitter Followers" + " " + datetime.today().strftime('%d-%m')].append(followers)
                    except:
                        try:
                            soup = bs(driver.page_source, 'html.parser')
                            Members = soup.find("meta", {"name": "description"})["content"]
                            Members = re.findall(r"[-+]?\d*\,\d+|\d+", Members)[0]
                            Members = int(Members.replace(",",""))
                            Members = str(round(Members/1000, 1)) + "K"
                            dict["Discord Members" + " " + datetime.today().strftime('%d-%m')].append(Members)
                        except:
                            try:
                                soup = bs(driver.page_source, 'html.parser')
                                Members = soup.find("div", {"class":"tgme_page_extra"}).contents[0]
                                if len(re.findall(r"[-+]?\d*\,\d+|\d+", Members)) > 1:
                                    Members = re.findall(r"[-+]?\d*\,\d+|\d+", Members)[0] + re.findall(r"[-+]?\d*\,\d+|\d+", Members)[1]
                                    Members = int(Members)
                                    Members = str(round(Members / 1000, 1)) + "K"
                                else:
                                    print(re.findall(r"[-+]?\d*\,\d+|\d+", Members)[0])
                                    Members = re.findall(r"[-+]?\d*\,\d+|\d+", Members)[0]

                                dict["Telegram Members" + " " + datetime.today().strftime('%d-%m')].append(Members)
                            except:
                                False
            if len(dict["Telegram Members" + " " + datetime.today().strftime('%d-%m')]) < len(dict["Twitter Followers" + " " + datetime.today().strftime('%d-%m')]):
                dict["Telegram Members" + " " + datetime.today().strftime('%d-%m')].append("")
            if len(dict["Discord Members" + " " + datetime.today().strftime('%d-%m')]) < len(dict["Twitter Followers" + " " + datetime.today().strftime('%d-%m')]):
                dict["Discord Members" + " " + datetime.today().strftime('%d-%m')].append("")
            # Import to google sheets
            print(dict)
            dataframe = pd.DataFrame.from_dict(dict)
            sh.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())

        #Update sheet if already exists
    else:
        #Import google sheet as a list fo dicts
        values = sh.get_all_values()
        head = values.pop(0)
        list_of_dicts = [{head[i]: col for i, col in enumerate(row)} for row in values]
        print(list_of_dicts)


        print(list_of_dicts)
        for n in list_of_dicts:
            print(n)
            url = n["Marketplace"]
            dict = {
                "Floor" + " " + datetime.today().strftime('%d-%m'): [],
                "Discord Members" + " " + datetime.today().strftime('%d-%m'): [],
                "Twitter Followers" + " " + datetime.today().strftime('%d-%m'): [],
                "Telegram Members" + " " + datetime.today().strftime('%d-%m'): [],
            }

            driver.get(url)
            soup = bs(driver.page_source, 'html.parser')

            try:
                floorPrice = soup.find("div", {
                    "class": "Blockreact__Block-sc-1xf18x6-0 InfoItemreact__BlockContainer-sc-gubhmc-0 ctiaqU ipynZW"}).find(
                    "div", {"class": "Overflowreact__OverflowContainer-sc-10mm0lu-0 fqMVjm"}).contents[0]
            except:
                floorPrice = ""
            dict["Floor" + " " + datetime.today().strftime('%d-%m')] = floorPrice.replace(".",",")


            projectLinks = soup.find("div", {
                "class": "Blockreact__Block-sc-1xf18x6-0 Flexreact__Flex-sc-1twd32i-0 ButtonGroupreact__StyledButtonGroup-sc-1skvztv-1 ctiaqU jYqxGr daKevg"}).find_all(
                "a")

            for links in projectLinks:
                link = links["href"]
                (bool, twitterHref) = parseLinks(link)
                if bool:
                    try:
                        driver.get(link)
                        time.sleep(2)
                        soup = bs(driver.page_source, 'html.parser')
                        followers = soup.find("div", {"class": "css-1dbjc4n r-1ifxtd0 r-ymttw5 r-ttdzmv"}).find("div", {
                            "class": "css-1dbjc4n r-13awgt0 r-18u37iz r-1w6e6rj"}).find_all("span", {
                            "class": "css-901oao css-16my406 r-poiln3 r-bcqeeo r-qvutc0"})[2].contents[0]
                        try:
                            followers.index("mil")
                            followers = ''.join(followers.split())
                            followers = followers.replace("mil", "K").replace(",", ".")
                        except:
                            followers = int(followers.replace(".", ""))
                            followers = str(round(followers / 1000, 1)) + "K"

                        dict["Twitter Followers" + " " + datetime.today().strftime('%d-%m')] = followers
                    except:
                        try:
                            soup = bs(driver.page_source, 'html.parser')
                            Members = soup.find("meta", {"name": "description"})["content"]
                            Members = re.findall(r"[-+]?\d*\,\d+|\d+", Members)[0]
                            Members = int(Members.replace(",", ""))
                            Members = str(round(Members / 1000, 1)) + "K"
                            dict["Discord Members" + " " + datetime.today().strftime('%d-%m')] = Members
                        except:
                            try:
                                soup = bs(driver.page_source, 'html.parser')
                                Members = soup.find("div", {"class": "tgme_page_extra"}).contents[0]
                                if len(re.findall(r"[-+]?\d*\,\d+|\d+", Members)) > 1:
                                    Members = re.findall(r"[-+]?\d*\,\d+|\d+", Members)[0] + \
                                              re.findall(r"[-+]?\d*\,\d+|\d+", Members)[1]
                                    Members = int(Members)
                                    Members = str(round(Members / 1000, 1)) + "K"
                                else:
                                    Members = re.findall(r"[-+]?\d*\,\d+|\d+", Members)[0]

                                dict["Telegram Members" + " " + datetime.today().strftime('%d-%m')] = Members
                            except:
                                False
            if len(dict["Telegram Members" + " " + datetime.today().strftime('%d-%m')]) == 0:
                dict["Telegram Members" + " " + datetime.today().strftime('%d-%m')] = ""
            if len(dict["Discord Members" + " " + datetime.today().strftime('%d-%m')]) == 0:
                dict["Discord Members" + " " + datetime.today().strftime('%d-%m')] = ""
            if len(dict["Twitter Followers" + " " + datetime.today().strftime('%d-%m')]) == 0:
                dict["Twitter Followers" + " " + datetime.today().strftime('%d-%m')] = ""

            # Import to google sheets

            n.update(dict)
            df = pd.DataFrame(list_of_dicts)

        dataframe = pd.DataFrame.from_dict(df)

        sh.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())

        values = sh2.get_all_values()
        head = values.pop(0)
        list_of_dicts2 = [{head[i]: col for i, col in enumerate(row)} for row in values]
        for n in list_of_dicts2:
            print(n)
            url = n["Marketplace"]
            dict2 = {
                "Floor" + " " + datetime.today().strftime('%d-%m'): [],
            }

            driver.get(url)
            soup = bs(driver.page_source, 'html.parser')

            try:
                floorPrice = soup.find("div", {
                    "class": "Blockreact__Block-sc-1xf18x6-0 InfoItemreact__BlockContainer-sc-gubhmc-0 ctiaqU ipynZW"}).find(
                    "div", {"class": "Overflowreact__OverflowContainer-sc-10mm0lu-0 fqMVjm"}).contents[0]
            except:
                floorPrice = ""
            dict2["Floor" + " " + datetime.today().strftime('%d-%m')] = floorPrice.replace(".",",")


            n.update(dict2)
            print(n)

            df2 = pd.DataFrame(list_of_dicts2)
            print(df2)
        dataframe2 = pd.DataFrame.from_dict(df2)
        sh2.update([dataframe2.columns.values.tolist()] + dataframe2.values.tolist())





    k = input("press close to exit")


    # Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
