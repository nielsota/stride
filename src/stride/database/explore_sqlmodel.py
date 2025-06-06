import sqlmodel


class Team(sqlmodel.SQLModel, table=True):
    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    name: str = sqlmodel.Field(index=True)
    headquarters: str

    # relationship to the Hero table -> gets all the heroes associated with the team
    heroes: list["Hero"] = sqlmodel.Relationship(back_populates="team")


class Hero(sqlmodel.SQLModel, table=True):
    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    name: str = sqlmodel.Field(index=True)
    secret_name: str
    age: int | None = None

    # foreign key to the Team table -> gets the team associated with the hero
    team_id: int | None = sqlmodel.Field(default=None, foreign_key="team.id")
    team: Team | None = sqlmodel.Relationship(back_populates="heroes")


sqllite_url = "sqlite:///database.db"

# handles communication with the database
engine = sqlmodel.create_engine(sqllite_url)


# creaetes database.db file, and adds tables to it
def create_database():
    sqlmodel.SQLModel.metadata.create_all(engine)


# create a session
# use a session to stage changes to the database, and commit them to the database later
# commits everything at once, so it's more efficient than committing each change individually


# create heroes
def create_heroes():
    # create teams
    team_1 = Team(name="Avengers", headquarters="New York")
    team_2 = Team(name="Justice League", headquarters="Metropolis")

    # create heroes -> the team ID does not exist yet, so it's None... PROBLEM
    hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson", team=team_1)
    hero_2 = Hero(name="Spider-Boy", secret_name="Pedro Parqueador", team=team_1)
    hero_3 = Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48, team=team_2)

    with sqlmodel.Session(engine) as session:
        session.add(hero_1)
        session.add(hero_2)
        session.add(hero_3)
        session.commit()

        session.refresh(hero_1)
        session.refresh(hero_2)
        session.refresh(hero_3)

        print("Created hero: ", hero_1)
        print("Created hero: ", hero_2)
        print("Created hero: ", hero_3)


def select_heroes():
    with sqlmodel.Session(engine) as session:
        statement = sqlmodel.select(Hero)
        results = session.exec(statement)
        for hero in results:
            print(hero)


def main():
    create_database()
    create_heroes()
    select_heroes()


if __name__ == "__main__":
    main()
