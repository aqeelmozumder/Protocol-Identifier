To run this program: python3 smartClient.py www.example.com
Note: Enter any url instead of www.example.com

This smartclient will take any URL input from the user which will be in the form of "www.example.com". If the user does not input "www." then different answers might come up
#     The smartClient will check if the website supports HTTPS, http1.1 and http2. 
#     The smartclient will also print the Cookies

#     The idea of this code is that first the program will wrap the socket and send request with the filename index.html to see if it supports https or not
#     1) if it supports https then it will obvioulsy receive 200 status code, meaning it supports hhtp1.1 as well. Then it checks for http2.
#     2) else if it doesnot support https then the program will send the request without the filename index.html and check again
#         2.1) if it supports https then then it will will receive 200|301|302 status code, meaning it supports hhtp1.1 as well. Then it checks for http2.
#         2.2) else if it doesnot support https then we are guranteed that the website does not support https and http2, so we check for http1.1 by using port 80 and send request without wrapping


