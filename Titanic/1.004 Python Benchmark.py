# Code adapted from https://www.kaggle.com/omarelgabry/titanic/a-journey-through-titanic

# 1. Import
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC, LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB

# 2. Import data.
titanic_df = pd.read_csv("./Titanic/Raw Data/train.csv")
test_df = pd.read_csv("./Titanic/Raw Data/test.csv")

# 3. Preview data. 
titanic_df.head()
titanic_df.info()
test_df.info()

# 4. Drop unnecessary columns.
titanic_df = titanic_df.drop(['PassengerId','Name','Ticket'], axis = 1)
test_df = test_df.drop(['Name','Ticket'], axis = 1)

# 5. Clean embarked
titanic_df["Embarked"] = titanic_df["Embarked"].fillna("S")
sns.factorplot("Embarked", "Survived", data = titanic_df, size = 4, aspect = 3)
fig, (axis1, axis2, axis3) = plt.subplots(1, 3, figsize = (15, 5))
sns.countplot(x = "Embarked", data = titanic_df, ax = axis1)
sns.countplot(x = "Survived", hue = "Embarked", data = titanic_df, order = [1,0], ax = axis2)
embark_perc = titanic_df[["Embarked", "Survived"]].groupby(["Embarked"], as_index = False).mean()
sns.barplot(x = "Embarked", y = "Survived", data = embark_perc, order = ["S", "C", "Q"], ax = axis3)
embark_dummies_titanic  = pd.get_dummies(titanic_df['Embarked'])
embark_dummies_titanic.drop(['S'], axis=1, inplace=True)
embark_dummies_test  = pd.get_dummies(test_df['Embarked'])
embark_dummies_test.drop(['S'], axis=1, inplace=True)
titanic_df = titanic_df.join(embark_dummies_titanic)
test_df    = test_df.join(embark_dummies_test)
titanic_df.drop(['Embarked'], axis=1,inplace=True)
test_df.drop(['Embarked'], axis=1,inplace=True)

# 6. Fare
test_df["Fare"].fillna(test_df["Fare"].median(), inplace = True)
titanic_df["Fare"] = titanic_df["Fare"].astype(int)
test_df["Fare"] = test_df["Fare"].astype(int)
fare_not_survived = titanic_df["Fare"][titanic_df["Survived"] == 0]
fare_survived = titanic_df["Fare"][titanic_df["Survived"] == 1]
avgerage_fare = pd.DataFrame([fare_not_survived.mean(), fare_survived.mean()])
std_fare = pd.DataFrame([fare_not_survived.std(), fare_survived.std()])
titanic_df["Fare"].plot(kind = "hist", figsize = (15,3), bins = 100, xlim = (0,50))
avgerage_fare.index.names = std_fare.index.names = ["Survived"]
avgerage_fare.plot(yerr = std_fare, kind = "bar", legend = False)

# 7. Age
fig, (axis1, axis2) = plt.subplots(1, 2, figsize = (15,4))
axis1.set_title("Original Age values - Titanic")
axis2.set_title("New Age values - Titanic")
average_age_titanic = titanic_df["Age"].mean()
std_age_titanic = titanic_df["Age"].std()
count_nan_age_titanic = titanic_df["Age"].isnull().sum()
average_age_test = test_df["Age"].mean()
std_age_test = test_df["Age"].std()
count_nan_age_test = test_df["Age"].isnull().sum()
rand_1 = np.random.randint(average_age_titanic - std_age_titanic, average_age_titanic + std_age_titanic, 
                           size = count_nan_age_titanic)
rand_2 = np.random.randint(average_age_test - std_age_test, average_age_test + std_age_test, 
                           size = count_nan_age_test)
titanic_df["Age"].dropna().astype(int).hist(bins = 70, ax = axis1)
titanic_df["Age"][np.isnan(titanic_df["Age"])] = rand_1
test_df["Age"][np.isnan(test_df["Age"])] = rand_2
titanic_df["Age"] = titanic_df["Age"].astype(int)
test_df["Age"] = test_df["Age"].astype(int)
titanic_df["Age"].hist(bins = 70, ax = axis2)

# 8. Age
facet = sns.FacetGrid(titanic_df, hue = "Survived", aspect = 4)
facet.map(sns.kdeplot, "Age", shade = True)
facet.set(xlim = (0, titanic_df["Age"].max()))
facet.add_legend()
fig, axis1 = plt.subplots(1, 1, figsize = (18, 4))
average_age = titanic_df[["Age", "Survived"]].groupby(["Age"], as_index = False).mean()
sns.barplot(x = "Age", y = "Survived", data = average_age)

