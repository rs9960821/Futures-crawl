#!/usr/bin/env python
# coding: utf-8

# In[562]:


import pymongo
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import matplotlib.dates as mdate
import matplotlib.patches as mpatches
import re
pd.set_option('display.max_columns', 3000)
pd.set_option('display.width', 3000)
sns.set(font = ['Microsoft YaHei'])


# In[563]:


client = pymongo.MongoClient('localhost', 27017)
db = client.txDataNew
collection = db.txDec


# In[564]:


result = collection.find()


# In[565]:


df = pd.DataFrame([i for i in result]).drop(columns="_id")


# In[566]:


df.shape


# In[567]:


df["日期"].unique()


# In[568]:


df["漲跌%"] = [re.findall("[-]\d+[.]\d+",i)[0] if "-" in i else re.findall("\d+[.]\d+",i)[0]for i in df["漲跌%"]]


# In[569]:


df["漲跌%"].unique()


# In[570]:


df["漲跌價"] = [re.findall("[-]\d+",i)[0] if "-" in i else re.findall("\d+",i)[0]for i in df["漲跌價"]]


# In[571]:


df["漲跌價"].unique()


# In[572]:


df.head()


# In[573]:


cList = ["到期月份(週別)","契約","日期"]
for i in df.columns:
    try:
        if i in cList:
            continue
        elif "%" in i:
            df[i] = df[i].astype("float")
        else:
            df[i] = df[i].astype("int")
    except Exception as e:
        print(i, e)


# In[574]:


df.loc[df["結算價"]=="-",:].shape[0]


# In[575]:


[df.loc[i, "日期"] for i in range(df.shape[0]) if df.loc[i, "結算價"]=="-"]


# In[576]:


df["結算價"] = [i if i != "-" else int(pd.Series([int(i) for i in df["結算價"] if i != "-"]).mean())for i in df["結算價"]]


# In[577]:


df["結算價"].unique()


# In[578]:


df["結算價"] = df["結算價"].astype("int")


# In[579]:


df["日期"] = pd.to_datetime(df["日期"])


# In[580]:


df.dtypes


# In[581]:


df_2 = df.loc[df["到期月份(週別)"] == "202003",:]
df_2.shape


# In[582]:


df_2.head()


# In[583]:


df_2 = df_2.sort_values(by="日期")


# In[584]:


df_2.head()


# In[585]:


def adjustDate():
    global df_2
    alldaylocator = mdate.DayLocator()#設定日期
    plt.gcf().autofmt_xdate()#自動調整刻度
    plt.gca().xaxis.set_major_locator(alldaylocator)#設定美日為主要刻度
    plt.gca().xaxis.set_major_formatter(mdate.DateFormatter('%m%d'))#設定時間 mm-dd
    plt.xlim(list(df_2["日期"])[0] - pd.Timedelta(hours = 10), list(df_2["日期"])[-1] + pd.Timedelta(hours = 10))
    plt.setp(plt.xticks()[1], ha = "center")


# In[586]:


plt.figure(figsize = (18, 8))
plt.plot(df_2["日期"], df_2["最高價"], linestyle = "--", marker = "o", label = "最高價")
plt.plot(df_2["日期"], df_2["最低價"], linestyle = "--", marker = "o", label = "最低價")
plt.legend(loc = "upper left")
bboxTuple = (dict(edgecolor = "blue", facecolor = "red", alpha = 0.2), dict(edgecolor = "orange", facecolor = "blue", alpha = 0.2))
for i, j, z in zip(df_2["日期"], df_2["最高價"], df_2["最低價"]):
    xPoissition = i - pd.Timedelta(hours = 10)
    plt.text(xPoissition, j+10, format(j, ","), fontsize = 8, bbox = bboxTuple[0], color = "blue")
    plt.text(xPoissition, z-30, format(z, ","), fontsize = 8, bbox = bboxTuple[1], color = "red")
    plt.plot([i, i], [0, j], linestyle = "--", alpha = 0.5)
plt.ylim(11330, 12135)
adjustDate()
plt.title("2019/12 到期月份202003 TX 最高最低價折線圖", fontsize = 20)
plt.ylabel("價格")
plt.xlabel("日期")
plt.show()


# In[589]:


plt.figure(figsize = (16, 8))
ColorArray = np.zeros(df_2.shape[0], dtype = "3f4")
btZero = np.array(df_2["漲跌價"]) > 0
stZero = np.array(df_2["漲跌價"]) < 0
ColorArray[btZero] = (1,0,0)
ColorArray[stZero] = (0,1,0)
plt.bar(df_2["日期"], df_2["漲跌價"], color = ColorArray, width = 0.6)
pop_a = mpatches.Patch(color = "red", label = "漲價")
pop_b = mpatches.Patch(color = "green", label = "跌價")
plt.legend(handles = [pop_a, pop_b])
timeTuple = (list(df_2["日期"])[0] - pd.Timedelta(hours = 10), list(df_2["日期"])[-1] + pd.Timedelta(hours = 10))
adjustDate()
plt.plot([timeTuple[0],timeTuple[1]], [0,0])
for i, j in zip(df_2["日期"], df_2["漲跌價"]):
    setpUp = 3.5 if j > 0 else -8.5
    timepass = pd.Timedelta(hours = 8) if j < 0 else pd.Timedelta(hours = 5)
    colorop = "red" if j > 0 else "green"
    bboxop = dict(edgecolor = "red", facecolor = "green", alpha = 0.2) if j > 0 else dict(edgecolor = "green", facecolor = "red", alpha = 0.2)
    plt.text(i-timepass, j+setpUp, str(j).zfill(2), color = colorop, bbox = bboxop)
plt.title("2019/12 TX 202003 漲跌圖", fontsize = 20)
plt.ylim(-95, 170)
plt.ylabel("價格")
plt.xlabel("日期")
plt.show()


# In[591]:


moving = df_2["最後成交價"].rolling(3).mean()


# In[593]:


result = plt.figure(figsize = (25, 14))
result.tight_layout()
result.suptitle("2019/12 202003 期貨", fontsize = 40)
ax0 = plt.subplot2grid((3,1), (0,0), rowspan=2)
ax0.tick_params(pad=1, labelsize = 10)
rise = df_2["最後成交價"] - df_2["開盤價"] > 0
fall = df_2["最後成交價"] - df_2["開盤價"] < 0
fc = np.zeros(df_2.shape[0],dtype = "3f4")
fc[rise] = (1,0,0)
fc[fall] = (0,1,0)
ax0.bar(df_2["日期"], df_2["最高價"] - df_2["最低價"], 0, df_2["最低價"], color = fc, edgecolor = fc)
ax0.bar(df_2["日期"], df_2["最後成交價"] - df_2["開盤價"], 0.4, df_2["開盤價"], color = fc, edgecolor = fc)
ax0.plot(df_2["日期"], moving, color = "blue")
plt.ylim(11200, 12200)
ax0.grid(axis = "y", color = "k", linestyle = "--", alpha = 0.5)
adjustDate()
ax1 = plt.subplot2grid((3,1), (2,0))
ax1.plot(df_2["日期"], df_2["*合計成交量"], linestyle = "--", marker = "s", color = "red", label = "合計成交量")
for i, j in zip(df_2["日期"], df_2["*合計成交量"]):
    plt.plot([i, i], [0, j], alpha = 0.5)
ax1.legend(prop = {'size':20})
ax1.set_ylim([20, 380])
ax1.grid(axis = "y", color = "k", linestyle = "--", alpha = 0.5)
adjustDate()


# In[ ]:




