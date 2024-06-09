import pandas as pd

# Step 1: Read the original CSV file
df = pd.read_excel("global_superstore_2016.xlsx") 

# Step 2: Split the DataFrame into three smaller DataFrames
# Define the number of splits
num_splits = 3

# Calculate the size of each split
split_size = len(df) // num_splits

# Create a list to hold the smaller DataFrames
dfs = []

# Split the DataFrame into smaller DataFrames
for i in range(num_splits):
    start_index = i * split_size
    end_index = (i + 1) * split_size if i < num_splits - 1 else len(df)
    dfs.append(df.iloc[start_index:end_index])

# Step 3: Save each of the smaller DataFrames into separate CSV files
for i, df_split in enumerate(dfs):
    df_split.to_csv(f'split_file_{i + 1}.csv', index=False)

print("CSV file has been split into 3 files successfully.")
