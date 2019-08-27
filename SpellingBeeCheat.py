import re
import pandas as pd

center_letter = 'N'
other_letters = 'ADHRTY'+center_letter

df_words = pd.read_csv('scrabble_words.txt', names=['words'], header=None)

print(df_words.size)

df_words['has_center'] = df_words['words'].str.contains(pat=f'[{center_letter}]')
df_words = df_words[df_words['has_center']==True]

print(df_words.size)

df_words['other'] = df_words['words'].str.contains(pat=f'[^{other_letters}]')
df_words = df_words[df_words['other']==False]

df_words['len'] = df_words['words'].str.len()
df_words = df_words[df_words['len'] > 3]


print(df_words)
