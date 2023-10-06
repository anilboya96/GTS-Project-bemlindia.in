import os
import sys
import time
from datetime import datetime
import mimetypes
import mysql.connector as mysql
import pymysql.cursors
import boto3
import Global_var
import requests
import re

def db_connection():
    while True:
        try:
            connection = pymysql.connect(host = "185.142.34.92", user = "ams", passwd = "TgdRKAGedt%h", db ="tenders_db")
            # connection = pymysql.connect(host = 'localhost', user = "root", passwd = "root", db ="cloud data")  # type: ignore
            # connection = pymysql.connect(host = 'localhost', user = "root", passwd = "root", db ="my_db")
            return connection 
        except Exception as e:
            print(e)

def Error_fun(Error,Function_name,Source_name):
    mydb = db_connection()
    mycursor = mydb.cursor()
    sql1 = "INSERT INTO errorlog_tbl(Error_Message,Function_Name,Exe_Name) VALUES('" + str(Error).replace("'","''") + "','" + str(Function_name).replace("'","''")+ "','"+str(Source_name)+"')"
    mycursor.execute(sql1)
    mydb.commit()
    mycursor.close()
    mydb.close()
    return sql1

def check_Duplication(SegFeild):
    while True:
        try:
            mydb = db_connection()
            mycursor = mydb.cursor()
            if SegFeild[13] != '' and SegFeild[24] != '' and SegFeild[7] != '':
                commandText = "SELECT Posting_Id from india_tenders_tbl where tender_notice_no = '" + str(SegFeild[13]) + "' and Country = '" + str(SegFeild[7]) + "' and doc_last= '" + str(SegFeild[24]) + "'"
            elif SegFeild[13] != "" and SegFeild[7] != "":
                commandText = "SELECT Posting_Id from india_tenders_tbl  where tender_notice_no = '" + str(SegFeild[13]) + "' and Country = '" + str(SegFeild[7]) + "'"
            elif SegFeild[19] != "" and SegFeild[24] != "" and SegFeild[7] != "":
                commandText = "SELECT Posting_Id from india_tenders_tbl where short_desc = '" + str(SegFeild[19]) + "' and doc_last = '" + SegFeild[24] + "' and Country = '" + SegFeild[7] + "'"
            else:
                commandText = "SELECT Posting_Id from india_tenders_tbl where short_desc = '" + str(SegFeild[19]) + "' and Country = '" + str(SegFeild[7]) + "'"
            mycursor.execute(commandText)
            results = mycursor.fetchall()
            mydb.close()
            mycursor.close()
            print("Code Reached On check_Duplication")
            if len(results) > 0:
                print('Duplicate Tender')
                Global_var.duplicate += 1
            else:
                create_html_file(SegFeild)
            break
        except Exception as e:
            Function_name: str = sys._getframe().f_code.co_name
            Error: str = str(e)
            Source_name = str(SegFeild[31])
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error ON : ", sys._getframe().f_code.co_name + "--> " + str(e), "\n", exc_type, "\n", fname, "\n",exc_tb.tb_lineno)
            Error_fun(Error,Function_name,Source_name)
            time.sleep(10)

def insert_in_local(SegFeild,Fileid):

    while True:
        mydb = db_connection()
        mycursor = mydb.cursor()
        Current_dateTime = datetime.now().strftime("%Y-%m-%d")
        sql = "INSERT INTO india_tenders_tbl(Tender_ID,EMail,add1,add2,City,State,PinCode,Country,URL,Tel,Fax,Contact_Person,Maj_Org,tender_notice_no,notice_type,ind_classification,global,MFA,tenders_details,short_desc,est_cost,currency,doc_cost,doc_start,doc_last,open_date,earnest_money,Financier,tender_doc_file,Sector,corregendum,source,entry_date,cpv)VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        val = (str(Fileid),SegFeild[1],SegFeild[2],SegFeild[3],SegFeild[4],SegFeild[5],SegFeild[6],SegFeild[7],SegFeild[8],SegFeild[9],SegFeild[10],SegFeild[11],SegFeild[12],SegFeild[13],SegFeild[14],SegFeild[15],SegFeild[16],SegFeild[17],SegFeild[18],SegFeild[19],SegFeild[20],SegFeild[21],SegFeild[22],SegFeild[23],SegFeild[24],SegFeild[25],SegFeild[26],SegFeild[27],SegFeild[28],SegFeild[29],SegFeild[30],SegFeild[31],str(Current_dateTime),SegFeild[36])
        try:
            mycursor.execute(sql , val)
            mydb.commit()
            mydb.close()
            mycursor.close()
            print("Code Reached On insert_in_Local")
            insert_l2l_tbl(SegFeild, Fileid)
            break
        except Exception as e:
            Function_name: str = sys._getframe().f_code.co_name
            Error: str = str(e)
            Source_name = str(SegFeild[31])
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error ON : ", sys._getframe().f_code.co_name + "--> " + str(e), "\n", exc_type, "\n", fname, "\n",exc_tb.tb_lineno)
            Error_fun(Error,Function_name,Source_name)
            time.sleep(10)
            
