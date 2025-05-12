
from ftplib import FTP
import os

port=21
ip="192.168.0.47"
password = "cameradeneme"
user = "cameradeneme"    
ftp = FTP(ip)
ftp.login(user,password)    
images_namelist = ftp.nlst()
if len(images_namelist) > 2:
    jpgfilelist = [f for f in images_namelist if f.endswith(".jpg") ]
    for filename in jpgfilelist:
        local_file = os.path.join('C:/Users/yourpath/ftp_images/', filename)
        file = open(local_file, 'wb') 
        ftp.retrbinary("RETR %s" % filename, file.write)
        
    jpglist = [f for f in images_namelist if f.endswith(".jpg") ]   
    for i in jpglist:
        ftp.delete(i)
    ftp.close()
