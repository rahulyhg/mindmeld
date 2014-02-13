'''
Classifier that tries to predict celebrity MBTI letter from
astrological parameters. Utilizes leave-one-out approach to test
results. One data point is left out of training whose data is used for
prediction, and verification.

SVD->SVM approach is used to predict.
'''
import scipy.sparse.linalg as slin
import scipy.sparse as sps
import numpy.linalg as lin
import pandas as pd
import sklearn as sk
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn import svm
import random

# rbf, k=1, 59,60

# sigmoid k==1, 56
# sigmoid k==10, 60,55
# rbf k==10, 59,54

def train(df_arg,letter,leave_out=None):
   #clf = svm.SVC(kernel='sigmoid')
   clf = RandomForestClassifier()
   k = 1
   X = df_arg.copy()
   X = X.fillna(0)
   y = df_arg[letter]*1
   testrow = testres = None
   if leave_out: 
      testrow = X.ix[leave_out]
      testres = X.ix[leave_out][letter]
      X = X.drop(leave_out)
      y = y.drop(leave_out)
   X = X.drop(cols,axis=1)
   try:
      Xs = sps.coo_matrix(X)
      U,Sigma,V=slin.svds(Xs,k=k)
      Sigma = np.diag(Sigma)
      res=clf.fit(U,y)
      return clf, testrow, testres, U,Sigma,V
   except Exception, e:
      print e
      pass

cols = ['I','N','T','P','mbti','name','occup','bday','bday2']
df = pd.read_csv("./data/celeb_astro_mbti.csv",sep=';')
df = df.reindex(np.random.permutation(df.index))
   
total = 0
predsum = 0
for idx in df.index:
   letter = random.choice(['I','N','T','P'])
   clf, testrow, testres,U,Sigma,V = train(df, letter, idx)
   if testres == None: continue
   testrow2=testrow.drop(cols)
   testrow2=np.dot(np.dot(lin.inv(Sigma),V),testrow2)
   pred = clf.predict(testrow2)
   total += 1
   if pred == testres: predsum += 1
   if total % 5 == 0:
      print df.ix[idx]['name']
      print 'pred',predsum, 'total', total, predsum/float(total)*100
      
print 'pred',predsum, 'total', total, predsum/float(total)*100