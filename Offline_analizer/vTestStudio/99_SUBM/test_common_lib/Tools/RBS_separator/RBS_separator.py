#
# This script substitutes the relative paths for files that are used by a CANoe configuration.
#
# The path is normally relative to the root directory of the RBS.
# Example: <VFileName V7 QL> 1 "Databases\STAR_3_MAIN_Ethernet_2019_05a_AR43.arxml"
#
# To be able to use the RBS in a common folder for all feature test configurations
# this script substitutes the paths relative to a configuration in another location.
# Example: <VFileName V7 QL> 1 "..\..\common\RBS\\MGW_3_2_9_OEMDai_Sec2_1_8_SW023_NwE_05a_withNM_u_SecOC_CANoe11SP3HF_SecPanel_varCoding\329_218_023NwE05a_11SP3HF\Databases\STAR_3_MAIN_Ethernet_2019_05a_AR43.arxml" 
#
# For call parameters see below and the batch file calling this python script.
#


# The exe can find the common RBS automatically (go up till you find DASy_Test\CANoe_Tests\TESTS\DAIMLER\RBS)

import os
import re
import string
import argparse
import filecmp
import shutil
import datetime

# print debug output
debug = 0

# For these files the path is not changed because they
# are part of the feature test configuration
ignoredFiles = ['"MAIN.cfg"', '"SysVarDef.xml"', '"SysVarReplay.xml"']

# Other files to be copied from the common RBS if there is no MAIN.cfg in the feature test RBS
otherFilesToBeCopied = ['SysVarDef.xml', 'SysVarReplay.xml']

# Pattern for files that can be removed and the path can be
# replaced with the path to the same file in the common RBS
##processedFilesPatternString = '.*\.arxml|.*\.xvp|.*\.cdd'
processedFilesPatternString = '.*\.arxml|.*\.xvp|.*\.cdd|.*\.dll|.*\.tse'
processedFilesPattern       = re.compile(processedFilesPatternString)

# pattern for the file name in MAIN.cfg
fileNamePatternString = '\".*\"'
fileNamePattern       = re.compile(fileNamePatternString)

# pattern for the XVP file name
xvpFileNamePatternString = '[\w\d -]+\.xvp'
xvpFileNamePattern       = re.compile(xvpFileNamePatternString)

rbsLocation = 'DASy_Test\\CANoe_Tests\\TESTS\\DAIMLER\\rbs'

MAINcfg = 'MAIN.cfg'

# List of panels already processed in function processPanels() called from processMAIN.cfg(),
# this panels have to be ignored in function processPanels() for the remaining panels
processedPanels = []

# Dictionary with substituted XVP files and the path to the common RBS.
# This is needed because it can happen that a file is referenced by more than one other file.
# If it was removed from the feature test RBS, it cannot be found any more when the second
# referencing file is processed and the reference stays unchanged.
# In this case the path to the common RBS is taken from this dictionary.
xvpCommonRBSPath = {}


timeStamp = datetime.datetime.now().strftime('%Y.%m.%d_%H.%M.%S')

##
# Go up in the directory tree and search for the RBS folder.
#
def findCommonRBSLocation():

  dirName = os.getcwd()
  rbsPath = os.path.join(dirName, rbsLocation)

  # go up in the directory tree and search for the RBS folder
  while not os.path.isdir(rbsPath) and rbsPath != os.path.join('C:\\', rbsLocation):
##    print('rbsPath: %s' %  rbsPath)
##    print('join:    %s' %  os.path.join('C:\\', rbsLocation))
    dirName = os.path.dirname(dirName)
    rbsPath = os.path.join(dirName, rbsLocation)

  if not os.path.isdir(rbsPath):
    # no RBS found
    rbsPath = ''
    print('ERROR: findCommonRBSLocation(): No common RBS found, was searching for %s\n' % rbsLocation)
  else:
    # get the immediate subfolders of the RBS
    dirs = [x[1] for x in os.walk(rbsPath)][0]

    if 0 == len(dirs):
      print('ERROR: findCommonRBSLocation(): No subdirectory found in common RBS: %s\n' % rbsPath)
      rbsPath = ''
    elif 1 < len(dirs):
      print('ERROR: findCommonRBSLocation(): More than one subdirectory found in common RBS: %s\n' % rbsPath)
      rbsPath = ''
    else:
      rbsPath = os.path.join(rbsPath, dirs[0])
      print('INFO:  findCommonRBSLocation(): Found common RBS: %s\n' % rbsPath)

  return rbsPath

