import sqlalchemy

# The purpose of the Engine is to connect to the database by providing a Connection object
engine = sqlalchemy.create_engine("sqlite+pysqlite:///:memory:", echo=True)

if __name__ == "__main__":
    # use execute to run a query
    with engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("SELECT 1"))
        print(result.all())

    # need to commit to save the changes
    # avoids sql injection through query parameterization
    with engine.connect() as conn:
        conn.execute(sqlalchemy.text("CREATE TABLE some_table (x int, y int)"))
        conn.execute(
            sqlalchemy.text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
            [{"x": 1, "y": 1}, {"x": 2, "y": 4}],
        )
        conn.commit()

    # can query from a table once committed
    with engine.connect() as conn:
        result = conn.execute(sqlalchemy.text("SELECT x, y FROM some_table"))
        print(result.all())

    # can also inspect the database and get tables
    with engine.connect() as conn:
        # Print all tables in the database
        inspector = sqlalchemy.inspect(engine)
        table_names = inspector.get_table_names()
        print(f"Tables in database: {table_names}")

    # result is iterable - namedtuple, dictionary, or list
    with engine.connect() as conn:
        result = conn.execute(sqlalchemy.text("SELECT x, y FROM some_table"))
        # for row in result:
        #    print(f"x: {row.x}  y: {row.y}")
        for row in result:
            print(f"x: {row[0]}  y: {row[1]}")
