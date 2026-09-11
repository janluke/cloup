from pathlib import Path

from hatchling.metadata.plugin.interface import MetadataHookInterface

PYPI_README_START = ".. docs-index-start"


class CustomMetadataHook(MetadataHookInterface):
    def update(self, metadata: dict) -> None:
        readme = Path(self.root, "README.rst").read_text(encoding="utf-8")
        try:
            pypi_readme = readme[readme.index(PYPI_README_START) :]
        except ValueError:
            msg = f"README.rst must contain the marker {PYPI_README_START!r}"
            raise ValueError(msg) from None

        metadata["readme"] = {
            "content-type": "text/x-rst",
            "text": pypi_readme,
        }