##
# Search for the file MAIN.cfg.
# If the file exists in the current directory, this file is used.
# Otherwise the file from the common RBS (given by the parameter commonRBSPath) is copied
# to the current directory.
# A backup copy of the file is created.
#
# @param[in]  commonRBSPath path to the common RBS
#
# @return tupel of\n
#         - return code: True if a MSAIN.cfg was found, False otherwise\n
#         - path to the MAIN.cfg file
#         - path to the backed-up MAIN.cfg file
#
def getMAINcfg(commonRBSPath):

  # return code
  rc = True

  cwd = os.getcwd()
  MAINcfgPath = os.path.join(cwd, MAINcfg)
  MAINcfgBackupPath = ''

  if os.path.isfile(MAINcfgPath):
    # found MAIN.cfg in feature test folder
    print('INFO:  getMAINcfg(): Use %s from feature test RBS: %s\n' % (MAINcfg, cwd))

  else:
    # no MAIN.cfg found in current directory
    commonMAINcfgPath = os.path.join(commonRBSPath, MAINcfg)

    if os.path.isfile(commonMAINcfgPath):
      # copy MAIN.cfg from the common RBS
      shutil.copyfile(commonMAINcfgPath, MAINcfgPath)
      print('INFO:  getMAINcfg(): Copied %s from\n%s\nto\n%s\n' % (MAINcfg, commonRBSPath, cwd))

      # copy all other needed files
      for file in otherFilesToBeCopied:
        commonFilePath = os.path.join(commonRBSPath, file)
        newFilePath    = os.path.join(cwd, file)
        shutil.copyfile(commonFilePath, newFilePath)
        print('INFO:  getMAINcfg(): Copied %s from\n%s\nto\n%s\n' % (file, commonRBSPath, cwd))

    else:
      print('ERROR: getMAINcfg(): No %s found in common RBS\n%s\n' % (MAINcfg, commonRBSPath))
      rc = False

  if rc:
    # make a backup of the original MAIN.cfg
    MAINcfgBackupPath = '%s_backup_%s' % (MAINcfgPath, timeStamp)
    shutil.copyfile(MAINcfgPath, MAINcfgBackupPath)

  return rc, MAINcfgPath, MAINcfgBackupPath

##
# Process all files of type xvp.
# They can reference other xvp files.
#
# @param[in]  XvpFileIn     the curent xvp file to be processed
# @param[in]  IsFileChanged True if the versions of the file in the feature test RBS \n
#                           and in the common RBS are different, False otherwise
# @param[in]  relRbsPath    relative path to the common RBS
# @param[in]  folderForRemovedFiles folder to store backup copies of the files removed from the feature test RBS
#
# @retval True  none of the referenced files in the file hierarchy were changed, reference to this file can be changed to the common RBS
# @retval False at least one of the referenced files in the file hierarchy was changed, reference to this file must be unchanged
#
def processPanels(XvpFileIn, IsFileChanged, relRbsPath, folderForRemovedFiles, calledFromMAINcfg):

  print('processPanels(%s) called' % XvpFileIn)

  if calledFromMAINcfg and XvpFileIn not in processedPanels:
    # This is one of the files referenced directly or indirectly from MAINcfg()
    # add them to list so that they are not processed again when calling this
    # function for the remaining panels
    processedPanels.append(XvpFileIn)

  elif not calledFromMAINcfg and XvpFileIn in processedPanels:
    # this file was already processed, don't remove it
    return False

  # if the file not exists, it was already referenced and processed by another call
  # path can substituted
