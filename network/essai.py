# def convert_to_subnet_mask(bits):
#     cidr_bits = [str(int(bits[i:i+8], 2)) for i in range(0, 32, 8)]
#     if cidr_bits < 0 or cidr_bits > 32:
#         return "Invalid CIDR bits"
#     binary_mask = "1" * cidr_bits + "0" * (32 - cidr_bits)
#     subnet_mask= ".".join([binary_mask[i:i+8] for i in range(0, 32, 8)])
#     return subnet_mask


# cidr_prefix = 32
# print(convert_to_subnet_mask(cidr_prefix))
def convert_to_subnet_mask(bits):
    cidr_bits = int(bits)
    if cidr_bits < 0 or cidr_bits > 32:
        return "Invalid CIDR bits"
    
    binary_mask = "1" * cidr_bits + "0" * (32 - cidr_bits)
    subnet_mask = ".".join([str(int(binary_mask[i:i+8], 2)) for i in range(0, 32, 8)])
    return subnet_mask
cidr_prefix = 32
print(convert_to_subnet_mask(cidr_prefix))