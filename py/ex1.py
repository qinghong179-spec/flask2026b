def Split(x):
	x = x.split(",")
	school = x[0].replace("我是","")
	print(f"學校:{school}")
	print(f"姓名:{x[2]}")

#只有執行ex1.py時,以下程式才能執行
if __name__ == "__main__":
	Name = "我是靜宜大學,資管二B,洪詩晴"
	Split(Name)