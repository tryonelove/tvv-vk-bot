from abc import ABC, abstractmethod
from constants import osuConstants


class IRepository(ABC):
    """
    Base interface for database interaction
    """
    def __init__(self, db) -> None:
        self.db = db
        self.c = db.cursor()

    @abstractmethod
    def add(self):
        pass

    @abstractmethod
    def save(self):
        pass


class Repository(IRepository):
    def __init__(self, db) -> None:
        super().__init__(db)
    
    def save(self):
        self.db.commit()


class UsersRepository(Repository):
    def __init__(self, db) -> None:
        super().__init__(db)

    def add(self, user_id, role = 1):
        self._c.execute("INSERT OR IGNORE INTO users(id) VALUES(?)", (user_id,))
        self.save()


class OsuRepository(Repository):
    def __init__(self, db) -> None:
        super().__init__(db)

    def add(self, user_id, server, username = None):
        self._c.execute("INSERT OR IGNORE INTO osu(id) VALUES(?)", (user_id,))
        if server == "bancho":
            self._c.execute("UPDATE osu SET main_server=?, bancho_username=? WHERE id=?",
                           (self._server, self._username, self._user_id))
        elif server == "gatari":
            self._c.execute("UPDATE osu SET main_server=?, gatari_username=? WHERE id=?",
                           (self._server, self._username, self._user_id))
        self.save()


class WeatherRepository(Repository):
    def __init__(self, db) -> None:
        super().__init__(db)

    def add(self, user_id, city):
        self.c.execute("INSERT OR IGNORE INTO weather VALUES (?, ?)",
                       (user_id, city))
        self.c.execute("UPDATE weather SET city=? WHERE id=?",
                       (city, user_id))
        self.db.commit()


class LevelsRepository(Repository):
    def __init__(self, db) -> None:
        super().__init__(db)


                           
        

    