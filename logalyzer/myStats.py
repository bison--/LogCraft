#!/usr/var/python
from datetime import datetime
from datetime import timedelta
import os
import sys
import time
import re
import json
from  logFileToJson import logFileToJson
import helper

DOWNLOAD_AVATARS = True
AVATAR_PATH = 'assets/avatars/'  # with / at the end!

startTime = time.time()
#2013-01-21 03:23:33 [INFO] [AuthMe] NAME logged in!
#2013-01-21 04:59:01 [INFO] Connection reset
#2013-01-21 04:59:01 [INFO] NAME lost connection: disconnect.endOfStream
#'/var/minecraftServer/theWorld/server.log.bak', 


REGEX_IP = "(\d+)\.(\d+)\.(\d+)\.(\d+)"

REGEX_LOGIN_USERNAME = re.compile("\[Server thread\/INFO\]: ([^]]+)\[")
REGEX_LOGOUT_USERNAME = re.compile("\[Server thread\/INFO\]: ([^ ]+) lost connection")
REGEX_LOGOUT_USERNAME2 = re.compile(
    "\[Server thread\/INFO\]:.*GameProfile.*name='?([^ ,']+)'?.* lost connection")
REGEX_KICK_USERNAME = re.compile("\[INFO\] CONSOLE: Kicked player ([^ ]*)")
REGEX_ACHIEVEMENT = re.compile("\[Server thread\/INFO\]: ([^ ]+) has just earned the achievement \[(.*)\]")

# regular expression to get the username of a chat message
# you need to change this if you have special chat prefixes or stuff like that
# this regex works with chat messages of the format: <prefix username> chat message
REGEX_CHAT_USERNAME = re.compile("\[Server thread\/INFO\]: <([^>]* )?([^ ]*)>")

DEATH_MESSAGES = (
    "was squashed by.*",
    "was pricked to death",
    "walked into a cactus whilst trying to escape.*",
    "drowned.*",
    "blew up",
    "was blown up by.*",
    "fell from a high place.*",
    "hit the ground too hard",
    "fell off a ladder",
    "fell off some vines",
    "fell out of the water",
    "fell into a patch of.*",
    "was doomed to fall.*",
    "was shot off.*",
    "was blown from a high place.*",
    "went up in flames",
    "burned to death",
    "was burnt to a crisp whilst fighting.*",
    "walked into a fire whilst fighting.*",
    "was slain by.*",
    "was shot by.*",
    "was fireballed by.*",
    "was killed.*",
    "got finished off by.*",
    "tried to swim in lava.*",
    "died",
    "was struck by lighting",
    "starved to death",
    "suffocated in a wall",
    "was pummeled by.*",
    "fell out of the world",
    "was knocked into the void.*",
    "withered away",
)

REGEX_DEATH_MESSAGES = set()
for message in DEATH_MESSAGES:
	REGEX_DEATH_MESSAGES.add(re.compile("\Server thread\/INFO\]: ([^ ]+) (" + message + ")"))


logFiles = []  #('/var/minecraftServer/theWorld/server.log',)
logFileDirs = []
outputMode = ''
#sys.argv.append('-html')
#sys.argv.append('../logs/')
if len(sys.argv) <= 2:
	print 'first parameter MUST be the mode -html or -shell'
	print 'all other parameters are the logfile folders'
	exit(1)
else:
	outputMode = sys.argv[1].replace('-', '')
	for i in range(2, len(sys.argv)):
		logFileDirs.append(sys.argv[i])

logFileJsonAr = []

for logFileDir in logFileDirs:
	lfToJson = logFileToJson(logFileDir)
	lfToJson.convertAll()
	allFiles = os.listdir(logFileDir)
	#allFiles.sort(key=lambda x: os.path.getctime(os.path.join(logFileDir, x)))
	allFiles.sort(key=lambda x: helper.getFileDate(x))
	for file in allFiles:
		if file.endswith('.json'):
			fh = open(os.path.join(logFileDir, file))
			jsonList = json.load(fh)
			fh.close()
			logFileJsonAr.extend(jsonList)


	#logFileH = open(logFile, 'r')
	#logFileStr += logFileH.read()
	#logFileH.close()
