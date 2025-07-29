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
                'x': '#energy',
                'y': '#shc_xyz_real',
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

    shc_label = Quantity(
        type=str,
        shape=[27],  # 30 tensor components (xxx ... zzz)
        default=[
            'xxx', 'xxy', 'xxz',
            'xyx', 'xyy', 'xyz',
            'xzx', 'xzy', 'xzz',
            'yxx', 'yxy', 'yxz',
            'yyx', 'yyy', 'yyz',
            'yzx', 'yzy', 'yzz',
            'zxx', 'zxy', 'zxz',
            'zyx', 'zyy', 'zyz',
            'zzx', 'zzy', 'zzz'
        ],
        description='Labels of SHC tensor components.'
    )

    energy = Quantity(
        type=np.float64,
        shape=['n_points'],
        unit='eV',
        description='Energy (Efermi) values.'
    )

    fermi_energy = Quantity(
        type=np.float64,
        shape=[],
        unit='eV',
        description='Fermi energy from Wannier90.win.',
        default=0.0,
    )

    shc_xyz_real = Quantity(
        type=np.float64,
        shape=['n_points'],
        unit='S/cm',
        description='Real part of the xyz component of the SHC tensor.'
    )

    shc_tensor_real = Quantity(
        type=np.float64,
        shape=['n_points', 27],
        description='Real parts of all SHC tensor components.'
    )

    shc_tensor_imag = Quantity(
        type=np.float64,
        shape=['n_points', 27],
        description='Imaginary parts of all SHC tensor components.'
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)

        logger.info("SHCResults.normalize", message="SHC parsing successful.")


m_package.__init_metainfo__()
