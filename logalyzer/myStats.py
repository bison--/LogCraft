#!/usr/var/python
from datetime import datetime
from datetime import timedelta
import time


startTime = time.time()
#2013-01-21 03:23:33 [INFO] [AuthMe] NAME logged in!
#2013-01-21 04:59:01 [INFO] Connection reset
#2013-01-21 04:59:01 [INFO] NAME lost connection: disconnect.endOfStream
#'/var/minecraftServer/theWorld/server.log.bak', 
logFiles = ('/var/minecraftServer/theWorld/server.log',)

logFileStr = ''

for logFile in logFiles:
	logFileH = open(logFile, 'r')
	logFileStr += logFileH.read()
	logFileH.close()

logFileAr = logFileStr.split('\n')

def getUsers(logFileAr):
	users = []
	
	for r in logFileAr:
		if '[AuthMe]' in r and 'logged in' in r:
			cols = r.split(' ')
			if len(cols) >= 4 and not cols[4] in users:
				users.append(cols[4])
	return users

def getRelevantEntrys(logFileAr):
	relEntrys = []
	relStuff = ['lost connection', 'logged in']
	for r in logFileAr:
		for entry in relStuff:
			if entry in r:
				relEntrys.append(r)
	
	return relEntrys

def getUserLogins(username, entrysAr):
	count = 0
	for r in entrysAr:
		if username in r and 'logged in' in r:
			count += 1
	return count

def getUserPlaytime(username, entrysAr):
	fmt = '%Y-%m-%d %H:%M:%S'
	#d1 = datetime.strptime('2010-01-01 17:31:22', fmt)
	#d2 = datetime.strptime('2010-01-03 17:31:22', fmt)
	#print (d2-d1).days * 24 * 60
	
	mode = 0
	seconds = 0
	lastStart = None
	for r in entrysAr:
		if username in r:
			col = r.split(' ')
		
			if 'logged in' in r:
				lastStart = datetime.strptime(col[0] + ' ' + col[1], fmt)
			elif 'lost connection' in r:
				dt = datetime.strptime(col[0] + ' ' + col[1], fmt)
				if lastStart != None:
					seconds += (dt - lastStart).seconds
				else:
					print 'WARNING! Logout without login:', r
	
	return str(timedelta(seconds=seconds))
	#datetime.timedelta(0, 65)
	#return time.strftime('%d %H:%M:%S', timedelta(0, seconds))
	#return time.strftime('%d %H:%M:%S', time.gmtime(seconds))

def getUserLastLogin(username, entrysAr):
	for r in reversed(entrysAr):
		if username in r:
			cols = r.split(' ')
			return cols[0] +' '+ cols[1]

def getUserTp(username, entrysAr):
	count = 0
	for r in entrysAr:
		if username in r and '/tp' in r:
			count += 1
	return count
	
def getUserWarps(username, entrysAr):
	count = 0
	for r in entrysAr:
		if username in r and '/warp' in r:
			count += 1
	return count


def getDateFromEntry(entry):
	tmp = entry.split(' ')
	if len(tmp) >= 2:
		return tmp[0] +' '+ tmp[1]
	else:
		print 'NO DATE'
		return 'NO DATE'
	
relevantEntrys = getRelevantEntrys(logFileAr)
users = getUsers(relevantEntrys)


print '# Zeilen:', len(logFileAr)
print '# Erster Eintrag vom:', getDateFromEntry(logFileAr[0]) #logFileAr[0].split(' ')[0], logFileAr[0].split(' ')[1]
print '# Letzer Eintrag vom:', getDateFromEntry(logFileAr[len(logFileAr)-2])
for user in users:
	print ''
	print (' '+ user +' ').center(23, '#') #'#'* 10, user, '#'*10
	print 'logins:',  getUserLogins(user, relevantEntrys)
	print 'last login:',  getUserLastLogin(user, relevantEntrys)
	print 'playtime:', getUserPlaytime(user, relevantEntrys)
	print 'warps:', getUserWarps(user, logFileAr)
	print 'teleports:', getUserTp(user, logFileAr)

print ''
print '# exectime:', time.time() - startTime 
