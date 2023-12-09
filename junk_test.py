row = "AArch64 rev 2 (aarch64) 8 2,320 898 NA Unknown Unknown"
headers = ['CPU name', 'Cores', 'CPU Mark', 'Thread Mark', 'TDP(W)', 'Socket', 'Category']
_list = row.split()
temp = {}
for i in range(len(headers) - 1):
    temp.update({headers[-1 - i]: _list.pop(-1)})

temp.update({headers[0]: " ".join(_list)})
print(temp)
