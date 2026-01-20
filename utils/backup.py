# -*- coding: utf-8 -*-
import os
import shutil
from datetime import datetime, timedelta
import json

class BackupManager:
    """数据库备份管理器"""
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置"""
        default_config = {
            "auto_backup": True,
            "backup_dir": "./backups",
            "backup_keep_days": 7,
            "db_path": "tsm_data.db"
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置
                    return {**default_config, **config}
            except:
                return default_config
        else:
            return default_config
    
    def save_config(self, config):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        self.config = config
    
    def create_backup(self, db_path=None, backup_dir=None):
        """创建备份"""
        if db_path is None:
            db_path = self.config.get('db_path', 'tsm_data.db')
        
        if backup_dir is None:
            backup_dir = self.config.get('backup_dir', './backups')
        
        # 检查数据库文件是否存在
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"数据库文件不存在: {db_path}")
        
        # 创建备份目录
        os.makedirs(backup_dir, exist_ok=True)
        
        # 生成备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"tsm_data_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # 复制数据库文件
        shutil.copy2(db_path, backup_path)
        
        # 清理旧备份
        self.cleanup_old_backups(backup_dir)
        
        return backup_path
    
    def list_backups(self, backup_dir=None):
        """列出所有备份文件"""
        if backup_dir is None:
            backup_dir = self.config.get('backup_dir', './backups')
        
        if not os.path.exists(backup_dir):
            return []
        
        backups = []
        for filename in os.listdir(backup_dir):
            if filename.startswith('tsm_data_backup_') and filename.endswith('.db'):
                filepath = os.path.join(backup_dir, filename)
                stat = os.stat(filepath)
                backups.append({
                    'filename': filename,
                    'filepath': filepath,
                    'size': stat.st_size,
                    'mtime': datetime.fromtimestamp(stat.st_mtime)
                })
        
        # 按时间倒序排列
        backups.sort(key=lambda x: x['mtime'], reverse=True)
        return backups
    
    def restore_backup(self, backup_file, db_path=None):
        """从备份恢复"""
        if db_path is None:
            db_path = self.config.get('db_path', 'tsm_data.db')
        
        if not os.path.exists(backup_file):
            raise FileNotFoundError(f"备份文件不存在: {backup_file}")
        
        # 备份当前数据库（以防恢复失败）
        if os.path.exists(db_path):
            temp_backup = db_path + '.before_restore'
            shutil.copy2(db_path, temp_backup)
        
        try:
            # 恢复备份
            shutil.copy2(backup_file, db_path)
            # 删除临时备份
            if os.path.exists(db_path + '.before_restore'):
                os.remove(db_path + '.before_restore')
        except Exception as e:
            # 恢复失败，还原原数据库
            if os.path.exists(db_path + '.before_restore'):
                shutil.copy2(db_path + '.before_restore', db_path)
                os.remove(db_path + '.before_restore')
            raise e
    
    def cleanup_old_backups(self, backup_dir=None):
        """清理过期备份"""
        if backup_dir is None:
            backup_dir = self.config.get('backup_dir', './backups')
        
        keep_days = self.config.get('backup_keep_days', 7)
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        
        backups = self.list_backups(backup_dir)
        for backup in backups:
            if backup['mtime'] < cutoff_date:
                try:
                    os.remove(backup['filepath'])
                except:
                    pass
