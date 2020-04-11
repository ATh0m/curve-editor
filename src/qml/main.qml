import Charts 1.0
import QtQuick 2.0
import QtQuick.Controls 2.4
import QtQuick.Window 2.0
import Qt.labs.platform 1.0

ApplicationWindow {
    id: window
    width: 640
    height: 480
    visible: true
    title: "Hello Python World!"

    MenuBar {
        id: menuBar

        Menu {
            id: fileMenu
            title: "File"
            MenuItem { text: "Quit"; onTriggered: Qt.quit() }
        }
    }

    Whiteboard {
        id: whiteboard
        anchors.centerIn: parent
        anchors.fill: parent

        color: "red"

        onChartCleared: console.log("The chart has been cleared")

        MouseArea {
            anchors.fill: parent
            onClicked: {
                console.log(mouse.x, mouse.y)
                fruitModel.append({"cost": 0, "name": mouse.x + ", " + mouse.y})
                whiteboard.clearChart()
            }
        }
    }

    Rectangle {
        width: 200; height: 200

        ListModel {
            id: fruitModel

            ListElement {
                name: "Point #1"
                cost: 2.45
                attributes: [
                    ListElement { description: "Core" },
                    ListElement { description: "Deciduous" }
                ]
            }
            ListElement {
                name: "Orange"
                cost: 3.25
                attributes: [
                    ListElement { description: "Citrus" }
                ]
            }
            ListElement {
                name: "Banana"
                cost: 1.95
                attributes: [
                    ListElement { description: "Tropical" },
                    ListElement { description: "Seedless" }
                ]
            }
        }

        Component {
            id: fruitDelegate
            Item {
                width: 200; height: 50
                Text { id: nameField; text: name }
                Text { text: '$' + cost; anchors.left: nameField.right }
                Row {
                    anchors.top: nameField.bottom
                    spacing: 5
                    Text { text: "Attributes:" }
                    Repeater {
                        model: attributes
                        Text { text: description }
                    }
                }
                // Double the price when clicked.
                MouseArea {
                    anchors.fill: parent
                    onClicked: fruitModel.setProperty(index, "cost", cost * 2)
                }
            }
        }

        ListView {
            anchors.fill: parent
            model: fruitModel
            delegate: fruitDelegate
        }
    }
}
