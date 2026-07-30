"""
卦辞爻辞管理模块
"""
import json
import os

class GuaciManager:
    def __init__(self, data_dir):
        self.guaci_file = os.path.join(data_dir, '64gua.json')
        self.yaoci_file = os.path.join(data_dir, 'yaoci.json')
    
    def load_guaci(self, gua_id):
        pass
    
    def load_yaoci(self, gua_id, yao_pos):
        pass
