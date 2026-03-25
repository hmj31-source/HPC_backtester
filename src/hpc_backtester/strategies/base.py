from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    @abstractmethod
    def prepare_features(self, df: pd.DataFrame)-> pd.DataFrame:
        pass

    @abstractmethod
    def generate_entries(seld, df: pd.DataFrame, params: dict) -> pd.DataFrame:
        pass
    