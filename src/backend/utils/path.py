from pathlib import Path



class PathManager:
    backend = Path(__file__).parents[1]
    resources = backend / "resources"

    
    def create_temp_folder():
        temp_folder = PathManager.resources / "figures"
        temp_folder.mkdir(exist_ok=True)

PATH = PathManager