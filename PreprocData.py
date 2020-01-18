import cv2, os, time
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

from tensorflow.keras.models import Model, Sequential, load_model
from tensorflow.keras.layers import MaxPooling2D, Conv2D,  Input, Conv2DTranspose, concatenate, SpatialDropout1D, Conv1D
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization, Embedding, Flatten, Activation, Reshape, MaxPooling1D
from tensorflow.keras.layers import LSTM, GRU, SimpleRNN, CuDNNLSTM, CuDNNGRU, Bidirectional, SeparableConv1D, GlobalAveragePooling1D, GlobalAveragePooling2D

from tensorflow.keras.callbacks import ModelCheckpoint

from tensorflow.keras.optimizers import Adam, RMSprop

from tensorflow.keras.losses import CosineSimilarity

from tensorflow.keras import backend as K

from tensorflow.keras import utils

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
      slice_arr = slice_
      temp = temp[:slice_arr]
    else:      
      slice_arr = temp.shape[0]    
    X_Train.extend(temp)    
    y_Train.extend([class_ for c in range(slice_arr)])   
  X_Train = np.array(X_Train) / 255
  y_Train = np.array(y_Train) 
  return  X_Train, y_Train

def getConfMatrix(model, X_Test, y_Test, num_pics_test):

  data = {'y_Actual':    y_Test,
          'y_Predicted': [ p.argmax() for p in model.predict(X_Test) ]
          }

  df = pd.DataFrame(data, columns=['y_Actual','y_Predicted'])

  confusion_matrix = pd.crosstab(df['y_Actual'], 
                                 df['y_Predicted'], 
                                 rownames=['Actual'], 
                                 colnames=['Predicted'], 
                                 margins = True)

  for row, countInClass in enumerate(num_pics_test):
    confusion_matrix.loc[row] = (confusion_matrix.loc[row]*100)/countInClass
    confusion_matrix.loc[row] = np.around(confusion_matrix.loc[row], 1)

  return confusion_matrix