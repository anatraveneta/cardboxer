import sys
from opt_cardboard_alg import *

# Function to load widths and heights from a file
def load_dimensions_from_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    
    # Clean up each line to remove any indentation or extra spaces
    cleaned_data = ""
    for line in lines:
        cleaned_data += line.strip() + "\n"  # Remove leading/trailing spaces and add newline
    
    # Execute the cleaned data to load widths and heights
    variables = {}
    exec(cleaned_data, variables)
    return variables['widths'], variables['heights']

# Example usage with the Problem class
if __name__ == "__main__":
    # Check if filename is provided as a command-line argument
    if len(sys.argv) < 2:
        print("Usage: python run_problem.py <filename>")
        sys.exit(1)

    # Get the filename from command-line arguments
    filename = sys.argv[1]

    # Container dimensions
    container_width = 1490
    container_height = 5000

    # Load dimensions from the specified file
    widths, heights = load_dimensions_from_file(filename)

    # List of (width, height) tuples instead of Rectangle objects
    rectangle_dimensions = list(zip(widths, heights))

    # Initialize Problem with dimensions rather than Rectangle instances
    problem = Problem(rectangle_dimensions, container_width, container_height)
    
    best_solution, best_waste = problem.solve()

    # Calculate waste and print result
    print(f"Final calculated waste: {best_waste} mm²")
    
    # Print the DataFrame before drawing
    best_solution.print_table()
    
    # Draw the best solution
    best_solution.show_diagram()
