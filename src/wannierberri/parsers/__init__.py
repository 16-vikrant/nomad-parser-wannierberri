from nomad.config.models.plugins import ParserEntryPoint
from pydantic import Field


class NewParserEntryPoint(ParserEntryPoint):
    parameter: int = Field(0, description='Custom configuration parameter')

    def load(self):
        from wannierberri.parsers.parser import WannierBerriParser

        return WannierBerriParser(**self.dict())


parser_entry_point = NewParserEntryPoint(
    name='WannierBerriParser',
    description='New parser entry point configuration.',
    mainfile_name_re='*result-SHC_*_*.dat',
    mainfile_content_re='Efermi',
    mainfile_mime_re='text/plain',
)
