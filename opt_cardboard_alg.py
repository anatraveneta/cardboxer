import itertools
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle as RectPatch
import sys

# Representation of the rectangle with rotation attributes and a unique ID
class Rectangle:
    def __init__(self, rect_id, width, height, rotated=False):
        self.id = rect_id  # Unique identifier for the rectangle
        self._width = width  # Private attribute for width
        self._height = height  # Private attribute for height
        self.rotated = rotated

    # Method to rotate the rectangle, swapping width and height
    def rotate(self):
        self.rotated = not self.rotated

    # Method to get the rectangle dimensions, considering its rotation status
    def get_dimensions(self):
        if self.rotated:
            return self._height, self._width  # Returns swapped dimensions if rotated
        return self._width, self._height  # Returns original dimensions if not rotated

    # Property to access the current width
    @property
    def width(self):
        return self.get_dimensions()[0]

    # Property to access the current height
    @property
    def height(self):
        return self.get_dimensions()[1]

# Solution class to store the ordered placement of rectangles in rows and containers
class Solution:
    def __init__(self, rectangle_placements, total_waste, total_rows, container_width, container_height):
        self.rectangle_placements = rectangle_placements  # List of placements [(rect_id, container, row, rotated, width, height, area)]
        self.total_waste = total_waste  # Total waste area
        self.total_rows = total_rows  # Total number of rows
        self.container_width = container_width  # Container width for visualization
        self.container_height = container_height  # Container height for visualization

    # Method to display the solution as a DataFrame with rectangle details
    def print_table(self):
        data = []

        # Populate data with rectangle placement details
        for placement in self.rectangle_placements:
            rect_id, container_num, row_num, rotated, width, height, area = placement
            data.append([rect_id, container_num, row_num, rotated, width, height, area])

        # Create DataFrame, order by specified columns, and exclude area from display
        df = pd.DataFrame(data, columns=['Rectangle ID', 'Container', 'Row', 'Rotated', 'Width', 'Height', 'Area'])
        df = df.sort_values(by=['Container', 'Row', 'Height'], ascending=[True, True, False])
        df = df.drop(columns=['Area'])

        # Display DataFrame with solution information and total waste
        print(df)
        print(f"Total Waste: {self.total_waste} mm²")
        print(f"Total Rows Used: {self.total_rows}")

    # Method to display the solution as a DataFrame with rectangle details
    def print_table(self):
        data = []

        # Populate data with rectangle placement details
        for placement in self.rectangle_placements:
            rect_id, container_num, row_num, rotated, width, height, area = placement
            data.append([rect_id, container_num, row_num, rotated, width, height, area])

        # Create DataFrame, order by specified columns, and exclude area from display
        df = pd.DataFrame(data, columns=['Rectangle ID', 'Container', 'Row', 'Rotated', 'Width', 'Height', 'Area'])
        df = df.sort_values(by=['Container', 'Row', 'Height'], ascending=[True, True, False])
        df = df.drop(columns=['Area'])

        # Display DataFrame with solution information and total waste
        print(df)
        print(f"Total Waste: {self.total_waste} mm²")
        print(f"Total Rows Used: {self.total_rows}")

    # Method to visualize the solution as a diagram with actual used container dimensions
    def show_diagram(self, title="Packing Solution Diagram"):
        num_containers = max([placement[1] for placement in self.rectangle_placements]) + 1
        _, axes = plt.subplots(1, num_containers, figsize=(10 * num_containers, 8))

        if num_containers == 1:
            axes = [axes]  # Ensure consistent indexing for a single container

        for container_num in range(num_containers):
            ax = axes[container_num]

            # Collect rows for this container
            container_rows = [p for p in self.rectangle_placements if p[1] == container_num]
            
            # Calculate maximum height and width used in this container
            max_height_used = sum([max([rect[5] for rect in container_rows if rect[2] == row_num]) for row_num in set(p[2] for p in container_rows)])
            max_width_used = max([sum([rect[4] for rect in container_rows if rect[2] == row_num]) for row_num in set(p[2] for p in container_rows)])

            # Set container dimensions for display
            ax.set_xlim(0, self.container_width)
            ax.set_ylim(0, self.container_height)

            # Display actual used width and height for this container
            ax.text(max_width_used / 2, self.container_height + 80, f"Width Used: {max_width_used}", 
                    ha='center', va='top', fontsize=12, color='black')
            ax.text(self.container_width + 50, max_height_used / 2, f"Height Used: {max_height_used}", 
                    ha='left', va='center', rotation='vertical', fontsize=12, color='black')

            # Start placing rectangles from the bottom of the container
            current_y = 0
            for row_num in sorted(set([p[2] for p in container_rows])):
                current_x = 0
                row_rectangles = [rect for rect in container_rows if rect[2] == row_num]
                row_height = max([rect[5] for rect in row_rectangles])  # Max height in this row
                
                for _, _, _, _, width, height, _ in row_rectangles:
                    # Draw rectangle with text showing dimensions
                    ax.add_patch(RectPatch((current_x, current_y), width, height, edgecolor='black', facecolor='cyan'))
                    ax.text(current_x + width / 2, current_y + height / 2, f'{width}x{height}', ha='center', va='center', fontsize=10)

                    # Update x position for the next rectangle in the row
                    current_x += width

                # Update y position for the next row
                current_y += row_height

            # Add container label
            ax.text(self.container_width / 2, -150, f"Container {container_num + 1}", ha='center', va='top', fontsize=14, color='red', fontweight='bold')
            ax.set_aspect('equal')

        plt.suptitle(title)
        plt.tight_layout()
        plt.show()


