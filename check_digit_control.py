"""
Check digit extraction using container ID 
@author: Ozan Gökkan
"""

container_id = input("enter the container ID :")
first_ten_digit = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512] 

dict = {'A':10, 'B':12, 'C':13, 'D':14, \
        'E':15, 'F':16, 'G':17, 'H':18, \
        'I':19, 'J':20, 'K':21, 'L':23, \
        'M':24, 'N':25, 'O':26, 'P':27, \
        'Q':28, 'R':29, 'S':30, 'T':31, \
        'U':32, 'V':34, 'W':35, 'X':36, \
        'Y':37, 'Z':38}
array = []
for i,j in dict.items():
    array.append([i,j])    
result = 0  
for indx, container_letter in enumerate(container_id[:4]):
    for index, (letter, digit) in enumerate(array):
        if container_letter == letter:
            result += digit * first_ten_digit[indx]
        else:
            pass          
for indexx, digitx in enumerate(container_id[4:]):
    result += int(digitx) * first_ten_digit[indexx+4]
value = int(result / 11)
value1 = value * 11
check_digit = result - value1
print("*************Result******************")
print("Entered number : ", container_id)
print("Full container ID : ", (str(container_id) + str(check_digit)))
print("Check digit number : " , check_digit)  