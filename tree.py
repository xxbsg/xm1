from datetime import datetime

time=datetime.now()
a=time.timetuple()
b=time.date()
print(b.replace(day=1)) #替换日
print(b.replace(day=a.tm_mday-1))

