import argparse, datetime, gspread, time, pdb, warnings
from cichlid_bower_tracking.helper_modules.file_manager import FileManager as FM
from cichlid_bower_tracking.helper_modules.log_parser import LogParser as LP
from cichlid_bower_tracking.helper_modules.googleController import GoogleController as GC

import matplotlib
matplotlib.use('Pdf')  # Enables creation of pdf without needing to worry about X11 forwarding when ssh'ing into the Pi
import matplotlib.pyplot as plt
import matplotlib.image as img
import numpy as np
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
import oauth2client
from skimage import morphology


parser = argparse.ArgumentParser()
parser.add_argument('Logfile', type = str, help = 'Name of logfile')
args = parser.parse_args()


class DriveUpdater:
    def __init__(self, logfile):
        self.lp = LP(logfile)

        self.fileManager = FM(projectID = self.lp.projectID, analysisID = self.lp.analysisID)
        self.node = self.lp.uname.split("node='")[1].split("'")[0]
        self.lastFrameTime = self.lp.frames[-1].time
        self.masterDirectory = self.fileManager.localMasterDir
        self.projectDirectory = self.fileManager.localProjectDir
        
        self.googleController = GC(self.fileManager.localCredentialSpreadsheet)
        self.googleController.addProjectID(self.lp.projectID, self.fileManager.localProjectDir + 'GoogleErrors.txt')

        self._createImage()

        self.credentialDrive = self.fileManager.localCredentialDrive

        self._uploadImage(self.projectDirectory + self.lp.tankID + '.jpg', self.projectDirectory + self.lp.tankID + '_2.jpg', self.lp.tankID, self.lp.tankID + '_2.jpg')

     def _createImage(self, stdcutoff = 0.1):
        lastHourFrames = [x for x in self.lp.frames if x.time > self.lastFrameTime - datetime.timedelta(hours = 1)]  
        lastTwoHourFrames = [x for x in self.lp.frames if x.time > self.lastFrameTime - datetime.timedelta(hours = 2)]  
        lastDayFrames = [x for x in self.lp.frames if x.time > self.lastFrameTime - datetime.timedelta(days = 1)]
        daylightFrames = [x for x in self.lp.frames if x.time.hour >= 8 and x.time.hour <= 18]
        lastTwoDaysFrames = [x for x in self.lp.frames if x.time > self.lastFrameTime - datetime.timedelta(days = 2)]
        lastThreeDaysFrames = [x for x in self.lp.frames if x.time > self.lastFrameTime - datetime.timedelta(days = 3)]
        if len(daylightFrames) != 0:
            t_change = str(self.lastFrameTime - daylightFrames[0].time)
        else:
            daylightFrames = lastDayFrames
            t_change = str(self.lastFrameTime - lastDayFrames[0].time)
        d_change = str(self.lastFrameTime - lastDayFrames[0].time)
        th_change = str(self.lastFrameTime-lastTwoHourFrames[0].time)
        h_change = str(self.lastFrameTime - lastHourFrames[0].time)
        td_change=str(self.lastFrameTime - lastTwoDaysFrames[0].time)
        thd_change=str(self.lastFrameTime - lastThreeDaysFrames[0].time)
        
        #these comments next to the axs are no longer correct
        
        fig = plt.figure(figsize=(14,23))
        fig.suptitle(self.lp.projectID + ' ' + str(self.lastFrameTime))
        ax1 = fig.add_subplot(6, 3, 1) #Pic from Kinect
        ax2 = fig.add_subplot(6, 3, 2) #Pic from Camera
        ax3 = fig.add_subplot(6, 3, 3) #Depth from Kinect
        ax4 = fig.add_subplot(6, 3, 4) #Total Depth Change
        ax5 = fig.add_subplot(6, 3, 5) #Day Depth Change
        ax6 = fig.add_subplot(6, 3, 6) #Hour Depth Change
        ax7 = fig.add_subplot(6, 3, 7) #Total Depth Change 
        ax8 = fig.add_subplot(6, 3, 8) #Day Depth Change
        ax9 = fig.add_subplot(6, 3, 9) #Hour Depth Change
        ax10 = fig.add_subplot(6, 3, 10) #Total Depth Change 
        ax11 = fig.add_subplot(6, 3, 11) #Day Depth Change
        ax12 = fig.add_subplot(6, 3, 12) #Hour Depth Change
        ax13 = fig.add_subplot(6, 3, 13) #Total Depth Change 
        ax14 = fig.add_subplot(6, 3, 14) #Day Depth Change
        ax15 = fig.add_subplot(6, 3, 15) #Hour Depth Change
        ax16 = fig.add_subplot(6, 3, 16) #Hour Depth Change
        ax17 = fig.add_subplot(6, 3, 17) #Hour Depth Change
        ax18 = fig.add_subplot(6, 3, 18) #Hour Depth Change

        img_1 = img.imread(self.projectDirectory + self.lp.frames[-1].pic_file)
        try:
            img_2 = img.imread(self.projectDirectory + self.lp.movies[-1].pic_file)
        except:
            img_2 = img_1

        dpth_3 = np.load(self.projectDirectory + self.lp.frames[-1].npy_file)
        dpth_4 = np.load(self.projectDirectory + daylightFrames[0].npy_file)
        dpth_5 = np.load(self.projectDirectory + lastDayFrames[0].npy_file)
        dpth_6 = np.load(self.projectDirectory + lastTwoHourFrames[0].npy_file)
        dpth_7 = np.load(self.projectDirectory + lastHourFrames[0].npy_file)
        dpth_8 = np.load(self.projectDirectory + lastTwoDaysFrames[0].npy_file)
        dpth_9 = np.load(self.projectDirectory + lastThreeDaysFrames[0].npy_file)
        
        #not showing standard deviation anymore
        std_3 = np.load(self.projectDirectory + self.lp.frames[-1].std_file)
        std_4 = np.load(self.projectDirectory + daylightFrames[0].std_file)
        std_5 = np.load(self.projectDirectory + lastDayFrames[0].std_file)
        std_6 = np.load(self.projectDirectory + lastTwoHourFrames[0].std_file)
        std_7 = np.load(self.projectDirectory + lastHourFrames[0].std_file)
        # Plot before filtering
        median_height = np.nanmedian(dpth_3)
        #removed non-filtered plots
        #ax10.imshow(dpth_5, vmin = median_height - 8, vmax = median_height + 8)
        #ax11.imshow(dpth_6, vmin = median_height - 8, vmax = median_height + 8)
        #ax12.imshow(dpth_7, vmin = median_height - 8, vmax = median_height + 8)

        # Filter out data thaat has a bad stdev
        #this part may need to be adjusted for 48-72 change
        bad_data_count = (std_3 > stdcutoff).astype(int) + (std_4 > stdcutoff).astype(int) + (std_5 > stdcutoff).astype(int) + (std_6 > stdcutoff).astype(int) + (std_7 > stdcutoff).astype(int)
        dpth_3[bad_data_count > 3] = np.nan
        dpth_4[bad_data_count > 3] = np.nan
        dpth_5[bad_data_count > 3] = np.nan
        dpth_6[bad_data_count > 3] = np.nan
        dpth_7[bad_data_count > 3] = np.nan
        dpth_8[bad_data_count > 3] = np.nan
        dpth_9[bad_data_count > 3] = np.nan
        

        # Filter out data that has bad initial height
        dpth_3[(dpth_4 > median_height + 4) | (dpth_4 < median_height - 4)] = np.nan # Filter out data 4cm lower and 8cm higher than tray
        dpth_5[(dpth_4 > median_height + 4) | (dpth_4 < median_height - 4)] = np.nan # Filter out data 4cm lower and 8cm higher than tray
        dpth_6[(dpth_4 > median_height + 4) | (dpth_4 < median_height - 4)] = np.nan # Filter out data 4cm lower and 8cm higher than tray
        dpth_7[(dpth_4 > median_height + 4) | (dpth_4 < median_height - 4)] = np.nan # Filter out data 4cm lower and 8cm higher than tray
        dpth_8[(dpth_4 > median_height + 4) | (dpth_4 < median_height - 4)] = np.nan 
        dpth_9[(dpth_4 > median_height + 4) | (dpth_4 < median_height - 4)] = np.nan 
        dpth_4[(dpth_4 > median_height + 4) | (dpth_4 < median_height - 4)] = np.nan # Filter out data 4cm lower and 8cm higher than tray
        


        total_change = dpth_4 - dpth_3
        three_daily_change=dpth_9-dpth_3
        two_daily_change=dpth_8-dpth_3
        daily_change = dpth_5 - dpth_3
        two_hourly_change = dpth_6 - dpth_3
        hourly_change = dpth_7 - dpth_3


        ### TITLES ###
        ax1.set_title('Kinect RGB Picture')
        ax2.set_title('PiCamera RGB Picture')
        ax3.set_title('Total Depth Change' + t_change)
        #above stays same
        ax4.set_title('Filtered Hour ago Depth')
        ax5.set_title('Last hour change\n'+h_change)
        ax6.set_title('Last hour bower\n')
        
        ax7.set_title('Filtered 2 Hour ago Depth')
        ax8.set_title('Last 2 hours change\n'+th_change)
        ax9.set_title('Last 2 hours bower\n')
        
        ax10.set_title('Filtered 24 Hour ago Depth')
        ax11.set_title('Last 24 hour change\n'+d_change)
        ax12.set_title('Last 24 hours bower\n')
        #this is all new
        ax13.set_title('Filtered 24-48 Hour ago Depth')
        ax14.set_title('Last 24-48 hour change\n'+td_change)
        ax15.set_title('Last 24-48 hours bower\n')
        
        ax16.set_title('Filtered 48-72 Hour ago Depth')
        ax17.set_title('Last 48-72 hour change\n'+thd_change)
        ax18.set_title('Last 48-72 hours bower\n')
