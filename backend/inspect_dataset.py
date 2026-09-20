from datasets import load_dataset
from collections import Counter

print("Loading dataset...")

dataset = load_dataset(
    "dhruv0808/indic_sentiment_analyzer"
)

df = dataset["train"].to_pandas()

print("\nDataset shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nSentiment distribution:")
print(df["Label"].value_counts())

print("\nFirst 10 records:")
print(df.head(10))

print("\nSample sentences:")
for sentence in df["Sentence"].head(20):
    print(sentence)