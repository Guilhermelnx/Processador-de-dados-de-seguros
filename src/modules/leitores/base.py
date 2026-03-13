import pandas as pd
from abc import ABC, abstractmethod

class LeitorSeguradora(ABC):
    @abstractmethod
    def padronizar_dados(self, df: pd.DataFrame) -> pd.DataFrame:
        pass