def AdditionalDocs(SegFeild,Fileid):
    
    all_link = []
    attach_docs = SegFeild[44]
    if (attach_docs != ""):
        doclinks = attach_docs.split(',')
        all_link = doclinks
        time.sleep(2)

    additional_docname = ""
    SegFeild[44] = ""
    
    # current_directory = 'C:\\Additional_Docs\\'
    current_directory = 'C:\\Additional_Docs\\'
    final_directory = os.path.join(current_directory,Global_var.source_name)
    if not os.path.exists(final_directory):
        os.makedirs(final_directory)
    for link in all_link:
        name_n_file = link
        try:
            
            urlnameArr = name_n_file.split('~')
            additional_docname += Fileid + "-" + urlnameArr[0] + ","
            if (len(additional_docname) > 3800):
                path = 'toomany_additional_docs.txt'
                my_file = open(path, "w")
                my_file.writelines(SegFeild[28])        
                my_file.close()
                break
            
            down_filename = Download_AdditionalDocs(name_n_file, Fileid,final_directory)
            if (down_filename != ""):
                filepath = "C:\\Additional_Docs\\" +Global_var.source_name+'\\'+ down_filename
                upload_to_s3(filepath)
                if (SegFeild[44] == ""):
                    SegFeild[44] = down_filename
                else:
                    SegFeild[44] += "," + down_filename
                
        except Exception as e:
            print(e)
    clear_files = os.path.join(current_directory,Global_var.source_name)
    for filename in os.listdir(clear_files):
        os.unlink(os.path.join(clear_files, filename))
    print("Code Reached On Additional Docs")
    insert_in_local(SegFeild,Fileid)
       
        
def Download_AdditionalDocs(name_n_file, Fileid,final_directory):
    urlnameArr = name_n_file.split('~')
    if (urlnameArr[0].strip() == "" or len(urlnameArr) == 1):
        return ""
    filename = Fileid + "-" + urlnameArr[0]
    
    filename = re.sub('[^0-9a-zA-Z .\-_]+', ' ', filename)
    filename = re.sub('\s+', ' ', filename)
    filename = filename.replace(" ", "-")
    filename = filename.replace("--", "-")
    
    url = urlnameArr[1]
    d = 0
    while (d <= 5):
        try:
            
            # current_directory = 'C:\\Additional_Docs\\'
            # final_directory = os.path.join(current_directory,Global_var.source_name)
            # if not os.path.exists(final_directory):
            #     os.makedirs(final_directory)
            # else:
            file_path = os.path.join(final_directory, filename)
            response = requests.get(url,verify=False)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            if not os.path.exists(file_path):
                filename = '' # if flile not exist or not downloaded
            else:
                fileSize = os.path.getsize(file_path) # check file size if <= 0 then return = ''
                if (fileSize <= 0):
                    filename = ""
            
            d = 10
        except Exception as e:
            print(e)
            Function_name :str = sys._getframe().f_code.co_name
            Error : str = str(e)
            Error_fun(Error,Function_name)
            exc_type , exc_obj , exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error ON : " , sys._getframe().f_code.co_name + "--> " + str(e) , "\n" , exc_type , "\n" ,fname , "\n" , exc_tb.tb_lineno)
            time.sleep(3)
        
    return filename

def upload_to_s3(filepath):
    try:
        awsaccesskey_id = 'AKIAI5CVZMHMTTC7WXRA'
        awssecretaccess_key = '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'
        aws_bucket = 'tottestupload3'
        content_type = mimetypes.MimeTypes().guess_type(filepath)[0]
        key_names = filepath
        path = 'additional_docs'
        if  '\\' in filepath:
            key_nameArr = filepath.split('\\')
            key_names = key_nameArr.pop() #get last element
        
        s3obj = boto3.Session(
            aws_access_key_id=awsaccesskey_id,
            aws_secret_access_key=awssecretaccess_key
        )
        key_name = path+'/'+key_names
        s3 = s3obj.resource('s3')
        object = s3.Object(aws_bucket, key_name)
        if content_type != None and content_type != '':
            result = object.put(Body=open(filepath, 'rb'), ContentType=content_type)
        else:
            result = object.put(Body=open(filepath, 'rb'))
        res = result.get('ResponseMetadata')
        if res.get('HTTPStatusCode') == 200:
            return True
        else:
            return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("Error ON : ", sys._getframe().f_code.co_name + "--> " + str(e), "\n", exc_type, "\n", fname, "\n",exc_tb.tb_lineno)
        # Error_fun(Error,Function_name,Source_name)
        time.sleep(10)
        print(e)
        return False

