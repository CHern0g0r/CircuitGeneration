# %%
import pandas as pd
import numpy as np
import random

from sklearn.model_selection import train_test_split

from pathlib import Path
from tqdm.notebook import tqdm
import pickle

# %%
# Paths
_pth = Path('')
basepth = _pth / 'heap/data/circ/graphml/cirbo'
cirbo_pth = _pth / 'heap/data/circ/pickle/cirbo'
csv_path = _pth / 'workspace/circ/CircuitGeneration/datasets/data/cirbo_df.csv'
cirbo_small_pth = _pth / 'heap/data/circ/pickle/cirbo_small'

# Reproducibility: global seed
seed = 42
random.seed(seed)
np.random.seed(seed)

# %%
# Read dataframe and compute output size
df = pd.read_csv(csv_path)
df['outsize'] = df['circuit_name'].apply(lambda x: len(x.split('_')))
df['outsize'].value_counts()
print(len(df))
df.head()

# %%
# Load raw shards into a single dict
data = dict()
for pth in sorted(basepth.iterdir()):
    shard = pickle.load(open(pth, 'rb'))
    for k, v in tqdm(shard.items(), desc=f'Processing {pth.name}'):
        data[k] = v
print(len(data))

# %%
# Create train/val/test splits (stratified by outsize)
X, Xtest = train_test_split(df, test_size=0.05, random_state=seed, stratify=df['outsize'])
X, Xval = train_test_split(X, test_size=0.03, random_state=seed, stratify=X['outsize'])

X['split'] = 'train'
Xval['split'] = 'val'
Xtest['split'] = 'test'
print(len(X), len(Xval), len(Xtest))
ndf = pd.concat([X, Xval, Xtest], axis=0)
ndf['split'].value_counts()
ndf.head()

# %%
# Group counts by split and outsize
gr = ndf[['split', 'outsize', 'idx']].groupby(['split', 'outsize']).count()
gr.head(9)

# %%
# Optional: save updated dataframe
ndf.to_csv(cirbo_pth / 'cirbo_df.csv', index=False)

# %%
# Example: create raw split pickles (commented)
for split, idx_set in zip(['train', 'val', 'test'], [X, Xval, Xtest]):
    subset = dict()
    print(split)
    for _, row in idx_set.iterrows():
        subset[row['circuit_name']] = data[row['circuit_name']]
    print(f'Saving {split} set with {len(subset)} samples')
    pickle.dump(subset, open(cirbo_pth / 'raw' / f'cirbo_{split}.pkl', 'wb'))

# %%
# Cirbo sample small

df['outsize'] = df['circuit_name'].apply(lambda x: len(x.split('_')))
df['outsize'].value_counts()
small_df = df[df['outsize'] < 3]
print(len(small_df))
small_df.head()

# %%
data_small = dict()
for pth in sorted(basepth.iterdir()):
    shard = pickle.load(open(pth, 'rb'))
    for k, v in tqdm(shard.items(), desc=f'Processing {pth.name}'):
        if k in small_df['circuit_name'].values:
            data_small[k] = v
print(len(data_small))

# %%
# Create splits for small_df
X, Xtest = train_test_split(small_df, test_size=0.05, random_state=seed, stratify=small_df['outsize'])
X, Xval = train_test_split(X, test_size=0.05, random_state=seed, stratify=X['outsize'])

X['split'] = 'train'
Xval['split'] = 'val'
Xtest['split'] = 'test'
print(len(X), len(Xval), len(Xtest))
X = pd.concat([X, Xval, Xtest], axis=0)
X['split'].value_counts()
X.to_csv(cirbo_small_pth / 'cirbo_small_df.csv', index=False)
X.head()

# %%
# Optional saving for small dataset
for split, idx_set in zip(['train', 'val', 'test'], [X, Xval, Xtest]):
    subset = dict()
    print(split, type(subset))
    for _, row in idx_set.iterrows():
        subset[row['circuit_name']] = data[row['circuit_name']]
    print(f'Saving {split} set with {len(subset)} samples')
    pickle.dump(subset, open(cirbo_small_pth / 'raw' / f'cirbo_{split}.pkl', 'wb'))

# %%
p = _pth / 'heap/data/circ/pickle/cirbo/cirbo_df.csv'
df = pd.read_csv(p)
df.head()

# %%
p = _pth / 'heap/data/circ/pickle/cirbo_small/cirbo_small_df.csv'
df = pd.read_csv(p)
print(df['split'].value_counts())
df.head()
