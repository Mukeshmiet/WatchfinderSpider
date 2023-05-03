import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import time
from datetime import datetime as dt

# for errors handling 
import sys
import logging as l


class WatchFinder(scrapy.Spider):
    name = 'watchfinderspider'
    start_urls = ['https://www.google.com']
    url = 'https://www.watchfinder.co.uk/new-arrivals'
    product_url = []
    req_info = []

    # feed is used to generate csv file from scraped data
    custom_settings = {
        'FEEDS': {
            'watchfinderdata.csv': {'format': 'csv'}}
    }

    def __init__(self, name=None, **kwargs):
        super(WatchFinder, self).__init__(name, **kwargs)
        options = Options()
        options.add_argument("--headless")
        # options.add_argument('--disable-javascript')
        # options.add_argument('--no-sandbox')
        # options.add_argument("test-type")
        # options.add_argument("--disable-web-security")
        # options.add_argument("--allow-running-insecure-content")
        # options.add_argument("--disable-popup-blocking")
        # options.add_argument('--disable-dev-shm-usage')
        # options.add_argument('--disable-gpu')
        # options.add_argument("--window-size=1920,1080")
        self.driver = webdriver.Chrome(executable_path='c:/Users/Dell/Downloads/chromedriver.exe', chrome_options=options)
        self.driver.maximize_window()

    def page_init(self, url):
        """Initilize the url in browser and close language popup"""
        try:
            self.driver.get(url)
            time.sleep(2)
            
            #this will close the language selection popup
            try:
                popup_close = self.driver.find_element_by_xpath('//div[@id="modal_region-selector"]//button[@class="btn-modal-close"]').click()
            except:
                pass
                
            # this will scroll page to bottom
            self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")

        except Exception as e:
            # this will print the error on consol with error generating line no.
            print("___________________ ERROR ____________________")
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            message = str(exc_type) + str(exc_obj) + \
                ' At line no : ' + str(exc_tb.tb_lineno)
            l.error(message)
            self.driver.quit()

    def prod_link(self):
        """Extract new arrivals product url from first page"""

        # this will scrape all watches url from new arrival page and append in product_url list attribute (first page only)
        try:
            all_links = self.driver.find_elements(by=By.XPATH, value='//div[@class="bg-wf-white msm:w-48 mb-8 relative group"]/a[@data-testid="watchLink"]')
            for l in all_links:
                self.product_url.append(l.get_attribute("href"))
        
        except Exception as e:
            print("___________________ ERROR ____________________")
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            message = str(exc_type) + str(exc_obj) + \
                ' At line no : ' + str(exc_tb.tb_lineno)
            l.error(message)
            self.driver.quit()

    def web_element_text(self, weblist):
        """ extract data from selenium web element, which is a list type """
        for webtext in weblist:
            wtext = webtext.text
        return wtext

    def prod_page(self, p_url):
        """ scrape the data from each product page """
        try:
            for lnk in p_url:
                time.sleep(3)
                self.page_init(lnk)

                # scraping req data
                
                #this will find itemId column data
                try:
                    item_id = self.driver.find_element_by_xpath('//li[@class="breadcrumb_item active"]').text
                    
                except:
                    item_id = "not able to detect"
                
                #this will find url column data
                try:
                    prod_url = self.driver.current_url
                
                except:
                    prod_url = "not able to detect"
                
                #this will find name column data
                try:
                    prod_name = self.driver.find_elements_by_xpath('//nav[@aria-label="Breadcrumb"]//li[3]/a')
                    prod_name = self.web_element_text(prod_name)
                    
                except:
                    prod_name = "not able to detect"
                
                #this will find brand column data
                try:
                    prod_brand = self.driver.find_elements_by_xpath('//span[@class="h3"][1]')
                    prod_brand = self.web_element_text(prod_brand)
                    
                except:
                    prod_brand = "not able to detect"
                
                #this will find finalPrice column data
                try:
                    try:
                        prod_finalprice = self.driver.find_element_by_xpath('//span[@class="h2 bold reduced-padding  "]').text
                    except:
                        prod_finalprice = self.driver.find_element_by_xpath('//span[@class="h2 bold reduced-padding  with-saving"]').text
                    try:
                        prod_finalprice = prod_finalprice.replace("£", "")
                    except:
                        pass
                
                except:
                    prod_finalprice = "not able to detect"
                
                #this will find estimatedRetailPrice column data
                try:
                    prod_erp = self.driver.find_element_by_xpath('//span[@class="product--rrp"]').text
                    try:
                        prod_erp = prod_erp.replace("£", "").split(" ")[-1]
                    except:
                        pass
                    try:
                        if "discontinued" in prod_erp.lower():
                            prod_erp = 'null'
                    except:
                        pass
                
                except:
                    prod_erp = "not able to detect"
                
                #this will find modelName column data
                try:
                    prod_modelname = self.driver.find_elements_by_xpath('//nav[@class="breadcrumb_nav"]//li[3]/a')
                    prod_modelname = self.web_element_text(prod_modelname)
                
                except:
                    prod_modelname = "not able to detect"
                
                #this will find modelNo column data
                try:
                    prod_modelno = self.driver.find_element_by_xpath('//nav[@class="breadcrumb_nav"]//li[4]/a').text
                
                except:
                    prod_modelno = "not able to detect"
                
                # this will store the length on specification content rows
                desc_len= len(self.driver.find_elements_by_xpath(f'//div[@id="specification-content"]//tr'))+1
                
                #this will find year column data
                try:
                    for i in range(1,desc_len):
                        prod_yer = self.driver.find_elements_by_xpath(f'//div[@id="specification-content"]//tr[{i}]/td[1]')
                        prod_yer = self.web_element_text(prod_yer)
                        if "year" in prod_yer.lower():
                            prod_year = self.driver.find_elements_by_xpath(f'//div[@id="specification-content"]//tr[{i}]/td[2]')
                            prod_year = self.web_element_text(prod_year)
                            break
                        else:
                            continue
                    try:
                        prod_year = prod_year.split(" ")[-1]
                    except:
                        pass
                
                except:
                    prod_year = "not able to detect"
                
                #this will find condition column data
                try:
                    prod_condition = self.driver.find_elements_by_xpath('//meta[@itemprop="itemCondition"]')
                    for val in prod_condition:
                        prod_condition = val.get_attribute("content")
                
                except:
                    prod_condition = "not able to detect"
                
                #this will all find image urls for the images column
                try:
                    img_links = []
                    prod_image = self.driver.find_elements_by_xpath('//div[@class="prod-thumbs"]//div[@class="owl-item active"]//source')
                    time.sleep(2)
                    for val in prod_image:
                        img_links.append(str(val.get_attribute("srcset").split(";")[0]))
                
                except:
                    img_links = "not able to detect"
                
                #this will find description column data
                try:
                    prod_desc = self.driver.find_elements_by_xpath('//div[@id="description-content"]')
                    prod_desc = self.web_element_text(prod_desc)
                
                except:
                    prod_desc = "not able to detect"
                
                #this will find box column data
                try:
                    for i in range(1,desc_len):
                        prod_bx = self.driver.find_elements_by_xpath(f'//div[@id="specification-content"]//tr[{i}]/td[1]')
                        prod_bx = self.web_element_text(prod_bx)
                        if "box" in prod_bx.lower():
                            prod_box = self.driver.find_elements_by_xpath(f'//div[@id="specification-content"]//tr[{i}]/td[2]')
                            prod_box = self.web_element_text(prod_box)
                            break
                        else:
                            continue
                
                except:
                    prod_box = "not able to detect"
                
                #this will find papers column data
                try:
                    for i in range(1,desc_len):
                        prod_paper = self.driver.find_elements_by_xpath(f'//div[@id="specification-content"]//tr[{i}]/td[1]')
                        prod_paper = self.web_element_text(prod_paper)
                        if "papers" in prod_paper.lower():
                            prod_papers = self.driver.find_elements_by_xpath(f'//div[@id="specification-content"]//tr[{i}]/td[2]')
                            prod_papers = self.web_element_text(prod_papers)
                            break
                        else:
                            continue
                
                except:
                    prod_papers = "not able to detect"
                
                #this will find caseSize column data
                try:
                    for i in range(1,desc_len):
                        prod_csiz = self.driver.find_elements_by_xpath(f'//div[@id="specification-content"]//tr[{i}]/td[1]')
                        prod_csiz = self.web_element_text(prod_csiz)
                        if "case size" in prod_csiz.lower():
                            prod_csize = self.driver.find_elements_by_xpath(f'//div[@id="specification-content"]//tr[{i}]/td[2]')
                            prod_csize = self.web_element_text(prod_csize)
                            break
                        else:
                            continue
                    
                except:
                    prod_csize = "not able to detect"
                
                #this will find caseMaterial column data
                try:
                    for i in range(1,desc_len):
                        prod_cmat = self.driver.find_elements_by_xpath(f'//div[@id="specification-content"]//tr[{i}]/td[1]')
                        prod_cmat = self.web_element_text(prod_cmat)
                        if "case material" in prod_cmat.lower():
                            prod_cmate = self.driver.find_elements_by_xpath(f'//div[@id="specification-content"]//tr[{i}]/td[2]')
                            prod_cmate = self.web_element_text(prod_cmate)
                            break
                        else:
                            continue
                    
                except:
                    prod_cmate = "not able to detect"
                
                #this will find dialType column data
                try:
                    for i in range(1,desc_len):
                        prod_dial = self.driver.find_elements_by_xpath(f'//div[@id="specification-content"]//tr[{i}]/td[1]')
                        prod_dial = self.web_element_text(prod_dial)
                        if "dial type" in prod_dial.lower():
                            prod_dialc = self.driver.find_elements_by_xpath(f'//div[@id="specification-content"]//tr[{i}]/td[2]')
                            prod_dialc = self.web_element_text(prod_dialc)
                            break
                        else:
                            continue
                    
                except:
                    prod_dialc = "not able to detect"
                
                #this will find movement column data
                try:
                    for i in range(1,desc_len):
                        prod_mov = self.driver.find_elements_by_xpath(f'//div[@id="specification-content"]//tr[{i}]/td[1]')
                        prod_mov = self.web_element_text(prod_mov)
                        if "movement" in prod_mov.lower():
                            prod_move = self.driver.find_elements_by_xpath(f'//div[@id="specification-content"]//tr[{i}]/td[2]')
                            prod_move = self.web_element_text(prod_move)
                            break
                        else:
                            continue
                    
                except:
                    prod_move = "not able to detect"
                
                #this will find bandColor and braceletMaterial column data
                try:
                    for i in range(1,desc_len):
                        prod_band = self.driver.find_elements_by_xpath(f'//div[@id="specification-content"]//tr[{i}]/td[1]')
                        prod_band = self.web_element_text(prod_band)
                        if "bracelet material" in prod_band.lower():
                            prod_bandc = self.driver.find_elements_by_xpath(f'//div[@id="specification-content"]//tr[{i}]/td[2]')
                            prod_bandc = self.web_element_text(prod_bandc)
                            break
                        else:
                            continue
                except:
                    prod_bandc = "not able to detect"
                
                prod_brac = prod_bandc
                try:
                    prod_bandc = prod_bandc.split("-")[1]
                except:
                    pass
                
                #this will find waterResistance column data
                try:
                    for i in range(1,desc_len):
                        prod_w = self.driver.find_elements_by_xpath(f'//div[@id="specification-content"]//tr[{i}]/td[1]')
                        prod_w = self.web_element_text(prod_w)
                        if "water" in prod_w.lower():
                            prod_wr = self.driver.find_elements_by_xpath(f'//div[@id="specification-content"]//tr[{i}]/td[2]')
                            prod_wr = self.web_element_text(prod_wr)
                            break
                        else:
                            continue
                
                except:
                    prod_wr = "not able to detect"
                
                req_data = {
                            "itemId": item_id.strip(), "url": prod_url.strip(), "name": prod_name.strip(), "brand": prod_brand.strip(),
                            "price": "null", "finalPrice": prod_finalprice.strip(),"estimatedRetailPrice": prod_erp.strip(), "currency": "£",
                            "model": prod_modelname.strip(), "modelNo": prod_modelno.strip(), "gender": 'null', "year": prod_year.strip(),
                            "condition": prod_condition.strip(), "images": img_links, "description": prod_desc.strip(),
                            "box": prod_box.strip(), "papers": prod_papers.strip(), "caseSize": prod_csize.strip(),
                            "caseMaterial": prod_cmate.strip(), "caseShape": "-", "dialColor": prod_dialc.strip(),
                            "movement": prod_move.strip(), "bandColor": prod_bandc.strip(), "braceletMaterial": prod_brac.strip(),
                            "waterResistance": prod_wr.strip(), "details": "null", "fetchData": dt.strftime(dt.now(), "%Y-%m-%d")
                            }
                self.req_info.append(req_data)
        except Exception as e:
            print("___________________ ERROR ____________________")
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            message = str(exc_type) + str(exc_obj) + \
                ' At line no : ' + str(exc_tb.tb_lineno)
            l.error(message)
            self.driver.quit()

    def parse(self, response):
        try:
            self.page_init(self.url)
            self.prod_link()
            self.prod_page(self.product_url)

            for data in self.req_info:
                yield data
            self.driver.quit()

        except Exception as e:
            print("___________________ ERROR ____________________")
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            message = str(exc_type) + str(exc_obj) + \
                ' At line no : ' + str(exc_tb.tb_lineno)
            l.error(message)
            self.driver.quit()