#stay same
        ax1.imshow(img_1)
        ax2.imshow(img_2)
        ax3.imshow(total_change, vmin = -2, vmax = 2)

#
        ax11.imshow(daily_change, vmin = -1, vmax = 1) # +- 2 cms
        ax8.imshow(two_hourly_change, vmin = -.5, vmax = .5)
        ax5.imshow(hourly_change, vmin = -.5, vmax = .5)
        ax14.imshow(two_daily_change, vmin = -1, vmax = 1)#might need to change 1
        ax17.imshow(three_daily_change, vmin = -1, vmax = 1)#might need to change 1
       
        #may want to change 0.4 for 48-72
        three_daily_bower = three_daily_change.copy()
        thresholded_change = np.where((three_daily_change >= 0.4) | (three_daily_change <= -0.4), True, False)
        thresholded_change = morphology.remove_small_objects(thresholded_change,1000).astype(int)
        three_daily_bower[(thresholded_change == 0) & (~np.isnan(three_daily_change))] = 0
        
        two_daily_bower = two_daily_change.copy()
        thresholded_change = np.where((two_daily_change >= 0.4) | (two_daily_change <= -0.4), True, False)
        thresholded_change = morphology.remove_small_objects(thresholded_change,1000).astype(int)
        two_daily_bower[(thresholded_change == 0) & (~np.isnan(two_daily_change))] = 0
        
        daily_bower = daily_change.copy()
        thresholded_change = np.where((daily_change >= 0.4) | (daily_change <= -0.4), True, False)
        thresholded_change = morphology.remove_small_objects(thresholded_change,1000).astype(int)
        daily_bower[(thresholded_change == 0) & (~np.isnan(daily_change))] = 0

        two_hourly_bower = two_hourly_change.copy()
        thresholded_change = np.where((two_hourly_change >= 0.3) | (two_hourly_change <= -0.3), True, False)
        thresholded_change = morphology.remove_small_objects(thresholded_change,1000).astype(int)
        two_hourly_bower[(thresholded_change == 0) & (~np.isnan(two_hourly_change))] = 0

        hourly_bower = hourly_change.copy()
        thresholded_change = np.where((hourly_change >= 0.3) | (hourly_change <= -0.3), True, False)
        thresholded_change = morphology.remove_small_objects(thresholded_change,1000).astype(int)
        hourly_bower[(thresholded_change == 0) & (~np.isnan(daily_change))] = 0
        
