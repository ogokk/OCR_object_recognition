
import pyodbc
import numpy as np
from PIL import Image
import pytesseract
import cv2
import re
import time
import os.path
import os
from ftplib import FTP
import cx_Oracle as cx
import glob
import datetime 
import traceback
import logging
import openpyxl



#******************************************************************************
#log counters
#******************************************************************************
log_count = 1
error_count = 1
my_log_control = []


while True:
    start_time = time.time()
    
    
    
    
    
    #**************************************************************************
    # ftp connection + file downloading from ftp + 
    # deleting the files from ftp + fault detection
    #**************************************************************************
    try:
        port=21
        ip="192.168.0.16"
        password = "cameradeneme"
        user = "cameradeneme"
        ftp = FTP(ip)
        ftp.login(user,password)
        ftp.cwd('192.168.0.199')
        images_namelist = []
        images_namelist = ftp.nlst()
        ftp_directory_content = ftp.retrlines('LIST')
        if len(images_namelist) > 1 and ftp_directory_content[:3] == "226":
            jpgfilelist = [f for f in images_namelist if f.endswith(".jpg") ]
            for filename in jpgfilelist:
                with open(filename, 'wb') as file:
                    ftp.retrbinary('RETR ' + filename, file.write)
            jpglist = [f for f in images_namelist if f.endswith(".jpg") ]
            
            for i in jpglist:
                f = None
                try:
                    f = open(i, 'rb')
                    ftp.delete(i)
                    f.close()
                    
                finally:
                    if f is not None:
                        f.close()
        else:
            ftp.close()
            pass
    except Exception as e: 
        error_path = "C:/Users/your_error_log_path"
        os.chdir(error_path)
        with open("ERROR_LOG.txt", "a") as error:
            error.write("%s\nError Info : %s\nError capturing Time : %s\n" % (error_count, e, datetime.datetime.now()))
            error.write("----------------------****************************-------------------\n")
            error_count += 1
        logging.error(traceback.format_exc())
        pass    
    

    
    #**************************************************************************
    #image retrieving from windows folder 
    #**************************************************************************
    images = [ cv2.imread(file) for file in glob.glob("C:/Users/your_path/*.jpg") if os.path.getsize(file) > 0 and file != None]
    number_of_images_for_each_vehicle = len(images)
    ocr_list = []
#    namee get from db like folder_directory_to process_images
    namee = "C:/Users/your_path/"
    if len(images) >= 1:
        inFilejpegs = [jf for jf in os.listdir(namee) if jf.endswith(".jpg")]
        filename_for_database = inFilejpegs[len(images)-1]
        tt = "C:/Users/your_path/results/archieve/%s.jpg" % filename_for_database
        d = r'C:/Users/your_path/results/archieve/'
#        ospath = os.path.join(d, inFilejpegs[len(images)-1])
        directory_name = os.path.split(d)[0]
        cv2.imwrite(tt, images[len(images)-1])
        for im_index in  range(0,len(images)): # horizontal image copy files with their file names
            hor_image_files = [ind for ind in os.listdir(namee) if ind.endswith(".jpg")]
            file_name_copy = 'C:/Users/your_path/horizontal/%s.jpg' % hor_image_files[im_index]
            cv2.imwrite(file_name_copy, images[im_index])
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        
        
     #*************************************************************************   
     # checking # of images for processing + image processing
     #*************************************************************************
    if number_of_images_for_each_vehicle >= 1:
        for ocr in range(0, number_of_images_for_each_vehicle):
            orig_img = images[ocr] 
            original_image = orig_img
            def keep(contour):
                first = contour[0][0] # first (x,y) coordinate of the contour
                last = contour[len(contour) - 1][0] # last (x,y) coordinate of the contour
                connected_contour = abs(first[0] - last[0]) <= 1 and abs(first[1] - last[1]) <= 1

                xx, yy, w_, h_ = cv2.boundingRect(contour)
                w_ *= 1.0
                h_ *= 1.0          
                # aspect ratio check
                asratio = 1
                if w_ / h_ < 0.1 or w_ / h_ > 10 or (w_ * h_) / (2 * (w_ + h_)) < 5 or (w_ * h_) / (2 * (w_ + h_)) > 20:
                    asratio = 0            
                # check size of the target object edge box --EB (w_*h_) that should be greater than 15 pixels
                # or smaller than 1/5th of the image dimension
                if ((w_ * h_) > ((img_x * img_y) / 5)) or ((w_ * h_) < 15):
                    asratio = 0
                return asratio and connected_contour
              
            #******************************************************************
            # target wide region (ROI) cropping for fast computing
            #******************************************************************
            x = 157
            y = 134
            w = 3162
            h = 1839
            cropped_orig_img = orig_img[y:y+h, x:x+w]
            # Add a border to the image for processing sake
            img = cv2.copyMakeBorder(cropped_orig_img, 10, 10, 10, 10, cv2.BORDER_CONSTANT)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            #img = cropped_orig_img.copy()
            # Calculate the width and height of the image
            img_y = len(img)
            img_x = len(img[0])
            
           
            
            #******************************************************************
            # adaptive [ canny ] edge detection for dynamically light changing
            #******************************************************************
            median_value = np.median(img)

            lower = int(max(0, 0.77*median_value))
            upper = int(min(255, 1.33*median_value))
            
            edges = cv2.Canny(img, lower, upper)
            # Split out each channel
