# Uncomment 3 instances of msvcrt to have user press key after finished to exit
import os, math, time, sys, re, tkinter as tk#, msvcrt
from tkinter import filedialog

# Presents file dialog to ask user for directory to traverse
# Returns all files matching search criteria in findLargeFiles
def promptUserForDir():
    root = tk.Tk()
    root.withdraw()
    directoryToSearch = filedialog.askdirectory()
    root.update()
    sys.stdout.flush()

    return findLargeFiles(directoryToSearch)

# Traverses the given directory
# Returns a list of files matching the criteria
def findLargeFiles(directoryToSearch):
    filesToSplit = []
    for root, dirs, files in os.walk(directoryToSearch):
        for eachFile in files:
            eachFileFullPath = os.path.join(root, eachFile)
            if eachFile.endswith(".lvm") and os.path.getsize(eachFileFullPath) > 200000000:
                filesToSplit.append(eachFileFullPath)

    return filesToSplit

# Finds the time offset necessary for writing files after the first split
# Returns a float, which will be substracted from each time in the later files
def getTimeOffset(firstLine):
    nums = firstLine.split('\t')
    timeOffset = float(nums[0])

    return timeOffset

# Writes a time-updated line for split files 2 and higher, since each file's
# time should start at 0. Each file after the first partition will start
# counting at 0 by writing each line's time subtracted by the timeOffset
def writeUpdatedLine(line, timeOffset):
    indexOfFirstTab = line.find('\t')
    firstFloat = float(line[0:indexOfFirstTab]) - timeOffset
    restOfLine = line[indexOfFirstTab:]

    return('{:f}'.format(firstFloat) + restOfLine)

### PROGRAM BEGIN ###

# Retrieves files to be split from user-specified directory
filesToSplit = promptUserForDir()

print("Found " + str(len(filesToSplit)) + " files to split.")

# Close program if no files found
# Uncomment the three lines to have user press key to exit
if(len(filesToSplit) == 0):
    #print("Press any key to exit.")
    #while(True):
        #if msvcrt.kbhit():
            exit()

progressCount = 1
for fileToSplit in filesToSplit:
    print("  ---------------------------------")
    print("  Splitting file " + str(progressCount) + " of " + str(len(filesToSplit)) + ".")
    origFile = open(fileToSplit, "r")

    # Finds the file's length in number of lines
    numLines = 0
    for line in origFile:
        numLines += 1

    # Calculates how to partition files
    fileSize = os.stat(origFile.name).st_size
    print("File size is " + str(fileSize/1000000) + " MB.")
    numFiles = int(math.ceil(fileSize / 200000000.0))
    print("Splitting into " + str(numFiles) + " files.")
    linesPerFile = numLines / numFiles

    # Vars to keep track of file writing
    lineProgress = 0 # This is compared to linesPerFile to signal file-writing completion
    currentFile = 1
    timeOffset = float(0) # For 1st partition, times begin at 0, so offset is 0

    # File directories/names used for writing new files
    newFile = None
    newFileDirectory = os.path.dirname(fileToSplit)
    origFileName = os.path.splitext(os.path.basename(fileToSplit))[0]
    newFilePath = newFileDirectory + "/" + origFileName + "_split"

    # Used to store the header to be added at the top of each new file
    headerDone = False
    header = ""

    # Reopen the file
    origFile = open(fileToSplit, "r")

    # Main loop to extract header and write split files
    for line in origFile:
        # Extract the header, if block skipped when header is found
        if(not headerDone):
            header += line
            if line.startswith("X_Value"): # Beginning of last header line
                headerDone = True
                print("Ready to write a file!")
                # First, check if split file name already exists, if so, update
                # First, check if split file name already exists, if so, update
                fileExists = True
                duplicateFileCount = 1
                testFilePath = newFilePath + str(currentFile) + ".lvm"
                while(fileExists):
                    if(os.path.isfile(testFilePath)):
                        testFilePath = newFilePath + str(currentFile) + "_dup" + str(duplicateFileCount) + ".lvm"
                        duplicateFileCount = duplicateFileCount + 1
                    else:
                        fileExists = False

                # Since the header is found before file writing, the first new
                # file is now created/opened and the header is written
                print("    Writing split file 1.")
                newFile = open(testFilePath, "w+")
                newFile.writelines(header)

        # If the number of lines has been met for a file, close it, create/open
        # the next file, and write the header and first line
        elif(lineProgress >= linesPerFile):
            # Close file and reset progress
            newFile.close()
            lineProgress = 0

            # Increment to the next file
            currentFile += 1

            # First, check if split file name already exists, if so, update
            fileExists = True
            duplicateFileCount = 1
            testFilePath = newFilePath + str(currentFile) + ".lvm"
            while(fileExists):
                if(os.path.isfile(testFilePath)):
                    testFilePath = newFilePath + str(currentFile) + "_dup" + str(duplicateFileCount) + ".lvm"
                    duplicateFileCount = duplicateFileCount + 1
                else:
                    fileExists = False

            # Create new file, write the header
            print("    Writing split file " + str(currentFile) + ".")
            newFile = open(testFilePath, "w+")
            newFile.write(header)

            # Get timeOffset to update times for new files to start at 0.0
            timeOffset = getTimeOffset(line)

            # Write the updated file
            newFile.write(writeUpdatedLine(line, timeOffset))
            lineProgress += 1

        # Write updated lines while under the new file size limit
        else:
            newFile.write(writeUpdatedLine(line, timeOffset))
            lineProgress += 1

    # Close the last split file and original file
    newFile.close()
    origFile.close()

    # Print progress and increment
    print("  Finished splitting file " + str(progressCount) + " of " + str(len(filesToSplit)) + ".")
    progressCount += 1

print("  ---------------------------------")
print("Finished splitting " + str(progressCount - 1) + " files.")

# Uncomment to close program after any key is pressed
#print("Press any key to exit.")
#while(True):
    #if msvcrt.kbhit():
        #break
