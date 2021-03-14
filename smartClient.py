# Name: Aqeel Mozumder
# Vnumber: V00884880
# File: smartClient.py
# Course: CSC 361
# Description:
#     This smartclient will take a URL input from the user which will be in the form of "www.example.com". If the user does not input "www." then different answers might come up
#     The smartClient will check if the website supports HTTPS, http1.1 and http2. 
#     The smartclient will also print the Cookies

#     The idea of this code is that first the program will wrap the socket and send request with the filename index.html to see if it supports https or not
#     1) if it supports https then it will obvioulsy receive 200 status code, meaning it supports hhtp1.1 as well. Then it checks for http2.
#     2) else if it doesnot support https then the program will send the request without the filename index.html and check again
#         2.1) if it supports https then then it will will receive 200|301|302 status code, meaning it supports hhtp1.1 as well. Then it checks for http2.
#         2.2) else if it doesnot support https then we are guranteed that the website does not support https and http2, so we check for http1.1 by using port 80 and send request without wrapping



import ssl
import re
import sys
import socket
import struct

from socket import AF_INET, SOCK_STREAM



host, port = sys.argv[1], 443 #port 443 as we will start observing HTTPS
SupportHttps = False
SupportHttp1_1 = False
SupportHttp2 = False
CookieList = []

def GetCookies(file):
    check = [s for s in test if  "set-cookie"  in s.lower()]
    
    for check1 in check:
        
        test1 = re.match("(S|s)et-(C|c)ookie: ([^;]*)", check1)

        if(test1):
            cookiename = "cookie name: "+ test1.group(3)
        #endif        

        test2 = re.search("(e|E)xpires=([^;]*)", check1)
        
        if(test2):
            expiretime = ", expire time: " + test2.group(2)
        #endif        

        test3 = re.search("(D|d)omain=([^;]*)", check1)

        if(test3):
            domain = ", domain name: " + test3.group(2)
        #endif   
                
        if(test1 and test2 and test3):
            CookieList.append(cookiename+expiretime+domain)
        elif(test1 and test2):
            CookieList.append(cookiename+expiretime)
        elif(test1 and test3):
            CookieList.append(cookiename+domain)
        else:
            CookieList.append(cookiename)       
        #endelse   
    #endfor

#endfunction

def CheckHttp2():
    ctx = ssl.create_default_context()
    ctx.set_alpn_protocols(["h2", "spdy/3", "http/1.1"])

    sock = ctx.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname=host)

    try:
        sock.connect((host, port))
    except (ssl.SSLError,socket.error,socket.timeout,socket.gaierror,socket.timeout,ssl.CertificateError):
        pass
    
    if(sock.selected_alpn_protocol() == "h2"):
        SupportHttp2 = True #because alpn protocol is h2
        # print(SupportHttp2)
    else:
        SupportHttp2 = False    
        
    sock.close()
    return SupportHttp2
#endfunction



s = socket.socket(AF_INET,SOCK_STREAM)
version = "HTTP/1.1"
request = "GET / "+version+"\r\nHost:"+host+"/index.html\r\n\r\n"
s = ssl.wrap_socket(s, server_side=False, ssl_version=ssl.PROTOCOL_SSLv23) # Lets check if it supports ssl to determine if it supports https
ip = socket.gethostbyname(host)
try:
    s.connect((ip, port)) #connect to remote socket at address
    s.sendall(request.encode()) #send HTTP request
except (ssl.SSLError,socket.error,socket.timeout,socket.gaierror,socket.timeout,ssl.CertificateError):
    #guranteed does not support https and http2
    
    SupportHttps = False
    SupportHttp2 = False

reply = s.recv(2500)
DecodeReply = reply.decode(errors="ignore")
s.close()


if(re.match(".*(200)", DecodeReply)):
    SupportHttp1_1 = True #because it responds with the Http1.1
    SupportHttps = True #because we send the request by wrapping the scoket       
    SupportHttp2 = CheckHttp2() #Lets check if it supports http2

    test = DecodeReply.split("\r\n")
    GetCookies(test)
#endif        
else:
    #if we did not get a 200 response then it could be something else could be 3xx|4xx|5xx
    #maybe index.html is not found, so we remove index.html and try with ssl
        
    s = socket.socket(AF_INET,SOCK_STREAM)
    version = "HTTP/1.1"
    request = "GET / "+version+"\r\nHost:"+host+"\r\n\r\n"
    s = ssl.wrap_socket(s, server_side=False, ssl_version=ssl.PROTOCOL_SSLv23)
    ip = socket.gethostbyname(host)

    try:
        s.connect((ip, port)) #connect to remote socket at address
        s.sendall(request.encode()) #send HTTP request
    except (ssl.SSLError,socket.error,socket.timeout,socket.gaierror,socket.timeout,ssl.CertificateError):
        # print("Does not support HTTP")
        SupportHttps= False

    reply = s.recv(2500)
    DecodeReplyNoFile = reply.decode(errors="ignore")
    s.close()
    

    if(re.match(".*(200|301|302)", DecodeReplyNoFile)):
        SupportHttps = True
        SupportHttp1_1 = True
        SupportHttp2 = CheckHttp2() #Lets check if it supports http2
        test = DecodeReplyNoFile.split("\r\n")
        GetCookies(test)      
    #endif  
    else:
        # if we still did not get a 200 response then we are guranteed that the website does not support https
        # Therefore it will not support Http2 as well
        # We now just need to check if it supports http1.1, thus we wont wrap the socket and connect it normally

        s = socket.socket(AF_INET,SOCK_STREAM)
        version = "HTTP/1.1"
        request = "GET / "+version+"\r\nHost:"+host+"\r\n\r\n"
        port = 80
        s.connect((ip, port)) #connect to remote socket at address
        s.sendall(request.encode()) #send HTTP request
        reply = s.recv(2500)
        print(reply)
        DecodeReplyNoSSL = reply.decode(errors="ignore")

        if(re.match(".*(200)", DecodeReplyNoSSL)):
            SupportHttp1_1 = True 
        elif(re.match(".*(301|302)", DecodeReplyNoSSL)):
            SupportHttp1_1 = True
        else:
            SupportHttp1_1 = False

        test = DecodeReplyNoSSL.split("\r\n")
        GetCookies(test)
    #endelse    
#endelse       



print("----------------------------------------")
print("website: "+host)
if(SupportHttps == True):
    print("1.Supports of HTTPS: yes")
else:
    print("1.Supports of HTTPS: no")
if(SupportHttp1_1 == True):
    print("2.Supports of http1.1: yes")
else:
    print("2.Supports of http1.1: no")
if(SupportHttp2 == True):
    print("3.Supports of http2: yes")
else:
    print("3.Supports of http2: no")   

print("4.List of Cookies:")    
for x in CookieList:
    print(x)