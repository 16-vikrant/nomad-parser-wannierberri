from typing import (
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
        EntryData,
        ArchiveSection,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

from nomad.config import config
from nomad.datamodel.data import Schema
from nomad.datamodel.metainfo.annotations import ELNAnnotation, ELNComponentEnum
from nomad.metainfo import (
    Quantity,
    SchemaPackage,
    Section,
    SubSection,
)
from nomad.datamodel.metainfo.plot import (
    PlotlyFigure,
    PlotSection,
)

import numpy as np

configuration = config.get_plugin_entry_point(
    'wannierberri.schema_packages:schema_package_entry_point'
)

m_package = SchemaPackage()

class NewSchemaPackage(Schema):
    name = Quantity(
        type=str, a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity)
    )
    message = Quantity(type=str)
class SHCResults(PlotSection, Schema):
    m_def = Section(
        a_plotly_express={
            'method': 'line',
            'x': '#energies',
            'y': '#xyz_real',
            'label': 'SHC vs Energy',
            'index': 0,
            'layout': {
                'title': {'text': 'Spin Hall Conductivity'},
                'xaxis': {'title': {'text': 'Energy (eV)'}},
                'yaxis': {'title': {'text': 'SHC-xyz (S/m)'}},
            },
        },
    )
    efermi = Quantity(
        type=np.float64,
        unit='eV',
        description='Fermi energy corresponding to SHC data.'
    )

    omega = Quantity(
        type=np.float64,
        shape=['n_points'],
        unit='eV',
        description='Frequency at which SHC is computed.'
    )

    shc_components = Quantity(
        type=np.complex128,
        shape=['n_points', 'n_components'],
        description='Complex SHC values for different components like xyz, xxy, etc.'
    )

    xyz_real = Quantity(
    type=np.float64,
    shape=['n_energy'],
    description='Real part of SHC xyz component',
    unit='S/m',
    )

    xyz_imag = Quantity(
    type=np.float64,
    shape=['n_energy'],
    description='Imaginary part of SHC xyz component',
    unit='S/m',
    )

    shc_labels = Quantity(
        type=str,
        shape=['n_components'],
        description='Labels for the SHC tensor components (e.g., xyz, xxy, ...).'
    )

    energies = Quantity(
        type=np.float64,
        shape=['n_points'],
        unit='eV',
        description='Energy points at which SHC is computed.'
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)

        logger.info("SHCResults.normalize", message="SHC parsing successful.")


m_package.__init_metainfo__()
