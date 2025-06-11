import sqlmodel

sqllite_url = "sqlite:///database.db"

# handles communication with the database
engine = sqlmodel.create_engine(sqllite_url)


# creaetes database.db file, and adds tables to it
def create_database() -> None:
    sqlmodel.SQLModel.metadata.create_all(engine)
