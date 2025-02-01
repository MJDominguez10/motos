import pandas as pd
import statsmodels.api as sm
from datetime import datetime

# Load the dataset
file_path = "/Users/monkiky/Desktop/motos_collect/data2plot/cleaned_autotrader_data.csv"
df = pd.read_csv(file_path)

# Keep only necessary columns
df = df[['Make', 'Model', 'Year', 'Price']]

# Remove rows with missing values in the required columns
df = df.dropna(subset=['Make', 'Model', 'Year', 'Price'])

# Convert Year to integer
df['Year'] = df['Year'].astype(int)

# Get current year
current_year = datetime.now().year

# Compute the age of the motorcycle
df['Age'] = current_year - df['Year']

# Step 1: Identify models without data for 2024 or 2025 (consider these as new)
models_without_new_bike_data = df.groupby('Model').apply(
    lambda x: not any(x['Year'].isin([2024, 2025]))  # Check if there are no new bikes (Year 2024 or 2025)
).loc[lambda x: x].index.tolist()

print(f"Models without new bike data (2024 or 2025): {models_without_new_bike_data}")

# Step 2: Calculate depreciation for all models, including those without new data
model_results = []
for (make, model), group in df.groupby(['Make', 'Model']):
    # Check if there's enough data for this model (at least 2 entries for regression)
    if len(group) > 1:
        X = group[['Age']]
        y = group['Price']
        
        X = sm.add_constant(X)  # Add constant term for intercept
        reg_model = sm.OLS(y, X).fit()  # Ordinary Least Squares (OLS) Regression
        
        depreciation_rate = reg_model.params['Age']  # Slope (Price drop per year)
        r_squared = reg_model.rsquared  # Model fit quality

        # Store model-level results
        model_results.append({
            'Make': make,
            'Model': model,
            'Depreciation Score': depreciation_rate,
            'R-squared': r_squared
        })

# Convert model-level results to DataFrame
model_df = pd.DataFrame(model_results)

# Sort by Depreciation Score (ascending order: lowest depreciation first)
model_df = model_df.sort_values(by='Depreciation Score', ascending=True)

# Step 3: Remove models that don't have data for 2024 or 2025 bikes
model_df = model_df[~model_df['Model'].isin(models_without_new_bike_data)]

# Step 4: Calculate brand-level average depreciation (using the models left after removing those without new bike data)
brand_results = model_df.groupby('Make')['Depreciation Score'].mean().reset_index()

# Sort by Average Depreciation (ascending order: lowest depreciation first)
brand_results = brand_results.sort_values(by='Depreciation Score', ascending=True)

# Save the sorted model-level results to CSV
output_model_path = "/Users/monkiky/Desktop/motos_collect/data2plot/depreciation_by_model.csv"
model_df.to_csv(output_model_path, index=False)

# Save the sorted brand-level results to CSV
output_brand_path = "/Users/monkiky/Desktop/motos_collect/data2plot/depreciation_by_brand.csv"
brand_results.to_csv(output_brand_path, index=False)

print(f"Model-level depreciation sorted and saved to {output_model_path}")
print(f"Brand-level depreciation sorted and saved to {output_brand_path}")
