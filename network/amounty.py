import random

def get_unique_random_exclude(exclude_list, min_val, max_val):
    while True:
        random_num = random.randint(min_val, max_val)
        if random_num not in exclude_list:
            return random_num

exclude_list = []
min_val = 1
max_val = 20

random_excluded = get_unique_random_exclude(exclude_list, min_val, max_val)
print(random_excluded)
exclude_list.append(random_excluded)
a=exclude_list
print(a)