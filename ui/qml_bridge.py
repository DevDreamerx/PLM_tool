# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from collections import defaultdict

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, pyqtProperty

from db.database import DatabaseManager
from ui.main_window import MainWindow


class DashboardProvider(QObject):
    dataChanged = pyqtSignal()

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
        self._data = {}
        self.refresh()

    @pyqtProperty("QVariantMap", notify=dataChanged)
    def data(self):
        return self._data

    @pyqtSlot()
    def refresh(self):
        rows = self._fetch_rows()
        product_count = self._fetch_product_count()

        issue_counts = defaultdict(int)
        missing_count = 0
        unimplemented_count = 0
        week_counts = defaultdict(int)
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
                    week_counts[week_key] += len(issues)

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

        self._data = {
            "update_time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "kpi": {
                "total": total_issues,
                "density": round(density, 1),
                "implement_rate": int(round(implement_rate)),
                "missing": missing_count,
                "unimplemented": unimplemented_count,
                "avg_age": round(avg_age, 1),
                "trend_text": self._trend_text(rows),
            },
            "pareto": self._build_pareto(issue_counts),
            "trend": self._build_trend(week_counts),
            "severity": self._build_severity(issue_counts),
            "heatmap": self._build_heatmap(heatmap_counts),
            "age": self._build_age(issue_ages),
            "radar": self._build_radar(issue_counts, implement_rate, density, product_count),
        }
        self.dataChanged.emit()

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

    def _week_key(self, created_at):
        try:
            created_dt = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
        except Exception:
            return ""
        year, week, _ = created_dt.isocalendar()
        return f"{year}-W{week:02d}"

    def _trend_text(self, rows):
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

    def _build_pareto(self, issue_counts):
        items = self._apply_top_n(list(issue_counts.items()), top_n=5, other_label="其他")
        return [{"label": k, "value": v} for k, v in items]

    def _build_trend(self, week_counts):
        week_items = sorted(week_counts.items())
        if len(week_items) > 8:
            week_items = week_items[-8:]
        return [{"label": k, "value": v} for k, v in week_items]

    def _build_severity(self, issue_counts):
        critical = issue_counts.get(self.ISSUE_LABELS[2], 0)
        major = issue_counts.get(self.ISSUE_LABELS[0], 0)
        minor = issue_counts.get(self.ISSUE_LABELS[1], 0)
        trivial = max(0, int((critical + major + minor) * 0.15))
        return [
            {"label": "高", "value": critical},
            {"label": "中", "value": major},
            {"label": "低", "value": minor},
            {"label": "提示", "value": trivial},
        ]

    def _build_heatmap(self, heatmap_counts):
        model_totals = [
            (model, sum(issues.values())) for model, issues in heatmap_counts.items()
        ]
        model_totals = self._apply_top_n(model_totals, top_n=6, other_label="其他")
        models = [m for m, _ in model_totals]

        x_labels = [self.ISSUE_LABELS_SHORT.get(label, label) for label in self.ISSUE_LABELS]
        values = []
        for model in models:
            row = [heatmap_counts[model].get(label, 0) for label in self.ISSUE_LABELS]
            values.append(row)
        return {"x": x_labels, "y": models, "values": values}

    def _build_age(self, issue_ages):
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
        return [{"label": label, "value": value} for label, value in zip(labels, counts)]

    def _build_radar(self, issue_counts, implement_rate, density, product_count):
        labels = ["更改落实率", "缺失完整率", "缺失图样率", "问题密度", "型号覆盖", "数据完整"]
        total_issues = sum(issue_counts.values()) or 1
        missing_doc = issue_counts.get(self.ISSUE_LABELS[0], 0)
        missing_draw = issue_counts.get(self.ISSUE_LABELS[1], 0)
        current = [
            max(0.0, min(100.0, implement_rate)),
            max(0.0, 100.0 - (missing_doc / total_issues * 100.0)),
            max(0.0, 100.0 - (missing_draw / total_issues * 100.0)),
            max(0.0, 100.0 - min(100.0, density * 20.0)),
            min(100.0, (product_count / max(1, product_count)) * 100.0),
            max(0.0, 100.0 - min(100.0, (total_issues / max(1, product_count)) * 30.0)),
        ]
        target = [95, 95, 95, 95, 95, 95]
        return {"labels": labels, "current": current, "target": target}


class UiBridge(QObject):
    def __init__(self, app):
        super().__init__()
        self._app = app
        self._legacy_window = None

    @pyqtSlot()
    def openLegacy(self):
        if self._legacy_window is None:
            self._legacy_window = MainWindow()
        self._legacy_window.show()
        self._legacy_window.raise_()
        self._legacy_window.activateWindow()
