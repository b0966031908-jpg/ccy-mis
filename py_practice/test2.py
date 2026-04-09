def compute():
    x = input("請輸入西元生日(格式:yyyymmdd): ")
    t = 0
    
    for char in x:
        t += int(char)
        

    print(f"您的西元生日8位數相加為 : {t}")
compute()
