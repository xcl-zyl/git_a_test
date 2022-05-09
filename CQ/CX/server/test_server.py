import socket
import logging
import os
import json
import random
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.header import Header
import smtplib
from email.mime.multipart import MIMEMultipart 
import shutil
import threading

host= '192.168.0.4'
port=9999

users_online=[]

user = {}  # {name : address}

code=random.randint(100000, 999999)

host_port_start = {}     # {'host' : 'host:port'}
def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = (host, port)
    s.bind(addr)
    logging.info('UDP Server on %s:%s...', addr[0], addr[1])

    while True:
        try:
            data, addrr = s.recvfrom(1024)
            print(addrr)
            print(data)
            ins=json.loads(data.decode('utf-8'))
            try:
                if ins["Attributes"]=="start":
                    host_port_start[addrr[0]]=str(addrr)
                    # print(host_port_start+"--------------------") 
                user[ins['userId']] = str(addrr)
                # print(host_port_start)
                # print()
                if ins['userId'] not in users_online:
                    users_online.append(ins['userId'])
            except Exception as e: 
                print(e)
                pass
            res = choose_func(ins,s)
            # print(res, type(res))
            s.sendto(res.encode(), addrr)

        except ConnectionResetError:
            logging.warning('Someone left unexcept.')


def choose_func(ins,soc):   # 选择功能
    attri=ins['Attributes']
    if attri=="enroll":
        return enroll(ins)
    elif attri=="login_with_password":
        return login_password(ins)
    elif attri=="login_with_email":
        if ins['password']=="":
            return login_send_email(ins)
        else:
            return login_email(ins)
    elif (attri=="add_friend") | (attri=="del_friend"):
        if 'reply' in ins:
            return add_friend_confirm(ins, soc)
        else:
            return A_D_friend(ins,soc)
    elif (attri=="add_group") | (attri=="del_group"):
        if ins['???']=="reply":
            return add_group_confirm(ins)
        else:
            return A_D_group(ins,soc)
    elif attri=="create_group":
        return create_group(ins,soc)
    elif attri=="message":
        if ins['mes_attrib']=="person":
            return chat_person(ins,soc)
        else:
            return chat_group(ins,soc) 
    elif attri=="search_person":
        return search_person(ins['search_Id'])
    elif attri=="search_group":
        return search_group(ins['search_Id'])
    else:
        return "{'Attributes': 'Error'}"

def enroll(ins):    # 用户注册
    path=".\\data\\users\\"+ins['userId']

    isExists=os.path.exists(path)
    if isExists:
        return "user already exists" 
    else:
        os.makedirs(path) 
        os.makedirs(path+"\\friend_history") 
        os.makedirs(path+"\\image") 
        f = open(path+'\\friend_list.txt','w')
        f.close()
        f = open(path+'\\group_list.txt','w')
        f.close()
        f = open(path+'\\config.txt','w')
        f.write(json.dumps(ins)+"\n")
        f.close()
        return "succeed in registration"

def login_password(ins):    # 密码登录
    path=".\\data\\users\\"+ins['userId']
    isExists=os.path.exists(path)
    if not isExists:
        return "用户不存在"
    else:
        path=path+"\\config.txt"
        f=open(path,'r')
        data=f.readline().strip()
        f.close()
        config=json.loads(data)
        if ins['password'] != config['password']:
            return "密码错误"
        else:
            users_online.append(ins['userId'])
            return "Login success"

def login_send_email(ins):    # 邮件登录发送邮件部分
    path=".\\data\\users\\"+ins['userId']
    isExists=os.path.exists(path)
    if not isExists:
        return "user does not exist"
    else:
        path=path+"\\config.txt"
        f=open(path,'r')
        data=f.readline().strip()
        ins_now=json.loads(data)
        t_send_email = threading.Thread(target=sendqqmail, args=(ins_now, str(code)))
        t_send_email.start()
        # sendqqmail(ins_now,str(code))
        return "email sent"

        
def login_email(ins):    # 邮件登录验证邮件部分
    global code
    path=".\\data\\users\\"+ins['userId']
    isExists=os.path.exists(path)
    if not isExists:
        return "user does not exist"
    else:
        # print(code, ins['password'], type(ins['password']), type(code))
        if ins['password'] != str(code):
            return "Verification Code mismatch"
        else:
            users_online.append(ins['userId'])
            code=random.randint(100000,999999)
            return "Login success"

