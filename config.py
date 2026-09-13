CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

from pathlib import Path



RAW_DATA_DIR = r"D:\Policy_IQ\data\raw"
MANIFEST_PATH = r"D:\Policy_IQ\data\menifest.csv"
PROCESSED_DATA_DIR = r"D:\Policy_IQ\data\processed"

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200




BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"

RAW_DATA_DIR = DATA_DIR / "raw"

PROCESSED_DATA_DIR = DATA_DIR / "processed"

MANIFEST_PATH = DATA_DIR / "menifest.csv"