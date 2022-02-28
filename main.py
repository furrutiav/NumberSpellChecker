from model import NumberSpellChecker
import pickle

# Initialize

# >vocab
base_symspell = pickle.load(open("base_symspell.pickle", "rb"))
D_correction = pickle.load(open("D_correction.pickle", "rb"))

# >class
nsc = NumberSpellChecker(base_symspell, D_correction)

# Use

print(nsc.apply("trecientos catorse flores"))
# >>> 314 flores