#  if not os.path.isfile(XvpFileIn):
 #   print('processPanels(): file not found, already processed: %s' % XvpFileIn)
  #  return True
  
  refCanBeChanged = True
  thisFileChanged = False

  # make a backup of the original file
  xvpBackupPath = '%s_backup_%s' % (XvpFileIn, timeStamp)
  shutil.copyfile(XvpFileIn, xvpBackupPath)

  fi = open(xvpBackupPath,  'r')
  fo = open(XvpFileIn, 'w')

  # if the files comes with a dirname, we also have to use that for the referenced files
  dirname = os.path.dirname(XvpFileIn)

  dirnameParts = dirname.split('\\')

  # for every part of the dirname extend relRbsPath because the relative path
  # has to point deeper in the hierarchy
  relRbsPathExtended = relRbsPath
  for p in range(len(dirnameParts)):
    relRbsPathExtended = '.\\..\\' + relRbsPathExtended
  
  for line in fi:
    if line.lstrip().startswith('<Property Name="PanelList"'):
      # extract the file name
      match = xvpFileNamePattern.search(line)
      if match:
        filename = match.group()

        # remove leading and trailing quotation marks
        filenameOrig = filename.strip('"')

        if dirname != '':
          filenameWithDirName = dirname + '\\' + filenameOrig

        # join the relative path to the RBS root directory with the file name
        relRbsFilename = '.\%s' % os.path.join(relRbsPath, filenameWithDirName)
        absRbsFilename = os.path.abspath(os.path.join(os.getcwd(), relRbsFilename))

        relRbsFilenameExtended = '.\%s' % os.path.join(relRbsPathExtended, filenameWithDirName)

        if debug:
          print('DEBUG: processPanels(): relRbsFilename         = %s' % relRbsFilename)
          print('DEBUG: processPanels(): absRbsFilename         = %s\n' % absRbsFilename)
          print('DEBUG: processPanels(): relRbsFilenameExtended = %s' % relRbsFilenameExtended)
        
        if os.path.isfile(filenameWithDirName) and not os.path.isfile(absRbsFilename):
          # file only exists in the feature test RBS
          print('INFO:  processPanels(%s): File only exists in feature test RBS, not substituted: %s\n' % (XvpFileIn, filenameWithDirName))
          refCanBeChanged = False
          # recursive call
          processPanels(filenameWithDirName, True, relRbsPathExtended, folderForRemovedFiles, calledFromMAINcfg)

        elif os.path.isfile(filenameWithDirName) and os.path.isfile(absRbsFilename) and filecmp.cmp(filenameWithDirName, absRbsFilename, shallow=True):
          # file exists in the common RBS and in the feature test RBS and the contents are the same
          # recursive call
          if processPanels(filenameWithDirName, False, relRbsPathExtended, folderForRemovedFiles, calledFromMAINcfg):
            print('INFO:  processPanels(%s): File exists in common RBS and in feature test RBS with same content, no referenced files changed, substituted:  %s (%s)\n' % (XvpFileIn, filenameOrig, relRbsFilenameExtended))

            # create a subfolder in the folderForRemovedFiles
            subDir = os.path.join(folderForRemovedFiles, os.path.dirname(filenameWithDirName))
            if not os.path.isdir(subDir):
              os.makedirs(subDir)

            # move the file from the feature test RBS to the folder for removed files
            shutil.move(filenameWithDirName, subDir)
          
            # substitute the original file name by the new one
##            print('line: %s' % line)
            line = line.replace(filenameOrig, relRbsFilenameExtended)
