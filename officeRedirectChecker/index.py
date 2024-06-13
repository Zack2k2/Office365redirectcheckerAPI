from flask import Flask, render_template
from flask import jsonify, request, flash, url_for
from flask import Response
import sys
import os
#import tinydb
import json
import time
import requests as req
#from seleniumwire import webdriver
#from selenium.webdriver.common.by import By
import re
import datetime


global_email_logs_name = "/var/log/collectedEmails.txt" 

intercepted_reqs = []

main_ms_login_site = "https://login.microsoftonline.com"

login_post_endpoint = "https://login.microsoftonline.com/common/GetCredentialType"

#
# is365office - return true if the response body contains indication that
# the email does exist in Microsoft office.
#
def is365office(json_body:dict):
    if json_body.get("IfExistsResult") != 1:
        if json_body.get('IfExistsResult') == 0:
            return True
        elif "FederationRedirectUrl" in json_body.get("Credentials").keys():
            return True
        else:
            return True
    else:
        return False

#
# isResponseValid - return True if the response valid else false
# redementry check 
#
def isResponseValid(json_body:dict):
    return "Credentials" in json_body.keys() and 'Username' in json_body.keys() and 'IfExistsResult' in json_body.keys()

#
# isEmailValid - check if an email is valid
#
def isEmailValid(i_email):
    email_reg = r'\b^[a-zA-Z][a-zA-Z0-9._%+-]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$\b'
        # pass the regular expression
    # and the string into the fullmatch() method
    if(re.fullmatch(email_reg, i_email)):
        return True
    else:
        return False


#
# hasRedirect - True if response has RedirectUrl, false otherwise
#
def hasRedirect(json_body:dict):
    return "FederationRedirectUrl" in json_body.get("Credentials").keys()

#
# getRedirectUrl - get the url of redirect 
#
def getRedirectUrl(json_body:dict):
    return json_body.get("Credentials").get("FederationRedirectUrl")


def changeEmailUsername(body:dict, new_email:str):
    body['username'] = new_email
    
    return body


#
# post_isexist_email - HTTP POST to microsoft to check 
# if an email exist or not.
#
def post_isemail(endpoint:str, email):
    s = req.session()
    body = '{\"Username\":\"'+ email+' \"}'

    res = req.post(endpoint,data=body)

    if res.ok:
        return res
    else:
        print("[::ERROR::] resource not found")
        sys.exit(1)



#
# post_important_req - HTTP POST to Microsoft office login   
# end point, if response if ok then return otherwise exit the program

def post_important_req(endpoint:str , req_headers:dict , body:str):
    res = req.post(endpoint,headers=req_headers, data=body)

    if res.ok:
        return res
    else:
        print("[::ERROR::] Network Error while sending POST HTTP requests")
        sys.exit(1)
        return


def findInputTagList(browser, css_sel):
    input_elem = browser.find_elements(By.CSS_SELECTOR,css_sel) 
    return input_elem

def findSubmitButtonList(browser , css_sel):
    submit_but = browser.find_elements(By.CSS_SELECTOR,css_sel) 
    return submit_but

'''
def create_app():
    driver = webdriver.Firefox()
    driver.get(main_ms_login_site)
    
    driver.implicitly_wait(15)

    email_input_css_selector = "input[placeholder='Email, phone, or Skype']" 
    email_next_button_css_selector = "input[value='Next']"

    input_tag_elems = findInputTagList(driver,email_input_css_selector)
    submit_buttons_tags = findSubmitButtonList(driver, email_next_button_css_selector)
    
    if len(input_tag_elems) > 1:
        print("Some thing is wrong please check")
        print("")
        sys.exit(1)

    if len(submit_buttons_tags) > 1:
        print("some thing is wrong")
        sys.exit(1)

    input_tag_elems[0].send_keys("tea@maker.edu")
    submit_buttons_tags[0].click()

    time.sleep(1)


    intercepted_reqs.extend([req for req in driver.requests if login_post_endpoint in req.url])

    driver.quit()
    

    #print(body_found)
    app = Flask(__name__)
    return app
'''




# packages
# basic:0
# standard:1
# premium:2
# elite:3
'''
customers = {
    "1010000000":
    {
        "limit":10000,
        "package":3,
        "isblacklisted":False,
        "invalidEmails":0,
        "maxallowed":10000
    }
}
'''
email_data_log = "collectedemails.txt"

email_data_fd = open(email_data_log,'ab+',0)
max_faulty_emails = 7

# request POST structure
'''
{
    "id":num,
    "emails":[elem1, elem2, ... elemN]
}
'''

# POST Response structure

'''
{
   [
    {"email1@dom.com":
        {
            "isExist":bool,
            "RedirectUrl":url 
        }
    }
   ] 
}

ALLOWED_EXTENSIONS = {'txt','pdf'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def get_db(json_db_file):
    db = tinydb.TinyDB(json_db_file)

    return db
'''


def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = '/home/plank/python_programs/'
    return app


