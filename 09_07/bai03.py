numbers=[12,5,8,19,20,11,7,14,3]
so_chan = []
so_le = []
for num in numbers:
    if num % 2 == 0:
        so_chan.append(num)
    else:
        so_le.append(num)
tong_chan = sum(so_chan)
if len(so_le)>0:
    trung_binh_le=sum(so_le)/len(so_le)
else:
    trung_binh_le = 0
print("So chan:",so_chan)
print("Tong so chan:",tong_chan)
print("So le:",so_le)
print("Trung binh so le:",trung_binh_le)
    