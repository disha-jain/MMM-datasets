# Disha Jain - dj9am
# Sameer Gupta - sg4vh
# Jason Quinn - jtq5ba
# Sindhu Ranga - sgr7va


# Import the libraries and give them abbreviated names:
import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

# load the data, use the directory where you saved the data: (please do not change)
df_properties = pd.read_csv('properties_2017.csv') 
df_train = pd.read_csv('train_2017.csv', parse_dates=["transactiondate"])
merged_inner = pd.merge(left=df_train,right=df_properties, left_on='parcelid', right_on='parcelid')


def get_predictions():
    predictions = {}
    # write code here
    # fill in your algorithm to calculate predicted log-error values here
    train_df = merged_inner
    train_df.dropna(subset=['parcelid'])
    y_train=train_df[['logerror']]
    X_train=train_df.drop(columns=['logerror','parcelid'], axis=0)

    variable = 'calculatedbathnbr'
    variable1 = 'garagetotalsqft'
    variable2 = 'finishedsquarefeet6'
    X_train.loc[X_train[variable].isnull(), variable] =0
    X_train.loc[X_train[variable1].isnull(), variable1] =X_train[variable1].mean()
    X_train.loc[X_train[variable2].isnull(), variable2] = X_train[variable2].mean()
    my_variable = X_train[[variable, variable1, variable2]]

    poly = PolynomialFeatures(degree=5)
    my_variable = poly.fit_transform(my_variable)

    X, X_test, y, y_test = train_test_split(my_variable, y_train, test_size=0.20, random_state=42)

    lin_reg = LinearRegression()

    lin_reg.fit(X, y[['logerror']])

    predictions = lin_reg.predict(X_test)
    i = 0
    for logerror in y_test['logerror']:
        logerror = predictions[i]
        i+=1
    return y_test
get_predictions()