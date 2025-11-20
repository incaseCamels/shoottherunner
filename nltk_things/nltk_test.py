import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

# Ensure NLTK resources are downloaded

nltk.download('punkt')
nltk.download('stopwords')

# Simple synonym dictionary for compression

synonyms = {
"utilize": "use",
"approximately": "about",
"demonstrate": "show",
"implement": "do",
"requirement": "need",
"functionality": "feature",
"performance": "speed",
"component": "part"
}

stop_words = set(stopwords.words('english'))

def compress_sentence(sentence):
words = word_tokenize(sentence)
compressed_words = []
for w in words:
lw = w.lower()
if lw not in stop_words:
w = synonyms.get(lw, w)
compressed_words.append(w)
return " ".join(compressed_words)

def compress_text(text):
sentences = sent_tokenize(text)
compressed = [compress_sentence(s) for s in sentences]
return " ".join(compressed)

# Example

text = """
We need to implement a Python script that utilizes AST parsing
to efficiently handle large code files. The script should demonstrate
performance improvements while maintaining all functionality.
"""

compressed = compress_text(text)
print("Original text:\n", text)
print("\nCompressed text:\n", compressed)
