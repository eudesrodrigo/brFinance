import pandas as pd
from datetime import date
from dataclasses import dataclass
from dateutil.relativedelta import relativedelta


@dataclass
class Dates:
    def __init__(self, _date: date):
        self.date = _date
    
    @property
    def previous_quarter_end_date(self) -> date:
        return (self.date - relativedelta(months=3) - pd.tseries.offsets.DateOffset(day=1) + pd.tseries.offsets.QuarterEnd()).date()