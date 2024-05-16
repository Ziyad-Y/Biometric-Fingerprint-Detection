from Sensor import * 
from Fingerprint import *  
import json   
import os
DATABASE="Database"
def enrollement(ID): 
    print("Creating Database Entry")
    path=f"Database/{ID}" 
    os.mkdir(path)  
    os.mkdir(f"{path}/Images")  
    os.mkdir(f"{path}/Features") 
    os.mkdir(f"{path}/Features/L1")  
    os.mkdir(f"{path}/Features/L2")  
    print("Created DB") 
    time.sleep(2)
    enroll_fingerprint(image_num=6,ID=ID)   
       
    images=[f"{path}/Images/{image}" for image in os.listdir(f"{path}/Images")]
    for img in images:
        f=Fingerprint()
        f.extract_all_features(img,Save_Features=True, L1_Path=f"{path}/Features/L1", L2_Path=f"{path}/Features/L2" ) 
    return True

def calculate_score(Query,Template, termination_match,bifurcation_match):
    numerator=len(termination_match) + len(bifurcation_match)  
    Total_Q=len(Query) 
    Total_T=len(Template) 
    avg=((numerator/Total_Q) + (numerator/Total_T))/2 
    return avg


def Verification(ID,Threshold=0.70):
    if ID not in os.listdir("Database"):
        return None 
    print("Scanning Fingeprint")
    scan() 
    f=Fingerprint() 
    f.extract_all_features("Scan/Query.tif")  
    Query=f.Level_2_Features
    Total=len(Query) 
    
    DB_feats=f"Database/{ID}/Features/L2/" 
    scores=[]  
    for file in os.listdir(DB_feats):
        Template=np.load(f"{DB_feats}/{file}",allow_pickle=True)  
        bifur=Matching(Query,Template,"Bifurcation",Threshold_Distance=80)
        term=Matching(Query,Template,"Termination",Threshold_Distance=80)  
        scores.append((calculate_score(Query,Template,term,bifur),pathlib.Path(file).stem))    

    Highest=max(scores,key= lambda x : x[0])    
    if Highest[0] >= Threshold:
        return True     
    
    else:
        return False
    
def Identification(): 
    print("scanning finger")
    scan() 
    f=Fingerprint() 
    f.extract_all_features("Scan/Query.tif")  
    Query=f.Level_2_Features 
    scores=[]
    for Entry in os.listdir("Database"):
        temp=[]
        for file in os.listdir(f"Database/{Entry}/Features/L2/"):
            Template=np.load(f"Database/{Entry}/Features/L2/{file}",allow_pickle=True) 
            Total_T=len(Template)
            bifur=Matching(Query,Template,"Bifurcation",Threshold_Distance=80) 
            term=Matching(Query,Template,"Termination",Threshold_Distance=80) 
            avg=calculate_score(Query,Template,term,bifur)
            temp.append((avg,file))  
        scores.append(max(temp,key= lambda x:x[0])) 
    print(scores)
    identity=max(scores,key= lambda x: x[0])  
    if identity[0] >=0.70:
        ID=identity[1].split("_")[0]
        return ID 
    else:
        return None
    







