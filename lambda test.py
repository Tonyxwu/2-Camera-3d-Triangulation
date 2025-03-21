n = int(input())

def intToBinary(n):
	return list(map(int,bin(n)[2:])) 

for i in range(n):
	lovers = list(map(int, input().split()))
	bigLover = 0
	smallLover = 0
	if lovers[0] < lovers[1]:
		bigLover = lovers[1]
		smallLover = lovers[0]
	else:
		bigLover = lovers[0]
		smallLover = lovers[1]

	bigLover = intToBinary(bigLover)
	smallLover = intToBinary(smallLover)
	print (bigLover)
	print (smallLover)

	#going small to big