#print logFileJsonAr


def getUsers(jsonAr):
	users = []
	
	for r in jsonAr:
		# only for the add-in module 'AuthMe'
		# '[AuthMe]' in r and 
		if 'logged in' in r['line']:
			cols = r['line'].split(' ')
			#if len(cols) >= 4 and not cols[4] in users:
			#	users.append(cols[4])
			if len(cols) >= 3 and '[/' in cols[3]:
				userName = cols[3].split('[/')[0]
				if not userName in users:
					users.append(userName)
	return users

def getRelevantEntrys(jsonAr):
	relEntrys = []
	relStuff = ['lost connection', 'logged in', 'fell from a high place', 'was slain by', 'drowned', 'in lava']
	for r in jsonAr:
		for entry in relStuff:
			if entry in r['line']:
				relEntrys.append(r)
	
	return relEntrys

def getUuidFromUser(username, jsonAr):
	#[19:49:20] [User Authenticator #10/INFO]: UUID of player Name is xxxxxx-f1d5-xxxx-xxxx-xxxxxxxx
	uuid = ''
	for r in jsonAr:
		if username in r['line'] and 'UUID of player' in r['line']:
			parts = r['line'].split(' ')
			uuid = parts[:0]
			uuid = uuid.replace('-', '')
			break

	return uuid

def downloadAvatarForUser(username, uuid):
	#https://sessionserver.mojang.com/session/minecraft/profile/<UUID>
	#{"id":"<UUID>","name":"<USERNAME>","properties":[{"name":"textures","value":"eyJ0aW1lc3RhbXAiOjE0NDUzNjQ4NTkxODcsInByb2ZpbGVJZCI6ImFlYTdhYzE3YzYwNzQ0YWNhNzlkNjM0ZjVmZTI2ZTRmIiwicHJvZmlsZU5hbWUiOiJHZW5lcmFsTUJpc29uIiwidGV4dHVyZXMiOnsiU0tJTiI6eyJ1cmwiOiJodHRwOi8vdGV4dHVyZXMubWluZWNyYWZ0Lm5ldC90ZXh0dXJlL2U3NjlkNTRhNzgwMTM3MDhlYTA0ZDhmOTRmNWVkNDE5MTUxZjE5NTU1M2Q4NTU2ZDg0M2I5ZmE1NDM1OTE1In19fQ=="}],"legacy":true}
	import urllib
	import base64
	url = 'https://sessionserver.mojang.com/session/minecraft/profile/'+uuid
	response = urllib.urlopen(url)
	data = json.loads(response.read())
	response.close()
	#ON ERROR:{"error":"TooManyRequestsException","errorMessage":"The client has sent too many requests within a certain amount of time"}
	if 'error' in data:
		return ''

	for properti in data['properties']:
		if properti['name'] == 'textures':
			textureBase64 = properti['value']
			textureJson = json.loads(base64.b64decode(textureBase64))
			urllib.urlretrieve(textureJson['testure']['SKIN']['url'], username+'.png')

	return username+'.png'

def getUserLogins(username, jsonAr):
	count = 0
	for r in jsonAr:
		if username in r['line'] and 'logged in' in r['line']:
			count += 1
	return count