##            print('line: %s' % line)

            xvpCommonRBSPath[filenameOrig] = relRbsFilenameExtended

            thisFileChanged = True

            # this file was changed, so the reference to this file cannot be changed
            refCanBeChanged = False
          else:
            refCanBeChanged = False
            print('INFO:  processPanels(%s): File exists in common RBS and in feature test RBS with same content, but referenced files changed, not substituted:  %s (%s)\n' % (XvpFileIn, filenameWithDirName, relRbsFilename))

        elif os.path.isfile(filenameWithDirName) and os.path.isfile(absRbsFilename) and not filecmp.cmp(filenameWithDirName, absRbsFilename, shallow=True):
          # file exists in the common RBS and in the feature test RBS and the contents are NOT the same
          # keep the file from the feature test RBS
          print('INFO:  processPanels(%s): File exists in common RBS and in feature test RBS, but different content, not substituted: %s (%s)\n' % (XvpFileIn, filenameWithDirName, relRbsFilename))
          refCanBeChanged = False
          # recursive call
          processPanels(filenameWithDirName, True, relRbsPathExtended, folderForRemovedFiles, calledFromMAINcfg)

        elif not os.path.isfile(filenameWithDirName) and os.path.isfile(absRbsFilename):
          # file not exists in the feature test RBS, but in the common RBS
          print('INFO:  processPanels(%s): File only exists in common RBS, path will be adjusted: %s\n' % (XvpFileIn, filenameWithDirName))
          # substitute the original file name by the new one
          line = line.replace(filenameWithDirName, relRbsFilenameExtended)

          thisFileChanged = True

          # this file was changed, so the reference to this file cannot be changed
          refCanBeChanged = False

        else:
          print('WARNING: processPanels(%s): File is configured in %s, but neither exists in feature test RBS nor in common RBS: %s\nMaybe the absolute path exceeds 260 chars.\n' % (XvpFileIn, XvpFileIn, filenameWithDirName))
          pass

    # write the original or the modified line
    fo.write(line)

  fo.close()
  fi.close()

  if not thisFileChanged:
    # backup copy can be removed
    os.remove(xvpBackupPath)

  return refCanBeChanged

##
# Process all files of type xvp.
# They can reference other xvp files.
#
# @param[in]  relRbsPath    relative path to the common RBS
# @param[in]  folderForRemovedFiles folder to store backup copies of the files removed from the feature test RBS
#
def processRemainingPanels(relRbsPath, folderForRemovedFiles):

  print('processRemainingPanels() called')

  # process all files of type XVP
  for root, dirs, files in os.walk('panels'):
    for file in files:
        if file.endswith(".xvp"):
          filePath = os.path.join(root, file)
#          try:
          # it can be that a file was already removed, so call this function only for existing files
          if os.path.isfile(filePath):
            print('processRemainingPanels(): processing %s' % filePath)
            processPanels(filePath, False, relRbsPath, folderForRemovedFiles, False)
#         except:
#          print('processRemainingPanels(): exception while processing file: %s' % filePath)

