import time
import datetime
import os
import gzip
import json
import helper

class logFileToJson(object):
	def __init__(self, directory=''):
		self.logDir = directory
		self.forceJsonWrite = False

	def convertAll(self):
		allFiles = os.listdir(self.logDir)
		#allFiles.sort(key=lambda x: os.path.getctime(os.path.join(self.logDir, x)))
		allFiles.sort(key=lambda x: helper.getFileDate(x))
		print allFiles
		for file in allFiles:
			#print file
			logFileFullPath = os.path.join(self.logDir, file)
			if os.path.isfile(logFileFullPath):
				jsonName = ''
				jsonPath = ''
				if file.endswith('.gz'):
					jsonName = file[:-3]
					jsonName += '.json'
				elif file.endswith('.log'):
					jsonName = file[:-4]
					jsonName += '.json'

				jsonPath = os.path.join(self.logDir, jsonName)
				#print jsonName
				#self.convertFile(file)
				if self.forceJsonWrite or jsonName == 'latest.log' or (jsonName != '' and not os.path.isfile(jsonPath)):
					self.convertFile(logFileFullPath, jsonPath, file)


	def getFileDateString(self, logFileFullPath, logFileName):
		fileDateString = ''
		if logFileName == 'latest.log':
			fileDateString = time.strftime('%Y-%m-%d', time.gmtime(os.path.getmtime(logFileFullPath)))
		else:
			fileDateParts = logFileName.split('-')
			fileDateString = '{0}-{1}-{2}'.format(fileDateParts[0], fileDateParts[1], fileDateParts[2])
		return fileDateString

	def getLineTime(self, linePart):
		return linePart[1:-1]

	def convertFile(self, logFileFullPath, jsonPath, logFileName):
		fileDateString = ''
		fileContent = ''

		fh = None
		if logFileName.endswith('.gz'):
			fh = gzip.open(logFileFullPath,'rb')
		else:
			fh = open(logFileFullPath, 'r')

		fileContent = fh.read()
		fh.close()

		fileDateString = self.getFileDateString(logFileFullPath, logFileName)

		lines = fileContent.split('\n')
		jsonList = []
		for line in lines:
			line = line.strip()
			if line != '':
				lineParts = line.split(" ")

				lineTimeString = self.getLineTime(lineParts[0])

				finalJsonDict = {
									'dateTime':fileDateString + ' ' + lineTimeString,
									'date':fileDateString,
									'time':lineTimeString,
									'line':line
								}
				jsonList.append(finalJsonDict)
				#print '<',finalJsonDict,'>'

		fh = open(jsonPath, 'w')
		fh.write(json.dumps(jsonList))
		fh.close()

