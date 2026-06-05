import pandas as pd
import plotly.express as px
import numpy as np

# Read CSV Files
train = pd.read_csv('train.csv', encoding='utf-8-sig')
test  = pd.read_csv('test.csv',  encoding='utf-8-sig')

# Combine

df = pd.concat([train, test], ignore_index=True)

# Standardize

df.columns = (df.columns
               .str.strip()
               .str.lower()
               .str.replace(' ', '_')
               .str.replace('-', '_'))

print(df.columns.tolist())
print('Shape:', df.shape)

print('Shape : \n', df.shape)
print('Data Types : \n',df.dtypes)
print('Head :\n',df.head(10))
print('Tail : \n',df.tail(10))
print('\nMissing Value :')
df.info()
print('Describe : \n',df.describe())

# Fix company_tenure outlier

df['company_tenure'] = df['company_tenure'].clip(upper=60)
print('\nThe shape : \n',df.shape)
print('Discribe after fixed : \n',df.describe)

# Missing Value

df.isnull().sum()
df.duplicated().sum

# UNIVARITE FOR ATTRITION DISTRIBUTION
from matplotlib import color_sequences

attrition_count = df['attrition'].value_counts().reset_index()
attrition_count.columns = ['attrition', 'count']

fig = px.pie(
    attrition_count,
    names='attrition',
    values='count',
    title='Employee Attrition Distribution',
    color_discrete_sequence=['pink', 'purple']
)
fig.show()

# UNIVARITE FOR AGE DISTRIBUTION

age_data = df[['age','attrition']].copy()

fig = px.histogram(
    age_data,
    x='age',
    color='attrition',         
    title='Age Distribution by Attrition',
    barmode='overlay',
    opacity=0.7,
    color_discrete_sequence=['purple', 'pink']
) 
fig.show()

# UNIVARITE FOR MONTLY INCOME DISTRIBUTION

income_data = df[['monthly_income', 'attrition']].copy()


fig = px.histogram(
    income_data,
    x='monthly_income',
    color='attrition',
    title='Monthly Income Distribution by Attrition',
    barmode='overlay',
    opacity=0.7,
    color_discrete_sequence=['purple', 'blue']
)
fig.show()

# BIVARIATE ATTRITION BY JOB ROLE
role_data = (df.groupby(['job_role', 'attrition'])
               .size()
               .reset_index(name='count'))

fig = px.bar(
    role_data,
    x='job_role',
    y='count',
    color='attrition',
    title='Attrition by Job Role',
    barmode='group',
    color_discrete_sequence=['purple', 'blue']
)
fig.show()

# BIVARIATE WORK-LIFE BALANCE AND ATTRITON
print(df['work_life_balance'].unique())
wlb_data = (df.groupby(['work_life_balance', 'attrition'])
              .size()
              .reset_index(name='count'))


wlb_data = (df.groupby(['work_life_balance', 'attrition'])
              .size()
              .reset_index(name='count'))

fig = px.bar(
    wlb_data,
    x='work_life_balance',
    y='count',
    color='attrition',
    title='Distribution Work-Life Balance and Attrition',
    barmode='group',
    color_discrete_sequence=['purple', 'blue'],
    category_orders={
        'work_life_balance': ['Poor', 'Fair', 'Good', 'Excellent']
    }
)
fig.show()

# BIVARIATE BETWEEN MOONTHLY INCOME AND ATTRITION
from matplotlib.pyplot import title


income_attr = df[['monthly_income', 'attrition']].copy()


fig = px.box(
    income_attr,
    x='attrition',
    y='monthly_income',
    color='attrition',
    title='Distribution Monthly Income and Attrition',
    color_discrete_sequence=['purple', 'blue']
)
fig.show()

# BIVRIATE BETWEEN JOB
print(df['job_satisfaction'].unique())
js_data = (df.groupby(['job_satisfaction', 'attrition'])
             .size()
             .reset_index(name='count'))

# fig
fig = px.bar(
    js_data,
    x='job_satisfaction',
    y='count',
    color='attrition',
    title='Job Satisfaction vs Attrition',
    barmode='group',
    color_discrete_sequence=['purple', 'blue'],
    category_orders={
        'job_satisfaction': ['Low', 'Medium', 'High', 'Very High']
    }
)
fig.show()

#MULTIVARIATE CORRELATION HEATMAP

numaric_cols = numeric_cols = ['age', 'monthly_income', 'years_at_company',
                'distance_from_home', 'number_of_promotions',
                'company_tenure', 'number_of_dependents']

corr = df[numaric_cols].corr().round(2)

fig = px.imshow(
    corr,
    title = 'Correlation Heatmap',
    color_continuous_scale = 'RdBu_r',
    text_auto = True
)
fig.show()