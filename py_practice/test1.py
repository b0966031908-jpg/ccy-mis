def square(y):
  print("{} 的平方為 {}".format(y, y*y)) 

x = int(input("請輸入數字:"))
#x += int(100)
#print("您得到的是:",x)

if(x <= 0):
	print(f"您輸入的數字{x}小於等於0")
else:
	print(f"您輸入的數字{x}大於0")
	for i in range(1,x+1):
		#print(i, end=";")
		square(i)