def create_html_file(SegFeild):

    while True:
        try:
            exe_number = str(Global_var.exe_no)
            Current_dateTime = datetime.now().strftime("%Y%m%d%H%M%S%f")
            Fileid = "".join([exe_number , Current_dateTime])
            Path = "Z:\\" + Fileid + ".html"
            file1 = open(Path , "w" , encoding='utf-8')
            string_Translate_Table ="<table align=\"center\" border=\"1\" style=\"width:95%;border-spacing:0;border-collapse: collapse;border:1px solid #666666; margin-top:5px; margin-bottom:5px;\">" + \
                                    "<tr><td colspan=\"2\"; style=\"background-color:#004040; font-weight: bold; padding:7px;border-bottom:1px solid #666666; color:white;\">Tender Details</td></tr>" + \
                                    "<tr bgcolor=\"#e8eff1\" onmouseover=\"this.style.backgroundColor='#d6edf5'\" onmouseout=\"this.style.backgroundColor=''\"><td style=\"padding:7px;\">REFERENCE NO </td><td style=\"padding:7px;\">" + str(SegFeild[13]) + "</td></tr>" + \
                                    "<tr bgcolor=\"#e8eff1\" onmouseover=\"this.style.backgroundColor='#d6edf5'\" onmouseout=\"this.style.backgroundColor=''\"><td style=\"padding:7px;\">TENDER TITLE </td><td style=\"padding:7px;\">" + str(SegFeild[19]) + "</td></tr>" + \
                                    "<tr bgcolor=\"#e8eff1\" onmouseover=\"this.style.backgroundColor='#d6edf5'\" onmouseout=\"this.style.backgroundColor=''\"><td style=\"padding:7px;\">OPENING DATE </td><td style=\"padding:7px;\">" + str(SegFeild[25]) + "</td></tr>" + \
                                    "<tr bgcolor=\"#e8eff1\" onmouseover=\"this.style.backgroundColor='#d6edf5'\" onmouseout=\"this.style.backgroundColor=''\"><td style=\"padding:7px;\">CLOSING DATE </td><td style=\"padding:7px;\">" + str(SegFeild[24]) + "</td></tr>" + \
                                    "<tr bgcolor=\"#e8eff1\" onmouseover=\"this.style.backgroundColor='#d6edf5'\" onmouseout=\"this.style.backgroundColor=''\"><td style=\"padding:7px;\">Tender Document </td><td style=\"padding:7px;\">"+ str(SegFeild[6]) +"</td></tr></table>"
            Final_Doc = "<HTML><head><meta content=\"text/html; charset=utf-8\" http-equiv=\"Content-Type\" /><title>Tender Document</title></head><BODY><Blockquote style='border:0px solid; padding:10px;'>" + str(string_Translate_Table)+ "</Blockquote></BODY></HTML>"
            file1.write(Final_Doc)
            file1.close()
            SegFeild[6] = ''
            AdditionalDocs(SegFeild,Fileid)
            break
        except Exception as e:
            Function_name: str = sys._getframe().f_code.co_name
            Error: str = str(e)
            Source_name = str(SegFeild[31])
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error ON : ", sys._getframe().f_code.co_name + "--> " + str(e), "\n", exc_type, "\n", fname, "\n",exc_tb.tb_lineno)
            Error_fun(Error,Function_name,Source_name)
            time.sleep(10)

        