def getUserPlaytime(username, jsonAr):
	fmt = '%Y-%m-%d %H:%M:%S'
	#d1 = datetime.strptime('2010-01-01 17:31:22', fmt)
	#d2 = datetime.strptime('2010-01-03 17:31:22', fmt)
	#print (d2-d1).days * 24 * 60
	
	mode = 0
	seconds = 0
	lastStart = None
	logErrors = []

	lostConString = username + ' lost connection'
	for r in jsonAr:
		if username in r['line']:
			#col = r['line'].split(' ')
		
			if 'logged in with entity id' in r['line']:
				#print '<b>LOGIN</b>:', r['dateTime'], r['line'], '<br>'
				lastStart = datetime.strptime(r['dateTime'], fmt)
			elif lostConString in r['line']:
				#print '<b>LOGOUT</b>:', r['dateTime'], r['line'], '<br>'
				dt = datetime.strptime(r['dateTime'], fmt)
				if lastStart != None:
					seconds += (dt - lastStart).seconds
				else:
					logErrors.append('WARNING! Logout without login: ' + str(r))

	if len(logErrors):
		print logErrors

	return str(timedelta(seconds=seconds))
	#datetime.timedelta(0, 65)
	#return time.strftime('%d %H:%M:%S', timedelta(0, seconds))
	#return time.strftime('%d %H:%M:%S', time.gmtime(seconds))

def isUserLoggedIn(username, jsonAr):
	lostConString = username + ' lost connection'
	for r in reversed(jsonAr):
		if username in r['line']:
			if 'logged in with entity id' in r['line']:
				#print 'Online:', r
				return True
			if lostConString in r['line']:
				#print 'Offline:', r
				return False
	#print 'WTF'
	return False

def getUserFirstLogin(username, jsonAr):
	for r in jsonAr:
		if username in r['line']:
			#cols = r.split(' ')
			return r['dateTime']

def getUserLastLogin(username, jsonAr):
	for r in reversed(jsonAr):
		if username in r['line']:
			#cols = r.split(' ')
			return r['dateTime']

def getUserTp(username, jsonAr):
	count = 0
	for r in jsonAr:
		if username in r['line'] and '/tp' in r['line']:
			count += 1
	return count
	
def getUserWarps(username, jsonAr):
	count = 0
	for r in jsonAr:
		if username in r['line'] and '/warp' in r['line']:
			count += 1
	return count

def getDateFromEntry(entry):
	tmp = entry.split(' ')
	if len(tmp) >= 2:
		return tmp[0] +' '+ tmp[1]
	else:
		print 'NO DATE'
		return 'NO DATE'

def getAchievements(username, jsonAr):
	achievements = []
	for r in jsonAr:
		if username in r['line']:
			search = REGEX_ACHIEVEMENT.search(r['line'])
			if not search:
				#print "### Warning: Unable to find achievement username or achievement:", line
				#return None, None
				pass
			else:
				#username = search.group(1)
				#return username.decode("ascii", "ignore").encode("ascii", "ignore"), search.group(2)
				achievement = r['dateTime'] + ': ' + search.group(2)
				achievements.append(achievement)

	return achievements

def grepDeath(line):
	for regex in REGEX_DEATH_MESSAGES:
		search = regex.search(line)
		if search:
			return search.group(1), search.group(2)
	return None, None

def getDeaths(username, jsonAr):
	deathDict = {}
	for r in jsonAr:
		if username in r['line']:
			deadUser, deathType = grepDeath(r['line'])
			if deadUser != None and deadUser == username:
				if not deathType in deathDict:
					deathDict[deathType] = 0
				deathDict[deathType] += 1
	return deathDict

relevantEntrys = logFileJsonAr  #getRelevantEntrys(logFileJsonAr)
users = getUsers(relevantEntrys)

if outputMode == 'shell':
	print '# Zeilen:', len(logFileJsonAr)
	print '# Erster Eintrag vom:', logFileJsonAr[0]['dateTime']  #getDateFromEntry(logFileAr[0]) #logFileAr[0].split(' ')[0], logFileAr[0].split(' ')[1]
	print '# Letzer Eintrag vom:', logFileJsonAr[-1]['dateTime']  #getDateFromEntry(logFileAr[len(logFileAr)-2])
	for user in users:
		print ''
		print (' '+ user +' ').center(23, '#') #'#'* 10, user, '#'*10
		print 'logins:',  getUserLogins(user, relevantEntrys)
		print 'first login:',  getUserFirstLogin(user, relevantEntrys)
		print 'last login:',  getUserLastLogin(user, relevantEntrys)
		print 'playtime:', getUserPlaytime(user, relevantEntrys)
		print 'warps:', getUserWarps(user, relevantEntrys)
		print 'teleports:', getUserTp(user, relevantEntrys)

	print ''
	print '# exectime:', time.time() - startTime
