import sys

sys.set_int_max_str_digits(100000)

def szudzik_pack(x, y):
    if x >= y:
        return x * x + x + y
    else:
        return y * y + x

def obfuscate_payload(data):
    length = len(data)
    if length == 1:
        return data[0]
    elif length == 2:
        return szudzik_pack(data[0], data[1])
    
    mid = length // 2
    return szudzik_pack(obfuscate_payload(data[:mid]), obfuscate_payload(data[mid:]))

if __name__ == "__main__":
    with open("flag.txt", "rb") as f:
        flag = list(f.read().strip())
    
    signature = obfuscate_payload(flag)
    print("Obfuscated payload signature:")
    print(signature)
