from PIL import Image, ImageDraw

class skin2avatar(object):
	"""skin2avatar

	minecraft body coordinates
	full avatar size: 16x32

	head
	8x8
	+8+8
	new: 4x0

	body
	20x20
	+8+12
	new: 4x8

	left leg
	4x20
	+4+12
	new: 4x20

	right leg
	12x20
	+4+12
	new: 8x20

	left arm
	44x20
	+4+12
	new: 0x8

	right arm
	52x20
	+4+12
	new: 12x8
	"""

	def __init__(self):
		self.allPixels = list()
		self.pixels = None

		self.newImg = Image.new("RGBA", (16, 32), (255, 0, 0, 0))  # transparent: (255,0,0,0) some sort of grey: (50,50,50,50)
		self.newImgDraw = ImageDraw.Draw(self.newImg)

	def transform(self, sourceFile, destFile):
		img = Image.open(sourceFile)

		self.pixels = img.load()  # this is not a list, nor is it list()'able

		self.remapPixels(8,8,8+8,8+8, 4,0,4+8,0+8)  # head
		self.remapPixels(20,20,20+8,20+12, 4,8,4+8,8+12)  # body
		self.remapPixels(4,20,4+4,20+12, 4,20,4+4,20+12)  # left leg
		self.remapPixels(12,20,12+4,20+12, 8,20,8+4,20+12)  # right leg
		self.remapPixels(44,20,44+4,20+12, 0,8,0+4,8+12)  # left arm
		self.remapPixels(52,20,52+4,20+12, 12,8,12+4,8+12)  # right arm

		self.newImg.save(destFile, "PNG")

	def getPartFromImage(self, fromX, fromY, toX, ToY):
		partPixels = list()
		for x in range(fromX, toX):
			for y in range(fromY, ToY):
				partPixels.append(self.pixels[x, y])
		return partPixels

	def drawPartOnNewImage(self, fromX, fromY, toX, ToY, pixels):
		pass

	def remapPixels(self, fromX, fromY, toX, toY, newFromX, newFromY, newToX, newToY):
		partPixels = []
		for x in range(fromX, toX):
			for y in range(fromY, toY):
				#print x, y
				partPixels.append(self.pixels[x, y])

		#print len(partPixels)
		index = 0
		for x in range(newFromX, newToX):
			for y in range(newFromY, newToY):
				if index < len(partPixels):
					self.newImgDraw.point((x, y), fill=partPixels[index])
				else:
					pass
					#print 'over:', index
				index += 1


if __name__ == '__main__':
	s2a = skin2avatar()
	s2a.transform('../assets/avatars/scot_raw.png', '../assets/avatars/scot_avatar.png')
