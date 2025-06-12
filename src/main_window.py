    def train_model(self):
        """训练模型"""
        try:
            if self.viewmodel.is_training_model():
                return
                
            self.control_panel.train_button.setEnabled(False)
            
            # 使用默认的数据YAML和迭代次数
            data_yaml = "data/data.yaml"
            epochs = 50
            self.viewmodel.train_model(data_yaml=data_yaml, epochs=epochs)
        except Exception as e:
            self.logger.error(f"训练模型失败: {str(e)}")
            self.status_bar.update_status(f"训练模型失败: {str(e)}")
            self.control_panel.train_button.setEnabled(True) 