# Problem class that uses heuristic and brute-force combination to solve rectangle packing
class Problem:
    def __init__(self, rectangles, container_width, container_height):
        # Assign unique IDs to rectangles upon Problem creation and prepare initial DataFrame
        self.rectangles = [Rectangle(i, rect[0], rect[1]) for i, rect in enumerate(rectangles)]
        self.container_width = container_width
        self.container_height = container_height
        self.rect_df = pd.DataFrame({
            'id': [rect.id for rect in self.rectangles],
            'width': [rect._width for rect in self.rectangles],
            'height': [rect._height for rect in self.rectangles],
            'area': [rect._width * rect._height for rect in self.rectangles]
        })

    # Method to find the optimal arrangement of rectangles with minimal waste
    def solve(self):
        best_solution = None
        min_waste = float('inf')
        max_rows_in_valid_solution = 0

        try:
            # Generate all possible rotation combinations for the rectangles' starting row positions
            num_rectangles = len(self.rectangles)
            rotation_combinations = itertools.product([0, 1], repeat=num_rectangles)

            for i, rotations in enumerate(rotation_combinations):
                # Stop the process if we exceed the max allowed number of rows for valid solutions
                if max_rows_in_valid_solution > 0 and i >= (2 ** max_rows_in_valid_solution):
                    break

                solution, waste = self.try_rotation_combination(rotations)
                
                if solution:
                    if max_rows_in_valid_solution < solution.total_rows:
                        max_rows_in_valid_solution = solution.total_rows  # Update maximum rows in valid solutions
                    if waste < min_waste:
                        best_solution = solution
                        min_waste = waste
                        # Show the current best waste dynamically
                        sys.stdout.write(f"\rBest waste to date: {min_waste} mm², with {solution.total_rows} rows.")
                        sys.stdout.flush()

            print()  # Move to the next line after loop completes

        except KeyboardInterrupt:
            # Handle user interruption by printing the best solution so far
            print("\n\nProcess interrupted by user.")
            if best_solution:
                print("Best solution found so far:")
                best_solution.print_table()
                best_solution.show_diagram(title="Best Solution So Far")

        # Return the best solution found (even if interrupted)
        return best_solution, min_waste


    # Method to apply a specific rotation pattern and attempt to place rectangles
    def try_rotation_combination(self, rotations):
        remaining_rect_df = self.rect_df.copy()  # Clone DataFrame of remaining rectangles

        rectangle_placements = []  # Track rectangle ID placements in (rect_id, row, rotated, width, height, area) format
        row_num = 0  # Cumulative row index across all rows

        for rotation in rotations:
            if remaining_rect_df.empty:
                break
            
            # Select the largest rectangle by area and apply rotation if specified
            largest_rect_id = remaining_rect_df.loc[remaining_rect_df['area'].idxmax(), 'id']
            largest_rect = next(rect for rect in self.rectangles if rect.id == largest_rect_id)
            if rotation == 1:
                largest_rect.rotate()

            # If the largest rectangle's width exceeds container width, discard this configuration
            if largest_rect.width > self.container_width:
                return None, float('inf')

            # Initialize a new row with the largest rectangle
            current_row = [largest_rect]
            row_height = largest_rect.height
            row_width_used = largest_rect.width
            remaining_rect_df = remaining_rect_df[remaining_rect_df['id'] != largest_rect.id]

            # Register placement of the largest rectangle with rotation status and dimensions
            rectangle_placements.append((largest_rect.id, None, row_num, largest_rect.rotated, largest_rect.width, largest_rect.height, largest_rect.width * largest_rect.height))

            # Call the fill_row function to fill the row with remaining rectangles
            row_width_remaining = self.container_width - row_width_used
            row_area_remaining = (self.container_width - largest_rect.width) * row_height
            current_row, remaining_rect_df = self.fill_row(
                row_height, row_width_remaining, row_area_remaining, current_row, remaining_rect_df, rectangle_placements, row_num
            )

            row_num += 1  # Increment row number across containers

        # If no valid placement is found, return None with -1 rows
        if not rectangle_placements:
            return None, -1

        # Assign rows to containers based on row heights and calculate waste
        waste, updated_placements = self.assign_containers(rectangle_placements)
        total_rows = row_num
        return Solution(updated_placements, waste, total_rows, self.container_width, self.container_height), waste


    # Method to assign containers based on cumulative row heights and calculate remaining waste per container
    def assign_containers(self, rectangle_placements):
        container_num = 0
        current_height = 0
        updated_placements = []
        total_waste = 0

        for row_num in sorted(set([placement[2] for placement in rectangle_placements])):
            # Filter rows by the current row number
            row_rects = [p for p in rectangle_placements if p[2] == row_num]
            row_height = max(rect[5] for rect in row_rects)  # Max height among all rectangles in the row
            row_area = sum(rect[6] for rect in row_rects)  # Sum of areas of all rectangles in the row

            # Compute row waste
            row_waste = (self.container_width * row_height) - row_area
            total_waste += row_waste

            # Start a new container if adding this row exceeds container height
            if current_height + row_height > self.container_height:
                total_waste += (self.container_height - current_height) * self.container_width  # Add remaining space in container as waste
                container_num += 1
                current_height = 0  # Reset height for new container

            # Assign container number to each rectangle in the current row
            for rect_id, _, row_num, rotated, width, height, area in row_rects:
                updated_placements.append((rect_id, container_num, row_num, rotated, width, height, area))

            # Update cumulative container height
            current_height += row_height

        # Final container waste if container is not fully utilized. You can comment this line if you think you can
        # re-use an uncomplete container.
        total_waste += (self.container_height - current_height) * self.container_width
        return total_waste, updated_placements

    # Method to fill a row with remaining rectangles that fit within the specified width and height constraints
    def fill_row(self, row_height, row_width_remaining, row_area_remaining, current_row, remaining_rect_df, rectangle_placements, row_num):
        # Filter rectangles by area that fits within remaining row area
        candidate_df = remaining_rect_df[remaining_rect_df['area'] <= row_area_remaining]

        # If the filtered DataFrame is empty, return the row as is
        if candidate_df.empty:
            return current_row, remaining_rect_df

        # Duplicate rows for both orientations (original and rotated) and update width/height accordingly
        candidate_df = pd.concat([candidate_df.assign(rotated=False), candidate_df.assign(rotated=True)])
        
        # Retrieve dimensions directly using Rectangle objects' get_dimensions
        candidate_df[['width', 'height']] = candidate_df.apply(
            lambda x: pd.Series(
                next(rect for rect in self.rectangles if rect.id == x['id']).get_dimensions() if not x['rotated'] 
                else next(rect for rect in self.rectangles if rect.id == x['id']).get_dimensions()[::-1]
            ), axis=1
        )
        
        # Calculate the height difference from the current row height
        candidate_df['height_diff'] = abs(candidate_df['height'] - row_height)
        
        # Sort candidates by ascending height difference and descending width
        candidate_df = candidate_df.sort_values(by=['height_diff', 'width'], ascending=[True, False])

        # Try to add rectangles to the row in sorted order based on fitting within row width
        for _, rect_data in candidate_df.iterrows():
            if rect_data['width'] <= row_width_remaining:
                rect_id = rect_data['id']
                rect = next(r for r in self.rectangles if r.id == rect_id)
                
                # Rotate rectangle if required
                if rect_data['rotated']:
                    rect.rotate()
                
                # Add rectangle to current row, update row dimensions, and remove from remaining DataFrame
                current_row.append(rect)
                row_width_remaining -= rect.width
                row_height = max(row_height, rect.height)
                row_area_remaining -= rect.width * row_height
                remaining_rect_df = remaining_rect_df[remaining_rect_df['id'] != rect.id]

                # Register placement of the rectangle with rotation and dimensions
                rectangle_placements.append((rect.id, None, row_num, rect.rotated, rect.width, rect.height, rect.width * rect.height))

                # Restart the loop to consider the next candidate for the updated row state
                return self.fill_row(row_height, row_width_remaining, row_area_remaining, current_row, remaining_rect_df, rectangle_placements, row_num)

        return current_row, remaining_rect_df