def insert_l2l_tbl(SegFeild, Fileid):
    ncb_icb = str(Global_var.ncb_icb)
    dms_entrynotice_tblstatus = "1"
    added_on = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    search_id = "1"
    cpv_userid = ""
    dms_entrynotice_tblquality_status = '1'
    quality_id = '1'
    quality_addeddate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    Col1 = str(Global_var.Col1)
    Col2 = ''
    Col3 = ''
    Col4 = ''
    Col5 = str(SegFeild[3])
    file_name = "D:\\Tide\\DocData\\" + Fileid + ".html"
    file_upload = str(Global_var.file_upload)
    dms_downloadfiles_tbluser_id = str(Global_var.dms_downloadfiles_tbluser_id)
    dms_downloadfiles_tblstatus = '1'
    dms_downloadfiles_tblsave_status = '1'
    selector_id = ''
    select_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    dms_downloadfiles_tbldatatype = "A"
    dms_entrynotice_tblnotice_type = '2'
    dms_entrynotice_tbl_cqc_status = '1'
    file_id = Fileid
    is_english = str(Global_var.is_english)
    mydb = db_connection()
    mycursor = mydb.cursor()
    if SegFeild[12] != "" and SegFeild[19] != "" and SegFeild[24] != "" and SegFeild[7] != "":
        dms_entrynotice_tblcompulsary_qc = "2"
    else:
        dms_entrynotice_tblcompulsary_qc = "1"
        Global_var.QC_Tenders += 1  # type: ignore
        sql = "INSERT INTO qctenders_tbl(Source,tender_notice_no,short_desc,doc_last,Maj_Org,Address,doc_path,Country)VALUES(%s,%s,%s,%s,%s,%s,%s,%s) "
        val = (str(SegFeild[31]) , str(SegFeild[13]) , str(SegFeild[19]) , str(SegFeild[24]) , str(SegFeild[12]) ,str(SegFeild[2]) , "http://tottestupload3.s3.amazonaws.com/" + file_id + ".html" , str(SegFeild[7]))
        a4 = 0
        while a4 == 0:
            try:
                mydb = db_connection()
                mycursor = mydb.cursor()
                mycursor.execute(sql , val)
                mydb.commit()
                mycursor.close()
                mydb.close()
                a4 = 1
                print("Code Reached On QC Tenders")
            except Exception as e:
                Function_name: str = sys._getframe().f_code.co_name
                Error: str = str(e)
                Source_name = str(SegFeild[31])
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print("Error ON : ", sys._getframe().f_code.co_name + "--> " + str(e), "\n", exc_type, "\n", fname, "\n",exc_tb.tb_lineno)
                Error_fun(Error,Function_name,Source_name)
                a4 = 0
                time.sleep(10)

    sql = "INSERT INTO l2l_tenders_tbl(notice_no,file_id,purchaser_name,deadline,country,description,purchaser_address,purchaser_email,purchaser_url,purchaser_emd,purchaser_value,financier,deadline_two,tender_details,ncbicb,status,added_on,search_id,cpv_value,cpv_userid,quality_status,quality_id,quality_addeddate,source,tender_doc_file,Col1,Col2,Col3,Col4,Col5,file_name,user_id,status_download_id,save_status,selector_id,select_date,datatype,compulsary_qc,notice_type,cqc_status,DocCost,DocLastDate,is_english,currency,sector,project_location,set_aside,other_details,file_upload,file_name_additional)VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    val = (str(SegFeild[13]) , file_id , str(SegFeild[12]) , str(SegFeild[24]) , str(SegFeild[7]) , str(SegFeild[19]) ,str(SegFeild[2]) ,str(SegFeild[1]) , str(SegFeild[8]) , str(SegFeild[26]) , str(SegFeild[20]) , str(SegFeild[27]) ,str(SegFeild[24]) , str(SegFeild[18]) , ncb_icb , dms_entrynotice_tblstatus , str(added_on) , search_id ,str(SegFeild[36]) ,cpv_userid , dms_entrynotice_tblquality_status , quality_id , str(quality_addeddate) , str(SegFeild[31]) ,str(SegFeild[28]) ,Col1 , Col2 , Col3 , Col4 , Col5 ,file_name , dms_downloadfiles_tbluser_id , dms_downloadfiles_tblstatus , dms_downloadfiles_tblsave_status ,selector_id , str(select_date) , dms_downloadfiles_tbldatatype ,dms_entrynotice_tblcompulsary_qc , dms_entrynotice_tblnotice_type , dms_entrynotice_tbl_cqc_status ,str(SegFeild[22]) , str(SegFeild[41]),is_english, str(SegFeild[21]),SegFeild[29],SegFeild[42],SegFeild[43], str(SegFeild[46]),file_upload,(SegFeild[44]))
    a5 = 0
    while a5 == 0:
        try:
            mydb = db_connection()
            mycursor = mydb.cursor()
            mycursor.execute(sql , val)
            mydb.commit()
            mydb.close()
            mycursor.close()
            print("Code Reached On insert_L2L")
            print(' Live Tender ')
            Global_var.inserted += 1
            a5 = 1
        except Exception as e:
            Function_name: str = sys._getframe().f_code.co_name
            Error: str = str(e)
            Error_fun(Error,Function_name,SegFeild)
            Global_var.Print_Exception_detail(e)  # type: ignore
            a5 = 0
            time.sleep(10)

db_connection()

