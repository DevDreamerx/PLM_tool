import QtQuick 2.12
import QtQuick.Controls 2.12

Rectangle {
    id: root
    property string title: ""
    property string value: ""
    property string trend: ""
    property color trendColor: "#7ee787"
    radius: 10
    color: Qt.rgba(1, 1, 1, 0.08)
    border.color: Qt.rgba(1, 1, 1, 0.22)

    Column {
        anchors.fill: parent
        anchors.margins: 14
        spacing: 6

        Label {
            text: root.title
            color: "#a0d5ff"
            font.pixelSize: 12
        }
        Label {
            text: root.value
            color: "#ffffff"
            font.pixelSize: 24
            font.bold: true
        }
        Label {
            text: root.trend
            color: root.trendColor
            font.pixelSize: 11
        }
    }
}
