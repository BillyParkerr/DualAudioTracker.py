import datetime
import os
import re
import sys

import enzyme as enzyme


class VideoFile:
    def __init__(self, FileName, Path):
        self.FileName = FileName
        self.Path = Path


class Show:
    def __init__(self, Title):
        self.Title = Title
        self.Seasons = []

    def addSeason(self, Season):
        self.Seasons.append(Season)


class Season:
    def __init__(self, SeasonNumber):
        self.SeasonNumber = SeasonNumber
        self.EpisodeNumbers = []

    def addEpisodeNumber(self, EpisodeNumber):
        self.EpisodeNumbers.append(EpisodeNumber)


class Release:
    def __init__(self, Title, SeasonNumber, EpisodeNumber):
        self.Title = Title
        self.SeasonNumber = SeasonNumber
        self.EpisodeNumber = EpisodeNumber


def main():
    print(f"Looking for recent dual audio additions in path {sys.argv[1]}")
    entries = getAllRecentlyModifiedFilesInDirectory(sys.argv[1])
    videoFiles = GetAllFilesWithinPaths(entries)
    recentlyModifiedVideoFiles = CheckLastModifiedOfFiles(videoFiles)
    dualAudioVideoFiles = GetFilesWithDualAudio(recentlyModifiedVideoFiles)
    addedDualAudioShows = CreateListOfAddedDualAudioMedia(dualAudioVideoFiles)
    PrintOutAddedDualAudioMedia(addedDualAudioShows)

    
def PrintOutAddedDualAudioMedia(Shows):
    print("The following media has been added in dual audio:")
    for show in Shows:
        print("")
        print(show.Title)
        for season in show.Seasons:
            print(f"Season {season.SeasonNumber}")
            if IsSingleRangeOfNumbers(season.EpisodeNumbers):
                print(f"Episodes {min(season.EpisodeNumbers)}-{max(season.EpisodeNumbers)}")
            else:
                for episodeNumber in season.EpisodeNumbers:
                    print(f"Episode {episodeNumber}")


def IsSingleRangeOfNumbers(episodeNumbers):
    valid = True
    for i in range(len(episodeNumbers)-1):
        if int(episodeNumbers[i])+1 != int(episodeNumbers[i + 1]):
            valid = False

    return valid


def CreateListOfAddedDualAudioMedia(dualAudioVideoFiles):
    releases = FormatIntoReleases(dualAudioVideoFiles)
    addedShows = []
    for release in releases:
        showMatch = False
        seasonMatch = False
        if any(addedShows):
            for show in addedShows:
                if show.Title == release.Title:
                    showMatch = True
                    for season in show.Seasons:
                        if season.SeasonNumber == release.SeasonNumber:
                            season.EpisodeNumbers.append(release.EpisodeNumber)
                            seasonMatch = True
                            break
                    if not seasonMatch:
                        season = Season(release.SeasonNumber)
                        season.EpisodeNumbers.append(release.EpisodeNumber)
                        show.Seasons.append(season)
                        break
            if not showMatch:
                addedShows.append(CreateNewShow(release.Title, release.SeasonNumber, release.EpisodeNumber))
        else:
            addedShows.append(CreateNewShow(release.Title, release.SeasonNumber, release.EpisodeNumber))

    return addedShows


def CreateNewShow(title, seasonNumber, episodeNumber):
    season = Season(seasonNumber)
    season.EpisodeNumbers.append(episodeNumber)
    show = Show(title)
    show.Seasons.append(season)
    return show


def FormatIntoReleases(videoFiles):
    releases = []
    for videoFile in videoFiles:
        releaseTitle = videoFile.FileName.split(" - ")[0]
        releaseNumber = getEpisode(videoFile.FileName)
        releaseSeason = getSeason(videoFile.FileName)
        release = Release(releaseTitle, releaseSeason, releaseNumber)
        releases.append(release)

    return releases


def getSeason(filename):
    match = re.search(
        r'''(?ix)                 # Ignore case (i), and use verbose regex (x)
        (?:                       # non-grouping pattern
          s|season|[-]\s|         # s or season or -whitespace
          )                       # end non-grouping pattern 
        \s*                       # 0-or-more whitespaces
        (\d{2})                   # exactly 2 digits
        ''', filename)
    if match:
        return match.group(1)
    else:
        print(filename)


def getEpisode(filename):
    match = re.search(
        r'''(?ix)                 # Ignore case (i), and use verbose regex (x)
        (?:                       # non-grouping pattern
          e|x|episode|^           # e or x or episode or start of a line
          )                       # end non-grouping pattern 
        \s*                       # 0-or-more whitespaces
        (\d{2})                   # exactly 2 digits
        ''', filename)
    if match:
        return match.group(1)


def GetFilesWithDualAudio(videoFiles):
    dualAudioVideoFiles = []
    for videoFile in videoFiles:
        if videoFile.FileName.endswith(".mkv"):
            with open(videoFile.Path, 'rb') as f:
                mkvinfo = enzyme.MKV(f)
                if len(mkvinfo.audio_tracks) > 1:
                    dualAudioVideoFiles.append(videoFile)
    return dualAudioVideoFiles


def getAllRecentlyModifiedFilesInDirectory(directory):
    scanner = os.scandir(directory)
    recentlyModifiedEntries = []
    for entry in scanner:
        lastModifiedTimestamp = entry.stat().st_mtime
        lastModifiedDateTime = datetime.datetime.fromtimestamp(lastModifiedTimestamp)
        timeDifference = lastModifiedDateTime - (datetime.datetime.utcnow() - datetime.timedelta(30))
        if timeDifference > datetime.timedelta():
            recentlyModifiedEntries.append(entry)

    return recentlyModifiedEntries


def GetAllFilesWithinPaths(entries):
    videoFiles = []
    for entry in entries:
        for (dirpath, subdirs, files) in os.walk(entry.path):
            for file in files:
                if file.endswith(".mkv") or file.endswith(".mp4") or file.endswith(".avi"):
                    videoFile = VideoFile(file, os.path.join(dirpath, file))
                    videoFiles.append(videoFile)

    return videoFiles


def CheckLastModifiedOfFiles(videoFiles):
    recentlyModifiedVideoFiles = []
    for video in videoFiles:
        timestamp = os.path.getctime(video.Path)
        lastModifiedDateTime = datetime.datetime.fromtimestamp(timestamp)
        timeDifference = lastModifiedDateTime - (datetime.datetime.utcnow() - datetime.timedelta(30))
        if timeDifference > datetime.timedelta():
            recentlyModifiedVideoFiles.append(video)

    return recentlyModifiedVideoFiles


if __name__ == '__main__':
    main()
