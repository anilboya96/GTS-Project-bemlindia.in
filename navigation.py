from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
import requests
import json
from datetime import datetime
import html
import wx
import Global_var
from insert_on_database import *
import urllib3
App = wx.App()

def chromedriver():
    browser = webdriver.Chrome('C:\\Translation EXE\\chromedriver.exe')
    browser.get('https://www.bemlindia.in/tenders/active-tenders/#')
    browser.maximize_window()
    time.sleep(5)
    navigation(browser)
    
# def remove_html(text):
#     cleanr = re.compile('<.*?>')
#     cleantext = re.sub(cleanr, '', str(text))
#     return cleantext

def document_link(doc_text):
    # global q 
    # defining the api-endpoint 
    API_ENDPOINT = "https://www.bemlindia.in/wp-admin/admin-ajax.php"

    data = {'action':'Add_tender_download',
            'tender_no': doc_text[0],
            'pos': doc_text[1],
            'type': doc_text[2]}
            # 'name' : 'Anil',
            # 'organisation_name': 'kjnkj',
            # 'phone_number': 5153513143,
            # 'email': 'abc@gmail.com'}
    

    #   1612,1,1
    #   16247,1,1
    # sending post request and saving response as response object
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    r = requests.post(url = API_ENDPOINT, data = data, verify=False)
    
    # extracting response text 
    data = json.loads(r.text)
    q = data["file_path"]
    return q

    pastebin_url = r.text
    print("The pastebin URL is:%s"%pastebin_url)
       
def navigation(browser):    
    a = 1
    while a == 1:
        try:
            for close in browser.find_elements(By.XPATH,'//*[@class="mfp-close"]'):
                close_text = close.get_attribute('innerText')
                if '×' in close_text:
                    close.click()
                    a = 0
                    time.sleep(2)
                else:
                    a = 1
        except:
            a = 1
      
    location = 1
    collected_list = []
    location = browser.find_elements(By.XPATH,'//*[@id="location"]/option')
    for select in range (1,len(location)+1,1):
        for option in browser.find_elements(By.XPATH,'//*[@id="location"]/option['+str(select)+']'):
            browser.execute_script("arguments[0].scrollIntoView(true);", option)
            option_text = option.get_attribute('innerText')
            option.click()
            time.sleep(4)
            break
        count = 1
        a = True
        while a == True:
            for _ in browser.find_elements(By.XPATH,'//*[@id="service-table"]/tbody/tr'):
                for description in browser.find_elements(By.XPATH,'//*[@id="service-table"]/tbody/tr['+str(count)+']/td[1]'):
                    browser.execute_script("arguments[0].scrollIntoView(true);", description)
                    desc = description.get_attribute('outerHTML').strip()
                if "No data available in table" not in desc:
                    desc_text = desc.split('<br>')
                               
                    for close_date in browser.find_elements(By.XPATH,'//*[@id="service-table"]/tbody/tr['+str(count)+']/td[2]'):
                        close_date_text = close_date.get_attribute('innerText').strip()
                        if 'Extended till' in close_date_text:
                            deadline = close_date_text.partition('\n')[2]
                        else:
                            deadline = close_date_text.partition('\n')[0]
                        # print(deadline)
                        break
                                        
                    for opening_date in browser.find_elements(By.XPATH,'//*[@id="service-table"]/tbody/tr['+str(count)+']/td[3]'):
                        open_date = opening_date.get_attribute('innerText').strip()
                        opening_date_text = open_date.partition('\n')[0]
                        # print(opening_date_text)
                        break
                                        
                    for inviting_officer in browser.find_elements(By.XPATH,'//*[@id="service-table"]/tbody/tr['+str(count)+']/td[4]'):
                        inviting_officer_text = inviting_officer.get_attribute('innerText').strip()
                        # print(inviting_officer_text)
                        break
                                        
                    for type in browser.find_elements(By.XPATH,'//*[@id="service-table"]/tbody/tr['+str(count)+']/td[5]'):
                        type_text = type.get_attribute('innerText').strip()
                        # print(type_text)
                        break  
                        
                    link_list = []
                    for documents in browser.find_elements(By.XPATH,'//*[@id="service-table"]/tbody/tr['+str(count)+']/td[1]/table/tbody/tr/td[1]/a'):
                        document_text = documents.get_attribute('onclick').strip()
                        doc = document_text.partition('(')[2].partition(')')[0]  
                        doc_text = doc.split(',')             
                        # print(document_text)               
                        doc_link = document_link(doc_text)
                        # print(doc_link)
                        link_list.append(doc_link)
                            
                    count += 1
                    collected_list.append({'Reference_no': desc_text[0],'Tender_title':desc_text[1], 'Deadline': deadline, 'Opening_date': opening_date_text, 'Inviting_officer': inviting_officer_text, 'Type': type_text, "document_link": link_list, "Purchaser": option_text})                    
            
            for next_page in browser.find_elements(By.XPATH,'//*[@id="service-table_paginate"]'):
                next_page_html = next_page.get_attribute('outerHTML')
                if "paginate_button next disabled" not in next_page_html:
                    next_page.click()
                    count = 1
                    time.sleep(2)               
                else:
                    a = False
                    break
    scrape(collected_list,browser)            

