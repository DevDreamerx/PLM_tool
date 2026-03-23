# -*- coding: utf-8 -*-
import random
from datetime import datetime, timedelta
from db.database import DatabaseManager

def seed():
    db = DatabaseManager()
    print("正在初始化种子数据 (50条)...")
    
    models = ["型号A", "型号B", "型号C", "其他"]
    statuses = ["active", "active", "active", "draft"] # 3/4 正式, 1/4 草稿
    
    for i in range(1, 51):
        # 1. 生成产品编码
        p_code = f"PROD-{2024}-{i:03d}"
        p_name = f"关键控制组件-{i:02d}"
        model = random.choice(models)
        status = random.choice(statuses)
        
        product_data = {
            "product_code": p_code,
            "product_name": p_name,
            "batch_number": f"BATCH-{random.randint(202300, 202499)}",
            "model": model,
            "status": status
        }
        
        try:
            # 插入产品
            product_id = db.insert_product(product_data)
            
            # 2. 生成技术状态
            tech_data = {
                "drawing_number": f"DWG-{model[-1]}-{1000+i}",
                "drawing_version": f"V{random.randint(1, 5)}.{random.randint(0, 9)}",
                "software_version": f"SW-{random.randint(10, 30)}",
                "firmware_version": f"FW-{random.randint(1, 10)}",
                "hardware_config": f"配置方案 {random.choice(['Alpha', 'Beta', 'Standard'])}",
                "change_order": f"ECN-{2024}-{random.randint(100, 999)}",
                "change_description": f"完成了第 {i} 次迭代的功能优化说明。",
                "effective_date": (datetime.now() - timedelta(days=random.randint(0, 100))).strftime("%Y-%m-%d")
            }
            
            # 插入技术状态
            tech_status_id = db.insert_tech_status(product_id, tech_data)
            
            # 3. 插入变更日志
            db.insert_change_log(tech_status_id, "create", f"系统自动导入种子数据 - {p_code}")
            
            if i % 10 == 0:
                print(f"已完成 {i} 条...")
                
        except Exception as e:
            print(f"插入数据 {p_code} 时出错: {e}")

    print("\n✅ 数据生成完成！现在可以打开程序测试了。")

if __name__ == "__main__":
    seed()
