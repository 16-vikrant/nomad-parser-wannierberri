from typing import (
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

from nomad.config import config
from nomad.datamodel.metainfo.workflow import Workflow
from nomad.parsing.parser import MatchingParser

configuration = config.get_plugin_entry_point(
    'wannierberri.parsers:parser_entry_point'
)


class WannierBerriParser(MatchingParser):
    def parse(
        self,
        mainfile: str,
        archive: 'EntryArchive',
        logger: 'BoundLogger',
        # child_archives: dict[str, 'EntryArchive'] = None,
    ) -> None:
        
        # Read the mainfile and extract the data
        df = pd.read_csv(mainfile, sep=r"\s+", comment="#", header=None)
        logger.info('WannierBerriParser.parse', parameter=configuration.parameter)

        archive.workflow2 = Workflow(name='test')
