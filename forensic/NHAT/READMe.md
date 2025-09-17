# NHAT

Challenge author: zach 

Challenge file: [https://drive.google.com/file/d/1q4cYE5t-yaJpS70K6n-JqiL3EsddDmEJ/view?usp=sharing](https://drive.google.com/file/d/1q4cYE5t-yaJpS70K6n-JqiL3EsddDmEJ/view?usp=sharing) 

## Solution:

#### NHAT 1
Step 1: Navigate to the Chrome browser history file
Path: NHAT\DESKTOP-GBETLNV\C\Users\zach\AppData\Local\Google\Chrome\User Data\Default\History
Flag: `gctf{w4Rm!ng_Up_WItH_BROw$3r_HIsToRY}`

#### NHAT 2
Step 1: Go through the URL links from the browser history one by one
Step 2: Find the flag in the GitHub repository: https://github.com/ourokronii-hololive/SharpUp
Flag: `gctf{57E4LINg_froM_Gh0STPACk}`

### NHAT 3
Step 1: Find the payload in the same GitHub repository from NHAT 2
Path: SharUp/SharUp/SharUp.csproj
Step 2: Analyze the payload containing 3 variables (b, c, d) that appear to be base64 encoded
Step 3: Concatenate the strings in order: b, d, c
Step 4: Base64 decode the concatenated string to get another payload
Step 5: Decrypt the obfuscated strings in sequence:

Reverse the string
AES-CBC decryption (function D)
Reverse the output string again
Base64 decode it

Step 6: Decrypt 4 URL-encoded URLs using password: h9B0p#q1q5Z>
Step 7: Decode the base64 encrypted URL at https://rlim.com/wkrDnK1Lyc/raw using second password: 9XkOr4Z37g>?@J4
Step 8: Visit the resulting link: https://github.com/tamtender/Face-Recognition-using-Python-PYQT5/releases
Flag: `gctf{MA5qU3Rad!N6_!n_inn0c3NcE}`

### NHAT 4
Step 1: Download the 7zip file from the URL found in NHAT 3
Step 2: Extract the 7zip file using password: 4vum2sP3w&3#
Step 3: Extract AppVClient.exe from AppVClient.7z
Step 4: Run strings on the executable and identify it as a PyInstaller-packaged Python executable (contains zPYZ-00.pyz)
Step 5: Use pyinstxtractor.py to extract the archive and retrieve the original .pyc files
Step 6: Navigate to the extracted folder and use strings + grep to search for the flag format "gctf"

Flag: `gctf{No_h0nOuR_AmOn9_TH13v3S}` 


