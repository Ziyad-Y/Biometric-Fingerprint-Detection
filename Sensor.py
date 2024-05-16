import time 
import adafruit_fingerprint 
import serial   
from PIL import Image,ImageOps 
import uuid

#Initialized


def enroll_fingerprint(image_num, ID ):
    try:   
        uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1,)
        finger=adafruit_fingerprint.Adafruit_Fingerprint(uart=uart) 
            #empty the fingerpirnt library to make sure there are no fingerprints active.
        if finger.check_module:
            print("sensor is working")
            print("Begining Fingerprint Enrollment")
            print(f"We will be collecting {image_num} Images of Fingerprint")
            time.sleep(3)
            count=0 
            while count<image_num:          
                #empty the sensor if any fingerprint remain  
                finger.empty_library() 
                print("\n PLACE YOUR FINGER ON SENSOR\n") 
                print("Wait until you see message \" IMAGE CAPTURED \" before removing finger ") 
                time.sleep(3)
                print("Begining Finger SCAN")
                time.sleep(3)
                while finger.get_image():
                    pass
                
                image=Image.new("L",(256,288),"white") 
                pixeldata=image.load() 
                mask=0x0F 
                result=finger.get_fpdata(sensorbuffer="image")  
                x = 0
                # pylint: disable=invalid-name
                y = 0
                # pylint: disable=consider-using-enumerate
                for i in range(len(result)):
                    pixeldata[x, y] = (int(result[i]) >> 4) * 17
                    x += 1
                    pixeldata[x, y] = (int(result[i]) & mask) * 17
                    if x == 255:
                        x = 0
                        y += 1
                    else:
                        x += 1  
                #image=ImageOps.flip(image)
                if not image.save(f"Database/{ID}/Images/{ID}_{count+1}.tif"):
                    print(f"IMAGE CAPTURED")
                    count+=1 
                    time.sleep(3)

                    continue
                else:
                    print("Failed to Save image")
                    exit(1)

        else:
            print("Error: Module Not Found")
            exit(1) 
        uart.close()  
      
    except Exception as e:
        print("Error %s"%(str(e)))   
        exit(1)

def scan():
    try:   
        uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1,)
        finger=adafruit_fingerprint.Adafruit_Fingerprint(uart=uart)  
        #empty the fingerpirnt library to make sure there are no fingerprints active.
        if finger.check_module:
            print("sensor is working")  
            #empty the sensor if any fingerprint remain  
            finger.empty_library() 
            print("\n PLACE YOUR FINGER ON SENSOR\n") 
            print("Wait until you see message \" IMAGE CAPTURED \" before removing finger ") 
            time.sleep(2)
            print("Begining Finger SCAN")
            time.sleep(3)
            while finger.get_image():
                pass
            
            image=Image.new("L",(256,288),"white") 
            pixeldata=image.load() 
            mask=0x0F 
            result=finger.get_fpdata(sensorbuffer="image")  
            x = 0
            # pylint: disable=invalid-name
            y = 0
            # pylint: disable=consider-using-enumerate
            for i in range(len(result)):
                pixeldata[x, y] = (int(result[i]) >> 4) * 17
                x += 1
                pixeldata[x, y] = (int(result[i]) & mask) * 17
                if x == 255:
                    x = 0
                    y += 1
                else:
                    x += 1  
            #image=ImageOps.flip(image)
            if not image.save(f"Scan/Query.tif"):
                print("IMAGE CAPTURED") 
                uart.close()
                return True  
            return False

        else:
            print("Error: Module Not Found")
            exit(1)        

    except Exception as e:
        print("Error %s"%(str(e)))   
        exit(1)




    