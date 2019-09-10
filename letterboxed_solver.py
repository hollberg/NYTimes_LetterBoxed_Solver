"""
Solver for the NY Times "LetterBoxed" puzzle
Mitch Hollberg (github.com/hollberg)
# File of dictionary words from
# https://drive.google.com/file/d/0B9-WNydZzCHrdDVEc09CamJOZHc/view
"""

import re
import pandas as pd
import openpyxl


# **** ENTER IN THE CHARACTERS ON EACH SIDE OF THE SQUARE IN THE STRING BELOW ****
board = ['EGW', 'OKI', 'SLP', 'CDA']

alphabet = set(list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'))

# Build a set of the letters that exist on the board:
allowed_letters = set()
for side in board:
    for letter in side:
        allowed_letters.add(letter)

# If not in allowed set, then must be omitted/invalid. No words containing these
# letters can be used
omitted_letters = {letter for letter in alphabet if letter not in allowed_letters}

# Letters on the same "side" of the letter box CAN NOT be used in sequence. Generate list
# of all permutations of these invalid sequences of letters
nope_combos = list()
for side in board:
    for letter in side:
        others = side.replace(letter, '')
        for element in others:
            nope_combos.append((letter, element))

# Build Regex based on invalid combinations
nope_patterns = list()
for combo in nope_combos:
    nope_patterns.append(combo)

# Build Regex of all invalid strings:
re_nopes = ''

for nope in nope_patterns:
    re_nopes = re_nopes + f'|{nope[0]}{nope[1]}'

for letter in allowed_letters:  # Can't duplicate letters
    re_nopes = re_nopes + f'|{letter}{letter}'

# Cut off leading '|'
re_nopes = re_nopes[1:]

omitted_letters_string = ''.join(sorted(list(omitted_letters)))
re_omitted = f'[{omitted_letters_string}]'

# Read in file of words
df_words = pd.read_csv('scrabble_words.txt', names=['words'], header=None)

# Pare down words, eliminating words containing disallowed letters/patterns
df_words['status'] = df_words['words'].str.contains(pat=re_omitted)
df_words = df_words[df_words['status']==False]

# Words must be 3 characters
df_words['length'] = df_words['words'].apply(lambda x: len(x))
df_words = df_words[df_words['length'] > 2]

# Add convenience columns to dataframe: 1st/last letters
df_words['first_letter'] = df_words['words'].apply(lambda x: x[0])
df_words['last_letter'] = df_words['words'].apply(lambda x: x[-1])

def get_complements(word: str):
    """
    Given a word and string of allowable characters, return the
    characters not found in allowable characters list
    :param word:
    :param letters:
    :return:
    """
    letters = allowed_letters
    word_set = set(word)
    letters_set = set(letters)
    # Set Operations - "-" returns difference
    complements_set = letters_set - word_set
    return sorted(list(complements_set))


df_words['nopes'] = df_words['words'].str.contains(pat=re_nopes)
df_words = df_words[df_words['nopes']==False]
df_words['complements'] = df_words['words'].apply(func=get_complements)
df_words['set'] = df_words['words'].apply(lambda x: sorted(list(set(x))))
df_words['set_length'] = df_words['set'].apply(lambda x: len(x))

# Add a T/F column (indicating presence/absence) for each letter in the puzzle
for letter in sorted(list(allowed_letters)):
    df_words[letter] = \
        df_words['words'].apply(lambda x: True if letter in x else False)

# df_words.to_clipboard()
# df_words.to_excel('Letterboxed_Cheat_20190909.xlsx')


# Find Word Pairs to create complete solution
for letter in allowed_letters:
    df_ends_with = df_words.loc[df_words['last_letter'] == letter]

    # Loop over all words with same final letter -
    for row in df_ends_with.itertuples():
        # Get all words that START with this end letter
        df_starts_with = df_words.loc[df_words['first_letter'] == letter]
        row_set = {letter for letter in row.set}
        for starts_row in df_starts_with.itertuples():
            starts_set = {letter for letter in starts_row.set}
            net_set = row_set.union(starts_set)
            if net_set == allowed_letters:
                print(f"{row.words} , {starts_row.words}")
