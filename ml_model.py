import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
import pickle
import streamlit as st
import io
import base64
import matplotlib.pyplot as plt

# Load data and train model
data = pd.read_csv('mine_data3.csv')

# Process strategy_label if it contains multiple labels
data['strategy_label'] = data['strategy_label'].apply(lambda x: x.split(','))

# Convert strategy_label to a format suitable for MultiOutputClassifier
y = pd.get_dummies(data['strategy_label'].apply(pd.Series).stack()).groupby(level=0).sum()

X = data[['coalQty', 'elecConsump', 'transportation', 'deforestedArea']]

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a MultiOutputClassifier with class balancing
model = MultiOutputClassifier(RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced'))
model.fit(X_train, y_train)

# Save model to file
with open('ml_model.pkl', 'wb') as model_file:
    pickle.dump(model, model_file)

# Load model from file
def load_model():
    with open('ml_model.pkl', 'rb') as model_file:
        return pickle.load(model_file)

def predict_strategy(coalQty, elecConsump, transportation, deforestedArea, threshold=0.18):
    model = load_model()
    
    # Prepare input data
    input_data = pd.DataFrame({
        'coalQty': [coalQty],
        'elecConsump': [elecConsump],
        'transportation': [transportation],
        'deforestedArea': [deforestedArea]
    })

    # Get probabilities for each output label from MultiOutputClassifier
    probas = model.predict_proba(input_data)

    # Convert probabilities into binary predictions with dynamic thresholding
    predictions = []
    
    for prob_list in probas:
        binary_predictions = []
        for prob in prob_list:
            if len(prob) > 1:
                binary_predictions.append(1 if prob[1] > threshold else 0)
            else:
                binary_predictions.append(1 if prob[0] > threshold else 0)
        predictions.append(binary_predictions)

    # Flatten predictions into a single list
    predictions = [item for sublist in predictions for item in sublist]

    # Strategy mapping
    strategy_map = {
        'Switching to renewables': [
            "Install solar panels on your premises to harness solar energy.",
            "Invest in wind energy by installing wind turbines if feasible.",
            "Explore geothermal energy options for heating and cooling.",
            "Purchase green energy from renewable sources through your energy supplier."
        ],
        'Adopting electric vehicles': [
            "Replace your gasoline or diesel vehicles with electric vehicles (EVs).",
            "Install EV charging stations at your facility or home.",
            "Encourage the use of public transportation or carpooling to reduce reliance on personal vehicles.",
            "Explore incentives and rebates for purchasing electric vehicles."
        ],
        'Afforestation': [
            "Participate in local tree planting initiatives and support reforestation projects.",
            "Partner with organizations focused on forest conservation and management.",
            "Encourage the use of sustainable land management practices to prevent deforestation.",
            "Support policies and programs that promote the growth of urban green spaces."
        ],
        'Implementing methane capture': [
            "Install methane capture systems at landfills to collect and utilize methane gas.",
            "Implement anaerobic digesters in agricultural operations to capture methane from organic waste.",
            "Use captured methane as a renewable energy source for heating or electricity generation.",
            "Support and invest in technologies that improve the efficiency of methane capture and utilization."
        ],
        'Estimating Carbon Credits': [
            "Calculate your carbon footprint to understand the amount of carbon credits you need.",
            "Invest in certified carbon offset projects such as renewable energy or reforestation initiatives.",
            "Monitor and verify the performance of carbon offset projects to ensure they meet standards.",
            "Explore opportunities to generate your own carbon credits through sustainability projects."
        ],
        'General Suggestions': [
            "Improve energy efficiency across all operations to reduce overall carbon emissions.",
            "Implement waste reduction strategies and enhance recycling efforts.",
            "Engage with stakeholders to promote sustainability and environmental responsibility.",
            "Continuously monitor and report on your environmental impact to track progress and make improvements."
        ]
    }

    if coalQty == 0 and elecConsump == 0 and transportation == 0 and deforestedArea == 0:
        active_labels = ['General Suggestions']
    else:
        active_labels = [label for label, is_active in zip(strategy_map.keys(), predictions) if is_active]

    # Collect suggestions for each active strategy
    suggestions = [strategy_map.get(label, ["No suggestions available for this label."]) for label in active_labels]

    return {
        "strategy_labels": active_labels,
        "suggestions": suggestions
    }

# Streamlit app configuration
st.set_page_config(page_title="Personalized Suggestions", layout="wide")

st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stAppDeployButton {display:none;}
        #stDecoration {display:none;}
        .stSlider [data-baseweb=slider] {
        width: 70%;
        }
    </style>
""", unsafe_allow_html=True)

# Function to safely convert strings to floats, handling invalid inputs
def safe_float_conversion(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

# Function to calculate carbon reduction based on trees planted
def calculate_tree_carbon_offset(num_trees):
    return num_trees * 0.021

# Access query parameters using the updated method
params = st.query_params

# Extract query parameters or default to empty string
coalQty = safe_float_conversion(params.get('coalQty', ''))
elecConsump = safe_float_conversion(params.get('elecConsump', ''))
transportation = safe_float_conversion(params.get('transportation', ''))
deforestedArea = safe_float_conversion(params.get('deforestedArea', ''))
coalf = safe_float_conversion(params.get('coalf', ''))
elecf = safe_float_conversion(params.get('elecf', ''))
transf = safe_float_conversion(params.get('transf', ''))
deforestf = safe_float_conversion(params.get('deforestf', ''))
total = safe_float_conversion(params.get('total', ''))

# Create two columns for the layout
left_column, right_column = st.columns([2.1, 1.2])

# Display content in the left column
with left_column:
    st.markdown("<h1 style='margin-top: -0.5em; margin-bottom: 0.3em; color: #f39c12; font-size: 3.5rem;'>Personalized Suggestions to Offset Your Carbon Footprint</h1>", unsafe_allow_html=True)

    st.markdown("<h2>Your Carbon Footprint:</h2>", unsafe_allow_html=True)
    st.markdown(f"""Direct Emissions - :green[{coalf} tCO2e]""")
    st.write(f"""Electricity Emissions - :green[{elecf} tCO2e]""")
    st.write(f"""Transport Emissions - :green[{transf} tCO2e]""")
    st.write(f"""Deforestation Emissions - :green[{deforestf} tCO2e]""")
    st.write(f"""**Total Emissions - :green[{total} tCO2e]**""")

    if None not in [coalQty, elecConsump, transportation, deforestedArea]:
        # If all inputs are valid, proceed with prediction
        st.markdown("<h2>Tailored Suggestions:</h2>", unsafe_allow_html=True)

        # Display suggestions
        result = predict_strategy(coalQty, elecConsump, transportation, deforestedArea)
        st.write(f"**Strategy Labels:** {', '.join(result['strategy_labels'])}")

        # Show the list of suggestions
        for label, suggestions in zip(result['strategy_labels'], result['suggestions']):
            st.markdown(f"<h4>For {label},</h4>", unsafe_allow_html=True)
            for suggestion in suggestions:
                st.write(f"- {suggestion}")
            if label == 'Afforestation':
                st.markdown("<h4 style='color: green; font-size: 1.2rem;'>How does planting trees affect your Carbon Footprint?</h4>", unsafe_allow_html=True)
                num_trees = st.slider('Number of trees to plant:', min_value=0, max_value=5000, value=0, step=100)
                carbon_footprint_placeholder = st.empty()
                if num_trees > 0:
                    carbon_reduction = calculate_tree_carbon_offset(num_trees)
                    new_deforestf = deforestf - carbon_reduction
                    new_total_cf = total - carbon_reduction
                    new_deforestf = max(new_deforestf, 0)
                    new_total_cf = max(new_total_cf, 0)
                    st.write(f"**Number of trees planted - {num_trees}**")
                    st.write(f"**Carbon reduction from trees - :green[{carbon_reduction:.2f} tCO2e]**")
                    st.write(f"**New Deforestation Emissions after Afforestation - :green[{new_deforestf:.2f} tCO2e]**")
                    st.write(f"**New Total Emissions after Afforestation - :green[{new_total_cf:.2f} tCO2e]**")

    else:
        st.error("Invalid input values. Please enter valid numbers.")

with right_column:
    # Optionally, display another graph or summary
    st.subheader("Graphical Overview")
    fig, ax = plt.subplots()
    labels = ['Direct Emissions', 'Electricity Emissions', 'Transportation Emissions', 'Deforestation Emissions']
    sizes = [coalf, elecf, transf, deforestf]
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie chart is drawn as a circle.
    st.pyplot(fig)

    # Display a bar chart for the input values
    st.subheader("Input Values Visualization")
    input_data = {
        'Parameter': ['Coal Quantity', 'Electricity Consumption', 'Transportation', 'Deforested Area'],
        'Values': [coalQty, elecConsump, transportation, deforestedArea]
    }
    input_df = pd.DataFrame(input_data)
    st.bar_chart(input_df.set_index('Parameter'))

# Recommendations section
st.markdown("<h2>Further Recommendations:</h2>", unsafe_allow_html=True)
st.write("Explore more options for reducing your carbon footprint:")
st.write("- [Adopt Renewable Energy Solutions](#)")
st.write("- [Join Carbon Offset Programs](#)")
st.write("- [Implement Energy-Efficient Practices](#)")

# Add buttons for "Calculate Again"
st.markdown(
    """
    <div style="text-align: center; margin-top: 30px;">
        <a href="http://localhost:3000/calculate">
            <button style="background-color: #f39c12; color: #fff; border: none; padding: 10px 20px; border-radius: 5px; font-size: 16px; cursor: pointer;">
                Calculate Again
            </button>
        </a>
        <a href="http://localhost:3000/home">
            <button style="background-color: #3498db; color: #fff; border: none; padding: 10px 48px; border-radius: 5px; font-size: 16px; cursor: pointer; margin-left: 20px;">
                Home
            </button>
        </a>
        <a href="http://localhost:3000/index">
            <button style="background-color: #188753; color: #fff; border: none; padding: 10px 33px; border-radius: 5px; font-size: 16px; cursor: pointer; margin-left: 20px;">
                View Data
            </button>
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

# Footer section
st.markdown("""
    <footer style="text-align: center; margin-top: 50px;">
        <p style="font-size: 14px;">&copy; 2024 MineTrace. All rights reserved.</p>
    </footer>
""", unsafe_allow_html=True)