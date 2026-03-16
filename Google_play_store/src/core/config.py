import os

class Config:
    DATABASE_URL = "sqlite:///data/google_play.db"
    
    CSV_DATA_PATH = "data/google_play_data.csv"
    
    MIN_ROWS = 1000