#may need to change 1 for 48-72

        ax18.imshow(three_daily_bower, vmin = -1, vmax = 1)
        ax15.imshow(two_daily_bower, vmin = -1, vmax = 1)
        ax12.imshow(daily_bower, vmin = -1, vmax = 1) # +- 2 cms
        ax9.imshow(two_hourly_bower, vmin = -.5, vmax = .5)
        ax6.imshow(hourly_bower, vmin = -.5, vmax = .5) # +- 1 cms
        
        ax16.imshow(dpth_9, vmin = median_height - 8, vmax = median_height + 8)
        ax13.imshow(dpth_8, vmin = median_height - 8, vmax = median_height + 8)
        ax10.imshow(dpth_5, vmin = median_height - 8, vmax = median_height + 8)
        ax7.imshow(dpth_6, vmin = median_height - 8, vmax = median_height + 8)
        ax4.imshow(dpth_7, vmin = median_height - 8, vmax = median_height + 8)

        #ax16.imshow(std_5, vmin = 0, vmax = .25)
        #ax17.imshow(std_6, vmin = 0, vmax = .25)
        #ax18.imshow(std_7, vmin = 0, vmax = .25)

        #plt.subplots_adjust(bottom = 0.15, left = 0.12, wspace = 0.24, hspace = 0.57)
        plt.savefig(self.projectDirectory + self.lp.tankID + '.jpg')
        #return self.graph_summary_fname

        fig = plt.figure(figsize=(6,3))
        fig.tight_layout()
        ax1 = fig.add_subplot(1, 2, 1) #Pic from Kinect
        ax2 = fig.add_subplot(1, 2, 2) #Pic from Camera
        ax1.imshow(two_hourly_change, vmin = -.75, vmax = .75)
        ax1.axes.get_xaxis().set_visible(False)
        ax1.axes.get_yaxis().set_visible(False)

        ax2.imshow(hourly_change, vmin = -.75, vmax = .75) # +- 1 cms
        ax2.axes.get_xaxis().set_visible(False)
        ax2.axes.get_yaxis().set_visible(False)

        fig.tight_layout()

        fig.savefig(self.projectDirectory + self.lp.tankID + '_2.jpg')


    def _uploadImage(self, image_file1, image_file2, name1, name2): #name should have format 't###_icon' or 't###_link'
        self._authenticateGoogleDrive()
        drive = GoogleDrive(self.gauth)
        folder_id = "'151cke-0p-Kx-QjJbU45huK31YfiUs6po'"  #'Public Images' folder ID
        
        try:
            file_list = drive.ListFile({'q':"{} in parents and trashed=false".format(folder_id)}).GetList()
        except oauth2client.clientsecrets.InvalidClientSecretsError:
            self._authenticateGoogleDrive()
            file_list = drive.ListFile({'q':"{} in parents and trashed=false".format(folder_id)}).GetList()
        #print(file_list)
        # check if file name already exists so we can replace it
        flag1 = False
        flag2 = False
        count = 0
        while flag1 == False and count < len(file_list):
            if file_list[count]['title'] == name1:
                fileID1 = file_list[count]['id']
                flag1 = True
            else:
                count += 1
        count = 0
        while flag2 == False and count < len(file_list):
            if file_list[count]['title'] == name2:
                fileID2 = file_list[count]['id']
                flag2 = True
            else:
                count += 1

        if flag1 == True:
            # Replace the file if name exists
            f1 = drive.CreateFile({'id': fileID1})
            f1.SetContentFile(image_file1)
            f1.Upload()
            # print("Replaced", name, "with newest version")
        else:
            # Upload the image normally if name does not exist
            f1 = drive.CreateFile({'title': name1, 'mimeType':'image/jpeg',
                                 "parents": [{"kind": "drive#fileLink", "id": folder_id[1:-1]}]})
            f1.SetContentFile(image_file1)
            f1.Upload()                   
            # print("Uploaded", name, "as new file")

        if flag2 == True:
            # Replace the file if name exists
            f2 = drive.CreateFile({'id': fileID2})
            f2.SetContentFile(image_file2)
            f2.Upload()
            # print("Replaced", name, "with newest version")
        else:
            # Upload the image normally if name does not exist
            f2 = drive.CreateFile({'title': name2, 'mimeType':'image/jpeg',
                                 "parents": [{"kind": "drive#fileLink", "id": folder_id[1:-1]}]})
            f2.SetContentFile(image_file2)
            f2.Upload()                   
            # print("Uploaded", name, "as new file")


        info = '=HYPERLINK("' + f1['webContentLink'].replace('&export=download', '') + '", IMAGE("' + f2['webContentLink'] + '"))'

        #info = '=HYPERLINK("' + f['alternateLink'] + '", IMAGE("' + f['webContentLink'] + '"))'
        self.googleController.modifyPiGS('Image', info, ping = False)
    
    def _authenticateGoogleDrive(self):
        self.gauth = GoogleAuth()
        # Try to load saved client credentials
        self.gauth.LoadCredentialsFile(self.credentialDrive)
        if self.gauth.credentials is None:
            # Authenticate if they're not there
            self.gauth.LocalWebserverAuth()
        elif self.gauth.access_token_expired:
            # Refresh them if token is expired
            self.gauth.Refresh()
        else:
            # Initialize with the saved creds
            self.gauth.Authorize()
        # Save the current credentials to a file
        self.gauth.SaveCredentialsFile(self.credentialDrive)

dr_obj = DriveUpdater(args.Logfile)
#try:
#    dr_obj = DriveUpdater(args.Logfile)
#except Exception as e:
#    print(f'skipping drive update due to error: {e}')
