import os
import numpy as np
import pandas as pd

def newDataFrame():
  db = pd.DataFrame(columns=['Class', 'Arr'], dtype=np.int32)
  return db


def dataInputPreprocess(main_dirpatch, pic_in_dir = True, db = None):
  if not db:
    db = newDataFrame()
  try:    
    if pic_in_dir:                
      file_names = os.listdir(main_dirpatch)        
      flag = 0      
      run = 0.
      numClass = 0
      for index_for_db, file_name in enumerate(file_names):                              
        img_path = os.path.join(main_dirpatch, file_name)          
        img = Image.open(img_path)          
        if img.size[0] >= img.size[1]:
          img = img.transform((img.size[0],img.size[0]), Image.AFFINE,(1, 0, 0, 0, 1, 0), Image.BILINEAR)
        else:
          img = img.transform((img.size[1],img.size[1]), Image.AFFINE,(1, 0, 0, 0, 1, 0), Image.BILINEAR) 
        #делаем стандартизацию размеров
        img = img.transform((150,150), Image.AFFINE,(1, 0, 0, 0, 1, 0), Image.BILINEAR)                 
        img = img.convert('LA')          
        img2npArr = np.array(img)
        db.loc[index_for_db] = (numClass, img2npArr)        
        if run != (flag*100//len(file_names)):    
          run = (flag*100//len(file_names))        
          print(':', end='')                    
        flag += 1        
      print()
      print(main_dirpatch, 'Обработано элементов:', int(flag))               
      return db                
      
    else:      
      second_dirs_name = os.listdir(main_dirpatch) 
      index_for_db = 0  
      num_pics = []   
      for numClass, second_dir_name in enumerate(second_dirs_name):           
        second_dir_path = os.path.join(main_dirpatch, second_dir_name)      
        file_names = os.listdir(second_dir_path)  
        flag = 0
        run = 0        
        for file_name in file_names:                              
          img_path = os.path.join(second_dir_path, file_name)          
          img = Image.open(img_path)          
          if img.size[0] >= img.size[1]:
            img = img.transform((img.size[0],img.size[0]), Image.AFFINE,(1, 0, 0, 0, 1, 0), Image.BILINEAR)
          else:
            img = img.transform((img.size[1],img.size[1]), Image.AFFINE,(1, 0, 0, 0, 1, 0), Image.BILINEAR) 
          #делаем стандартизацию размеров
          img = img.transform((150,150), Image.AFFINE,(1, 0, 0, 0, 1, 0), Image.BILINEAR)                 
          img = img.convert('LA')          
          img2npArr = np.array(img)

          db.loc[index_for_db] = (numClass, img2npArr)
          index_for_db += 1

          if run != (flag*100//len(file_names)):    
            run = (flag*100//len(file_names))        
            print(':', end='')            
          flag += 1               
        print()
        print(second_dir_path, 'Обработано элементов:', int(flag))    
        num_pics.append(int(flag))      
      return num_pics, db                

  except:
    print('Ошибка. Введите корректный путь к папке с изображениями.')
    return None


def makeXYdata(db, slice_ = None):
  X_Train = []
  y_Train = []
  classes = db['Class'].unique() 
  for class_ in classes:
    temp = db['Arr'] [db['Class'] == class_].values
    np.random.shuffle(temp)
    if slice_:
      temp = temp[:slice_]
    else:      
      slice_ = temp.shape[0]
    X_Train.extend(temp)
    y_Train.extend([i for c in range(slice_)])      
  X_Train = np.array(X_Train) / 255
  y_Train = np.array(y_Train) 
  return  X_Train, y_Train
