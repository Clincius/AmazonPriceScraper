from lxml import html  
import csv,os,json
import requests
import builtins
from time import sleep
 

url_dict = dict()

def find_region(url_string):
    region=url_string[19:22]
    if(region[2]=='/'): region = region[:2]
    elif region[2]=='.' : region = 'co.uk'
    return region


def find_dp(url_string):
    before_dp = url_string.find("dp")
    return url_string[before_dp+3:before_dp+13]


file_url = open('gpurls.txt', 'r')
string_list = file_url.readlines()
for strings in string_list:
    region = find_region(strings)
    if region in url_dict.keys():
        url_dict[region].append(find_dp(strings))
    else: url_dict[region]=[find_dp(strings)]


url_list = []
for key, values in url_dict.items():
    for dps in values:
        url_list.append("http://www.amazon."+key+"/dp/"+dps)
        

def AmzonParser(url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    page = requests.get(url,headers=headers)
    while True:
        sleep(2)
        try:
            doc = html.fromstring(page.content)
            XPATH_NAME = '//h1[@id="title"]//text()'
            XPATH_SALE_PRICE = '//span[contains(@id,"ourprice") or contains(@id,"saleprice")]/text()'
            XPATH_ORIGINAL_PRICE = '//td[contains(text(),"List Price") or contains(text(),"M.R.P") or contains(text(),"Price")]/following-sibling::td/text()'
            
            RAW_NAME = doc.xpath(XPATH_NAME)
            RAW_SALE_PRICE = doc.xpath(XPATH_SALE_PRICE)
            RAW_ORIGINAL_PRICE = doc.xpath(XPATH_ORIGINAL_PRICE)
            
            NAME = ' '.join(''.join(RAW_NAME).split()) if RAW_NAME else None
            SALE_PRICE = ' '.join(''.join(RAW_SALE_PRICE).split()).strip() if RAW_SALE_PRICE else None
            ORIGINAL_PRICE = ''.join(RAW_ORIGINAL_PRICE).strip() if RAW_ORIGINAL_PRICE else None
            
            if not ORIGINAL_PRICE:
                ORIGINAL_PRICE = SALE_PRICE
 
            if page.status_code!=200:
                raise ValueError('captha')
            data = {
                    'NAME':NAME,
                    'SALE_PRICE':SALE_PRICE,
                    'ORIGINAL_PRICE':ORIGINAL_PRICE,
                    'URL':url,
                    }
 
            return data
        except Exception as e:
            print(e)
 
def ReadAsin():
    extracted_data = []
    for url in url_list:
        print("Processing: "+url)
        elem = AmzonParser(url)
        extracted_data.append(elem)
        #extracted_data.append(AmzonParser(url))
        if elem['SALE_PRICE']==elem['ORIGINAL_PRICE']==None: continue
        print(elem['NAME']+' '+elem['SALE_PRICE']) if elem['SALE_PRICE']!=None else print(elem['NAME']+' '+elem['ORIGINAL_PRICE'])
    #f=open('data.json','w')
    #json.dump(extracted_data,f,indent=4)
 
if __name__ == "__main__":
    ReadAsin()