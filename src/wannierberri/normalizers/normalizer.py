from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive
    from structlog.stdlib import BoundLogger

from nomad.config import config
from nomad.normalizing import Normalizer
import numpy as np

configuration = config.get_plugin_entry_point(
    'wannierberri.normalizers:normalizer_entry_point'
)


class WannierBerriNormalizer(Normalizer):
    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)

        if not hasattr(archive, 'data'):
            logger.warning(
                'No data attribute found in archive; skipping SHC normalization'
            )
            return

        # If your data has shc_results subsection, use that
        shc = getattr(archive.data, 'shc_results', None)
        if shc is None:
            logger.warning(
                'No shc_results found in archive.data; skipping SHC normalization'
            )
            return

        # Convert to numpy arrays for consistency
        shc.energy = np.array(shc.energy, dtype=np.float64)
        shc.shc_xyz_real = np.array(shc.shc_xyz_real, dtype=np.float64)
        shc.shc_labels = np.array(shc.shc_labels, dtype=str)
        shc.shc_tensor_real = np.array(shc.shc_tensor_real, dtype=np.float64)
        shc.shc_tensor_imag = np.array(shc.shc_tensor_imag, dtype=np.float64)

        logger.info(
            "WannierBerriNormalizer.normalize", message="SHC normalization successful."
        )
