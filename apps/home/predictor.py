import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import numpy as np

# Load datasets
users_df = pd.read_csv('D:/Oddssey/media/users_data.csv')
books_df = pd.read_csv('D:/Oddssey/media/books_updated.csv')
ratings_df = pd.read_csv('D:/Oddssey/media/interactions.csv')

# Merge datasets
merged_data = pd.merge(ratings_df, users_df, on='user_id', how='left')
merged_data = pd.merge(merged_data, books_df, on='book_id', how='left')

# Data preprocessing
# Handle missing values, for example by filling them with 0
merged_data.fillna(0, inplace=True)

# Drop irrelevant columns (e.g., 'user_name', 'description')
merged_data = merged_data.drop(columns=['user_name', 'description'])

# Label encode any remaining text data (if necessary)
label_encoder = LabelEncoder()

# One-hot encoding for categorical data (like 'category', 'availability')
merged_data = pd.get_dummies(merged_data, columns=['category', 'availability'], drop_first=True)

# If any column still has text data (categorical), apply label encoding
for column in merged_data.columns:
    if merged_data[column].dtype == 'object':  # Check for object (string) columns
        merged_data[column] = label_encoder.fit_transform(merged_data[column])

# Define target variable (e.g., 'demand' or 'rating') and features
X = merged_data.drop(columns=['rating', 'user_id', 'book_id'])  # Drop irrelevant columns
y = merged_data['rating']  # Assuming rating is your proxy for demand

# Check if target variable has enough variance
if np.var(y) == 0:
    print("The target variable 'rating' has no variance!")
else:
    # Split data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=2, random_state=42)

    # Check if test set is too small
    if len(y_test) < 2:
        print("Test set is too small!")
    else:
        # Scale features (make sure only numerical columns are passed)
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Train a model (you can try other models like GradientBoosting as well)
        model = RandomForestRegressor(random_state=42)
        model.fit(X_train_scaled, y_train)

        # Make predictions
        predictions = model.predict(X_test_scaled)

        # Evaluate the model with multiple metrics
        mae = mean_absolute_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)

        print(f'Mean Absolute Error: {mae}')
        print(f'R² Score: {r2}')
        
        # Check if predictions are constant
        if np.var(predictions) == 0:
            print("Warning: The model is predicting a constant value!")
