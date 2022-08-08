import subprocess, os, pdb


class FishTrackingPreparer():
	# This class takes in directory information and a logfile containing depth information and performs the following:
	# 1. Identifies tray using manual input
	# 2. Interpolates and smooths depth data
	# 3. Automatically identifies bower location
	# 4. Analyze building, shape, and other pertinent info of the bower

	def __init__(self, fileManager, videoIndex, gpu = 0):

		self.__version__ = '1.0.0'

		self.fileManager = fileManager
		self.videoObj = self.fileManager.returnVideoObject(videoIndex)
		self.videoIndex = videoIndex
		self.gpu = str(gpu)

	def validateInputData(self):
		
		assert os.path.exists(self.videoObj.localVideoFile)

		assert os.path.exists(self.fileManager.localTroubleshootingDir)
		assert os.path.exists(self.fileManager.localAnalysisDir)
		assert os.path.exists(self.fileManager.localTempDir)
		assert os.path.exists(self.fileManager.localLogfileDir)
		assert os.path.exists(self.fileManager.localYolov5WeightsFile)

	def runClusterAnalysis(self):

		command = ['python3', 'detect.py']
		command.extend(['--weights', self.fileManager.localYolov5WeightsFile])
		command.extend(['--source', self.localVideoFile])
		command.extend(['--device', self.gpu])
		command.extend(['--project', self.localTempDir + self.videoObj.localVideoFile.split('/')[-1].remove('.mp4')])
		command.extend(['--save-txt', '--nosave', '--save-conf'])


		os.chdir(os.getenv('HOME') + '/yolov5')
#		subprocess.run(['git', 'pull'])
		subprocess.run(command)
		os.chdir(os.getenv('HOME') + '/CichlidBowerTracking/cichlid_bower_tracking')


