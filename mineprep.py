import os
from datetime import datetime
import pandas as pd
import mindmeld, numpy as np

from sklearn.feature_extraction import DictVectorizer
def one_hot_dataframe(data, cols, replace=False):
    vec = DictVectorizer()
    mkdict = lambda row: dict((col, row[col]) for col in cols)
    tmp = data[cols].apply(mkdict, axis=1)
    vecData = pd.DataFrame(vec.fit_transform(tmp).toarray())
    vecData.columns = vec.get_feature_names()
    vecData.index = data.index
    if replace is True:
        data = data.drop(cols, axis=1)
        data = data.join(vecData)
    return (data, vecData, vec)

'''
Processes birthday field on each row of the dataframe, adding 
astrological parameters, returns the result
'''
def astro_enrich(df_arg):
   df = df_arg.copy()
   # change format of the date
   def f(s):
      try: return datetime.strptime(s, '%d/%m/%Y').date().strftime('%Y%m%d')
      except: return None
   df['bday2'] = df['bday'].apply(f)

   # create (empty) grant lewi fields
   cols = []
   lewi = range(278)
   lewi = map(lambda x: 'lewi'+str(x),lewi)
   cols += lewi
   for x in cols: df[x] = np.nan

   # millman fields
   for i in range(10): df['mills'+str(i)] = np.nan

   # filter out null birthdays
   df2 = df[pd.isnull(df['bday2']) == False]

   # now populate all astrological values using results from mindmeld.calculate
   def f(x):
      res = mindmeld.calculate(x['bday2'])
      for lew in res['lewi']: x['lewi'+str(lew)] = 1
      if res['chinese']: x['chinese'] = res['chinese']
      if res['spiller']: x['spiller'] = res['spiller']
      x['sun'] = str(res['sun'])
      x['moon'] = str(res['moon'])
      x['milla'] = str(res['millman'][0])
      x['millb'] = str(res['millman'][1])
      x['mills'+str(res['millman'][2])] = 1
      x['mills'+str(res['millman'][3])] = 1
      x['mills'+str(res['millman'][4])] = 1
      return x
   df3 = df2.apply(f, axis=1)

   df4, _, _ = one_hot_dataframe(df3,['spiller','chinese','milla','millb','sun'], \
                                 replace=True)
   df4 = df4.replace(0.0,np.nan)
   return df4

celebs = pd.read_csv("./data/famousbday.txt",sep=':',header=None, 
names=['name','occup','bday','spiller','chinese','milla','millb','sun','moon'])
celeb_mbti = pd.read_csv("./data/myer-briggs.txt",header=None,sep=':',\
names=['mbti','name'])

df = pd.merge(celeb_mbti,celebs)

df4 = astro_enrich(df)

df4['I'] = df4.apply(lambda x: 1 if x['mbti'][0] == 'I' else 0, axis=1)
df4['N'] = df4.apply(lambda x: 1 if x['mbti'][1] == 'N' else 0, axis=1)
df4['T'] = df4.apply(lambda x: 1 if x['mbti'][2] == 'T' else 0, axis=1)
df4['P'] = df4.apply(lambda x: 1 if x['mbti'][3] == 'P' else 0, axis=1)

df4.to_csv('./data/celeb_astro_mbti.csv',sep=';',index=None)
