import QtQuick 2.12
import QtQuick.Controls 2.12

Rectangle {
    id: root
    property string title: ""
    radius: 12
    color: Qt.rgba(1, 1, 1, 0.08)
    border.color: Qt.rgba(1, 1, 1, 0.22)

    Column {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 8

        Label {
            text: root.title
            color: "#a0d5ff"
            font.pixelSize: 13
            font.bold: true
        }

        Item {
            id: contentHolder
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: parent.height - 26
            clip: true
        }
    }
}
