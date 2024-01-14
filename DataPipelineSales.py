#!/usr/bin/env python
# coding: utf-8

# ## Data pipeline for sales forecast
# 

# In[1]:


import pandas as pd
import matplotlib.pyplot as plt
from tqdm.notebook import tqdm

# Load the data
file_path = 'data.csv'
data = pd.read_csv(file_path, encoding='iso-8859-1')

# Show the head of the DataFrame
tqdm.pandas()
print('Head of the DataFrame:')
print(data.head())

# Describe the DataFrame to get an overview of the numerical fields
describe_data = data.describe(include='all', datetime_is_numeric=True)
print('\nDescription of the DataFrame:')
print(describe_data)

# Check for missing values
missing_values = data.isnull().sum()
print('\nMissing values in each column:')
print(missing_values)

# Check for duplicates
print('\nNumber of duplicate records:', data.duplicated().sum())

# Check for any negative values in 'Quantity' and 'UnitPrice'
negative_quantity = data[data['Quantity'] < 0].shape[0]
negative_unit_price = data[data['UnitPrice'] < 0].shape[0]
print('\nRecords with negative Quantity:', negative_quantity)
print('Records with negative UnitPrice:', negative_unit_price)

# Convert 'InvoiceDate' to datetime and check for any conversion issues
data['InvoiceDate'] = pd.to_datetime(data['InvoiceDate'], errors='coerce')
invalid_dates = data['InvoiceDate'].isnull().sum()
print('\nInvalid dates found:', invalid_dates)

# Validate data types
print('\nData types after conversion:')
print(data.dtypes)


# Here are the summarized results of the executed code:
# 
# The head of the DataFrame shows the first few rows of the dataset.
# The description of the DataFrame provides a statistical summary of the numerical fields.
# There are missing values in some columns that need to be addressed.
# There are 5,268 duplicate records in the dataset.
# There are 10,624 records with negative 'Quantity' and 2 records with negative 'UnitPrice'.
# No invalid dates were found after converting the 'InvoiceDate' column to datetime.
# The data types for each column were displayed, showing the types after conversion.

# ### Data cleaning
# Remove the unnecessary 'Unnamed: 0' column.
# Drop duplicate records.
# Remove records with negative or zero 'Quantity'.
# Remove records with negative or zero 'UnitPrice'.
# Drop rows with missing 'Description' or 'CustomerID'.
# Convert 'InvoiceDate' to datetime format.

# In[3]:


# Remove unnecessary 'Unnamed: 0' column if it exists
if 'Unnamed: 0' in data.columns:
    data.drop('Unnamed: 0', axis=1, inplace=True)

# Remove duplicate records
data.drop_duplicates(inplace=True)

# Remove records with negative or zero Quantity
data = data[data['Quantity'] > 0]

# Remove records with negative or zero UnitPrice
data = data[data['UnitPrice'] > 0]

# Check for missing values and remove rows with missing 'Description' or 'CustomerID'
data.dropna(subset=['Description', 'CustomerID'], inplace=True)

# Convert 'InvoiceDate' to datetime
data['InvoiceDate'] = pd.to_datetime(data['InvoiceDate'], errors='coerce')

# Check the final state of the data
print('Data after cleaning:')
print(data.head())
print('\nData types:')
print(data.dtypes)
print('\nMissing values:')
print(data.isnull().sum())
print('\nDuplicate records:', data.duplicated().sum())


# 
# Here's the state of the data after cleaning:
# 
# The head of the cleaned DataFrame is displayed.
# Data types for each column have been confirmed.
# Missing values have been checked, and necessary rows have been removed.
# Duplicate records have been verified as removed.
# The dataset is now cleaner and should be ready for further analysis or processing steps

# In[4]:


import seaborn as sns

# Basic distribution plots for 'Quantity' and 'UnitPrice'
plt.figure(figsize=(14, 6))

# Distribution plot for 'Quantity'
plt.subplot(1, 2, 1)
sns.histplot(data['Quantity'], bins=50, kde=False)
plt.title('Distribution of Quantity')
plt.xlabel('Quantity')
plt.ylabel('Frequency')

# Distribution plot for 'UnitPrice'
plt.subplot(1, 2, 2)
sns.histplot(data['UnitPrice'], bins=50, kde=False)
plt.title('Distribution of UnitPrice')
plt.xlabel('UnitPrice')
plt.ylabel('Frequency')

plt.tight_layout()
plt.show()


# If we  look at the distribution plots for 'Quantity' and 'UnitPrice' to identify any anomalies or outliers that may need to be addressed, we can observe the following:
# 
# The 'Quantity' distribution is highly skewed to the right, indicating that there are transactions with very high quantities.
# The 'UnitPrice' distribution is also skewed to the right, suggesting that most products are in a lower price range, but there are a few with a very high unit price.
# These observations suggest that we may need to further investigate the outliers and consider whether they are valid transactions or if they need to be cleaned from the dataset. 

# Create the DBT project structure and define the models for data transformation.
# I will  create the necessary project structure and configuration files for the DBT project by creating the appropriate directories and SQL files to define the data transformations.

# In[5]:


get_ipython().system('mkdir my_project && cd my_project && mkdir models')


# In[6]:


get_ipython().system('touch my_project/models/model1.sql my_project/models/model2.sql')


# In[7]:


get_ipython().system('cat my_project/models/model1.sql')


# In[8]:


get_ipython().system('pip install ipython-sql')


# In[9]:


get_ipython().run_line_magic('load_ext', 'sql')


# In[10]:


get_ipython().run_line_magic('sql', 'sqlite://')


# In[11]:


get_ipython().run_cell_magic('sql', '', '-- model1.sql\n-- DBT Model for Cleaning Data\n-- Remove Duplicates\ncreate view cleaned_data as \n    select distinct *\n    from source_data;\n\n-- Handle Missing Values\ncreate view missing_values as \n    select \n        sum(case when Description is null then 1 else 0 end) as missing_description,\n        sum(case when CustomerID is null then 1 else 0 end) as missing_customer_id\n    from cleaned_data;\n\n-- Filter Outliers\ncreate view filtered_data as \n    select *\n    from cleaned_data\n    where Quantity >= 0 and UnitPrice >= 0;\n\n-- DBT Model for Aggregating Data\n-- Total Sales per Product\ncreate view total_sales_per_product as \n    select \n        Description,\n        sum(Quantity) as total_quantity\n    from filtered_data\n    group by Description;\n\n-- Average Sales per Customer\ncreate view average_sales_per_customer as \n    select \n        CustomerID,\n        avg(Quantity) as average_quantity\n    from filtered_data\n    group by CustomerID;\n\n')


# In[12]:


get_ipython().run_cell_magic('sql', '', '-- model2.sql\n-- Additional Aggregations\n-- Total Sales per Country\ncreate view total_sales_per_country as \n    select \n        Country,\n        sum(Quantity) as total_quantity\n    from filtered_data\n    group by Country;\n\n-- Total Sales per Invoice Date\ncreate view total_sales_per_invoice_date as \n    select \n        InvoiceDate,\n        sum(Quantity) as total_quantity\n    from filtered_data\n    group by InvoiceDate;\n\n-- Average Unit Price per Product\ncreate view average_unit_price_per_product as \n    select \n        Description,\n        avg(UnitPrice) as average_unit_price\n    from filtered_data\n    group by Description;\n')


# In[13]:


get_ipython().system('cat my_project/models/model1.sql')


# In[ ]:




