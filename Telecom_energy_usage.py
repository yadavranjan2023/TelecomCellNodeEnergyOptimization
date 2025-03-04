# This code processes data in batches at regular intervals, allowing for continous batching.
# Batches are processed wihtin a loop, and latency, throughput, and cost aer calculated for each batch.
# This code uses batch size of 5, but you can adjust the batch size to fit your requirements
#
################################################################################

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import time

class SlidingWindow:
def __init__(self, window_size):
self.window_size = window_size
self.data = []

def add_data(self, new_data):
self.data.append(new_data)
if len(self.data) > self.window_size:
self.data.pop(0)
return np.array(self.data)

class RotationBuffer:
def __init__(self, buffer_size):
self.buffer_size = buffer_size
self.buffer = np.empty((0, buffer_size), float)

def add_data(self, new_data):
if self.buffer.shape[0] < self.buffer_size:
self.buffer = np.vstack((self.buffer, new_data))
else:
self.buffer[:-1] = self.buffer[1:]
self.buffer[-1] = new_data

# Initialize sliding windows and rotation buffer
window_size = 50
buffer_size = 10
mmWave_window = SlidingWindow(window_size)
spectrum_buffer = RotationBuffer(buffer_size)

# Load your dataset containing millimeter wave data and energy consumption
np.random.seed(0)
num_samples = 1000
mmWave_data = np.random.rand(num_samples, 10) # 10 features representing mmWave data
signal_strength = np.random.rand(num_samples) * 100 # Signal strength in arbitrary units
user_density = np.random.randint(1, 1000, num_samples) # Number of users in the cell
interference_level = np.random.rand(num_samples) * 100 # Interference level in arbitrary units
energy_consumption = np.random.rand(num_samples) * 100 # Energy consumption in arbitrary units

# Add initial data to sliding window and rotation buffer
for i in range(num_samples):
mmWave_window.add_data(mmWave_data[i])
spectrum_buffer.add_data(mmWave_data[i])

# Combine data into a single DataFrame
data = pd.DataFrame(mmWave_window.data, columns=[f'feature_{i+1}' for i in range(10)])
data['signal_strength'] = signal_strength[:window_size]
data['user_density'] = user_density[:window_size]
data['interference_level'] = interference_level[:window_size]
data['energy_consumption'] = energy_consumption[:window_size]

# Split data into training and testing sets
X = data.drop('energy_consumption', axis=1)
y = data['energy_consumption']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a linear regression model
model = LinearRegression()
model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = model.predict(X_test)

# Calculate mean squared error
mse = mean_squared_error(y_test, y_pred)
print(f'Mean Squared Error: {mse:.2f}')

# Display model coefficients
coefficients = pd.DataFrame(model.coef_, X.columns, columns=['Coefficient'])
print(coefficients)

# Function to optimize energy usage based on new mmWave data, while tracking inference cost, throughput, and latency
def optimize_energy_usage(new_mmWave_data, cache, batch_size):
num_batches = len(new_mmWave_data) // batch_size + (1 if len(new_mmWave_data) % batch_size > 0 else 0)

start_time = time.time()

# Process data in batches
for i in range(num_batches):
batch_start = i * batch_size
batch_end = min((i + 1) * batch_size, len(new_mmWave_data))
batch_data = new_mmWave_data[batch_start:batch_end]

# Check if data is in cache
if cache is not None:
batch_data = cache[batch_start:batch_end]

# Predict energy consumption for the batch
predicted_energy = model.predict(batch_data)

# Measure latency (in seconds)
latency = time.time() - start_time

# Throughput (inferences per second)
throughput = len(batch_data) / latency

# Cost of inference (example cost calculation)
cost_per_inference = 0.01 # Arbitrary cost per inference
total_cost = cost_per_inference * len(batch_data)

print(f'Predicted Energy Usage for Batch {i + 1}: {predicted_energy}')
print(f'Latency for Batch {i + 1}: {latency:.4f} seconds')
print(f'Throughput for Batch {i + 1}: {throughput:.2f} inferences/second')
print(f'Total Cost for Batch {i + 1}: ${total_cost:.2f}')

# Example usage with new data
new_mmWave_data = np.random.rand(15, 13) # 15 new samples of mmWave data with 13 features (10 mmWave + 3 telecom-specific)

# Simulate cache (for this example, we'll use the same new_mmWave_data as cache)
cache = new_mmWave_data

# Define batch size for continuous batching
batch_size = 5

optimize_energy_usage(new_mmWave_data, cache, batch_size)
