class BackupStrategy:
    def backup(self, config):
        raise NotImplementedError
    
    def restore(self, config):
        raise NotImplementedError
