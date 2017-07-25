import random
import time
import sys

random.seed()


def genList(size):
    randomList = []

    # initialize random list with values between 0 and 100
    for i in range(size):
        randomList.append(random.randint(0, 10))

    return randomList


# return the sum of all elements in the list
# This is the same as "return sum(inList)" but in long form for readability and emphasis
def sumList(inList):
    finalSum = 0

    # iterate over all values in the list, and calculate the cummulative sum
    for value in inList:
        finalSum = finalSum + value
    return finalSum


if __name__ == '__main__':
    N = int(10000000)
    # mark the start time
    startTime = time.time()
    # create a random list of N integers
    myList = genList(N)
    finalSum = sumList(myList)
    # mark the end time
    endTime = time.time()
    # calculate the total time it took to complete the work
    workTime = endTime - startTime

    # print results
    print "The job took " + str(workTime) + " seconds to complete"
    print "The final sum was: " + str(finalSum)

    """
    The job took 10.4809031487 seconds to complete
    The final sum was: 49984758
    """
