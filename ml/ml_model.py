import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import json
import sys
import joblib

# Load the dataset
data = pd.read_csv('mine_data3.csv')

# Define features and target variable
X = data[['mines.factors.coalQty', 'mines.factors.elecConsump', 'mines.factors.transportation', 'mines.factors.deforestedArea']]
y = data['strategy_label']

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Random Forest model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save the model to a file
joblib.dump(model, 'model.pkl')

def predict_strategy(coalQty, elecConsump, transportation, deforestedArea):
    # Ensure the input data has the same feature names as the training data
    input_data = pd.DataFrame({
        'mines.factors.coalQty': [coalQty],
        'mines.factors.elecConsump': [elecConsump],
        'mines.factors.transportation': [transportation],
        'mines.factors.deforestedArea': [deforestedArea]
    })
    
    strategy_label = model.predict(input_data)[0]
    
    # Map `strategy_label` to a more descriptive suggestion
    strategy_map = {
        'label_1': ["Suggestion 1", "Suggestion 2"],
        'label_2': ["Suggestion 3", "Suggestion 4"],
        'label_3': ["Suggestion 5", "Suggestion 6"],
        # Add more mappings as necessary
    }
    
    suggestions = strategy_map.get(strategy_label, ["No suggestions available for this input."])

    return {
        "strategy_label": strategy_label,
        "suggestions": suggestions
    }

if __name__ == "__main__":
    if len(sys.argv) == 5:
        coalQty = float(sys.argv[1])
        elecConsump = float(sys.argv[2])
        transportation = float(sys.argv[3])
        deforestedArea = float(sys.argv[4])
        
        # Load the model from file
        model = joblib.load('model.pkl')
        
        result = predict_strategy(coalQty, elecConsump, transportation, deforestedArea)
        print(json.dumps(result))
    else:
        print("Invalid number of arguments provided.")
