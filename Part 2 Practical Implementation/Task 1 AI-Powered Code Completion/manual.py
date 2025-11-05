def sort_list_of_dicts_manual(data, key):
    """
    Sorts a list of dictionaries by a specified key using AI-generated logic.
    
    Args:
        data (list): List of dictionaries to sort
        key (str): Key to sort by
    
    Returns:
        list: Sorted list of dictionaries
    """
    if not data:
        return []
    
    # Validate that key exists in all dictionaries
    if not all(key in item for item in data):
        missing_keys = [i for i, item in enumerate(data) if key not in item]
        raise KeyError(f"Key '{key}' missing in items: {missing_keys}")
    
    try:
        # Sort the data using the specified key
        sorted_data = sorted(data, key=lambda x: x[key])
        return sorted_data
    except TypeError as e:
        raise TypeError(f"Cannot sort by key '{key}': {str(e)}")

# Test the function
test_data = [
    {'name': 'Alice', 'age': 30, 'score': 85},
    {'name': 'Bob', 'age': 25, 'score': 92},
    {'name': 'Charlie', 'age': 35, 'score': 78}
]
# Test cases
print("Original:", test_data)
print("Sorted by age:", sort_list_of_dicts_manual(test_data, 'age'))
print("Sorted by score:", sort_list_of_dicts_manual(test_data, 'score'))
print("Sorted by score (desc):", sort_list_of_dicts_manual(test_data, 'score')[::-1])
# Edge case: empty list
print("Empty list:", sort_list_of_dicts_manual([], 'age'))