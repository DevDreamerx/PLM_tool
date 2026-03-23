import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12
import QtCharts 2.3

import "components"
import "themes"

ApplicationWindow {
    id: window
    visible: true
    width: 1280
    height: 860
    title: "技术状态管理助手 - 仪表盘"

    Theme { id: theme }

    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: theme.bgA }
            GradientStop { position: 0.5; color: theme.bgB }
            GradientStop { position: 1.0; color: theme.bgC }
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 18
            spacing: 18

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 88
                radius: 12
                color: Qt.rgba(1, 1, 1, 0.08)
                border.color: Qt.rgba(1, 1, 1, 0.22)

                Column {
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 4
                    Text {
                        text: "航空技术状态质量看板"
                        color: theme.textMain
                        font.pixelSize: 22
                        font.bold: true
                    }
                    Text {
                        text: "Aviation Technical State Quality Dashboard | DO-178C 风险监控"
                        color: theme.textSub
                        font.pixelSize: 12
                    }
                    Text {
                        text: "数据更新时间: " + (dashboardProvider.data.update_time || "--")
                        color: theme.textSub
                        font.pixelSize: 12
                    }
                }
            }

            GridLayout {
                Layout.fillWidth: true
                Layout.preferredHeight: 210
                columns: 3
                rowSpacing: 14
                columnSpacing: 14

                KpiCard {
                    title: "问题总数"
                    value: String(dashboardProvider.data.kpi ? dashboardProvider.data.kpi.total : 0)
                    trend: dashboardProvider.data.kpi ? dashboardProvider.data.kpi.trend_text : ""
                    trendColor: theme.success
                }
                KpiCard {
                    title: "问题密度"
                    value: String(dashboardProvider.data.kpi ? dashboardProvider.data.kpi.density : 0)
                    trend: "问题/型号"
                    trendColor: theme.textSub
                }
                KpiCard {
                    title: "落实率"
                    value: String(dashboardProvider.data.kpi ? dashboardProvider.data.kpi.implement_rate : 0) + "%"
                    trend: "更改落实"
                    trendColor: theme.success
                }
                KpiCard {
                    title: "缺失更改"
                    value: String(dashboardProvider.data.kpi ? dashboardProvider.data.kpi.missing : 0)
                    trend: "需补全资料"
                    trendColor: theme.warning
                }
                KpiCard {
                    title: "未落实"
                    value: String(dashboardProvider.data.kpi ? dashboardProvider.data.kpi.unimplemented : 0)
                    trend: "风险关注"
                    trendColor: theme.danger
                }
                KpiCard {
                    title: "平均存续"
                    value: String(dashboardProvider.data.kpi ? dashboardProvider.data.kpi.avg_age : 0)
                    trend: "天"
                    trendColor: theme.textSub
                }
            }

            GridLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                columns: 2
                rowSpacing: 16
                columnSpacing: 16

                ChartCard {
                    title: "缺失/未落实帕累托"
                    Layout.fillWidth: true
                    Layout.preferredHeight: 280
                    ChartView {
                        id: paretoChart
                        anchors.fill: parent
                        antialiasing: true
                        backgroundColor: "transparent"
                        legend.visible: false
                    }
                }
                ChartCard {
                    title: "问题趋势（近8周）"
                    Layout.fillWidth: true
                    Layout.preferredHeight: 280
                    ChartView {
                        id: trendChart
                        anchors.fill: parent
                        antialiasing: true
                        backgroundColor: "transparent"
                        legend.visible: false
                    }
                }
                ChartCard {
                    title: "问题严重度分布"
                    Layout.fillWidth: true
                    Layout.preferredHeight: 260
                    ChartView {
                        id: severityChart
                        anchors.fill: parent
                        antialiasing: true
                        backgroundColor: "transparent"
                        legend.visible: true
                        legend.labelColor: theme.textSub
                    }
                }
                ChartCard {
                    title: "型号问题热力分布"
                    Layout.fillWidth: true
                    Layout.preferredHeight: 260
                    HeatmapCanvas {
                        id: heatmapCanvas
                        anchors.fill: parent
                        xLabels: dashboardProvider.data.heatmap ? dashboardProvider.data.heatmap.x : []
                        yLabels: dashboardProvider.data.heatmap ? dashboardProvider.data.heatmap.y : []
                        values: dashboardProvider.data.heatmap ? dashboardProvider.data.heatmap.values : []
                    }
                }
                ChartCard {
                    title: "问题存续周期分布"
                    Layout.fillWidth: true
                    Layout.columnSpan: 2
                    Layout.preferredHeight: 260
                    ChartView {
                        id: ageChart
                        anchors.fill: parent
                        antialiasing: true
                        backgroundColor: "transparent"
                        legend.visible: false
                    }
                }
                ChartCard {
                    title: "质量门禁达成情况"
                    Layout.fillWidth: true
                    Layout.columnSpan: 2
                    Layout.preferredHeight: 300
                    PolarChartView {
                        id: radarChart
                        anchors.fill: parent
                        antialiasing: true
                        backgroundColor: "transparent"
                        legend.visible: false
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                Layout.preferredHeight: 40
                spacing: 10

                Item { Layout.fillWidth: true }

                Button {
                    text: "打开旧界面"
                    background: Rectangle {
                        radius: 8
                        color: Qt.rgba(1, 1, 1, 0.08)
                        border.color: Qt.rgba(160/255, 213/255, 255/255, 0.6)
                    }
                    contentItem: Text {
                        text: parent.text
                        color: theme.textSub
                        font.pixelSize: 12
                    }
                    onClicked: uiBridge.openLegacy()
                }
                Button {
                    text: "刷新"
                    background: Rectangle {
                        radius: 8
                        color: Qt.rgba(160/255, 213/255, 255/255, 0.2)
                        border.color: Qt.rgba(160/255, 213/255, 255/255, 0.6)
                    }
                    contentItem: Text {
                        text: parent.text
                        color: theme.textMain
                        font.pixelSize: 12
                    }
                    onClicked: dashboardProvider.refresh()
                }
            }
        }
    }

    Component.onCompleted: {
        updateAllCharts()
    }

    Connections {
        target: dashboardProvider
        onDataChanged: updateAllCharts()
    }

    function updateAllCharts() {
        updatePareto()
        updateTrend()
        updateSeverity()
        updateAge()
        updateRadar()
        heatmapCanvas.requestPaint()
    }

    function applyAxisStyle(axis) {
        if (!axis) return
        axis.labelsColor = "#e2f1ff"
        axis.linePen.color = "#3a5663"
        axis.gridLineColor = "#28414b"
    }

    function updatePareto() {
        paretoChart.removeAllSeries()
        paretoChart.axisX = null
        paretoChart.axisY = null
        var series = Qt.createQmlObject('import QtCharts 2.3; BarSeries {}', paretoChart)
        var barSet = Qt.createQmlObject('import QtCharts 2.3; BarSet {}', paretoChart)
        barSet.label = "问题数量"
        var labels = []
        var items = dashboardProvider.data.pareto || []
        for (var i = 0; i < items.length; i++) {
            barSet.append(items[i].value)
            labels.push(items[i].label)
        }
        series.append(barSet)

        var line = Qt.createQmlObject('import QtCharts 2.3; LineSeries {}', paretoChart)
        line.name = "累计占比"
        var total = 0
        for (i = 0; i < items.length; i++) total += items[i].value
        var running = 0
        for (i = 0; i < items.length; i++) {
            running += items[i].value
            line.append(i, total ? (running / total * 100.0) : 0)
        }

        paretoChart.addSeries(series)
        paretoChart.addSeries(line)

        var axisX = Qt.createQmlObject('import QtCharts 2.3; BarCategoryAxis {}', paretoChart)
        axisX.categories = labels
        var axisY = Qt.createQmlObject('import QtCharts 2.3; ValueAxis {}', paretoChart)
        axisY.min = 0
        var axisY2 = Qt.createQmlObject('import QtCharts 2.3; ValueAxis {}', paretoChart)
        axisY2.min = 0
        axisY2.max = 100
        axisY2.alignment = Qt.AlignRight

        paretoChart.setAxisX(axisX, series)
        paretoChart.setAxisY(axisY, series)
        line.attachAxis(axisX)
        line.attachAxis(axisY2)
        applyAxisStyle(axisX)
        applyAxisStyle(axisY)
        applyAxisStyle(axisY2)
        line.color = theme.warning
        series.barWidth = 0.6
    }

    function updateTrend() {
        trendChart.removeAllSeries()
        trendChart.axisX = null
        trendChart.axisY = null

        var line = Qt.createQmlObject('import QtCharts 2.3; LineSeries {}', trendChart)
        var labels = []
        var items = dashboardProvider.data.trend || []
        for (var i = 0; i < items.length; i++) {
            line.append(i, items[i].value)
            labels.push(items[i].label)
        }
        trendChart.addSeries(line)
        var axisX = Qt.createQmlObject('import QtCharts 2.3; CategoryAxis {}', trendChart)
        axisX.labelsPosition = CategoryAxis.AxisLabelsPositionOnValue
        for (i = 0; i < labels.length; i++) {
            axisX.append(labels[i], i)
        }
        var axisY = Qt.createQmlObject('import QtCharts 2.3; ValueAxis {}', trendChart)
        axisY.min = 0
        trendChart.setAxisX(axisX, line)
        trendChart.setAxisY(axisY, line)
        applyAxisStyle(axisX)
        applyAxisStyle(axisY)
        line.color = theme.accent
    }

    function updateSeverity() {
        severityChart.removeAllSeries()
        var pie = Qt.createQmlObject('import QtCharts 2.3; PieSeries {}', severityChart)
        pie.holeSize = 0.45
        var items = dashboardProvider.data.severity || []
        for (var i = 0; i < items.length; i++) {
            var slice = pie.append(items[i].label, items[i].value)
            if (items[i].label === "高") slice.color = theme.danger
            if (items[i].label === "中") slice.color = theme.warning
            if (items[i].label === "低") slice.color = theme.accent
        }
        severityChart.addSeries(pie)
    }

    function updateAge() {
        ageChart.removeAllSeries()
        ageChart.axisX = null
        ageChart.axisY = null
        var barSeries = Qt.createQmlObject('import QtCharts 2.3; BarSeries {}', ageChart)
        var barSet = Qt.createQmlObject('import QtCharts 2.3; BarSet {}', ageChart)
        barSet.label = "数量"
        var labels = []
        var items = dashboardProvider.data.age || []
        for (var i = 0; i < items.length; i++) {
            barSet.append(items[i].value)
            labels.push(items[i].label)
        }
        barSeries.append(barSet)
        ageChart.addSeries(barSeries)
        var axisX = Qt.createQmlObject('import QtCharts 2.3; BarCategoryAxis {}', ageChart)
        axisX.categories = labels
        var axisY = Qt.createQmlObject('import QtCharts 2.3; ValueAxis {}', ageChart)
        axisY.min = 0
        ageChart.setAxisX(axisX, barSeries)
        ageChart.setAxisY(axisY, barSeries)
        applyAxisStyle(axisX)
        applyAxisStyle(axisY)
        barSeries.barWidth = 0.6
    }

    function updateRadar() {
        radarChart.removeAllSeries()
        radarChart.axisAngular = null
        radarChart.axisRadial = null
        var current = Qt.createQmlObject('import QtCharts 2.3; LineSeries {}', radarChart)
        var target = Qt.createQmlObject('import QtCharts 2.3; LineSeries {}', radarChart)
        var radar = dashboardProvider.data.radar || {}
        var labels = radar.labels || []
        var values = radar.current || []
        var targets = radar.target || []

        for (var i = 0; i < labels.length; i++) {
            current.append(i, values[i] || 0)
            target.append(i, targets[i] || 0)
        }
        current.append(0, values[0] || 0)
        target.append(0, targets[0] || 0)

        radarChart.addSeries(current)
        radarChart.addSeries(target)

        var angular = Qt.createQmlObject('import QtCharts 2.3; CategoryAxis {}', radarChart)
        angular.labelsPosition = CategoryAxis.AxisLabelsPositionOnValue
        for (i = 0; i < labels.length; i++) {
            angular.append(labels[i], i)
        }
        var radial = Qt.createQmlObject('import QtCharts 2.3; ValueAxis {}', radarChart)
        radial.min = 0
        radial.max = 100
        radarChart.axisAngular = angular
        radarChart.axisRadial = radial
        radarChart.setAxisAngular(angular, current)
        radarChart.setAxisRadial(radial, current)
        radarChart.setAxisAngular(angular, target)
        radarChart.setAxisRadial(radial, target)
        applyAxisStyle(angular)
        applyAxisStyle(radial)
        current.color = theme.accent
        target.color = theme.success
    }
}
