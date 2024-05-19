from pathlib import Path
import tempfile


class PathManager:
    backend = Path(__file__).parents[2]
    source = backend / "src"
    resources = backend / "resources"
    output = backend / "output"
    config = source / "config"
    prompts = source / "rag" / "prompts"
    databases = source / "databases"
    documents = databases / "documents"
    postgres = databases / "postgres"

    def create_temp_folder() -> tempfile.TemporaryDirectory:
        return tempfile.TemporaryDirectory()


PATH = PathManager
