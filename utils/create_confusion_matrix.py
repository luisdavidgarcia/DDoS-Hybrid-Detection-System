import matplotlib.pyplot as plt
import numpy as np

# Define your confusion matrix values
model_name = 'XGBoost'
# TN, FP, FN, TP
TN, FP, FN, TP = 930, 0, 2674, 1004
conf_matrix = np.array([[TN, FP], 
                        [FN, TP]])

# Create a figure and axis
fig, ax = plt.subplots(figsize=(6, 4))  # Set the figure size to 8x6

# Plot the confusion matrix using matshow
cax = ax.matshow(conf_matrix, cmap='Blues')

# Add color bar
fig.colorbar(cax)

# Add annotations to the cells with conditional color
for (i, j), value in np.ndenumerate(conf_matrix):
    color = 'white' if conf_matrix[i, j] > conf_matrix.max() / 2 else 'black'
    ax.text(j, i, f'{value}', ha='center', va='center', color=color)

# Set axis labels and ticks
ax.set_xlabel('Predicted')
ax.set_ylabel('Actual')

# Define custom ticks for x and y axes
ax.set_xticks([0, 1])
ax.set_xticklabels(['Normal (0)', 'Attack (1)'])

# Fix x-ticks to appear below the plot
ax.xaxis.set_ticks_position('bottom')

# Define custom ticks for y axes
ax.set_yticks([0, 1])
ax.set_yticklabels(['Normal (0)', 'Attack (1)'])

# Set the title
plt.title(f'Confusion Matrix for {model_name}')

# Show the plot
plt.show()