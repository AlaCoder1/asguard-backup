exclude_list = [4,5,3,6]

# def hani(exclude_list):
#     num_start = min(exclude_list)+1
#     while num_start < max(exclude_list):
#         if num_start in exclude_list:
#             num_start+=1
#         else:
#             new_list = exclude_list + [num_start]
#             new_list = sorted(new_list)
#             return new_list
#     exclude_list = exclude_list + [max(exclude_list)+1]
#     return exclude_list

def hani(exclude_list):
    num_start = min(exclude_list)+1
    while num_start < max(exclude_list):
        if num_start in exclude_list:
            num_start+=1
        else:
            return num_start
    return max(exclude_list)+1
print(hani(exclude_list))


import random

my_list = ['LAN', 'WAN', "LAN1", "WAN1"]
num_elements_to_select = 3

if num_elements_to_select <= len(my_list):
    random_elements = random.sample(my_list, num_elements_to_select)
    print(random_elements)
else:
    print("The number of elements to select is greater than the available list size.")
