#!/usr/bin/env python
# coding: utf-8

# ### Generating 6 months stock price from NSE

# In[1]:


#pip install nsepy


# In[2]:


from nsepy import get_history
from datetime import date


# In[3]:


import pandas as pd
import numpy as np


# In[4]:


DRL = get_history(symbol="DRREDDY", start=date(2021,7,1), end=date(2022,1,9))
DRL


# ### Merging Stock prices with Polarity

# In[5]:


DRL_revised = DRL.drop(["Symbol","Series","Prev Close","Last","Turnover","Trades","Deliverable Volume","%Deliverble"], axis = 1)


# In[6]:


DRL_revised


# In[8]:


Polarity = pd.read_excel("C:/Users/sanyo/OneDrive - Indian School of Business/Term2/Foudation_Project/FinalOutput.xlsx")


# In[9]:


Polarity


# In[10]:


Polarity.set_index(["Date"],inplace=True)


# In[11]:


Polarity


# In[12]:


merged_data = pd.merge(DRL_revised,Polarity,left_index=True,right_index=True)


# In[13]:


merged_data


# ### Predicting trend with Random Forest Classifier Model

# In[14]:


# Dataframe with VWAP,  Volume, Polarity, Twitter_volume
DRL_df = merged_data[["VWAP", "Volume", "Polarity", "Count"]]
DRL_df.head()


# In[15]:


# Sorting Polarity into Positive, Negative and Neutral sentiment

sentiment = [] 
for score in DRL_df["Polarity"]:
    if score >= 0.05 :
          sentiment.append("Positive") 
    elif score <= - 0.05 : 
          sentiment.append("Negative")        
    else : 
        sentiment.append("Neutral")   

DRL_df["Sentiment"] = sentiment
DRL_df.head()


# In[16]:


# Sentiment Count
DRL_df["Sentiment"].value_counts()


# In[17]:


#Stock Trend based on difference between current price to previous day price and coverting them to '0' as fall and '1' as rise in stock price
DRL_df["Price Diff"] = DRL_df["VWAP"].diff()
DRL_df.dropna(inplace = True)
DRL_df["Trend"] = np.where(DRL_df['Price Diff'] > 0 , 1, 0)

DRL_df.head()


# In[18]:


# Binary encoding Sentiment column
DRL_trend = DRL_df[["VWAP", "Volume", 'Count', "Sentiment", "Trend"]]
DRL_trend = pd.get_dummies(DRL_trend, columns=["Sentiment"])
DRL_trend.head()


# In[19]:


# Defining features set
X = DRL_trend.copy()
X.drop("Trend", axis=1, inplace=True)
X.head()


# In[20]:


# Defining target vector
y = DRL_trend["Trend"].values.reshape(-1, 1)
y[:5]


# In[21]:


# Splitting into Train and Test sets
split = int(0.7 * len(X))

X_train = X[: split]
X_test = X[split:]

y_train = y[: split]
y_test = y[split:]


# In[22]:


from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report
from sklearn.ensemble import RandomForestClassifier


# In[23]:


# Using StandardScaler to scale features data
scaler = StandardScaler()
X_scaler = scaler.fit(X_train)
X_train_scaled = X_scaler.transform(X_train)
X_test_scaled = X_scaler.transform(X_test)


# In[24]:


# Create RFClassifier model
rf_model = RandomForestClassifier(n_estimators=500, random_state=78)

# Fit the model
rf_model = rf_model.fit(X_train_scaled, y_train.ravel())  


# In[25]:


# Make predictions
predictions = rf_model.predict(X_test_scaled)
pd.DataFrame({"Prediction": predictions, "Actual": y_test.ravel()}).head(20)

# Generate accuracy score for predictions using y_test
acc_score = accuracy_score(y_test, predictions)
print(f"Accuracy Score : {acc_score}")


# In[26]:


# Model Evaluation

# Generating the confusion matrix
cm = confusion_matrix(y_test, predictions)
cm_df = pd.DataFrame(
    cm, index=["Actual 0", "Actual 1"],
    columns=["Predicted 0", "Predicted 1"]
)

# Displaying results
display(cm_df)


# In[27]:


# Generating classification report
print("Classification Report")
print(classification_report(y_test, predictions))

