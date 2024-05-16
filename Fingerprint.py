import typing  
import cv2 
import numpy as np
import fingerprint_feature_extractor 
import fingerprint_enhancer
import time 
import pathlib
import statistics 
import math


class Minutiae (object):
    def __init__(self, Type : str, locX : int , locY : int, Orientation : float ) -> None:
        
        self.Type=Type
        self.locX=locX  
        self.locY=locY   
        self.Orientation=Orientation



class Fingerprint(object):
    def __init__(self) ->None :
        self.Level_1_Features: typing.List[Minutiae]=[]                 #Loops.Deltas,Whorls
        self.Level_2_Features : typing.List[fingerprint_feature_extractor.MinutiaeFeature]=[] #Terminations.Bifurcations
        



         

   #This function takes a shifted dft and returns a vector of the max magnitude
    def get_uv(self,dft):
        dft[15,15]=[0,0]
        max_maginitude=max([max(d,key=lambda x:np.sqrt(x[0]**2+x[1]**2)) for d in dft],key= lambda x: np.sqrt(x[0]**2+x[1]**2)) 
        for i in range(len(dft)):
            for j in range(len(dft[i])):  
                if dft[i,j][0]==max_maginitude[0] and dft[i,j][1]==max_maginitude[1]:
                    return 15-i,15-j  
      
    
    #read an image and obtain orienatation data from it 
    def obtain_orientation(self,image_path : str):
        img=cv2.imread(image_path,cv2.IMREAD_GRAYSCALE)  
        orienation_mat=np.full(img.shape, 300, dtype=float) #matrix used to store all angles 
        mean=cv2.mean(img)
        gaussian_window = np . zeros ((31 ,31))
        gaussian_window [15 , 15] = 1
        gaussian_window = cv2 . GaussianBlur (gaussian_window , (31 , 31) , 10 ,borderType = cv2 . BORDER_CONSTANT)
        gaussian_window = gaussian_window / np .max( gaussian_window )
        for y in range(0,img.shape[0],10): 
            for x in range(0,img.shape[1],10):
    
                #slice the image   
                y1,y2=y, min(y+31,img.shape[0])   
                x1,x2=x,min(x+31,img.shape[1])  
                portion=img[y1:y2,x1:x2] 
                portion=np.float32(portion)
                if portion.shape[:2]==(31,31):
                    #perform fourier transform  
                    reduced=(portion-mean[0])*gaussian_window 
                    fourier=cv2.dft(reduced,flags=cv2.DFT_COMPLEX_OUTPUT)  
                    fourier=np.fft.fftshift(fourier)   
                    #get vector and calculate the angle at that point
                    u,v=self.get_uv(fourier)
                    angle=np.arctan2(v,u) 
                    orienation_mat[y1,x1]=angle
    
        cv2.destroyAllWindows()
    
        return orienation_mat    
    
    
    
    
    #check if find silgularity is possible.
    # For the pointcare index Formula to work a point must have possbile neighbors 
    
    def check_possible_neighbors(self,x:int,y:int,img): 
        neighbors=[(x,y+10),(x,y-10),(x-10,y),(x+10,y), (x-10,y+10),(x+10,y+10),(x-10,y-10),(x+10,y-10)]  
        for points in neighbors:
            if 0<points[0]<=img.shape[1] and 0<points[1]<=img.shape[0] :
                continue
        
    
            else:
                return False  
    
        return True   
    
    #compute delta 
    # Delta is needed so that the point care fomula returns resonable values. Look at the point care formula
    def delta_f(self,angle):
        if angle > np.pi/2:
            return angle-np.pi   
        elif -np.pi/2 <= angle <= np.pi/2:
            return angle 
        elif angle < -np.pi/2:
            return angle + np.pi
    
    
    #compute the pointcare index 
    def calculate_pointcare(self,image_path : str):
        orientations=self.obtain_orientation(image_path) 
        pointcare_indices=[]
    
        for y in range(orientations.shape[0]):
            for x in range(orientations.shape[1]):
                if orientations[y,x] !=300:
                    if self.check_possible_neighbors(x,y,orientations):
                        neighbors=[(x,y+10),(x,y-10),(x-10,y),(x+10,y), (x-10,y+10),(x+10,y+10),(x-10,y-10),(x+10,y-10)] 
                        angles=[orientations[p[1],p[0]] for p in neighbors] 
                        if 300 not in angles:  
                            PI=0  
                            for i in range(8):
                                theta_difference=angles[(i+1)%8] - angles[i]  
                                PI+=self.delta_f(theta_difference) 
                            PI/=np.pi
                            pointcare_indices.append([(x,y),PI]) 
        return pointcare_indices   

 
    #Saves all Level 1 Minutiae
    def save_level1(self,image_path:str):
        #Reference Orientatio Field  
        
        ROL= lambda x,y: (1/2)*np.arctan2(x,y) 
        ROD= lambda x,y: -(1/2)*np.arctan2(x,y)  
        pointcare_indices=self.calculate_pointcare(image_path)
        for data in pointcare_indices:
            if data[1] == 1: 
                self.Level_1_Features.append(Minutiae("Loop",data[0][0],data[0][1],ROL(data[0][0],data[0][1])))   
            elif data[1] == -1: 
                self.Level_1_Features.append(Minutiae("Delta",data[0][0],data[0][1],ROD(data[0][0],data[0][1])))  
            elif data[1] == 2:
                self.Level_1_Features.append(Minutiae("Whorl",data[0][0],data[0][1],0))   
     
    #saves all Level 2 Minutiae
    def save_level2(self,image_path :str): 
        img=cv2.imread(image_path,0)
        img=fingerprint_enhancer.enhance_Fingerprint(img)
        Terminations, Bifurcations=fingerprint_feature_extractor.extract_minutiae_features(img,spuriousMinutiaeThresh=10,invertImage=False,showResult=False,saveResult=False)   
        self.Level_2_Features=Terminations+Bifurcations
        


    def extract_all_features(self,image_path:str,Save_Features=False, L1_Path=".", L2_Path="." ):
        self.save_level1(image_path) 
        self.save_level2(image_path)
        if Save_Features==True:
            np.save(f"{L1_Path}/{pathlib.Path(image_path).stem}.npy",self.Level_1_Features,allow_pickle=True) 
            np.save(f"{L2_Path}/{pathlib.Path(image_path).stem}.npy",self.Level_2_Features,allow_pickle=True)
            





def Hough_Transform(Query,Template,Type:str):     #seperating feature into bibfurcations and terminations
    template=[feat for feat in Query if feat.Type==Type] 
    query=[feature for feature in Template if feature.Type==Type]   

     
    if Type=="Termination":
        transform_list=[]
    
        for T in template:
            for Q in query:
                d_theta=math.ceil(T.Orientation[0]-Q.Orientation[0]) 
                dx=math.ceil(T.locX-(Q.locX* np.cos(d_theta*(np.pi/180))) - (Q.locY*np.sin(d_theta*(np.pi/180)))  )
                dy=math.ceil(T.locY+(Q.locX* np.sin(d_theta*(np.pi/180))) - (Q.locY*np.cos(d_theta*(np.pi/180))))  
                transform_list.append((dx,dy,d_theta))  

        return statistics.mode(transform_list)  
    
    elif Type =="Bifurcation":
        transform_list=[] 
        
        for T in template:
            for Q in query:
                d_theta=math.ceil(T.Orientation[0]-Q.Orientation[0])   
                dx=math.ceil(T.locX-(Q.locX* np.cos(d_theta*(np.pi/180))) - (Q.locY*np.sin(d_theta*(np.pi/180))))  
                dy=math.ceil(T.locY+(Q.locX* np.sin(d_theta*(np.pi/180))) - (Q.locY*np.cos(d_theta*(np.pi/180))) )     
                transform_list.append((dx,dy,d_theta))  

        return statistics.mode(transform_list)  
        
                  

def Translate_Rotate(dx,dy,dtheta,x,y):
    theta=dtheta*(np.pi/180)
    #TRanslation and Rotation
    Trasform_matrix=np.array([ 
                            
                            [np.cos(theta),-np.sin(theta),dx],  
                            [np.sin(theta),np.cos(theta),dy], 
                            [0,0,1] 
                              ])        
    position=np.array([ [x],[y],[1] ])    
    result=Trasform_matrix@position    # multiply both matrices  
    return result[0][0],result[1][0]        





def Matching(Query,Template,Type:str, Threshold_Distance =70.0, Threshold_Rotation=45.0 ): #type in this case will be type of feature     
    #seperating feature into bibfurcations and terminations 
    Q=[feat for feat in Query if feat.Type==Type]   
    T= [feat for feat in Template if feat.Type==Type]
    count=0 
    paired=[]
    
    if Type=="Termination":
        dx,dy,dtheta=Hough_Transform(Query,Template,Type)  
    
         
        



        f_T=[0] * len(T)  
        f_Q=[0] * len(Q) 
        for i in range(len(T)):
            for j in range(len(Q)):

                x,y=Translate_Rotate(dx,dy,dtheta,Q[j].locX,Q[j].locY)   
                x2,y2=Translate_Rotate(dx,dy,dtheta,T[i].locX,T[i].locY)   
                distance_between=np.sqrt((x2-x)**2 +(y2-y)**2 ) 
                rotation_between=abs(T[i].Orientation[0] - Q[j].Orientation[0])  
                if f_T[i]==0 and f_Q[j]==0 and distance_between < Threshold_Distance and rotation_between < Threshold_Rotation:
                    f_T[i]=1 
                    f_Q[j]=1 
                    count+=1  
                    paired.append((i,j))    
    
    elif Type =="Bifurcation": 
        dx,dy,dtheta=Hough_Transform(Query,Template,Type)    
          
        
        f_T=[0] * len(T)  
        f_Q=[0] * len(Q) 
        for i in range(len(T)):
            for j in range(len(Q)):

                x,y=Translate_Rotate(dx,dy,dtheta,Q[j].locX,Q[j].locY)
                x2,y2=Translate_Rotate(dx,dy,dtheta,T[i].locX,T[i].locY)   
                distance_between=np.sqrt((x2-x)**2 +(y2-y)**2 )  
                rotation_between=abs(T[i].Orientation[0] - Q[j].Orientation[0]) 
               

                if f_T[i]==0 and f_Q[j]==0 and distance_between < Threshold_Distance and rotation_between < Threshold_Rotation :
                    f_T[i]=1 
                    f_Q[j]=1 
                    count+=1  
                    paired.append((i,j))  
        
    


    return paired

#Did not use. ELiminate level1 duplicates
def eliminate_duplicates(level_1_feature : np.array,Type:str):
    data=[(feature.locX,feature.locY) for feature in level_1_feature if feature.Type==Type]

    data
    for cords in data:
        x=cords[0]
        y=cords[1] 
        neighbors=[(x,y+10),(x,y-10),(x-10,y),(x+10,y), (x-10,y+10),(x+10,y+10),(x-10,y-10),(x+10,y-10)]
        for n in neighbors:
            if n in data:
                data.remove(n)   

    return data   
    

