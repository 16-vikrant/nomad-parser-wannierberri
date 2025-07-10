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
from nomad.normalizing import Normalizer
from wannierberri.schema_packages.schema_package import SHCResults
import numpy as np

configuration = config.get_plugin_entry_point(
    'wannierberri.normalizers:normalizer_entry_point'
)


class WannierBerriNormalizer(Normalizer):
    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)

        if not hasattr(archive, 'data'):
            logger.warning('No data attribute found in archive; skipping SHC normalization')
            return
        
        if not isinstance(archive.data, SHCResults):
            logger.warning('archive.data is not SHCResults; skipping SHC normalization')
            return

        shc = archive.data
        
        # Example: ensure omega, energies, and shc_components are numpy arrays
        shc.Energies = np.array(shc.Energies, dtype=np.float64)
        # shc.shc_xyz_imag = np.array(shc.shc_xyz_imag, dtype=np.float64)
        shc.SHC_XYZ_Real = np.array(shc.SHC_XYZ_Real, dtype=np.float64)
        shc.SHC_Labels = np.array(shc.SHC_Labels, dtype=str)
