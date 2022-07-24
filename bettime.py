import datetime

def bettingTime(mmss):

	basetime = datetime.time(int(mmss[0:2]),int(mmss[-2:]),00)

	dt2=datetime.datetime.combine(datetime.date.today(), basetime) - datetime.timedelta(minutes=2)

	return dt2.strftime("%H:%M")

def beforebettingTime(mmss):
	
	basetime = datetime.time(int(mmss[0:2]),int(mmss[-2:]),00)

	dt2=datetime.datetime.combine(datetime.date.today(), basetime) - datetime.timedelta(minutes=1)

	return dt2.strftime("%H:%M")


