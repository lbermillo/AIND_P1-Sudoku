from collections import Counter

rows = 'ABCDEFGHI'
cols = '123456789'

assignments = []

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

# Get our diagonal units by populating a list with two lists, one list with the diagonal boxes from top-left to bottom-right
# and another list containing diagonal boxes from top-right to bottom-left
diagonal_units = [[rows[i]+cols[i] for i in range(len(rows))], [rows[-i-1]+cols[i] for i in range(len(rows))]]

unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    
    for unit in unitlist:
        # Get all values within a unit
        unit_values = [values[box] for box in unit]
        
        # Find duplicate values in the current unit with length of 2. This becomes the naked pair.
        naked_pair = [k for k, v in Counter(unit_values).items() if v == 2 and len(k) == 2]
        
        # If the naked pair exists in a unit, loop through each number in the naked pair value
        if naked_pair:
            for num in naked_pair[0]:
                
                # In each box within the unit, remove the number from the naked pair only if the box is unsolved and  
                # if the box value is not equal to the naked pair value  
                for box in unit:
                    if len(values[box]) > 1 and values[box] != naked_pair[0]:
                        values[box] = values[box].replace(num, '')        
    return values         


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    modified_grid = [g if g != '.' else '123456789' for g in grid ]
    return {k:v for (k, v) in zip(boxes, modified_grid)} 


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    if values:
        width = 1+max(len(values[s]) for s in boxes)
        line = '+'.join(['-'*(width*3)]*3)
        for r in rows:
            print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                          for c in cols))
            if r in 'CF': print(line)
        return


def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    # Obtain all the solved boxes in the current puzzle
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    
    # Loop through each box and obtain the box's value then eliminate this value from its unsolved peers
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            assign_value(values, peer, values[peer].replace(digit,''))
    return values    


def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    # Loop through each unit then through each number/digit in a completely unsolved value '123456789' in which this case, cols holds this value
    for unit in unitlist:
        for number in cols:
            
            # Go through each box and check if the value of that box houses the current number
            potential_fit = [box for box in unit if number in values[box]]
            
            # If this number is only contained in a single box within a unit, replace the value of the box to that number
            if len(potential_fit) == 1:
                values[potential_fit.pop()] = number
    return values


def reduce_puzzle(values): 
    stop = False
    
    # Loop through the reduction methods until a solution is found or 
    # we cannot further solve the problem
    while not stop:
        
        # Get the number of solved boxes before we apply reducing methods, we will use this as a metric for our stopping condition
        solved_values_before = check_number_of_solved_values(values) 
        
        # Apply constraint propagation methods to reduce the puzzle
        values = eliminate(values)
        values = only_choice(values)
        
        # Change the stop condition to True, if no changes are found in the original puzzle to the reduced puzzle
        # by comparing the number of solved values before the reduction was applied with the number of solved values after the reduction
        stop = solved_values_before == check_number_of_solved_values(values) 
        
        # If a box does not contain any values at all, return false
        if check_number_of_solved_values(values, length=0):
            return False
            
    return values


def check_number_of_solved_values(values, length=1):
    return len([value for value in values.values() if len(value) == length])


def search(values):
    # We want to reduce the the current puzzle first then check if the puzzle had been solved or not. 
    solved = reduce_puzzle(values)
    
    if not solved: return False
    
    # Check that all values in the puzzle have a length of 1 to indicate that the puzzle had been completely solved, 
    # in which case we return the solved puzzle.
    if all(len(value) == 1 for value in values.values()): return solved
    
    # Find an unsolved box with the fewest numbers to try to solve the puzzle through recursion
    box, box_value = min([(box, box_value) for (box, box_value) in values.items() if len(box_value) > 1])
    
    # Try every number in the chosen box's value and attempt to solve the puzzle
    for number in box_value:
        
        # Create a new variable and copy the current puzzle 
        new_values = values.copy()
        
        # Try out the number from the box in the same box in our copy 
        # and attempt to solve the copied puzzle through recursion
        assign_value(new_values, box, number)
        attempt = search(new_values)
        
        # Only return attempt if a solution had been found
        if attempt: return attempt


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    solution = search(values)
    
    return solution if solution else False 


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    #'9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................'
    display(solve(diag_sudoku_grid))    
    
    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