##
# Process the MAIN.cfg file.
#
# @param[in]  MAINcfgIn   original file
# @param[in]  MAINcfgOut  new file to be written with the substituted paths
# @param[in]  relRbsPath  relative path to the common RBS
# @param[in]  folderForRemovedFiles folder to store backup copies of the files removed from the feature test RBS
#
def processMAINcfg(MAINcfgIn, MAINcfgOut, relRbsPath, folderForRemovedFiles):

  fi = open(MAINcfgIn,  'r')
  fo = open(MAINcfgOut, 'w')

  for line in fi:
    if line.lstrip().startswith('<VFileName V7 QL>') or line.lstrip().startswith('<VFileName V7 BQL>'):
      # extract the file name
      match = fileNamePattern.search(line)
      if match:
        filename = match.group()
        # one of the files to be processed
        # no empty path
        # no path outside the shared RBS root directory
        # no path starting with C: and D:
        # no files to be ignored
        if (processedFilesPattern.search(filename)) and \
           (filename != '""') and \
           (not filename.startswith('"..')) and \
           (not filename.startswith('"C:')) and \
           (not filename.startswith('"D:')) and \
           (filename not in ignoredFiles):

          # remove leading and trailing quotation marks
          filenameStripped = filename.strip('"')

          # join the relative path to the RBS root directory with the file name
          relRbsFilename = '.\%s' % os.path.join(relRbsPath, filenameStripped)
          absRbsFilename = os.path.abspath(os.path.join(os.getcwd(), relRbsFilename))

          if debug:
            print('DEBUG: processMAINcfg(): filenameStripped = %s' % filenameStripped)
            print('DEBUG: processMAINcfg(): relRbsFilename   = %s' % relRbsFilename)
            print('DEBUG: processMAINcfg(): absRbsFilename   = %s\n' % absRbsFilename)
          
          #print('cwd            = %s' % os.getcwd())
          #ft=open(relRbsFilename, "r")

          if os.path.isfile(filenameStripped) and not os.path.isfile(absRbsFilename):
            # file only exists in the feature test RBS
            print('INFO:  processMAINcfg(): File only exists in feature test RBS, not substituted: %s\n' % filenameStripped)

          elif os.path.isfile(filenameStripped) and os.path.isfile(absRbsFilename) and filecmp.cmp(filenameStripped, absRbsFilename, shallow=True):
            # file exists in the common RBS and in the feature test RBS and the contents are the same

            if xvpFileNamePattern.search(filenameStripped):
              canBeChanged = processPanels(filenameStripped, False, relRbsPath, folderForRemovedFiles, True)

            if (not xvpFileNamePattern.search(filenameStripped)) or (xvpFileNamePattern.search(filenameStripped) and canBeChanged == True):
              # file exists in the common RBS and in the feature test RBS and the contents are the same
              print('INFO:  processMAINcfg(): File exists in common RBS and in feature test RBS with same content, substituted:  %s (%s)\n' % (filenameStripped, relRbsFilename))

              # create a subfolder in the folderForRemovedFiles
              subDir = os.path.join(folderForRemovedFiles, os.path.dirname(filenameStripped))
              if not os.path.isdir(subDir):
                os.makedirs(subDir)

              # move the file from the feature test RBS to the folder for removed files
              shutil.move(filenameStripped, subDir)
            
              # substitute the original file name by the new one
              #print('%s %s %d' % (filename, relRbsFilename, filecmp.cmp(filenameStripped, relRbsFilename, shallow=False)))
              line = line.replace(filenameStripped, relRbsFilename)

          elif os.path.isfile(filenameStripped) and os.path.isfile(absRbsFilename) and not filecmp.cmp(filenameStripped, absRbsFilename, shallow=True):
            # file exists in the common RBS and in the feature test RBS and the contents are NOT the same
            # keep the file from the feature test RBS
            #print('%s %s %d' % (filename, relRbsFilename, filecmp.cmp(filenameStripped, relRbsFilename, shallow=False)))
            print('INFO:  processMAINcfg(): File exists in common RBS and in feature test RBS, but different content, not substituted: %s (%s)\n' % (filenameStripped, relRbsFilename))

            if xvpFileNamePattern.search(filenameStripped):#
              # check all referenced XVP files in this file
              processPanels(filenameStripped, True, relRbsPath, folderForRemovedFiles, True)

          elif not os.path.isfile(filenameStripped) and os.path.isfile(absRbsFilename):
            # file not exists in the feature test RBS, but in the common RBS
            print('INFO:  processMAINcfg(): File only exists in common RBS, path will be adjusted: %s\n' % filenameStripped)
            # substitute the original file name by the new one
            line = line.replace(filenameStripped, relRbsFilename)

          else:
            print('WARNING: processMAINcfg(): File is configured in %s, but neither exists in feature test RBS nor in common RBS: %s\nMaybe the absolute path exceeds 260 chars.\n' % (MAINcfg, filenameStripped))
            pass


    # write the original or the modified line
    fo.write(line)

  fo.close()
  fi.close()

##
# Create a folder to store backup copies of the files removed from the feature test RBS.\n
# The folder name build of the static text '_removedFiles_' followed by the current time stamp
#
# @return path to the backup folder
#
def createFolderForRemovedFiles():

  newDir = os.path.join(os.getcwd(), '_removedFiles_%s' % timeStamp)
                        
  if not os.path.isdir(newDir):
    os.mkdir(newDir)

  return newDir


##
# Main function.
#
def main():

  print('\n')

  rbsPath = findCommonRBSLocation()

  if rbsPath != '':
    relRbsPath = os.path.relpath(rbsPath,
                                 os.getcwd())

    folderForRemovedFiles = createFolderForRemovedFiles()

    mainCfgTuple = getMAINcfg(rbsPath)

    # first entry of the tuple is the return code
    if mainCfgTuple[0]:
      # third entry of the tuple is the backup-ed MAIN.cfg as input
      # second entry of the tuple is the MAIN.cfg to be created
      processMAINcfg(mainCfgTuple[2], mainCfgTuple[1], relRbsPath, folderForRemovedFiles)

      print(processedPanels)
      # process the panels that are not already processes by processMAINcfg
      processRemainingPanels(relRbsPath, folderForRemovedFiles)

    else:
      # error handling is done in getMAINcfg()
      pass
      
  else:
    # error handling is done in findCommonRBSLocation()
    pass


main()