------------------------------------------------------------
-- 整体说明：
-- 1. 由于既模拟上游三方，又模拟银行，所以要有C端用户
-- 2. 需要提供用户输入用户名密码页
-- 3. (用户名，用户类型)维一,sqlite如何实现？
------------------------------------------------------------
-- 用户帐户表: B代表商户[.com]，C代理个人, 
create table user_account(id int primary key,name varchar,password varchar,type varchar,balance double,create_time date);
create table account_line(id int primary key,user_id int,merchant_id varchar,merchant_order_id int,type varchar,amount double,create_time date);

-- 初始化余额 用户10000,商户0
insert into user_account values(1,"baidu.com","baidu","B",0.0,datetime('now','localtime'));
insert into user_account values(2,"liunix","liunix","C",10000.0,datetime('now','localtime'));

-- 1笔支付交易(1元): B2C_PAY[T0] 
-- update多列用',',不要用and
insert into account_line values(1,2,1,"1","B2C_WEB_PAY_T0",1.0,datetime('now','localtime'));
update user_account set balance=balance-1.0,create_time=datetime('now','localtime') where id = 2;
update user_account set balance=balance+1.0,create_time=datetime('now','localtime') where id = 1;

