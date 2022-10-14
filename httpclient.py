#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        header = data.split("\r\n\r\n")[0]
        line = header.split("\r\n")[0]
        code = line.split(" ")[1]
        code = int(code)
        return code

    def get_headers(self,data):
        dict_headers = {}
        headers = data.split("\r\n")[1:]
        for header in headers:
            item = header.split(":")
            key = item[0]
            values = item[1:]
            dict_headers[key] = values
        return dict_headers

    def get_body(self, data):
        body = data.split("\r\n\r\n")
        if (len(body) <= 1):
            return None
        else:
            return body[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        parsed_url = urllib.parse.urlparse(url)
        port = 80        
        if parsed_url.port != None:
            port = parsed_url.port        
        path = parsed_url.path        
        if path == "":
            path = "/"        
        message = "GET " + path + " HTTP/1.1\r\n"
        message += "Host: " + parsed_url.hostname + "\r\n"
        message += "Accept: text/html, application/xhtml+xml, application/xml; q=0.9, */*; q=0.8\r\n"
        message += "Accept-Charset: utf-8\r\n"
        message += "Accept-Language: en-US, en; q=0.5\r\n"
        message += "Connection: close\r\n\r\n"        
        self.connect(parsed_url.hostname, port)
        self.sendall(message)
        response = str(self.recvall(self.socket))
        self.close()        
        body = self.get_body(response)
        code = self.get_code(response)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        parsed_url = urllib.parse.urlparse(url)
        port = 80        
        if parsed_url.port != None:
            port = parsed_url.port        
        path = parsed_url.path        
        if path == "":
            path = "/"   
        body = None
        if args != None:
            body = urllib.parse.urlencode(args)
        message = "POST " + path + " HTTP/1.1\r\n"
        message += "Host: " + parsed_url.hostname + "\r\n"
        message += "Accept: text/html, application/xhtml+xml, application/xml; q=0.9, */*; q=0.8\r\n"
        message += "Accept-Language: en-US\r\n"
        message += "Connection: close\r\n"
        len_body = 0
        if body != None:
            message += "Content-Type: application/x-www-form-urlencode\r\n"
            len_body = len(body)
        message += "Content-Length: " + str(len_body) + "\r\n\r\n"
        if body != None:
            message += body + "\r\n"
        self.connect(parsed_url.hostname, port)
        self.sendall(message)
        response = str(self.recvall(self.socket))
        self.close()        
        body = self.get_body(response)
        code = self.get_code(response)  
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
