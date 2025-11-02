def sort_list_of_dicts_manual(data, key):
    """
    Sorts a list of dictionaries by a specific key.
    
    Args:
        data (list): List of dictionaries
        key (str): Key to sort by
    
    Returns:
        list: Sorted list
    """
    return sorted(data, key=lambda x: x[key])

def sort_list_of_dicts_multikey(data, keys):
    """Sort by multiple keys"""
    return sorted(data, key=lambda x: tuple(x[k] for k in keys))

def sort_list_of_dicts_nested(data, key_path):
    """Sort by nested key using path like 'user.profile.age'"""
    def get_nested_value(item, path):
        keys = path.split('.')
        for k in keys:
            item = item[k]
        return item
    return sorted(data, key=lambda x: get_nested_value(x, key_path))

# Test data
test_data = [
    {'name': 'Alice', 'age': 30, 'score': 85},
    {'name': 'Bob', 'age': 25, 'score': 92},
    {'name': 'Charlie', 'age': 35, 'score': 78}
]

# Test the functions
if __name__ == "__main__":
    print("Sorted by age:")
    print(sort_list_of_dicts_ai(test_data, 'age'))
    
    print("\nSorted by multiple keys (score, name):")
    print(sort_list_of_dicts_multikey(test_data, ['score', 'name']))
