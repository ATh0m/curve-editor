import Charts 1.0
import QtQuick 2.0

Item {
    width: 600; height: 600

    PieChart {
        id: aPieChart
        anchors.centerIn: parent
        width: 600; height: 600
        color: "red"

        onChartCleared: console.log("The chart has been cleared") //?
    }

    MouseArea {
        anchors.fill: parent
        onClicked: aPieChart.clearChart()
    }

    Text {
        anchors { bottom: parent.bottom; horizontalCenter: parent.horizontalCenter; bottomMargin: 20 }
        text: "Click anywhere to clear the chart"
    }
}