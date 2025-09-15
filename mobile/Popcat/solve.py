import base64

# Get f1 and f2 from strings.xml
f1 = "MlUbKF4IXxQBVhgMWFcpIy4i"
f2 = "EEROVkwiAUYGBls/MgEGQz8BAUM=="

k1 = "meowmeowmeowmeow".encode()
k2 = "meowmeowmeowmeowmeow".encode()

c1 = base64.b64decode(f1)
c2 = base64.b64decode(f2)

# XOR ciphertext with key
h1 = bytes([d ^ k1[i % len(k1)] for i,d in enumerate(c1)])
h2 = bytes([d ^ k2[i % len(k2)] for i,d in enumerate(c2)])

# Reverse h1 and h2, then join them to get the flag
print((h1[::-1]+h2[::-1]).decode())
