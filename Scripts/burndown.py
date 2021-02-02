import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import json
import numpy as np
import datetime

def sortByDateEstimate(sprint):
    return datetime.date.fromisoformat(sprint['dateEstimate'])

def sortByStringDate(dateString):
    return datetime.date.fromisoformat(dateString)

class Burndown:
    def __init__(self):
        # Open the sprints JSON file to obtain the
        # necessary data
        with open('sprints.json') as json_file:
            self.data = json.load(json_file)

    def createBurndownChart(self):
        # Create the base figure
        fig = plt.figure()
        ax = plt.axes()
        # Sort the milestones by the estimated date of
        # completion.
        milestonesSortedByEstimatedDate = sorted(
            self.data['sprints'],
            key=sortByDateEstimate,
            reverse=True
        )
        # Iterate through the list of milestones to plot
        # the date estimates as red diamonds. Create
        # the list of tasks, and a placeholder point
        # estimate array for use later.
        allTasks = []
        placeholderPointEstimateSums = [0]
        futurePointEstimate = 0
        milestoneXAxis = [
            datetime.date.fromisoformat(
                self.data['startDate']
            )
        ]
        milestoneYAxis = [0]
        for milestone in milestonesSortedByEstimatedDate:
            milestoneXAxis.insert(
                1,
                datetime.date.fromisoformat(milestone['dateEstimate'])
            )
            milestoneYAxis.insert(
                0,
                milestoneYAxis[0] + milestone['pointEstimate']
            )
            # Add each task to allTasks
            tasks = milestone['tasks']
            if len(tasks) <= 0:
                futurePointEstimate += milestone['pointEstimate']
            else:
                for task in tasks:
                    allTasks.append(task)
            # Calculate the placeholderPointEstimateSum
            placeholderPointEstimateSums.insert(
                0,
                placeholderPointEstimateSums[0] + milestone['pointEstimate']
            )
        # Exempt the first entry from the placeholderPointEstimateSums array
        placeholderPointEstimateSums = placeholderPointEstimateSums[1:]
        # Plot the milestone data as a red line with diamonds
        ax.plot(
            milestoneXAxis,
            milestoneYAxis,
            'rD-',
            label='Milestone Estimates',
            zorder=2
        )
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.set_xticks(milestoneXAxis)
        ax.set_ylim(0, milestoneYAxis[0]*1.05)
        ax.vlines(milestoneXAxis, 0, milestoneYAxis, linestyle="dashed", color='r')
        fig.autofmt_xdate()
        # Compile a unique list of dates changed
        allDatesChanged = []
        for task in allTasks:
            if not task['dateCreated'] in allDatesChanged:
                allDatesChanged.append(task['dateCreated'])
            dateCompleted = task['dateCompleted']
            if dateCompleted and not dateCompleted in allDatesChanged:
                allDatesChanged.append(dateCompleted)
        # Sort the unique list of dates changed
        sortedDatesChanged = sorted(
            allDatesChanged,
            key=sortByStringDate
        )
        # Create a list of milestone dates for comparison
        sortedMilestoneDates = []
        for milestone in milestonesSortedByEstimatedDate:
            sortedMilestoneDates.insert(
                0,
                datetime.date.fromisoformat(milestone['dateEstimate'])
            )
        # Iterate through the list of changed dates
        actualXAxis, actualYAxis = [], []
        placeholderIndex = 0
        actualPointEstimate = 0
        for date in sortedDatesChanged:
            dateAsDatetime = datetime.date.fromisoformat(
                date
            )
            actualXAxis.append(dateAsDatetime)
            # If the date is greater than or equal to the
            # date specified as the end date of the current
            # sprint, use a new placeholder
            if dateAsDatetime >= sortedMilestoneDates[placeholderIndex]:
                placeholderIndex += 1
            # Fetch the proper placeholder point estimate for
            # the future
            placeholderPointEstimate = placeholderPointEstimateSums[placeholderIndex]\
            # Fetch all tasks whose creation date matches date
            createdOnDate = [v for v in allTasks if v['dateCreated'] == date]
            for task in createdOnDate:
                actualPointEstimate += task['pointEstimate']
            # Fetch all tasks whose completed date matches date
            completedOnDate = [v for v in allTasks if v['dateCompleted'] == date]
            for task in completedOnDate:
                actualPointEstimate -= task['pointEstimate']
            # Append the actual point estimate + the placeholder
            # point estimate to the y axis array
            actualYAxis.append(actualPointEstimate + placeholderPointEstimate)
        ax.plot(
            actualXAxis,
            actualYAxis,
            'bo-',
            label='Actual Progress',
            zorder=3,
            linewidth=2,
            markersize=4,
        )
        # Set the x-axis and y-axis labels as well as the
        # title of the plot
        ax.set_title('Burndown Chart')
        ax.set_xlabel('Date of Completion')
        ax.set_ylabel('Estimated Man Hours Remaining')
        # Set the legend of the chart
        ax.legend()

        plt.show()
        


if __name__ == '__main__':
    burndown = Burndown()
    burndown.createBurndownChart()