# 9. Cabin
titanic_df.drop("Cabin", axis = 1, inplace = True)
test_df.drop("Cabin", axis = 1, inplace = True)

# 10. Family
titanic_df["Family"] = titanic_df["Parch"] + titanic_df["SibSp"]
titanic_df["Family"].loc[titanic_df["Family"] > 0] = 1
titanic_df["Family"].loc[titanic_df["Family"] == 0] = 0
test_df["Family"] = test_df["Parch"] + test_df["SibSp"]
test_df["Family"].loc[test_df["Family"] > 0] = 1
test_df["Family"].loc[test_df["Family"] == 0] = 0
titanic_df = titanic_df.drop(["SibSp", "Parch"], axis = 1)
test_df = test_df.drop(["SibSp", "Parch"], axis = 1)
fig, (axis1, axis2) = plt.subplots(1, 2, sharex = True, figsize =(10, 5))
sns.countplot(x= "Family", data = titanic_df, order= [1,0], ax = axis1)
family_perc = titanic_df[["Family", "Survived"]].groupby(["Family"], as_index = False).mean()
sns.barplot(x = "Family", y = "Survived", data = family_perc, order = [1,0], ax = axis2)
axis1.set_xticklabels(["With Family", "Alone"], rotation = 0)

# 11. Sex
def get_person(passenger):
    age, sex = passenger
    return "child" if age < 16 else sex
titanic_df["Person"] = titanic_df[["Age", "Sex"]].apply(get_person, axis=1)
test_df['Person'] = test_df[["Age", "Sex"]].apply(get_person, axis = 1)
titanic_df.drop(["Sex"], axis = 1, inplace = True)
test_df.drop(["Sex"], axis = 1, inplace = True)
person_dummies_titanic = pd.get_dummies(titanic_df['Person'])
person_dummies_titanic.columns = ['Child','Female','Male']
person_dummies_titanic.drop(['Male'], axis=1, inplace=True)
person_dummies_test  = pd.get_dummies(test_df['Person'])
person_dummies_test.columns = ['Child','Female','Male']
person_dummies_test.drop(['Male'], axis=1, inplace=True)
titanic_df = titanic_df.join(person_dummies_titanic)
test_df    = test_df.join(person_dummies_test)
fig, (axis1,axis2) = plt.subplots(1,2,figsize=(10,5))
sns.countplot(x='Person', data=titanic_df, ax=axis1)
person_perc = titanic_df[["Person", "Survived"]].groupby(['Person'],as_index=False).mean()
sns.barplot(x='Person', y='Survived', data=person_perc, ax=axis2, order=['male','female','child'])
titanic_df.drop(['Person'],axis=1,inplace=True)
test_df.drop(['Person'],axis=1,inplace=True)

# create dummy variables for Pclass column, & drop 3rd class as it has the lowest average of survived passengers
pclass_dummies_titanic  = pd.get_dummies(titanic_df['Pclass'])
pclass_dummies_titanic.columns = ['Class_1','Class_2','Class_3']
pclass_dummies_titanic.drop(['Class_3'], axis=1, inplace=True)
pclass_dummies_test  = pd.get_dummies(test_df['Pclass'])
pclass_dummies_test.columns = ['Class_1','Class_2','Class_3']
pclass_dummies_test.drop(['Class_3'], axis=1, inplace=True)
titanic_df.drop(['Pclass'],axis=1,inplace=True)
test_df.drop(['Pclass'],axis=1,inplace=True)
titanic_df = titanic_df.join(pclass_dummies_titanic)
test_df = test_df.join(pclass_dummies_test)

# define training and testing sets
X_train = titanic_df.drop("Survived",axis=1)
Y_train = titanic_df["Survived"]
X_test  = test_df.drop("PassengerId",axis=1).copy()
logreg = LogisticRegression()
logreg.fit(X_train, Y_train)
Y_pred = logreg.predict(X_test)
logreg.score(X_train, Y_train)
random_forest = RandomForestClassifier(n_estimators=100)
random_forest.fit(X_train, Y_train)
Y_pred = random_forest.predict(X_test)
random_forest.score(X_train, Y_train)