def A_D_friend(ins,soc):    # 添加或删除好友
    path1=".\\data\\users\\"+ins['userId']+"\\friend_list.txt"
    path2=".\\data\\users\\"+ins['add_Id']+"\\friend_list.txt"
    f1=open(path1,'r')
    f2=open(path2,'r')
    data1=f1.readlines()
    data2=f2.readlines()
    data1=[str.strip() for str in data1]
    data2=[str.strip() for str in data2]
    f1.close()
    f2.close()
    # 对于删除，单方面删除
    if ins['Attributes']=="delete":
        f1=open(path1,'w')
        f1.close()
        
        for friend in data1:
            if ins['add_Id'] != friend:
                f1=open(path1,'a')
                f1.write(friend+"\n")
                f1.close()
        
        return "Friend deleted successfully"
    # 对于添加，需要对方同意
    else:
        # 发送加好友请求给对方
        # print(user,'--------!')
        for name,address in user.items():
            # print(name, ins['add_Id'], '---------!!!!')
            if name==ins['add_Id']:
                print(host_port_start)
                for host_,addr_ in host_port_start.items():
                    if address.find(host_)!=-1:
                        # print(addr_+'-----------------')
                        soc.sendto(json.dumps(ins).encode(), eval(addr_))
                        break
                break
        return "Waitinig for reply from another user"

            
def add_friend_confirm(ins,soc):    # 好友申请回复
    path1=".\\data\\users\\"+ins['userId']+"\\friend_list.txt"
    path2=".\\data\\users\\"+ins['add_Id']+"\\friend_list.txt"
    if ins['reply']=="accepted":
        f1=open(path1,'a')
        f1.write(ins['add_Id']+"\n")
        f1.close()
        f2=open(path2,'a')
        f2.write(ins['userId']+"\n")
        f2.close()
        for name,address in user.items():
            # print(name, ins['add_Id'], '---------!!!!')
            if name==ins['add_Id']:
                # print(host_port_start)
                for host_,addr_ in host_port_start.items():
                    if address.find(host_)!=-1:
                        # print(addr_+'-----------------')
                        soc.sendto(("friendreply "+ins['userId']+" application accepted").encode(), eval(addr_))
                        break
                break
        return "friendreply "+ins['add_Id']+" application accepted"
    else:
        return "friendreply "+ins['add_Id']+" application rejected"

def create_group(ins,soc):   # 创建群聊
    path=".\\data\\groups\\"+ins['group_name']
    isExists=os.path.exists(path)
    if isExists:
        return "群名已存在"
    else:
        os.makedirs(path) 
        os.makedirs(path+"\\image") 
        f = open(path+'\\history.txt','w')
        f.close()
        f = open(path+'\\member_list.txt','w')
        f.write(ins['userId']+"\n")
        f.close()
        
        # print(type(ins['members']))
        members=ins['members']
        for one in members:
            f = open(path+'\\member_list.txt','a')
            f.write(one+"\n")
            f.close()

        path=".\\data\\users\\"+ins['userId']
        f=open(path+'\\config.txt','a')
        f.write(ins['group_name']+"\n")
        f.close()
        f=open(path+'\\group_list.txt','a')
        f.write(ins['group_name']+"\n")
        f.close()
        for one in members:
            path=".\\data\\users\\"+one
            f=open(path+'\\group_list.txt','a')
            f.write(ins['group_name']+"\n")
            f.close()
        # print('aaaaaaaaaaaaaaaaa-------------')
        for name,address in user.items():
            # print(user)
            if name in members:
                # print(members)
                for host_,addr_ in host_port_start.items():
                    # print(host_port_start)
                    if address.find(host_)!=-1:
                        soc.sendto(json.dumps(ins).encode(), eval(addr_))
        return "Group created successfully"


def search_person(ins):     # 搜索用户
    result=[]
    chap=ins
    all_users=get_all_users()
    for name in all_users:
        if name.find(chap)!= -1:
            result.append(name)
    return str(result)

def search_group(ins):      # 搜索群组
    result=[]
    chap=ins
    all_groups=get_all_groups()
    for name in all_groups:
        if name.find(chap)!= -1:
            result.append(name)
    return str(result)

