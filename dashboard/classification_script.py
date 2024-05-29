
import pandas as pd
import json
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# Load dataset
data = pd.read_csv('data/products_final.csv')

# Load category mapping
with open('category_mapping.json', 'r') as file:
    category_mapping = json.load(file)

# Clean and map categories
data['category_cleaned'] = data['category'].str.strip().str.title()
category_mapping_cleaned = {key.strip().title(): value for key, value in category_mapping.items()}
data['broad_category'] = data['category_cleaned'].map(category_mapping_cleaned)

# Handle missing text data
data['text'] = data['name'] + " " + data['description']
data['text'].fillna('No description available', inplace=True)

# Filter classified data
classified_data = data.dropna(subset=['broad_category'])
X = classified_data['text']
y = classified_data['broad_category']

# Encode labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Create and train model
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(stop_words='english')),
    ('classifier', LogisticRegression(random_state=0, max_iter=1000))
])
pipeline.fit(X, y_encoded)

# Predict and save predictions
unclassified_data = data[data['broad_category'].isnull()]
unclassified_data['predicted_broad_category'] = label_encoder.inverse_transform(
    pipeline.predict(unclassified_data['text'])
)
unclassified_data.to_csv('data/products.csv', index=False)
