import logging

from nomad.datamodel import EntryArchive

from wannierberri.parsers.parser import WannierBerriParser


def test_parse_file():
    parser = WannierBerriParser()
    archive = EntryArchive()
    parser.parse(
        'tests/data/1/result-SHC_qiao_iter-0000.dat', archive, logging.getLogger()
    )

    assert archive.workflow2.name == 'Spin Hall Conductivity'
