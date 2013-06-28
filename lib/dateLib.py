"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: dateLib.py
#
# Author: Daniel Lemay
#
# Date: 2005-09-15
#
# Description:
#
#############################################################################################
"""
import time

MINUTE = 60
HOUR = 60 * MINUTE
DAY = 24 * HOUR

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

now = time.mktime

def getTimestamp(format="%Y%m%d%H%M%S"):
    return time.strftime(format, time.gmtime())

def getDatesInSeconds(startDate="", endDate="", span="0", offset="0"):
    if startDate:
        startDate = getSecondsSinceEpoch(startDate)
    else:
        startDate = ""

    if endDate:
        endDate = getSecondsSinceEpoch(endDate)
    else:
        endDate = ""

    if startDate and endDate:
        if startDate <= endDate:
            return (startDate, endDate)
        else:
            return (startDate, None)
    elif startDate and span:
        return convertStartDateSpanInDates(startDate, eval(span))
    elif endDate and span:
        return convertEndDateSpanInDates(endDate, eval(span))
    elif span and offset:
        return convertSpanOffsetInDates(eval(span), eval(offset))
    elif span:
        return convertSpanOffsetInDates(eval(span), 0)
    else:
        return None, None

def convertStartDateSpanInDates(startDate, span):
    """
    startDate in seconds since Epoch
    span in minutes
    """
    endDate = startDate + span * MINUTE
    return startDate, endDate

def convertEndDateSpanInDates(endDate, span):
    """
    endDate in seconds since Epoch
    span in minutes
    """
    startDate = endDate - span * MINUTE
    return startDate, endDate

def convertSpanOffsetInDates(span, offset):
    """
    span is in minutes
    offset is in minutes
    startDate, endDate in seconds
    """
    seconds = time.mktime(time.gmtime())

    if span > offset:
        offset = 0
        startDate = seconds - span * MINUTE
        endDate = seconds
    else:
        startDate = seconds - offset * MINUTE
        endDate = seconds - (offset - span) * MINUTE

    return startDate, endDate

def getYYGGgg():
    return time.strftime("%d%H%M", time.gmtime())

def getISODateParts(date):
    # year, month, day
    return (date[0:4], date[4:6], date[6:])

def getISODateDashed(ISODate):
    return ISODate[0:4] + '-' + ISODate[4:6] + '-' + ISODate[6:]

def getMonthAbbrev(month):
    return MONTHS[int(month) -1]

"""
def getSecondsSinceEpoch(date='08/30/05 20:06:59'):
    try:
        timeStruct = time.strptime(date, '%m/%d/%y %H:%M:%S')
    except:
        print date
    return time.mktime(timeStruct)
"""
def getSecondsSinceEpoch(date='2005-08-30 20:06:59', format='%Y-%m-%d %H:%M:%S'):
    try:
        timeStruct = time.strptime(date, format)
    except:
        print date
    return time.mktime(timeStruct)
    
def getYesterdayInSeconds():
    return now(time.gmtime()) - DAY

def getDateInSecondsFormatted(seconds, format="%Y-%m-%d %H:%M:%S"):
    return time.strftime(format, time.gmtime(seconds))

def getTodayFormatted(format='%Y%m%d'):
    return time.strftime(format, time.gmtime())

def getYesterdayFormatted(format='%Y%m%d'):
    return time.strftime(format, time.gmtime(getYesterdayInSeconds()))

def getISODate(string, dash=True):
    # Format of string is : MM/DD/YY
    month, day, year = string.split('/')
    year = 2000 + int(year)
    if dash: return (str(year) + '-' + month + '-' + day)
    else: return (str(year) + month + day)
    # In python 2.3 and later
    #return datetime.date(year, month, day).isoformat()

def ISOToBad(ISODate, dash=False):
    if dash:
        raise 'Not implemented'
    else:
        year = ISODate[2:4]
        month = ISODate[4:6]
        day = ISODate[6:8]
        return  '%s/%s/%s' % (month, day, year)

def getSeconds(string):
    # Should be used with string of following format: hh:mm:ss
    hours, minutes, seconds = string.split(':')
    return int(hours) * HOUR + int(minutes) * MINUTE + int(seconds)

def getSeparators(width=DAY, interval=20*MINUTE):
    separators = []
    for value in range(interval, width+interval, interval):
        separators.append(value)
    
    return separators

def getEmptyBuckets(separators=getSeparators()):
    buckets = {}
    buckets[0] = [0, separators[0], 0, 0.0] # min, max, count, total_lat

    for i in range(1, len(separators)):
        buckets[i] = [separators[i-1], separators[i], 0, 0.0]    
    return buckets

if __name__ == '__main__':

    """
    getSecondsSinceEpoch('09/01/05 21:53:15')
    print now(time.gmtime())
    print getYesterdayInSeconds()
    print getYesterdayFormatted()
    print getSeconds('08:07:04')
    print getSeparators()
    print len(getSeparators())
    print len(getEmptyBuckets())
    print ISOToBad('20050830') 
    print ISOToBad('20050830', True) 
    print getISODateParts('20050908')
    print getMonthAbbrev('12')
    """
    """
    from bisect import bisect
    sep = getSeparators(DAY, 60)
    insert_point = bisect(sep, 179)
    print insert_point
    """
    print getISODateDashed('20051207')
    print getSecondsSinceEpoch('1970-01-01 00:00:00')
    print getSecondsSinceEpoch('1970-01-01 00:00:05')
    print getYYGGgg()
