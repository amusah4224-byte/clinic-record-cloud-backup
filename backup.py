import sqlite3
import shutil
from datetime import datetime

database = "clinic_records.db"

backup_name = "clinic_backup_" +datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".db"

shutil.copy2(database,backup_name)

print("Backup completed successfully!")
print("Backup file:", backup_name)