app = create_app()
#db = get_db("./customers.json")

#db_query = tinydb.Query() 

@app.route('/checkemail',methods=['POST'])
def checkemail():
    #header = intercepted_reqs[0].headers
    #body = intercepted_reqs[0].body

    jsoned_req = request.get_json()
    user_id = jsoned_req['id']
   
    '''
    customer_record = db.search(db_query.id == user_id)[0]
    if customer_record["isblacklisted"]:
        return jsonify("[blacklisted]")
    '''
    
    email_list = request.get_json()["emails"]
    num_el = len(email_list)

    '''user_lim = customer_record['limit']
    if user_lim <= 0:
        return jsonify("['limit reached']")
     

    if num_el > user_lim:
        diff = num_el - user_lim
        email_list = email_list[:diff]


    user_lim = user_lim - num_el
    db.update({'limit':user_lim},db_query.id == user_id)
    '''
    email_result = {}

    for email in email_list:
        '''
        if not isEmailValid(email.strip()):
            n_invalid_emails = (db.search(db_query.id == user_id)[0]["invalidEmails"] + 1)
            db.update({"invalidEmails":n_invalid_emails}, db_query.id == user_id)

            if n_invalid_emails >= max_faulty_emails:
                customer_record.update({'isblacklisted':False},db_query.id == user_id)
            else:
                continue
        '''

        email_data_fd.write(str.encode(email + "\n"))
        exist_response = post_isemail(login_post_endpoint, email)
        text_res = exist_response.text
        json_res = exist_response.json()

        emailExistTrue = re.search('"IfExistsResult":0', text_res)
        emailExistFalse = re.search('"IfExistsResult":1', text_res)
    
        if emailExistFalse:
            #print(json_res)
            #print("bla: " + str(json_res["IfExistsResult"]))
            email_result.update({email:0})
            #print(email+"--> not office")

        if emailExistTrue:
            email_result.update({email:1})
            #print(email+"--> office ",end="") 
            if hasRedirect(json_res):
                redirecturl = getRedirectUrl(json_res)
                #print("--> " +str(redirecturl))
                email_result.update({email:redirecturl})


    return jsonify(email_result)



'''
@app.route("/getlimit", methods=['POST'])
def getremaninglimit():
    json_req = request.get_json()

    user_id = json_req.get('id')

    limitfound = db.search(db_query.id == user_id)[0]['limit'] 

    return jsonify("["+str(limitfound)+"]")
    

@app.route("/adminpanel",methods=["POST"])
def adminpanel():
    json_req = request.get_json()
    cookie = json_req.get('cookie')
    if str(cookie) != '713bfda78870bf9d1b261f565286f85e97ee614efe5f0faf7c34e7ca4f65baca':
        return jsonify("[\'Access Denied\']")

    user_id = json_req.get('id')
    command = json_req.get('command')

    if command == "customers":
        customers_info = []

        for rec in db.all():
            customers_info.append(rec['id'])
        return jsonify(customers_info)

    if command == "info":
        info = db.search(db_query.id == user_id)[0]
        return jsonify(info)

    if command == "resetlimit":
        max_allowed = db.search(db_query.id == user_id)[0]['maxallowed']
        db.update( {"limit":max_allowed} ,db_query.id == user_id )
        return jsonify(db.search(db_query.id == user_id)[0])

    if command == "ban":
        db.update( {"isblacklisted":True} ,db_query.id == user_id )
        return jsonify(db.search(db_query.id == user_id)[0])

    if command == "unban":
        db.update( {"isblacklisted":False} ,db_query.id == user_id )
        return jsonify(db.search(db_query.id == user_id)[0])


    if command == "changelimit":
        newlimit = json_req.get("newlimit")

        if newlimit == None:
            return jsonify("[None]")

        db.update( {"maxallowed":int(newlimit)},db_query.id == user_id )
        return jsonify(db.search(db_query.id == user_id)[0] )

    if command == "new_customer":
        customers_info = []
        
        for rec in db.all():
            customers_info.append(rec['id'])
        
        if user_id in customers_info:
            return jsonify("[Can't over ride]")

        new_customer = {'id':str(user_id),'limit':1000,'package':1,'isblacklisted':False,'invalidEmails':0, 'maxallowed':1000}

        db.insert(new_customer)
    

    if command == "remove_customer":
        status = db.remove(db_query.id == str(user_id))

        if len(status) > 0:
            return jsonify("[deleted]")
        else:
            return jsonify("[failed]")


    return jsonify("ok")

'''
'''
@app.route("/stream")
def generate_redirection_result():
    fd = open('./email_sample.txt')
    def generate():
        for line in fd:
            if isEmailValid(line)

'''


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/")
def json_schema():
    page = "This is An API app for connecting to office365 redirection checker\n" \
            "POST /checkemail\n" \
            "{ \"id\": 101,\n\"emails\":[str, str ,...] }\n\n" \
            "POST /getlimit\n"\
            "{\"id\": 101} # returns the remaining checks"

    return page 