def scrape(collected_list,browser):
    for data in collected_list:
        error = True
        while error == True:
            try:
                SegFeild = []
                for _ in range(50):
                    SegFeild.append('')
                
                x = ''
                w = 1
                document = data["document_link"]
                for link in document:
                    x += '<a href= "'+str(link)+'" target="_blank"><input class="btn btn-primary btn-sm" style="width:100px" type="button" value="Document_'+str(w)+'"></a>\n'
                    w += 1
                SegFeild[6] = x
                
                SegFeild[2] = 'Inviting_officer: ' + data['Inviting_officer'] + ' Location: '+ data["Purchaser"]
                
                SegFeild[7] = "IN"
                
                SegFeild[8] = "https://www.bemlindia.in/tenders/active-tenders/#"
                
                SegFeild[12] = "BEML LIMITED " + data["Purchaser"].upper()
                
                SegFeild[13] = data['Reference_no'].replace('<td>', '')
                
                SegFeild[18] = ''
                
                SegFeild[19] = data['Tender_title'].title().replace('&Amp;','&').replace('&amp;','&')
            
                closing_date = data['Deadline']
                if closing_date != '':
                    date = datetime.strptime(closing_date, "%d-%b-%Y")
                    final_date = date.strftime("%Y-%m-%d")
                    SegFeild[24] = final_date
                else:
                    print("Deadline not given")
                
                open_date = data['Opening_date']
                if open_date != '':
                    date1 = datetime.strptime(open_date, "%d-%b-%Y")
                    final_date = date1.strftime("%Y-%m-%d")
                    SegFeild[25] = final_date
                else:
                    print("Opening_date not given")
                        
                SegFeild[27] = "0"
                
                SegFeild[28] = "https://www.bemlindia.in/tenders/active-tenders/#"
                
                SegFeild[31] = "bemlindia"
                
                SegFeild[46] = 'Inviting_officer: ' + data['Inviting_officer'] + ' Type :' + data['Type'] 
                
                SegFeild[42] = SegFeild[7]
                
                link_list = []
                docum_link = data['document_link']
                for link in docum_link:
                    docum_text = link.rsplit( "/", 1)[-1]
                    link_list.append({'link_href': link, 'link_text': docum_text})
                
                full_links = ''
                for lists in link_list:
                    if lists['link_href'] != '':
                        full_link = lists['link_text']+'~'+lists['link_href']+','
                        full_links += full_link
                    
                SegFeild[44] = full_links.rstrip(',')
                
                for SegIndex, SegFeild_data in enumerate(SegFeild):
                    print(SegIndex, SegFeild_data)
                SegFeild[SegIndex] = html.unescape(str(SegFeild[SegIndex]))
                SegFeild[SegIndex] = str(SegFeild[SegIndex]).replace("'", "''")
            
                if SegFeild[18] == '':
                    SegFeild[18] = SegFeild[19]
                    
                if len(SegFeild[19]) >= 200:
                    if SegFeild[18] != SegFeild[19]:
                        SegFeild[18] = SegFeild[19]+'<br>\n'+SegFeild[18]
                    SegFeild[19] = str(SegFeild[19])[:200]+'...'
                    
                if len(SegFeild[46]) >= 1500:
                    SegFeild[46] = str(SegFeild[46])[:1500]+'...'

                if SegFeild[19] == '':
                    wx.MessageBox(' Short Desc Blank ','bemlindia', wx.OK | wx.ICON_ERROR)
                check_Duplication(SegFeild)
                # check_date(SegFeild)
                error = False
                print(" Total: " + str(len(collected_list)) + " Duplicate: " + str(Global_var.duplicate) + " Expired: " + str(Global_var.expired) + " Inserted: " + str(Global_var.inserted) + " Deadline Not given: " + str(Global_var.deadline_Not_given) + " QC Tenders: "+ str(Global_var.QC_Tenders),"\n")
                            
            except Exception as e:
                    error = True
                    print(e)
                    
    wx.MessageBox("Total: " + str(len(collected_list)) + "\n""Duplicate: " + str(Global_var.duplicate) + "\n""Expired: " + str(Global_var.expired) + "\n""Inserted: " + str(Global_var.inserted) + "\n""Deadline Not given: " + str(Global_var.deadline_Not_given) + "\n""QC Tenders: "+ str(Global_var.QC_Tenders) + "",'bemlindia.in', wx.OK | wx.ICON_INFORMATION)    
    browser.quit()     
    sys.exit()       
# def check_date(SegFeild):
#         deadline = (SegFeild[24])
#         curdate = datetime.now()
#         curdate_str = curdate.strftime("%Y-%m-%d")
#         try:
#             if deadline != '':
#                 datetime_object_deadline = datetime.strptime(deadline, '%Y-%m-%d')
#                 datetime_object_curdate = datetime.strptime(curdate_str, '%Y-%m-%d')
#                 timedelta_obj = datetime_object_deadline - datetime_object_curdate
#                 day = timedelta_obj.days
#                 if day > 0:
#                     check_Duplication(SegFeild)
#                 else:
#                     print("Expired Tender")
#                     Global_var.expired += 1
#             else:
#                 Global_var.deadline_Not_given += 1
#         except Exception as e:
#             print(e)
            
chromedriver()
        
