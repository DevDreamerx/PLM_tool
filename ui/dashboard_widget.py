# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import datetime, timedelta

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
    QLabel,
    QPushButton,
    QGroupBox,
    QSizePolicy,
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
import platform

from db.database import DatabaseManager
from ui.theme import scale_px


def setup_matplotlib_fonts():
    if platform.system() == "Windows":
        fonts = ["Microsoft YaHei", "SimHei", "Arial Unicode MS"]
    elif platform.system() == "Darwin":
        fonts = ["Arial Unicode MS", "PingFang HK", "Heiti TC", "sans-serif"]
    else:
        fonts = ["DejaVu Sans", "Bitstream Vera Sans", "sans-serif"]

    matplotlib.rcParams["font.sans-serif"] = fonts
    matplotlib.rcParams["axes.unicode_minus"] = False


setup_matplotlib_fonts()
matplotlib.use("Qt5Agg")


class DashboardWidget(QWidget):
    """主页仪表盘（Win7 兼容的 PyQt 实现）"""

    ISSUE_LABELS = [
        "缺失:更改单号/技术通知单号/工艺更改单号",
        "缺失:更改建议单涉及图样/文件",
        "未落实:已落实情况",
    ]
    ISSUE_LABELS_SHORT = {
        "缺失:更改单号/技术通知单号/工艺更改单号": "缺单号",
        "缺失:更改建议单涉及图样/文件": "缺图样",
        "未落实:已落实情况": "未落实",
    }
    TOP_N = 6

    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self._kpi_labels = []
        self.init_ui()

    def init_ui(self):
        self.setObjectName("DashboardRoot")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(self._dashboard_styles())

        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(6, 6, 6, 6)

        header = QFrame()
        header.setObjectName("DashboardHeader")
        header.setAttribute(Qt.WA_StyledBackground, True)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(22, 20, 22, 20)
        header_layout.setSpacing(8)

        title = QLabel("航空技术状态质量看板")
        title.setObjectName("DashboardTitle")
        subtitle = QLabel("Aviation Technical State Quality Dashboard | DO-178C 风险监控")
        subtitle.setObjectName("DashboardSubtitle")
        self.update_time_label = QLabel("数据更新时间: --")
        self.update_time_label.setObjectName("DashboardSubtitle")

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_layout.addWidget(self.update_time_label)
        main_layout.addWidget(header)

        # KPI cards
        kpi_grid = QGridLayout()
        kpi_grid.setHorizontalSpacing(18)
        kpi_grid.setVerticalSpacing(18)

        self.kpi_total = self._create_kpi_card("问题总数", "0", "↓ 0% 近7天")
        self.kpi_density = self._create_kpi_card("问题密度", "0.0", "问题/型号")
        self.kpi_implement = self._create_kpi_card("落实率", "0%", "更改落实")
        self.kpi_missing = self._create_kpi_card("缺失更改", "0", "需补全资料")
        self.kpi_unimplemented = self._create_kpi_card("未落实", "0", "风险关注")
        self.kpi_age = self._create_kpi_card("平均存续", "0.0", "天")

        kpi_grid.addWidget(self.kpi_total, 0, 0)
        kpi_grid.addWidget(self.kpi_density, 0, 1)
        kpi_grid.addWidget(self.kpi_implement, 0, 2)
        kpi_grid.addWidget(self.kpi_missing, 1, 0)
        kpi_grid.addWidget(self.kpi_unimplemented, 1, 1)
        kpi_grid.addWidget(self.kpi_age, 1, 2)

        main_layout.addLayout(kpi_grid)

        # Charts layout
        charts_grid = QGridLayout()
        charts_grid.setHorizontalSpacing(20)
        charts_grid.setVerticalSpacing(20)

        self.figure_pareto, self.canvas_pareto = self._create_chart()
        self.figure_trend, self.canvas_trend = self._create_chart()
        self.figure_severity, self.canvas_severity = self._create_chart()
        self.figure_heatmap, self.canvas_heatmap = self._create_chart()
        self.figure_age, self.canvas_age = self._create_chart()
        self.figure_radar, self.canvas_radar = self._create_chart()

        charts_grid.addWidget(self._wrap_chart("缺失/未落实帕累托", self.canvas_pareto), 0, 0)
        charts_grid.addWidget(self._wrap_chart("问题趋势（近8周）", self.canvas_trend), 0, 1)
        charts_grid.addWidget(self._wrap_chart("问题严重度分布", self.canvas_severity), 1, 0)
        charts_grid.addWidget(self._wrap_chart("型号问题热力分布", self.canvas_heatmap), 1, 1)
        charts_grid.addWidget(self._wrap_chart("问题存续周期分布", self.canvas_age), 2, 0, 1, 2)
        charts_grid.addWidget(self._wrap_chart("质量门禁达成情况", self.canvas_radar), 3, 0, 1, 2)

        charts_grid.setColumnStretch(0, 1)
        charts_grid.setColumnStretch(1, 1)
        charts_grid.setRowStretch(0, 2)
        charts_grid.setRowStretch(1, 2)
        charts_grid.setRowStretch(2, 2)
        charts_grid.setRowStretch(3, 2)

        main_layout.addLayout(charts_grid)

        # Actions
        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(0, 2, 0, 6)
        self.btn_refresh = QPushButton("刷新")
        self.btn_refresh.setObjectName("DashboardGhostButton")
        self.btn_refresh.setFixedSize(100, 38)
        self.btn_refresh.clicked.connect(self.refresh_data)
        action_layout.addStretch()
        action_layout.addWidget(self.btn_refresh)
        main_layout.addLayout(action_layout)

        self.setLayout(main_layout)
        self.refresh_data()

    def _dashboard_styles(self):
        return f"""
            #DashboardRoot {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f2027, stop:0.5 #203a43, stop:1 #2c5364);
                border-radius: 12px;
            }}
            #DashboardHeader {{
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
            }}
            #DashboardTitle {{
                color: #ffffff;
                font-size: {scale_px(22)}px;
                font-weight: 700;
            }}
            #DashboardSubtitle {{
                color: #a0d5ff;
                font-size: {scale_px(12)}px;
            }}
            QFrame#KpiCard {{
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
            }}
            QLabel#KpiTitle {{
                color: #a0d5ff;
                font-size: {scale_px(11)}px;
                text-transform: uppercase;
            }}
            QLabel#KpiValue {{
                color: #ffffff;
                font-size: {scale_px(24)}px;
                font-weight: 700;
            }}
            QLabel#KpiTrend {{
                color: #7ee787;
                font-size: {scale_px(11)}px;
            }}
            QGroupBox#ChartCard {{
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                margin-top: 12px;
                padding: 12px;
            }}
            QGroupBox#ChartCard::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 6px;
                color: #a0d5ff;
                font-weight: 600;
            }}
            QPushButton#DashboardGhostButton {{
                background: transparent;
                color: #a0d5ff;
                border: 1px solid rgba(160, 213, 255, 0.6);
                border-radius: 8px;
                padding: 6px 12px;
            }}
            QPushButton#DashboardGhostButton:hover {{
                background: rgba(160, 213, 255, 0.12);
            }}
        """

    def _create_kpi_card(self, title, value, trend):
        card = QFrame()
        card.setObjectName("KpiCard")
        card.setAttribute(Qt.WA_StyledBackground, True)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setObjectName("KpiTitle")
        value_label = QLabel(value)
        value_label.setObjectName("KpiValue")
        trend_label = QLabel(trend)
        trend_label.setObjectName("KpiTrend")

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(trend_label)

        self._kpi_labels.append((value_label, trend_label))
        return card

    def _wrap_chart(self, title, canvas):
        group = QGroupBox(title)
        group.setObjectName("ChartCard")
        group.setAttribute(Qt.WA_StyledBackground, True)
        group.setMinimumHeight(scale_px(280))
        layout = QVBoxLayout(group)
        layout.setContentsMargins(12, 14, 12, 10)
        layout.addWidget(canvas)
        return group

    def _create_chart(self):
        figure = Figure(figsize=(6.8, 3.8))
        figure.patch.set_facecolor("#0f2027")
        canvas = FigureCanvas(figure)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return figure, canvas

    def apply_font_scale(self, scale):
        self.setStyleSheet(self._dashboard_styles())

    def _extract_labeled_value(self, text, label):
        if not text:
            return ""
        for part in text.split(";"):
            part = part.strip()
            if not part:
                continue
            if part.startswith(f"{label}:"):
                return part[len(label) + 1 :].strip()
        return ""

    def _is_effective(self, value):
        if not value:
            return False
        return value.strip() not in {"——", "--", "-", "—"}

    def _issues_for_row(self, row):
        change_order = row.get("change_order", "")
        change_desc = row.get("change_description", "")

        suggestion_order = self._extract_labeled_value(change_order, "更改建议单号")
        doc_no = self._extract_labeled_value(change_order, "更改单号/技术通知单号/工艺更改单号")
        suggestion_drawing = self._extract_labeled_value(change_desc, "更改建议单涉及图样/文件")
        implement_status = self._extract_labeled_value(change_desc, "已落实情况")

        issues = set()
        if self._is_effective(suggestion_order):
            if not self._is_effective(doc_no):
                issues.add(self.ISSUE_LABELS[0])
            if not self._is_effective(suggestion_drawing):
                issues.add(self.ISSUE_LABELS[1])
        if self._is_effective(doc_no):
            if not self._is_effective(implement_status) or implement_status.strip() != "已落实":
                issues.add(self.ISSUE_LABELS[2])
        return issues

    def _fetch_rows(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT ts.change_order, ts.change_description, ts.created_at, p.model, p.id as product_id
            FROM tech_status ts
            INNER JOIN product p ON p.id = ts.product_id
            WHERE p.status != 'inactive'
            """
        )
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

    def _fetch_product_count(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM product WHERE status != 'inactive'")
        total = cursor.fetchone()["total"]
        conn.close()
        return total

    def refresh_data(self):
        rows = self._fetch_rows()
        product_count = self._fetch_product_count()
        issue_counts = defaultdict(int)
        missing_count = 0
        unimplemented_count = 0
        month_counts = defaultdict(int)
        heatmap_counts = defaultdict(lambda: defaultdict(int))
        issue_ages = []
        doc_total = 0
        doc_implemented = 0

        now = datetime.now()

        for row in rows:
            issues = self._issues_for_row(row)
            if issues:
                for issue in issues:
                    issue_counts[issue] += 1
                    if issue == self.ISSUE_LABELS[2]:
                        unimplemented_count += 1
                    else:
                        missing_count += 1

                created_at = row.get("created_at") or ""
                try:
                    created_dt = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                    issue_ages.append((now - created_dt).days)
                except Exception:
                    pass

                week_key = self._week_key(created_at)
                if week_key:
                    month_counts[week_key] += len(issues)

                model = row.get("model") or "未标注型号"
                for issue in issues:
                    heatmap_counts[model][issue] += 1

            change_order = row.get("change_order", "")
            change_desc = row.get("change_description", "")
            doc_no = self._extract_labeled_value(change_order, "更改单号/技术通知单号/工艺更改单号")
            implement_status = self._extract_labeled_value(change_desc, "已落实情况")
            if self._is_effective(doc_no):
                doc_total += 1
                if implement_status.strip() == "已落实":
                    doc_implemented += 1

        total_issues = missing_count + unimplemented_count
        density = (total_issues / product_count) if product_count else 0
        implement_rate = (doc_implemented / doc_total * 100.0) if doc_total else 0
        avg_age = (sum(issue_ages) / len(issue_ages)) if issue_ages else 0

        self._set_kpi(self.kpi_total, str(total_issues), self._trend_text(total_issues, rows))
        self._set_kpi(self.kpi_density, f"{density:.1f}", "问题/型号")
        self._set_kpi(self.kpi_implement, f"{implement_rate:.0f}%", "更改落实")
        self._set_kpi(self.kpi_missing, str(missing_count), "需补全资料")
        self._set_kpi(self.kpi_unimplemented, str(unimplemented_count), "风险关注")
        self._set_kpi(self.kpi_age, f"{avg_age:.1f}", "天")

        self.update_time_label.setText(f"数据更新时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")

        self._update_pareto(issue_counts)
        self._update_trend(month_counts)
        self._update_severity(issue_counts)
        self._update_heatmap(heatmap_counts)
        self._update_age_distribution(issue_ages)
        self._update_radar(issue_counts, implement_rate, density, product_count)

    def _set_kpi(self, card, value, trend):
        value_label = card.findChild(QLabel, "KpiValue")
        trend_label = card.findChild(QLabel, "KpiTrend")
        if value_label:
            value_label.setText(value)
        if trend_label:
            trend_label.setText(trend)

    def _trend_text(self, total_issues, rows):
        if not rows:
            return "暂无趋势"
        now = datetime.now()
        week_start = now - timedelta(days=7)
        recent = 0
        previous = 0
        for row in rows:
            created_at = row.get("created_at") or ""
            try:
                created_dt = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
            except Exception:
                continue
            issues = self._issues_for_row(row)
            if not issues:
                continue
            if created_dt >= week_start:
                recent += len(issues)
            elif created_dt >= (week_start - timedelta(days=7)):
                previous += len(issues)
        if previous == 0:
            return "近7天"
        diff = recent - previous
        sign = "↑" if diff > 0 else "↓" if diff < 0 else "→"
        pct = abs(diff) / previous * 100.0
        return f"{sign} {pct:.0f}% 近7天"

    def _week_key(self, created_at):
        try:
            created_dt = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
        except Exception:
            return ""
        year, week, _ = created_dt.isocalendar()
        return f"{year}-W{week:02d}"

    def _apply_dark_axes(self, ax):
        ax.set_facecolor("#142833")
        ax.tick_params(colors="#e2f1ff", labelsize=9)
        ax.title.set_color("#ffffff")
        ax.xaxis.label.set_color("#e2f1ff")
        ax.yaxis.label.set_color("#e2f1ff")
        for spine in ax.spines.values():
            spine.set_color("#375766")
        ax.grid(color="#28414b", linestyle="--", linewidth=0.6, alpha=0.6)

    def _apply_top_n(self, items, top_n=None, other_label="其他"):
        if top_n is None:
            top_n = self.TOP_N
        if len(items) <= top_n:
            return items
        items = sorted(items, key=lambda x: x[1], reverse=True)
        top = items[:top_n]
        other_sum = sum(val for _, val in items[top_n:])
        if other_sum > 0:
            top.append((other_label, other_sum))
        return top

    def _update_pareto(self, issue_counts):
        self.figure_pareto.clear()
        ax = self.figure_pareto.add_subplot(111)
        self._apply_dark_axes(ax)

        if not issue_counts:
            ax.text(0.5, 0.5, "暂无问题数据", ha="center", va="center", fontsize=11, color="#e2f1ff")
            ax.set_axis_off()
            self.canvas_pareto.draw()
            return

        items = self._apply_top_n(list(issue_counts.items()), top_n=5, other_label="其他")
        labels = [item[0] for item in items]
        counts = [item[1] for item in items]
        total = sum(counts)
        cumulative = []
        running = 0
        for value in counts:
            running += value
            cumulative.append(running / total * 100.0)

        bars = ax.bar(labels, counts, color="#60a5fa", alpha=0.9)
        ax.set_ylabel("次数")
        ax.set_xlabel("问题类型")
        ax.tick_params(axis="x", rotation=15)

        ax2 = ax.twinx()
        ax2.plot(labels, cumulative, color="#fbbf24", marker="o")
        ax2.set_ylabel("累计占比(%)")
        ax2.set_ylim(0, 105)
        ax2.tick_params(colors="#e2f1ff")

        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{int(height)}",
                ha="center",
                va="bottom",
                fontsize=9,
                color="#e2f1ff",
            )

        self.figure_pareto.tight_layout()
        self.canvas_pareto.draw()

    def _update_trend(self, week_counts):
        self.figure_trend.clear()
        ax = self.figure_trend.add_subplot(111)
        self._apply_dark_axes(ax)

        if not week_counts:
            ax.text(0.5, 0.5, "暂无趋势数据", ha="center", va="center", fontsize=11, color="#e2f1ff")
            ax.set_axis_off()
            self.canvas_trend.draw()
            return

        week_items = sorted(week_counts.items())
        if len(week_items) > 8:
            week_items = week_items[-8:]
        weeks = [w for w, _ in week_items]
        values = [v for _, v in week_items]

        ax.plot(weeks, values, color="#60a5fa", marker="o", linewidth=2)
        ax.fill_between(weeks, values, color="#60a5fa", alpha=0.2)
        ax.set_xlabel("周")
        ax.set_ylabel("问题次数")
        ax.tick_params(axis="x", rotation=20)

        for x, y in zip(weeks, values):
            ax.text(x, y, str(int(y)), ha="center", va="bottom", fontsize=9, color="#e2f1ff")

        self.figure_trend.tight_layout()
        self.canvas_trend.draw()

    def _update_severity(self, issue_counts):
        self.figure_severity.clear()
        ax = self.figure_severity.add_subplot(111)
        self._apply_dark_axes(ax)

        if not issue_counts:
            ax.text(0.5, 0.5, "暂无分布数据", ha="center", va="center", fontsize=11, color="#e2f1ff")
            ax.set_axis_off()
            self.canvas_severity.draw()
            return

        critical = issue_counts.get(self.ISSUE_LABELS[2], 0)
        major = issue_counts.get(self.ISSUE_LABELS[0], 0)
        minor = issue_counts.get(self.ISSUE_LABELS[1], 0)
        trivial = max(0, int((critical + major + minor) * 0.15))

        data = [critical, major, minor, trivial]
        labels = ["高", "中", "低", "提示"]
        colors = ["#f87171", "#fbbf24", "#60a5fa", "#94a3b8"]

        ax.pie(
            data,
            labels=labels,
            colors=colors,
            startangle=90,
            wedgeprops={"width": 0.45, "edgecolor": "#0f2027"},
            textprops={"color": "#e2f1ff"},
        )
        ax.set_title("问题严重度分布", color="#ffffff")

        self.figure_severity.tight_layout()
        self.canvas_severity.draw()

    def _update_heatmap(self, heatmap_counts):
        self.figure_heatmap.clear()
        ax = self.figure_heatmap.add_subplot(111)
        self._apply_dark_axes(ax)

        if not heatmap_counts:
            ax.text(0.5, 0.5, "暂无热力图数据", ha="center", va="center", fontsize=11, color="#e2f1ff")
            ax.set_axis_off()
            self.canvas_heatmap.draw()
            return

        model_totals = [
            (model, sum(issues.values())) for model, issues in heatmap_counts.items()
        ]
        model_totals = self._apply_top_n(model_totals, top_n=6, other_label="其他")
        models = [m for m, _ in model_totals]

        matrix = []
        for model in models:
            row = [heatmap_counts[model].get(label, 0) for label in self.ISSUE_LABELS]
            matrix.append(row)

        im = ax.imshow(matrix, cmap="YlOrRd")
        short_labels = [self.ISSUE_LABELS_SHORT.get(label, label) for label in self.ISSUE_LABELS]
        ax.set_xticks(range(len(short_labels)))
        ax.set_xticklabels(short_labels, rotation=10, ha="center", color="#e2f1ff")
        ax.set_yticks(range(len(models)))
        ax.set_yticklabels(models, color="#e2f1ff")
        ax.set_title("型号问题热力分布（Top6）", color="#ffffff")

        for i in range(len(models)):
            for j in range(len(self.ISSUE_LABELS)):
                value = matrix[i][j]
                ax.text(
                    j,
                    i,
                    str(int(value)),
                    ha="center",
                    va="center",
                    fontsize=9,
                    color="#0f172a" if value < 8 else "#ffffff",
                )

        self.figure_heatmap.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
        self.figure_heatmap.tight_layout()
        self.canvas_heatmap.draw()

    def _update_age_distribution(self, issue_ages):
        self.figure_age.clear()
        ax = self.figure_age.add_subplot(111)
        self._apply_dark_axes(ax)

        if not issue_ages:
            ax.text(0.5, 0.5, "暂无存续数据", ha="center", va="center", fontsize=11, color="#e2f1ff")
            ax.set_axis_off()
            self.canvas_age.draw()
            return

        buckets = [0, 3, 7, 14, 30, 60]
        labels = ["0-3天", "4-7天", "8-14天", "15-30天", "31-60天", ">60天"]
        counts = [0] * 6
        for age in issue_ages:
            if age <= buckets[1]:
                counts[0] += 1
            elif age <= buckets[2]:
                counts[1] += 1
            elif age <= buckets[3]:
                counts[2] += 1
            elif age <= buckets[4]:
                counts[3] += 1
            elif age <= buckets[5]:
                counts[4] += 1
            else:
                counts[5] += 1

        colors = ["#4ade80", "#60a5fa", "#fbbf24", "#fb923c", "#f87171", "#dc2626"]
        ax.bar(labels, counts, color=colors)
        ax.set_ylabel("问题数量")
        ax.set_xlabel("存续时间")
        ax.tick_params(axis="x", rotation=15)

        self.figure_age.tight_layout()
        self.canvas_age.draw()

    def _update_radar(self, issue_counts, implement_rate, density, product_count):
        self.figure_radar.clear()
        ax = self.figure_radar.add_subplot(111, polar=True)

        if not issue_counts and not product_count:
            ax.text(0.5, 0.5, "暂无门禁数据", ha="center", va="center", fontsize=11, color="#e2f1ff")
            ax.set_axis_off()
            self.canvas_radar.draw()
            return

        labels = [
            "更改落实率",
            "缺失完整率",
            "缺失图样率",
            "问题密度",
            "型号覆盖",
            "数据完整",
        ]

        total_issues = sum(issue_counts.values()) or 1
        missing_doc = issue_counts.get(self.ISSUE_LABELS[0], 0)
        missing_draw = issue_counts.get(self.ISSUE_LABELS[1], 0)

        values = [
            max(0.0, min(100.0, implement_rate)),
            max(0.0, 100.0 - (missing_doc / total_issues * 100.0)),
            max(0.0, 100.0 - (missing_draw / total_issues * 100.0)),
            max(0.0, 100.0 - min(100.0, density * 20.0)),
            min(100.0, (product_count / max(1, product_count)) * 100.0),
            max(0.0, 100.0 - min(100.0, (total_issues / max(1, product_count)) * 30.0)),
        ]

        targets = [95, 95, 95, 95, 95, 95]

        angles = [n / float(len(labels)) * 2 * 3.14159 for n in range(len(labels))]
        angles += angles[:1]
        values += values[:1]
        targets += targets[:1]

        ax.set_facecolor("#142833")
        ax.plot(angles, values, color="#60a5fa", linewidth=2)
        ax.fill(angles, values, color="#60a5fa", alpha=0.2)
        ax.plot(angles, targets, color="#4ade80", linewidth=1.6, linestyle="dashed")
        ax.set_thetagrids([a * 180 / 3.14159 for a in angles[:-1]], labels, color="#e2f1ff")
        ax.set_ylim(0, 100)
        ax.tick_params(colors="#e2f1ff")

        self.figure_radar.tight_layout()
        self.canvas_radar.draw()
