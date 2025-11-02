import timeit
import random
from manual import sort_list_of_dicts_manual
from ai import sort_list_of_dicts_ai

# Generate large test dataset
large_data = [
    {'id': i, 'value': random.randint(1, 1000), 'name': f'item_{i}'} 
    for i in range(10000)
]

# Performance testing
manual_time = timeit.timeit(
    lambda: sort_list_of_dicts_manual(large_data, 'value'), 
    number=100
)

ai_time = timeit.timeit(
    lambda: sort_list_of_dicts_ai(large_data, 'value'), 
    number=100
)

print(f"Manual implementation time: {manual_time:.4f}s")
print(f"AI implementation time: {ai_time:.4f}s")
print(f"Performance ratio: {manual_time/ai_time:.2f}x")