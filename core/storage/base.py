class StorageStrategy:
    def store(self, backup_file, config):
        raise NotImplementedError("Store method must be implemented by subclasses.")
    def retrieve(self, backup_file, config):
        raise NotImplementedError("Retrieve method must be implemented by subclasses.")
