# -*- coding: utf-8 -*-
import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    """数据库管理类"""
    
    def __init__(self, db_path="tsm_data.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 允许通过列名访问
        return conn

    def init_db(self):
        """初始化数据库表结构"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 创建产品表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_code TEXT UNIQUE NOT NULL,
                product_name TEXT NOT NULL,
                batch_number TEXT NOT NULL,
                model TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL
            )
        ''')
        
        # 创建技术状态表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tech_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                drawing_number TEXT NOT NULL,
                drawing_version TEXT NOT NULL,
                software_version TEXT,
                firmware_version TEXT,
                hardware_config TEXT,
                req_baseline TEXT,
                icd_version TEXT,
                bom_version TEXT,
                pcb_version TEXT,
                hw_serial TEXT,
                production_batch TEXT,
                sw_build TEXT,
                fw_build TEXT,
                test_status TEXT,
                qual_status TEXT,
                change_order TEXT,
                change_description TEXT,
                effective_date DATE,
                created_at DATETIME NOT NULL,
                FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE
            )
        ''')
        
        # 创建变更历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS change_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tech_status_id INTEGER NOT NULL,
                change_type TEXT NOT NULL,
                change_content TEXT NOT NULL,
                operator TEXT NOT NULL,
                created_at DATETIME NOT NULL,
                FOREIGN KEY (tech_status_id) REFERENCES tech_status(id) ON DELETE CASCADE
            )
        ''')

        # V2.0 新增: 基线表 (Baselines)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS baselines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                baseline_name TEXT NOT NULL,
                baseline_type TEXT NOT NULL,  /* 如: 功能基线, 生产基线 */
                snapshot_data TEXT NOT NULL,  /* JSON格式存储快照 */
                created_by TEXT,
                created_at DATETIME NOT NULL,
                FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE
            )
        ''')

        # V2.0 新增: 附件表 (Attachments)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_type TEXT NOT NULL,     /* product 或 tech_status */
                owner_id INTEGER NOT NULL,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                description TEXT,
                uploaded_at DATETIME NOT NULL
            )
        ''')

        # V2.0 升级: 检查 product 表是否有 lifecycle_state 字段
        cursor.execute("PRAGMA table_info(product)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'lifecycle_state' not in columns:
            cursor.execute("ALTER TABLE product ADD COLUMN lifecycle_state TEXT DEFAULT 'draft'")
            # 迁移旧数据状态
            cursor.execute("UPDATE product SET lifecycle_state = 'draft' WHERE status = 'draft'")
            cursor.execute("UPDATE product SET lifecycle_state = 'released' WHERE status = 'active'")

        # 扩展: 补齐 tech_status 字段
        cursor.execute("PRAGMA table_info(tech_status)")
        tech_columns = [column[1] for column in cursor.fetchall()]
        extra_columns = [
            ("req_baseline", "TEXT"),
            ("icd_version", "TEXT"),
            ("bom_version", "TEXT"),
            ("pcb_version", "TEXT"),
            ("hw_serial", "TEXT"),
            ("production_batch", "TEXT"),
            ("sw_build", "TEXT"),
            ("fw_build", "TEXT"),
            ("test_status", "TEXT"),
            ("qual_status", "TEXT"),
        ]
        for col_name, col_type in extra_columns:
            if col_name not in tech_columns:
                cursor.execute(f"ALTER TABLE tech_status ADD COLUMN {col_name} {col_type}")
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_code ON product(product_code)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_id ON tech_status(product_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tech_status_id ON change_log(tech_status_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_change_created_at ON change_log(created_at)')
        
        conn.commit()
        conn.close()

    def insert_product(self, data):
        """
        插入产品
        data: dict, 包含 product_code, product_name, batch_number, model, status (optional)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = data.get('status', 'active')
        lifecycle_state = 'draft' if status == 'draft' else 'released'
        
        try:
            cursor.execute('''
                INSERT INTO product (product_code, product_name, batch_number, model, status, lifecycle_state, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['product_code'],
                data['product_name'],
                data['batch_number'],
                data['model'],
                status,
                lifecycle_state,
                now,
                now
            ))
            product_id = cursor.lastrowid
            conn.commit()
            return product_id
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                raise ValueError("产品代号已存在")
            raise e
        finally:
            conn.close()

    def search_products(self, keyword=""):
        """模糊搜索产品（包含最新技术状态）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT p.*
            FROM product p
            LEFT JOIN tech_status ts ON ts.id = (
                SELECT id FROM tech_status
                WHERE product_id = p.id
                ORDER BY created_at DESC
                LIMIT 1
            )
            WHERE p.status = 'active'
        """
        params = []
        
        if keyword:
            query += """
                AND (
                    p.product_code LIKE ? OR p.product_name LIKE ? OR p.batch_number LIKE ? OR p.model LIKE ?
                    OR ts.drawing_number LIKE ? OR ts.drawing_version LIKE ?
                    OR ts.software_version LIKE ? OR ts.firmware_version LIKE ?
                    OR ts.hardware_config LIKE ? OR ts.req_baseline LIKE ? OR ts.icd_version LIKE ?
                    OR ts.bom_version LIKE ? OR ts.pcb_version LIKE ? OR ts.hw_serial LIKE ?
                    OR ts.production_batch LIKE ? OR ts.test_status LIKE ? OR ts.qual_status LIKE ?
                    OR ts.change_order LIKE ? OR ts.change_description LIKE ?
                )
            """
            like_kw = f"%{keyword}%"
            params.extend([like_kw] * 19)
            
        query += " ORDER BY p.created_at DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_product(self, product_id):
        """根据ID获取产品详情"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM product WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def delete_product(self, product_id):
        """删除产品 (软删除)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE product SET status = 'inactive' WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()

    def insert_tech_status(self, product_id, data):
        """插入技术状态"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('''
            INSERT INTO tech_status (
                product_id, drawing_number, drawing_version, 
                software_version, firmware_version, hardware_config,
                req_baseline, icd_version, bom_version, pcb_version,
                hw_serial, production_batch, test_status, qual_status,
                change_order, change_description, effective_date, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            product_id,
            data.get('drawing_number', ''),
            data.get('drawing_version', ''),
            data.get('software_version', ''),
            data.get('firmware_version', ''),
            data.get('hardware_config', ''),
            data.get('req_baseline', ''),
            data.get('icd_version', ''),
            data.get('bom_version', ''),
            data.get('pcb_version', ''),
            data.get('hw_serial', ''),
            data.get('production_batch', ''),
            data.get('test_status', ''),
            data.get('qual_status', ''),
            data.get('change_order', ''),
            data.get('change_description', ''),
            data.get('effective_date', ''),
            now
        ))
        
        tech_status_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return tech_status_id

    def get_tech_status(self, product_id):
        """根据产品ID获取技术状态"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tech_status WHERE product_id = ? ORDER BY created_at DESC LIMIT 1",
            (product_id,),
        )
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def update_tech_status(self, tech_status_id, data):
        """更新技术状态"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tech_status SET
                drawing_number = ?,
                drawing_version = ?,
                software_version = ?,
                firmware_version = ?,
                hardware_config = ?,
                req_baseline = ?,
                icd_version = ?,
                bom_version = ?,
                pcb_version = ?,
                hw_serial = ?,
                production_batch = ?,
                test_status = ?,
                qual_status = ?,
                change_order = ?,
                change_description = ?,
                effective_date = ?
            WHERE id = ?
        ''', (
            data.get('drawing_number', ''),
            data.get('drawing_version', ''),
            data.get('software_version', ''),
            data.get('firmware_version', ''),
            data.get('hardware_config', ''),
            data.get('req_baseline', ''),
            data.get('icd_version', ''),
            data.get('bom_version', ''),
            data.get('pcb_version', ''),
            data.get('hw_serial', ''),
            data.get('production_batch', ''),
            data.get('test_status', ''),
            data.get('qual_status', ''),
            data.get('change_order', ''),
            data.get('change_description', ''),
            data.get('effective_date', ''),
            tech_status_id
        ))
        
        conn.commit()
        conn.close()

    def insert_change_log(self, tech_status_id, change_type, content, operator="系统"):
        """插入变更日志"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('''
            INSERT INTO change_log (tech_status_id, change_type, change_content, operator, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (tech_status_id, change_type, content, operator, now))
        
        conn.commit()
        conn.close()

    def get_change_history(self, product_id):
        """获取产品的完整变更历史"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT cl.* FROM change_log cl
            INNER JOIN tech_status ts ON cl.tech_status_id = ts.id
            WHERE ts.product_id = ?
            ORDER BY cl.created_at DESC
        ''', (product_id,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_statistics(self):
        """获取统计数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 总记录数
        cursor.execute("SELECT COUNT(*) as total FROM product WHERE status != 'inactive'")
        total_count = cursor.fetchone()['total']
        
        # 正式记录数
        cursor.execute("SELECT COUNT(*) as active FROM product WHERE status = 'active'")
        active_count = cursor.fetchone()['active']
        
        # 草稿数
        cursor.execute("SELECT COUNT(*) as draft FROM product WHERE status = 'draft'")
        draft_count = cursor.fetchone()['draft']
        
        conn.close()
        
        return {
            'total_count': total_count,
            'active_count': active_count,
            'draft_count': draft_count
        }

    def get_model_distribution(self):
        """获取型号分布数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT model, COUNT(*) as count 
            FROM product 
            WHERE status != 'inactive'
            GROUP BY model
            ORDER BY count DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        return [(row['model'], row['count']) for row in rows]

    def get_products_with_tech_status(self, keyword="", model_filter=None, status_filter=None, date_from=None, date_to=None):
        """获取产品及其技术状态的合并数据（用于导出）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT 
                p.id, p.product_code, p.product_name, p.batch_number, p.model, p.status, p.created_at,
                ts.drawing_number, ts.drawing_version, ts.software_version, ts.firmware_version,
                ts.hardware_config, ts.req_baseline, ts.icd_version, ts.bom_version, ts.pcb_version,
                ts.hw_serial, ts.production_batch, ts.test_status, ts.qual_status,
                ts.change_order, ts.change_description, ts.effective_date
            FROM product p
            LEFT JOIN tech_status ts ON ts.id = (
                SELECT id FROM tech_status
                WHERE product_id = p.id
                ORDER BY created_at DESC
                LIMIT 1
            )
            WHERE p.status != 'inactive'
        '''
        params = []
        
        if keyword:
            query += " AND (p.product_code LIKE ? OR p.product_name LIKE ?)"
            like_kw = f"%{keyword}%"
            params.extend([like_kw, like_kw])
        
        if model_filter:
            query += " AND p.model = ?"
            params.append(model_filter)
        
        if status_filter:
            query += " AND p.status = ?"
            params.append(status_filter)
        
        if date_from:
            query += " AND DATE(p.created_at) >= ?"
            params.append(date_from)
        
        if date_to:
            query += " AND DATE(p.created_at) <= ?"
            params.append(date_to)
        
        query += " ORDER BY p.created_at DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # --- V2.0 Methods ---

    def create_baseline(self, product_id, name, baseline_type, snapshot_data, creator="System"):
        """创建基线"""
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('''
            INSERT INTO baselines (product_id, baseline_name, baseline_type, snapshot_data, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (product_id, name, baseline_type, snapshot_data, creator, now))
        
        conn.commit()
        conn.close()

    def get_baselines(self, product_id):
        """获取产品的所有基线"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM baselines WHERE product_id = ? ORDER BY created_at DESC", (product_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def add_attachment(self, owner_type, owner_id, file_name, file_path, description=""):
        """添加附件"""
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('''
            INSERT INTO attachments (owner_type, owner_id, file_name, file_path, description, uploaded_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (owner_type, owner_id, file_name, file_path, description, now))
        
        conn.commit()
        conn.close()

    def get_attachments(self, owner_type, owner_id):
        """获取附件列表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM attachments 
            WHERE owner_type = ? AND owner_id = ? 
            ORDER BY uploaded_at DESC
        ''', (owner_type, owner_id))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def delete_attachment(self, attachment_id):
        """删除附件"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM attachments WHERE id = ?", (attachment_id,))
        conn.commit()
        conn.close()

    def update_lifecycle_state(self, product_id, new_state):
        """更新生命周期状态"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE product SET lifecycle_state = ? WHERE id = ?", (new_state, product_id))
        
        # 同时更新旧的 status 字段以保持兼容性
        legacy_status = 'active' if new_state == 'released' else 'draft' if new_state == 'draft' else 'inactive' if new_state == 'obsolete' else 'active'
        cursor.execute("UPDATE product SET status = ? WHERE id = ?", (legacy_status, product_id))
        
        conn.commit()
        conn.close()
