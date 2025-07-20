from abc import ABC, abstractmethod


class GameBase(ABC):
    @abstractmethod
    def get_window_title(self) -> str:
        pass
