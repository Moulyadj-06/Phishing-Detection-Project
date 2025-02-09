import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib


# Feature extraction function
def extract_features(url):
    return {
        'url_length': len(url),
        'num_digits': sum(c.isdigit() for c in url),
        'num_special_chars': sum(c in ['-', '_', '/', '.', '@'] for c in url),
        'has_https': 1 if url.startswith('https') else 0,
    }


# Load dataset
data = pd.read_csv(r'C:\Data mining project\dataset\phishing_site_urls.csv')

# Apply feature extraction
X = pd.DataFrame([extract_features(url) for url in data['URL']])  # Update with the actual column name in your dataset
y = data['Label']  # Make sure 'Label' is the correct column for phishing (1) and safe (-1) sites

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Train RandomForest model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save the trained model
joblib.dump(model, 'model/phishing_model.joblib')
print("✅ Model trained and saved successfully!")
