from pathlib import Path
import tempfile

class PathManager:
    backend = Path(__file__).parents[1]
    resources = backend / "resources"
        
    def create_temp_folder() -> tempfile.TemporaryDirectory:
        return tempfile.TemporaryDirectory()
        

PATH = PathManager