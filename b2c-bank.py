#--coding--:utf8

# 一个小型的银行模拟程序
# 一个观念：小注释也是程序，重点在记忆，不在洁癖
import sqlite3
import json
from flask import Flask,redirect,request
import requests
import threading

#####################数据库准备部分#########################
conn = sqlite3.connect(':memory:',check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
with open("bank.sql","r") as infile:
    for line in infile:
        if line.strip() and not line.strip().startswith("--"): #if line.strip()如果不空为true
            cursor.execute(line.strip())
conn.commit()

#####################服务程序部分#######################
app = Flask(__name__,static_folder=".",static_url_path="") 

@app.route("/")
def hello():
    return app.send_static_file("index.html")

@app.route("/b2cpay",methods=['POST']) # request.values参数必须出现，可选参数只能try/catch
def b2cpay():
    merchant = request.values['merchant']
    password = request.values['password']
    amount = request.values['amount']
    #1， 检查商户名、密码即可，md5只是个工具,还不利于命令行测试(openssl md5)
    result = cursor.execute("select * from user_account where name = '%s' and password = '%s' and type='%s'"%(merchant,password,'B')).fetchone()
    if result:
        return '''
            <h3>测试三方支付公司：银行直联</h3>
            <form action="/bank_b2cpay" method="POST">
                <p>测试银行用户：<input type=text name="name" value="liunix">
                <p>测试银行密码：<input type=text name="password" value="liunix">
                <p><input type=hidden name="merchant" value="%s">
                <p><input type=hidden name="merchant_order_id" value="%s">
                <p><input type=hidden name="amount" value="%s">
                测试订单金额：%s &nbsp;&nbsp;元
                <p><input type=hidden name="returnUrl" value="%s">
                <p><input type=hidden name="notifyUrl" value="%s">
                <p><input type=submit value="提交">
            </form>
        '''%(merchant,request.values['merchant_order_id'],amount,amount,request.values['returnUrl'],request.values['notifyUrl'])
    else:
        returnUrl = request.values['returnUrl']
        returnUrl += "?result=FAIL&msg=MERCHANT_NOT_FOUND"
        return redirect(returnUrl)

@app.route("/bank_b2cpay",methods=['POST'])
def bank_b2cpay():
    name = request.values['name']
    password = request.values['password']
    merchant = request.values['merchant']
    amount = request.values['amount']
    merchant_order_id = request.values['merchant_order_id']

    user_account = cursor.execute("select * from user_account where name = '%s' and password = '%s' and type='%s'"%(name,password,'C')).fetchone()
    merchant_account = cursor.execute("select * from user_account where name = '%s' and type='%s'"%(merchant,'B')).fetchone()

    account_line = cursor.execute("select max(id) as id from account_line").fetchone()
    returnUrl = request.values['returnUrl']+"?"

    if user_account:
        #TODO: 增加商户订单号，不然商户无法对帐，即便是同步页面流返回，也是一个独立的http请求，商户订单号就像跨应用的session_id
        cursor.execute('''insert into account_line values(%d,%d,%d,"%s","B2C_WEB_PAY",%s,datetime('now','localtime'));'''%(account_line['id']+1,user_account['id'],merchant_account['id'],merchant_order_id,amount) )
        cursor.execute('''update user_account set balance = balance - %s,create_time = datetime('now','localtime') where name = '%s'  and type='%s' ;'''%(amount,name,'C'))
        cursor.execute('''update user_account set balance = balance + %s,create_time = datetime('now','localtime') where name = '%s'  and type='%s' ;'''%(amount,merchant,'B'))        
        conn.commit()

        order_id = cursor.execute("select max(id) as id from account_line").fetchone()["id"]
        user_balance = cursor.execute("select balance from user_account where name='%s' and type='%s'; "%(name,'C')).fetchone()["balance"]
        merchant_balance = cursor.execute("select balance from user_account where name='%s' and type='%s';"%(merchant,'B')).fetchone()["balance"]
        result={ \
            "result":"SUCCESS", \
            "order_id":cursor.execute("select max(id) as id from account_line").fetchone()["id"], \
            "amount":amount, \
            "user_name":name, \
            "merchant_name":merchant, \
            "merchant_order_id":merchant_order_id, \
            "user_balance": user_balance, \
            "merchant_balance": merchant_balance
        }
        returnUrl += "&".join(['%s=%s' % (key, value) for (key, value) in result.items()])
        notifyQue.put((merchant_order_id,request.values['notifyUrl']))
        return redirect(returnUrl)
    else:
        returnUrl += "?result=FAIL&msg=USER_NOT_FOUND"
        return redirect(returnUrl)

@app.route("/balance_query",methods=["GET","POST"])
def balance_query():
    result = cursor.execute("select balance from user_account where name='%s' and type='%s'; "%(request.values['name'],request.values['type'])).fetchone()
    app.logger.debug(str(dict(result)))
    return json.dumps(dict(result)) 

@app.route("/order_query",methods=["GET","POST"])
def order_query():
    result = cursor.execute("select * from account_line where merchant_order_id = '%s'; "%(request.values['merchant_order_id'])).fetchone()
    app.logger.debug(str(dict(result)))
    return json.dumps(dict(result)) #Sqlite3.Row 转换成dict的方式

@app.route("/merchant_withdraw",methods=["GET","POST"])
def merchant_withdraw():
    merchant = request.values["merchant"]
    amount = request.values["amount"]
    merchant_order_id = request.values['merchant_order_id']
    # returnUrl = request.values['returnUrl']+"?"

    merchant_account = cursor.execute("select * from user_account where name = '%s' and type='%s'"%(merchant,'B')).fetchone()
    if merchant_account:
        account_line = cursor.execute("select max(id) as id from account_line").fetchone()
        cursor.execute('''insert into account_line values(%d,null,%d,"%s","B2C_WEB_PAY",%s,datetime('now','localtime'));'''%(account_line['id']+1,merchant_account['id'],merchant_order_id,amount) )
        cursor.execute('''update user_account set balance = balance - %s,create_time = datetime('now','localtime') where name = '%s'  and type='%s' ;'''%(amount,merchant,'B'))  
        conn.commit()

        order_id = cursor.execute("select max(id) as id from account_line").fetchone()["id"]
        merchant_balance = cursor.execute("select balance from user_account where name='%s' and type='%s';"%(merchant,'B')).fetchone()["balance"]  

        result={ \
            "result":"SUCCESS", \
            "order_id":cursor.execute("select max(id) as id from account_line").fetchone()["id"], \
            "amount":amount, \
            "merchant_name":merchant, \
            "merchant_order_id":merchant_order_id, \
            "merchant_balance": merchant_balance
        }
        # returnUrl += "&".join(['%s=%s' % (key, value) for (key, value) in result.items()])
        # return redirect(returnUrl)  
        return json.dumps(result)
    else:
        # returnUrl += "?result=FAIL&msg=MERCHANT_NOT_FOUND"
        # return redirect(returnUrl)  
        result={\
            "result":"FAIL", \
            "msg":"MERCHANT_NOT_FOUND"
        }
        return json.dumps(result)      
#####################模拟支付返回客户端部分################################
@app.route("/returnUrl",methods=['GET','POST'])    
def returnUrl():
    app.logger.debug("/returnUrl"+str(request.values.to_dict())) #values 结合request.args(get),request.form(post),但url参数优先
    return json.dumps(request.values.to_dict())

@app.route("/notifyUrl",methods=['GET','POST'])    
def notifyUrl():
    app.logger.debug("/notifyUrl"+str(request.values.to_dict()))
    return json.dumps(request.values.to_dict())

######################商户后台订单通知任务部分################################
from queue import Queue
import time
notifyQue=Queue()  

def notify_task(thread_name):
    app.logger.debug("后台通知线程启动........................")
    while True:
        (merchant_order_id,notifyUrl) = notifyQue.get()
        app.logger.debug("处理通知目标:merchant_order_id = %s, notifyUrl=%s"%(merchant_order_id,notifyUrl))
        time.sleep(0.1)
        account_line = cursor.execute("select * from account_line where merchant_order_id = '%s'; "%(merchant_order_id)).fetchone()
        account_line_d = dict(account_line)
        notifyUrl += "?"
        notifyUrl += "&".join(['%s=%s' % (key, value) for (key, value) in account_line_d.items()])
        app.logger.debug("请求url为:%s"%(notifyUrl))
        result = requests.get(notifyUrl)
        app.logger.debug("后台通知后的结果为:%s"%(result.text))


####################启动器##############################################
if __name__ == "__main__":
    threading._start_new_thread(notify_task,("thread_name",))
    app.run(debug=True,host="0.0.0.0",port=8888)
