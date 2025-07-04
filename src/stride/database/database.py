import sqlmodel
import os
from pathlib import Path

# Get the path to the data directory relative to this file
package_root = Path(__file__).parent.parent
data_dir = package_root / "data"
db_path = data_dir / "database.db"

# Create data directory if it doesn't exist
os.makedirs(data_dir, exist_ok=True)

# Use absolute path for SQLite URL to ensure consistency
sqlite_url = f"sqlite:///{db_path.absolute()}"

# handles communication with the database
engine = sqlmodel.create_engine(sqlite_url)


# creates database.db file, and adds tables to it
def create_database() -> None:
    sqlmodel.SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_database()
