from bs4 import BeautifulSoup as bs
import cloudscraper
from selenium import webdriver
from google.oauth2 import service_account
from datetime import datetime
import gspread
import time
import pandas as pd

gc = gspread.service_account(filename='keys.json')
sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1D7F-38GMfyJDVI9pmiQiiau5qHcHekLcMXN2qxkGjkI/edit#gid=0").sheet1
datetime.today().strftime('%Y-%m-%d')

dict = {
"Project Site":[],	"Marketplace": [], "Floor" + " " + datetime.today().strftime('%d-%m'):[], "Owners":[], "Twitter": [], "Followers": []
}

def main():
    driver = webdriver.Chrome(executable_path = "C:/Users/berna/Downloads/chromedriver_win32 (1)/chromedriver.exe")
    driver.get("https://opensea.io/collection/crypto-raiders-characters")

    soup = bs(driver.page_source, 'html.parser')
    owners = soup.find_all("h3",{"class":"Blockreact__Block-sc-1xf18x6-0 Textreact__Text-sc-1w94ul3-0 iKSQyx kscHgv"})[1].find("div", {"class":"Overflowreact__OverflowContainer-sc-10mm0lu-0 fqMVjm"}).contents[0]
    marketplace = driver.current_url
    floorPrice = soup.find("div",{"class":"Blockreact__Block-sc-1xf18x6-0 InfoItemreact__BlockContainer-sc-gubhmc-0 ctiaqU ipynZW"}).find("div", {"class":"Overflowreact__OverflowContainer-sc-10mm0lu-0 fqMVjm"}).contents[0]
    project = soup.find("h2", {"class":"Blockreact__Block-sc-1xf18x6-0 Textreact__Text-sc-1w94ul3-0 cnMxgB dgOUEe"}).contents[0]
    twitterHref = soup.find("div", {"class":"Blockreact__Block-sc-1xf18x6-0 Flexreact__Flex-sc-1twd32i-0 ButtonGroupreact__StyledButtonGroup-sc-1skvztv-1 ctiaqU jYqxGr daKevg"}).find_all("a", {"class":"styles__StyledLink-sc-l6elh8-0 cnTbOd Blockreact__Block-sc-1xf18x6-0 Buttonreact__StyledButton-sc-glfma3-0 ctiaqU efDGWe ButtonGroupreact__StyledButton-sc-1skvztv-0 dBcbvG"})[3]["href"]
    website = soup.find("div", {"class":"Blockreact__Block-sc-1xf18x6-0 Flexreact__Flex-sc-1twd32i-0 ButtonGroupreact__StyledButtonGroup-sc-1skvztv-1 ctiaqU jYqxGr daKevg"}).find_all("a", {"class":"styles__StyledLink-sc-l6elh8-0 cnTbOd Blockreact__Block-sc-1xf18x6-0 Buttonreact__StyledButton-sc-glfma3-0 ctiaqU efDGWe ButtonGroupreact__StyledButton-sc-1skvztv-0 dBcbvG"})[1]["href"]
    dict["Project Site"].append(website)
    dict["Marketplace"].append(marketplace)
    dict["Floor" + " " + datetime.today().strftime('%d-%m')].append(floorPrice)
    dict["Owners"].append(owners)
    dict["Twitter"].append(twitterHref)
    #Will leave the page to get twitter followers
    driver.get(twitterHref)
    time.sleep(4)
    soup = bs(driver.page_source, 'html.parser')
    followers = soup.find("div", {"class":"css-1dbjc4n r-1ifxtd0 r-ymttw5 r-ttdzmv"}).find("div", {"class":"css-1dbjc4n r-13awgt0 r-18u37iz r-1w6e6rj"}).find_all("span",{"class":"css-901oao css-16my406 r-poiln3 r-bcqeeo r-qvutc0"})[2].contents[0]
    dict["Followers"].append(followers)
    print(dict)

    dataframe = pd.DataFrame.from_dict(dict)
    sh.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
