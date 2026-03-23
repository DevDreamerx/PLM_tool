import QtQuick 2.12

Canvas {
    id: root
    property var xLabels: []
    property var yLabels: []
    property var values: []
    property color lowColor: "#2563eb"
    property color highColor: "#f87171"

    onPaint: {
        var ctx = getContext("2d")
        ctx.reset()
        ctx.fillStyle = "#0f2027"
        ctx.fillRect(0, 0, width, height)

        var paddingLeft = 70
        var paddingTop = 20
        var paddingRight = 20
        var paddingBottom = 32

        var gridWidth = width - paddingLeft - paddingRight
        var gridHeight = height - paddingTop - paddingBottom

        var rows = yLabels.length
        var cols = xLabels.length
        if (rows === 0 || cols === 0) {
            ctx.fillStyle = "#a0d5ff"
            ctx.font = "12px sans-serif"
            ctx.fillText("暂无数据", paddingLeft + 10, paddingTop + 20)
            return
        }

        var maxVal = 0
        for (var i = 0; i < rows; i++) {
            for (var j = 0; j < cols; j++) {
                var v = values[i] ? values[i][j] : 0
                if (v > maxVal) maxVal = v
            }
        }
        if (maxVal === 0) maxVal = 1

        var cellW = gridWidth / cols
        var cellH = gridHeight / rows

        function lerp(a, b, t) { return a + (b - a) * t }
        function colorAt(t) {
            var r1 = 37, g1 = 99, b1 = 235
            var r2 = 248, g2 = 113, b2 = 113
            var r = Math.round(lerp(r1, r2, t))
            var g = Math.round(lerp(g1, g2, t))
            var b = Math.round(lerp(b1, b2, t))
            return "rgb(" + r + "," + g + "," + b + ")"
        }

        for (i = 0; i < rows; i++) {
            for (j = 0; j < cols; j++) {
                var val = values[i] ? values[i][j] : 0
                var t = Math.min(1, val / maxVal)
                ctx.fillStyle = colorAt(t)
                ctx.fillRect(
                    paddingLeft + j * cellW,
                    paddingTop + i * cellH,
                    cellW - 1,
                    cellH - 1
                )
                ctx.fillStyle = "#0f172a"
                ctx.font = "11px sans-serif"
                ctx.textAlign = "center"
                ctx.textBaseline = "middle"
                ctx.fillText(
                    val,
                    paddingLeft + j * cellW + cellW / 2,
                    paddingTop + i * cellH + cellH / 2
                )
            }
        }

        ctx.fillStyle = "#a0d5ff"
        ctx.font = "11px sans-serif"
        ctx.textAlign = "center"
        ctx.textBaseline = "top"
        for (j = 0; j < cols; j++) {
            ctx.fillText(
                xLabels[j],
                paddingLeft + j * cellW + cellW / 2,
                paddingTop + gridHeight + 6
            )
        }

        ctx.textAlign = "right"
        ctx.textBaseline = "middle"
        for (i = 0; i < rows; i++) {
            ctx.fillText(
                yLabels[i],
                paddingLeft - 6,
                paddingTop + i * cellH + cellH / 2
            )
        }
    }
}
