from nomad.config.models.plugins import NormalizerEntryPoint
from pydantic import Field


class WannierBerriNormalizerEntryPoint(NormalizerEntryPoint):
    parameter: int = Field(0, description='Custom configuration parameter')

    def load(self):
        from wannierberri.normalizers.normalizer import WannierBerriNormalizer

        return WannierBerriNormalizer(**self.dict())


normalizer_entry_point = WannierBerriNormalizerEntryPoint(
    name='WannierBerriNormalizer',
    description='WannierBerri normalizer entry point configuration.',
)
