import datetime
def getFileDate(logFileName=''):
	#print logFileName
	fileDate = None
	if logFileName == 'latest.log':
		fileDate = datetime.datetime.strptime('2999-12-12', '%Y-%m-%d')
	else:
		if logFileName.endswith('.log.gz'):
			logFileName = logFileName[0:-7]
		elif logFileName.endswith('.log.json'):
			logFileName = logFileName[0:-9]
		else:
			return datetime.datetime.strptime('2999-12-12', '%Y-%m-%d')
		#print logFileName
		fileDateParts = logFileName.split('-')
		fileDateString = '{0}-{1}-{2} {3}'.format(fileDateParts[0], fileDateParts[1], fileDateParts[2], fileDateParts[3])
		#print fileDateString
		fileDate = datetime.datetime.strptime(fileDateString, '%Y-%m-%d %H')
	return fileDate