#            blue, green, red = cv2.split(img)
            
            # Run canny edge detection on each channel
#            blue_edges = cv2.Canny(blue, 100, 100)
#            green_edges = cv2.Canny(green, 100, 100)
#            red_edges = cv2.Canny(red, 100, 100)
            
            # Join edges back into image
#            edges = blue_edges | green_edges | red_edges
            

            
            #******************************************************************
            # finding contours of an edge detected image
            #im2, contours, hierarchy = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
            #******************************************************************
            im2, contours, hierarchy = cv2.findContours(edges.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
            hierarchy = hierarchy[0] #hierarchy for each contour 
            
            
            #******************************************************************
            # Contour Box selection
            #******************************************************************
            keepers = []
            my_contour_ = [] # test

            for index_, contour_ in enumerate(contours):                         
                x, y, w, h = cv2.boundingRect(contour_)
                if keep(contour_):
                    keepers.append([contour_, [x, y, w, h]])
            
            new_image = edges.copy()
            new_image.fill(255)
            boxes = []
            
            
            #******************************************************************
            # For each box, find the foreground and background intensities
            #******************************************************************
            for index_, (contour_, box) in enumerate(keepers):
                fg_int = 0.0
                for p in contour_:
                    fg_int += gray[p[0][1], p[0][0]]
            
                fg_int /= len(contour_)            
                x_, y_, width, height = box
                width_  = 1.0 * width  
                height_ = 1.0 * height 
                bg_int = \
                    [
                        # bottom left corner 3 pixels
                        gray[y_ - 1, x_ - 1],
                        gray[y_ - 1, x_],
                        gray[y_, x_ - 1],
            
                        # bottom right corner 3 pixels
                        gray[y_ + height + 1, x_ - 1],
                        gray[y_ + height, x_ - 1],
                        gray[y_ + height + 1, x_],
            
                        # top left corner 3 pixels
                        gray[y_ - 1, x_ + width+ 1],
                        gray[y_ - 1, x_ + width],
                        gray[y_, x_ + width + 1],
            
                        # top right corner 3 pixels
                        gray[y_ + height+ 1, x_ + width+ 1],
                        gray[y_ + height, x_ + width + 1],
                        gray[y_ + height + 1, x_ + width]
                        
            
                bg_int = np.median(bg_int)
                if fg_int >= bg_int:
                    fg = 255
                    bg = 0
                else:
                    fg = 0
                    bg = 255
            

            #******************************************************************
            # Postprocessing to eliminate non-character symbols 
            # [noise reduction]
            #******************************************************************
                if (width_ * height_) > 20 and (width_ * height_) < 1e4:
                     if (width_ / height_) > 0.1 and (width_ / height_) < 10.0:
                         if (width_ * height_) < ((img_x * img_y) / 1e1): 
                            for x in range(x_, x_ + width):
                                for y in range(y_, y_ + height):
                                    if y >= img_y or x >= img_x:
                                        continue
                                    if gray[y][x] > fg_int:
                                        new_image[y][x] = bg
                                    else:
                                        new_image[y][x] = fg
    
            full_view = new_image.copy()

            full_view = cv2.blur(full_view, (1, 1))

            #******************************************************************
            # Template Matching [Object Detection'Con]
            # Vertical container text detection
            # Normalized Cross Correlation - similarity measurement
            #******************************************************************
            dilated_vertical_template = \
            cv2.imread('C:/Users/your_path/results/vertical_template1.jpg',0)
            h, w = np.array(dilated_vertical_template).shape[:2]
            img2_hor = new_image.copy()
            kernel     = cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5))
            dilated_img      = cv2.erode(img2_hor, kernel, iterations = 12)
            res = cv2.matchTemplate(dilated_img, dilated_vertical_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            top_left = max_loc
            bottom_right = min_loc
            final_vertical_cropped_image = new_image[top_left[1]-round(0.32*top_left[1]):top_left[1]+h+round(2.0*top_left[1]), top_left[0]-10:top_left[0]+w+50]
            row, col = np.array(final_vertical_cropped_image).shape
            if (row * col) > 0:
                final_vertical_cropped_image = cv2.dilate(final_vertical_cropped_image, kernel, iterations = 1)
                final_vertical_cropped_image = cv2.erode(final_vertical_cropped_image, kernel, iterations = 1)
                cv2.imwrite('C:/Users/your_path/results/cropped/ocr_vertical.jpg',final_vertical_cropped_image)
            
 
            #******************************************************************
            # Template Matching [Object Detection'Con]
            # Horizontal container text detection
            # Normalized Cross Correlation - similarity measurement
            #******************************************************************
            dilated_horizontal_template = \
            cv2.imread('C:/Users/your_path/results/horizontal_template.jpg',0)
            h_hor, w_hor = np.array(dilated_horizontal_template).shape[:2]
            img_hor = new_image.copy()
            kernel     = cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5))
            dilated_img_hor      = cv2.erode(img_hor, kernel, iterations = 12)
            res_hor = cv2.matchTemplate(dilated_img_hor, dilated_horizontal_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc_hor, max_loc_hor = cv2.minMaxLoc(res_hor)
            top_left_hor = max_loc_hor
            bottom_right_hor = min_loc_hor
            final_horizontal_cropped_image = new_image[top_left_hor[1]:top_left_hor[1]+h_hor, top_left_hor[0]-100:top_left_hor[0]+w_hor+50]
            row, col = np.array(final_horizontal_cropped_image).shape
            if (row * col) > 0:
                final_horizontal_cropped_image = cv2.dilate(final_horizontal_cropped_image, kernel, iterations = 1)
                final_horizontal_cropped_image = cv2.erode(final_horizontal_cropped_image, kernel, iterations = 1)
                cv2.imwrite('C:/Users/your_path/results/cropped/ocr_horizontal.jpg',final_horizontal_cropped_image)
           
            
            #******************************************************************
            # Template Matching [Object Detection'Con]
            # Double Horizontal container text detection
            # Normalized Cross Correlation - similarity measurement
            #******************************************************************
            dilated_double_horizontal_template = \
            cv2.imread('C:/Users/your_path/results/double_row.jpg',0)
            d_h_hor, d_w_hor = np.array(dilated_double_horizontal_template).shape[:2]
            img_double_hor = new_image.copy()
            kernel     = cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5))
            dilated_img_double_hor      = cv2.erode(img_double_hor, kernel, iterations = 5)
            res_double_hor = cv2.matchTemplate(dilated_img_double_hor, dilated_double_horizontal_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc_double_hor, max_loc_double_hor = cv2.minMaxLoc(res_double_hor)
            top_left_double_hor = max_loc_double_hor
            bottom_right_double_hor = min_loc_double_hor
            final_double_horizontal_cropped_image = new_image[top_left_double_hor[1]:top_left_double_hor[1]+d_h_hor, top_left_double_hor[0]-100:top_left_double_hor[0]+d_w_hor+50]
            row, col = np.array(final_double_horizontal_cropped_image).shape
            if (row * col) > 0:
                final_horizontal_cropped_image = cv2.dilate(final_double_horizontal_cropped_image, kernel, iterations = 1)
                final_horizontal_cropped_image = cv2.erode(final_double_horizontal_cropped_image, kernel, iterations = 1)
                cv2.imwrite('C:/Users/your_path/results/cropped/ocr_double_horizontal.jpg',final_double_horizontal_cropped_image)
            

            
            #******************************************************************
            # Template Matching [Object Detection'Con] 
            # Optimized Vertical container text detection
            # Normalized Cross Correlation - similarity measurement
            #******************************************************************
            
            dilated_optimized_vertical_template = \
            cv2.imread('C:/Users/your_path/results/ver_optimized.jpg',0)
            d_h_ver, opt_w_ver = np.array(dilated_optimized_vertical_template).shape[:2]
            img_optimized_ver = new_image.copy()
            kernel     = cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5))
            dilated_img_optimized_ver      = cv2.erode(img_optimized_ver, kernel, iterations = 5)
            res_optimized_ver = cv2.matchTemplate(dilated_img_optimized_ver, dilated_optimized_vertical_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc_optimized_ver, max_loc_optimized_ver = cv2.minMaxLoc(res_optimized_ver)
            top_left_optimized_ver = max_loc_optimized_ver
            bottom_right_optimized_ver = min_loc_optimized_ver
            final_optimized_vertical_cropped_image = new_image[top_left_optimized_ver[1]-50:top_left_optimized_ver[1]+d_h_ver, top_left_optimized_ver[0]:top_left_optimized_ver[0]+opt_w_ver]
            row, col = np.array(final_optimized_vertical_cropped_image).shape
            if (row * col) > 0:
                final_optimized_vertical_cropped_image = cv2.dilate(final_optimized_vertical_cropped_image, kernel, iterations = 1)
                final_optimized_vertical_cropped_image = cv2.erode(final_optimized_vertical_cropped_image, kernel, iterations = 1)
                cv2.imwrite('C:/Users/your_path/cropped/ocr_optimized_vertical.jpg',final_optimized_vertical_cropped_image)
                
                
                
            #******************************************************************
            # writing outputs into windows file
            #******************************************************************
            cv2.imwrite("C:/Users/your_ftp_server_path/results/ocredge.jpg", edges)
            cv2.imwrite("C:/Users/your_ftp_server_path/results/ocrfullview.jpg", full_view)
            cv2.imwrite('C:/Users/your_ftp_server_path/results/original_image.jpg', cropped_orig_img)
            cv2.imwrite("C:/Users/your_ftp_server_path/results/dilated_image.jpg", dilated_img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
                         
            
            #******************************************************************
            # extract and format the container ID 
            #******************************************************************
            def extract_horizontal_container_id(text):
                my_result = str(text)
                arr = [] 	
                for index in range(len(my_result)):
                    arr.append(my_result[index])
                    if my_result[index] == '\n':
                        break
                    else:
                        pass
                return arr
            
  
            
            #******************************************************************
            #control the check digit number for container ID
            #******************************************************************
            def check_digit_control(container_id):
                container_id = container_id[:10]
                first_ten_digit = [1,2,4,8,16,32,64,128,256,512]
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
                value = int(result/11)
                value1 = value * 11
                check_digit = result - value1
                if check_digit == 10:
                    check_digit = check_digit % 2
                container_id = (str(container_id[:10]) + str(check_digit))
                return container_id
            

            
            #******************************************************************
            # owner code of an ID checking -- e.x. [XXXX]1234567 
            #******************************************************************
            def owner_code_check(digit):
                os.chdir(namee)
                my_file = openpyxl.load_workbook("owner code full.xlsx")
                code_list = my_file.get_sheet_by_name("Sayfa1")
                sheet = my_file.worksheets[0]
                row_count = sheet.max_row 
                for i in range(0,row_count):
                    if digit[:4] == code_list['A' + str(i+1)].value:
                        code = True
                        break
                    else:
                        code = False
                return code
            
            
            
            
            #******************************************************************
            # main driver and getting ocr results
            #******************************************************************
            if __name__=='__main__':
                
                #**************************************************************
                # binary auto-cropped image array
                #**************************************************************
                file_path_ocr_cropped_horizontal = 'C:/Users/your_path/results/cropped/ocr_horizontal.jpg'
                im_horizontal = Image.open(file_path_ocr_cropped_horizontal)
                
                file_path_ocr_cropped_vertical = 'C:/Users/your_path/results/cropped/ocr_vertical.jpg'
                im_vertical = Image.open(file_path_ocr_cropped_vertical)
                
                file_path_ocr_cropped_double_horizontal = 'C:/Users/your_path/results/cropped/ocr_double_horizontal.jpg'
                im_double_horizontal = Image.open(file_path_ocr_cropped_double_horizontal)
                
                file_path_ocr_optimized_vertical = 'C:/Users/your_path/results/cropped/ocr_optimized_vertical.jpg'
                im_optimized_vertical = Image.open(file_path_ocr_optimized_vertical)
                
                im = [im_vertical, im_horizontal, im_double_horizontal, im_optimized_vertical]
                for i in range(0, len(im)):
                    
                    result = pytesseract.image_to_string(im[i])
                   
                    #**********************************************************
                    # check for horizontal ID
                    #**********************************************************
                    if len(str(result)) < 25: 
                        result = ''.join(i for i in result if i.isalnum())
                        container_id =  extract_horizontal_container_id(result)
                        check_letters = list(container_id)
                        for indexx,char in enumerate(check_letters[:4]):
                            if char.isalpha() == False:
                                if check_letters[indexx] == '6':
                                    check_letters[indexx] = 'G'
                                elif check_letters[indexx] == '[' or check_letters[indexx] == '(':
                                    check_letters[indexx] = 'C'
                                elif check_letters[indexx]== '5':
                                    check_letters[indexx] = 'S'
                                elif check_letters[indexx]  == '2':
                                    check_letters[indexx] = 'Z'
                                elif check_letters[indexx] == '1':
                                    check_letters[indexx] = 'I'
                                elif check_letters[indexx] == '0':
                                    check_letters[indexx] = 'O'
                            else:
                                pass
                        for index, char in enumerate(check_letters[4:]):
                            if char.isalpha() == True: # is it integer?
                                if check_letters[index+4] == 'Z' or check_letters[index] == 'z':
                                    check_letters[index+4] = '2'
                                elif check_letters[index+4] == 'O' or check_letters[index] == 'I]' or check_letters[index] == 'I}':
                                    check_letters[index+4] = '0'
                                elif check_letters[index+4] == 'I':
                                    check_letters[index+4] = '1'
                                elif check_letters[index+4] == 'S':
                                    check_letters[index+4] = '5'
                                else:
                                    pass
                        container_id = ''.join(i for i in check_letters if i.isalnum())    
                        container_id = container_id[:11]
                    else: # otherwise check the vertical ID
                        container_id = result.split()
                        container_id = ''.join(i for i in result if i.isalnum())
                        container_id = ''.join(i for i in container_id if not i.islower())
                        #check for the first four letters in container ID
                        check_letters = list(container_id)
                        for indexx,char in enumerate(check_letters[:4]): #first four # of conrainer ID
                            if char.isalpha() == False:
                                if check_letters[indexx] == '6':
                                    check_letters[indexx] = 'G'
                                elif check_letters[indexx] == '[' or check_letters[indexx] == '(':
                                    check_letters[indexx] = 'C'
                                elif check_letters[indexx] == '5':
                                    check_letters[indexx] = 'S'
                                elif check_letters[indexx] == '2':
                                    check_letters[indexx] = 'Z'
                                elif check_letters[indexx] == '1':
                                    check_letters[indexx] = 'I'
                                elif check_letters[indexx] == '0':
                                    check_letters[indexx] = 'O'
                            else:
                                pass
                        for index, char in enumerate(check_letters[4:]):
                            if char.isalpha() == True: # is it integer?
                                if check_letters[index+4] == 'Z' or check_letters[index] == 'z':
                                    check_letters[index+4] = '2'
                                elif check_letters[index+4] == 'O' or check_letters[index] == 'I]' or check_letters[index] == 'I}':
                                    check_letters[index+4] = '0'
                                elif check_letters[index+4] == 'I':
                                    check_letters[index+4] = '1'
                                elif check_letters[index+4] == 'S':
                                    check_letters[index+4] = '5'
                                else:
                                    pass
                        check_letters = ''.join(i for i in check_letters if i.isalnum())
                        check_last_six_digits = ''.join(j for j in check_letters[4:] if j.isdigit())
                        container_id = check_letters[:4] + check_last_six_digits
                    #The method isalnum() checks whether the string 
                    #          consists of alphanumeric characters.
                    container_id = ''.join(i for i in container_id if i.isalnum())
                    container_id = container_id[:11]
                    print ("******************************************") 
                    print ("Container ID is : %s" % container_id)
                    if len(container_id) == 11:
                        print ("Check Digit number is : %s" % container_id[len(container_id)-1])
                    else:
                        pass
                    
                    ocr_list.append(container_id)
    else:
        
        
        
        #**********************************************************************
        # if not the # of images for each vehicle is greter or equal to 1.
        # check the fault detection. if exist, then save into pc. 
        #**********************************************************************
        pathname = "ftp_server_path" 
        filelist = [f for f in os.listdir(pathname) if f.endswith(".jpg") and os.path.getsize(f) >= 0]
        for j in filelist:
            full_path = os.path.join(pathname,j)
            f = open(full_path)
            f.close()
            try:
                os.remove(full_path)
            except OSError as e:
                error_path = "your_error_log_path"
                os.chdir(error_path)
                with open("ERROR_LOG.txt", "a") as error:
                    error.write("%s\nError Info : %s\nError capturing Time : %s\n" % (error_count, e, datetime.datetime.now()))
                    error.write("----------------------****************************-------------------\n")
                    error_count += 1
                print("Error : %s" % (e.strerror))
                logging.error(traceback.format_exc())
                pass
    pathname = "C:/Users/ftp_server_path/"
    
    
    
    #**************************************************************************
    # check images in  the directory if any image exist or not.
    #**************************************************************************
    if len(os.listdir(pathname)) > 2:
        try:
            
            #******************************************************************
            # Oracle DB Connection
            #******************************************************************
#            dsn  = cx.makedsn("host","port","service ID")
#            conn = cx.connect(user="xxx", password="nnn",dsn=dsn)
#            cursor =conn.cursor()
            
            
            #******************************************************************
            # SQL Server DB Connection with pyodbc
            #******************************************************************
#            conn = pyodbc.connect(r'DSN=mynewdsn;UID=user;PWD=password') or
#            conn = pyodbc.connect(
#                    r'DSN=mynewdsn;'
#                    r'UID=user;'
#                    r'PWD=password;'
#                    r'APP=Daily Incremental Backup;'
#                    )
#            cursor =conn.cursor()
#            import pyodbc
            conn = pyodbc.connect('DRIVER={SQL Server};SERVER=192.168.45.67;DATABASE=db_name;UID=cam;PWD=cam111')
            cursor = conn.cursor()
#            cursor.execute("SELECT WORK_ORDER.TYPE,WORK_ORDER.STATUS, WORK_ORDER.BASE_ID, WORK_ORDER.LOT_ID FROM WORK_ORDER")
#            for row in cursor.fetchall():
#                print row
            #******************************************************************
            # Regular expression for ISO standard of container numbers
            #******************************************************************
            iso6346 = re.compile(r'^\w{3}(U|J|Z|R)\d{7}$')
            
            
            if len(ocr_list) >= 1:
                for k in range(len(ocr_list)):
#                    statement = 'select * from item where substr(item_code,1,10) = :id'
#                    id_check  = cursor.execute(statement, {'id':ocr_list[k][:10]})
#                    db_check_result = cursor.fetchall()
                    
                    
                    
                    #**********************************************************
                    # The conditions for ocr results in order to write into DB.
                    #**********************************************************
                    if len(ocr_list[k]) >= 10 and \
                    ocr_list[k].isupper() == True and \
                    ocr_list[k][4:].isdigit() == True and \
                    ocr_list[k][:4].isalpha() == True:# and len(db_check_result) == 1:
                        digit_controlled_ID = check_digit_control(ocr_list[k])
                        code_check = owner_code_check(digit_controlled_ID)
                        if iso6346.match(digit_controlled_ID) and len(digit_controlled_ID) == 11 and code_check:
                            stop_time = time.time()
                            total_execution_time_for_each_vehicle = stop_time - start_time
                            print("Total execution time : %d sn" % total_execution_time_for_each_vehicle)
                            my_log_control.append((digit_controlled_ID, datetime.datetime.now()))
                            camera_id = cursor.execute("select CAMERA_ID from OCR_CAMERA where CAMERA_IP = '192.168.0.199'")
                            for id in camera_id:
                                camera_ID = id
                            cursor.execute("insert into OCR_LOG(ITEM_CODE, RECORD_DATE, \
                                            FILE_PATH, FILE_NAME, CAMERA_ID, STATE) values(?, ?, ?, ?, ?, ?)",\
                                (digit_controlled_ID, datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"),\
                                 directory_name, filename_for_database, camera_ID[0],1))
                            
                            conn.commit()
                            cursor.close()
                            conn.close()
                            log_path = "your_ocr_detected_log_path"
                            os.chdir(log_path)
                            with open("OCR_LOG.txt", "a") as file:
                                file.write("%s\nContainer ID : %s\nRecognition Time : %s\n" % (log_count, digit_controlled_ID, datetime.datetime.now()))
                                file.write("----------------------****************************-------------------\n")
                                log_count += 1
                            break
                        else:
                            continue 
#        error_path = "your_path"
#        os.chdir(error_path)
#        with open("ERROR_LOG.txt", "a") as error:
#            error.write("%s\nError Info : %s\nError capturing Time : %s\n" % (error_count, e, datetime.datetime.now()))
#            error.write("----------------------****************************-------------------\n")
#            error_count += 1
        except Exception as e:
            error_path = "your_error_log_path"
            os.chdir(error_path)
            with open("ERROR_LOG.txt", "a") as error:
                error.write("%s\nError Info : %s\nError capturing Time : %s\n" % (error_count, e, datetime.datetime.now()))
                error.write("----------------------****************************-------------------\n")
                error_count += 1
#            logging.error(traceback.format_exc())
            pass
    else:
        #**********************************************************************
        # if not os.listdir(pathname) greater than 2.
        #**********************************************************************
        pass

    path_name_for_ocr_cropped_images = 'C:/Users/your_path/'
    path_name = 'C:/Users/your_path/'
    os.chdir(path_name)
    filelistx = [f for f in os.listdir(path_name) if f.endswith(".jpg") and os.path.getsize(f) >= 0]
    filelist_cropped = [f for f in os.listdir(path_name_for_ocr_cropped_images)]
    
    
    
    #**************************************************************************
    # remove jpg files from path_name & check fault detection
    #**************************************************************************
    for qq in filelistx:
        filepath = os.path.join(path_name, qq)
        try:
            os.remove(filepath)
        except Exception as e:
            with open("ERROR_LOG.txt", "a") as error:
                error.write("%s\nError Info : %s\nError capturing Time : %s\n" %(error_count, e, datetime.datetime.now()))
                error.write("----------------------****************************-------------------\n")
                error_count += 1
            print("Error : %s" % (e.strerror))
            logging.error(traceback.format_exc())
            pass
        
        
        
    #**************************************************************************
    # remove jpg files from path_name_for_ocr_cropped_images 
    # [dummy horizontal file] for checking the read/write procedure.
    # check fault detection
    #**************************************************************************
    for q in filelist_cropped:
        filepath1 = os.path.join(path_name_for_ocr_cropped_images, q)
        try:
            os.remove(filepath1)
        except Exception as e:
            error_path = "your_error_log_path"
            os.chdir(error_path)
            with open("ERROR_LOG.txt", "a") as error:
                error.write("%s\nError Info : %s\nError capturing Time : %s\n" % (error_count, e, datetime.datetime.now()))
                error.write("----------------------****************************-------------------\n")
                error_count += 1
            print("Error : %s" % (e.strerror))
            logging.error(traceback.format_exc())
            pass
    print("Done")
    print("------------------------------------------------------")
    time.sleep(10)        
    
