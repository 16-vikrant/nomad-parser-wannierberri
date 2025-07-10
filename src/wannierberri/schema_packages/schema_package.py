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
from nomad.datamodel.data import EntryData
from nomad.metainfo import (
    Quantity,
    SchemaPackage,
    Section,
    MSection,
)
from nomad.datamodel.metainfo.plot import (
    PlotSection,
)

import numpy as np

configuration = config.get_plugin_entry_point(
    'wannierberri.schema_packages:schema_package_entry_point'
)

m_package = SchemaPackage()
m_package.name = 'WannierBerri'
m_package.description = 'Schema package for WannierBerri Spin Hall Conductivity (SHC) results.'

class SHCResults(PlotSection, EntryData):
    m_def = Section(
        label='Spin Hall Conductivity',
        a_display={
            'visible': True,
        },
        a_plotly_express=[
            {
                'method': 'line',
                'x': '#Energies',
                'y': '#SHC_XYZ_Real',
                'label': 'SHC vs Energy',
                'index': 0,
                'layout': {
                    'title': {'text': 'Spin Hall Conductivity'},
                    'xaxis': {'title': {'text': 'Energy (eV)'}},
                    'yaxis': {'title': {'text': 'SHC-XYZ (S/m)'}},
                },
            }
        ],
    )
    # efermi = Quantity(
    #     type=np.float64,
    #     unit='eV',
    #     description='Fermi energy corresponding to SHC data.',
    #     a_display={'visible': False},
    # )

    # omega = Quantity(
    #     type=np.float64,
    #     shape=['n_points'],
    #     unit='eV',
    #     description='Frequency at which SHC is computed.',
    #     a_display={'visible': False},
    # )

    # shc_components = Quantity(
    #     type=np.complex128,
    #     shape=['n_points', 'n_components'],
    #     description='Complex SHC values for different components like xyz, xxy, etc.',
    #     a_display={'visible': False},
    # )

    SHC_XYZ_Real = Quantity(
    type=np.float64,
    shape=['n_points'],
    description='Real part of SHC xyz component',
    unit='S/m',
    a_display={'visible': False},
    )

    # shc_xyz_imag = Quantity(
    # type=np.float64,
    # shape=['n_points'],
    # description='Imaginary part of SHC xyz component',
    # unit='S/m',
    # a_display={'visible': False},
    # )

    SHC_Labels = Quantity(
        type=str,
        shape=['n_components'],
        description='Labels for the SHC tensor components (e.g., xyz, xxy, ...).',
        a_display={'visible': False},
    )

    Energies = Quantity(
        type=np.float64,
        shape=['n_points'],
        unit='eV',
        description='Energy points at which SHC is computed.',
        a_display={'visible': False},
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)

        logger.info("SHCResults.normalize", message="SHC parsing successful.")


m_package.__init_metainfo__()