def A_D_group(ins,soc):     # 个人添加或退出群聊天
    path1=".\\data\\users\\"+ins['userId']+"\\group_list.txt"
    path2=".\\data\\groups\\"+ins['group_name']+"\\member_list.txt"
    f=open(path1,'r')
    data1=f.readlines()
    f.close()
    f=open(path2,'r')
    data2=f.readlines()
    f.close()
    data1=[str.strip() for str in data1]
    data2=[str.strip() for str in data2]
    # 单方面退出/解散群聊
    if ins['Attributes']=="delete":
        f=open(path1,'w')
        f.close()
        for group in data1:
            if ins['group_name']!=group:
                f=open(path1,'a')
                f.write(group+"\n")
                f.close()
        if data2[0]==ins['userId']:
            dir_path=".\\data\\groups\\"+ins['group_name']
            shutil.rmtree(dir_path)

            path=".\\data\\users\\"+ins['userId']+"\\config.txt"
            f=open(path,'r')
            data=f.readlines()
            data=[str.strip() for str in data]
            f=open(path,'w')
            f.close()
            for conf in data:
                if ins['group_name'] != conf:
                    f=open(path,'a')
                    f.write(conf+"\n")
                    f.close()

            return "Group Dismissed"
        else:
            f=open(path2,'w')
            f.close()
            for member in data2:
                if ins['userId']!=member:
                    f=open(path2,'a')
                    f.write(member+"\n")
                    f.close()
            return "quit succed"
    # 向群主申请加入
    else:
        f=open(path2,'r')
        admin=f.readline().strip()
        for name,address in user.items():
            if name==admin:
                soc.sendto(json.dumps(ins).encode(),address )
                break
        return "Waitinig for reply from group administrator"

def add_group_confirm(ins): # 加群申请回复
    path1=".\\data\\users\\"+ins['userId']+"\\group_list.txt"
    path2=".\\data\\groups\\"+ins['group_name']+"\\member_list.txt"
    if ins['reply']=="accepted":
        f1=open(path1,'a')
        f1.write(ins['group_name']+"\n")
        f1.close()
        f2=open(path2,'a')
        f2.write(ins['userId']+"\n")
        f2.close()
        return "group application accepted"
    else:
        return "group application rejected"

def chat_person(ins,soc):   # 私聊
    path1=".\\data\\users\\"+ins['userId']+"\\friend_history\\"+ins['friend']+"_history.txt"
    path2=".\\data\\users\\"+ins['friend']+"\\friend_history\\"+ins['userId']+"_history.txt"
    f1=open(path1,'a')
    f2=open(path2,'a')
    f1.write(json.dumps(ins)+"\n")
    f2.write(json.dumps(ins)+"\n")
    f1.close()
    f2.close()

    # print('aaa')
    for name,address in user.items():
        # print(name, ins['friend'])
        if name==ins['friend']:
            # print('!!!!!!')
            for host_,addr_ in host_port_start.items():
                # print(host_port_start, address)
                if address.find(host_)!=-1:
                    # print('-----------')
                    soc.sendto(json.dumps(ins).encode(), eval(addr_))
                    break
            break
    return "private message sent"


def chat_group(ins,soc):    # 群聊
    # print(json.dumps(ins)+'wwwwwwwwwww')
    path_group_his=".\\data\\groups\\"+ins['friend']+"\\history.txt"
    path_group_mem=".\\data\\groups\\"+ins['friend']+"\\member_list.txt"
    f=open(path_group_his,'a')
    f.write(json.dumps(ins)+"\n")
    f.close()
    f=open(path_group_mem,'r')
    group_mem=f.readlines()
    group_mem=[str.strip() for str in group_mem]
    for name,address in user.items():
        if (name in group_mem) and (name != ins['userId']):
            for host_,addr_ in host_port_start.items():
                if address.find(host_)!=-1:
                    soc.sendto(json.dumps(ins).encode(), eval(addr_))
                    
    return "private message sent"


def get_all_users():
    all_users=[]
    all_dirs=[]
    path=".\\data\\users\\"
    for root, dirs, files in os.walk(path):
        all_dirs.append(dirs)
    for users in all_dirs[0]:
        all_users.append(users)
    return all_users

def get_all_groups():
    all_dirs=[]
    all_groups=[]
    path=".\\data\\groups\\"
    for root, dirs, files in os.walk(path):
        all_dirs.append(dirs)
    for groups in all_dirs[0]:
        all_groups.append(groups)
    return all_groups

def sendqqmail(ins,msginfo,html=False):
    _user = "952168447@qq.com"
    _pwd  = 'vspxplqfhzpcbbgj' 
    _to = ins['email']
    msg = MIMEMultipart('alternative') 
    msg["Subject"] = "验证登录"
    msg["From"]    = _user
    msg["To"]      = _to
    if html:
        text =MIMEText(msginfo,'html','utf-8') 
        msg.attach(text) 
    else:
        text = MIMEText(msginfo)
        msg.attach(text) 
        s = smtplib.SMTP_SSL("smtp.qq.com", 465)
        s.login(_user, _pwd)
        s.sendmail(_user, _to, msg.as_string())
        s.quit()

if __name__ == '__main__':
    main()

