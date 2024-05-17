from pathlib import Path
import tempfile


class PathManager:
    backend = Path(__file__).parents[1]
    resources = backend / "resources"
    config = backend / "config"
    databases = backend / "databases"
    documents = databases / "documents"
    postgres = databases / "postgres"

    def create_temp_folder() -> tempfile.TemporaryDirectory:
        return tempfile.TemporaryDirectory()


PATH = PathManager
