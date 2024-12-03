"""
Oracle DB connection check
@author: Ozan Gökkan
"""

import cx_Oracle as cx
import time
dsn  = cx.makedsn("host","port","ServiceID")
conn = cx.connect(user="username", password="pass",dsn=dsn)
cursor =conn.cursor()

my_query = cursor.execute("select * from OCR_LOG")
my_log = []
for i in my_query:
    my_log.append(i)       
#while True:
#    my_query = cursor.execute("select * from OCR_LOG")
#    my_log = []
#    for i in my_query:
#        my_log.append(i)
#    time.sleep(600)
#    
container_log, log_20, log_40 = [], [], []
non_20_40 = []
db_check = cursor.execute("select distinct item_code,\
                          (select deger from item_property where item_code = o.item_code and property_code = 1)\
                          iso_code from OCR_LOG o where record_date between \
                          to_date('25.05.2019 10:00:00','dd.mm.yyyy hh24:mi:ss') \
                          and to_date('28.05.2019 12:00:00','dd.mm.yyyy hh24:mi:ss')")

for counter in db_check:
    container_log.append(counter)

for ind in range(len(container_log)):
    if container_log[ind][1][0] == '2':
        log_20.append(ind)
    elif container_log[ind][1][0] == '4':
        log_40.append(ind)
    else:
        non_20_40.append(ind)