elif outputMode == 'html_online':
	print '<div class="table-responsive">'
	print '<table class="table table-striped"><tbody>'
	for user in users:
		userAvatarStr = ''
		if DOWNLOAD_AVATARS:
			imageName = downloadAvatarForUser(user, getUuidFromUser(user, jsonAr))
			if imageName != '':
				userAvatarStr = '<img src="'+AVATAR_PATH+imageName+'">'

		loggedInStr = ''
		if isUserLoggedIn(user, relevantEntrys):
			loggedInStr = '<span class="label label-success">Online</span>'
		else:
			loggedInStr = '<span class="label label-default">Offline</span>'

		print '<tr><td>', userAvatarStr, '</td><td>', user, '</td><td>', loggedInStr, '</td></tr>'

	print '</tbody></table>'
	print '</div>'
elif outputMode == 'html':
	print '<p>'
	print '<div class="table-responsive">'
	print '<table class="table"><tbody>'
	print '<tr><td>Zeilen:</td><td>', len(logFileJsonAr), '</td></tr>'
	print '<tr><td>Erster Eintrag vom:</td><td>', logFileJsonAr[0]['dateTime'], '</td></tr>' #logFileAr[0].split(' ')[0], logFileAr[0].split(' ')[1]
	print '<tr><td>Letzer Eintrag vom:</td><td>', logFileJsonAr[-1]['dateTime'], '</td></tr>'
	print '</tbody></table>'
	print '</div>'
	print '</p>'
	for user in users:
		loggedInStr = ''
		if isUserLoggedIn(user, relevantEntrys):
			loggedInStr = '<span class="label label-success">Online</span>'
		else:
			loggedInStr = '<span class="label label-default">Offline</span>'
		print '<h2>', user, loggedInStr, '</h2>'
		print '<p>'
		print '<div class="table-responsive">'
		print '<table class="table table-striped"><tbody>'
		print '<tr><td>logins:</td><td>',  getUserLogins(user, relevantEntrys), '</td></tr>'
		print '<tr><td>first login:</td><td>',  getUserFirstLogin(user, relevantEntrys), '</td></tr>'
		print '<tr><td>last log-in/out:</td><td>',  getUserLastLogin(user, relevantEntrys), '</td></tr>'
		print '<tr><td>playtime:</td><td>', getUserPlaytime(user, relevantEntrys), '</td></tr>'

		achievements = getAchievements(user, relevantEntrys)
		achievementStr = ''
		for achievement in achievements:
			achievementStr += achievement + '<br>'
		print '<tr><td>achievements:</td><td>', len(achievements), '</td></tr>'
		print '<tr><td>achievement kinds:</td><td>', achievementStr, '</td></tr>'

		deaths = getDeaths(user, relevantEntrys)
		totalDeaths = 0
		deathString = ''
		for death, deathCount in deaths.iteritems():
			totalDeaths += deathCount
			deathString += death + ': ' + str(deathCount) + '<br>'

		print '<tr><td>deaths:</td><td>', totalDeaths, '</td></tr>'
		print '<tr><td>death kinds:</td><td>', deathString.encode("utf-8"), '</td></tr>'
		#print '<tr><td>warps:</td><td>', getUserWarps(user, relevantEntrys), '</td></tr>'
		#print '<tr><td>teleports:</td><td>', getUserTp(user, relevantEntrys), '</td></tr>'
		print '</tbody></table>'
		print '</div>'
		print '</p>'
	print '<p><small class="disabled">exectime:', time.time() - startTime, '</small></p>'
