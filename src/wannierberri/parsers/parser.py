from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive
    from structlog.stdlib import BoundLogger

import pandas as pd
import numpy as np
import os

from nomad.config import config
from nomad.parsing.parser import MatchingParser
from runschema.run import Run, Program
from simulationworkflowschema import SinglePoint
from wannierberri.schema_packages.schema_package import SHCResults

configuration = config.get_plugin_entry_point(
    'wannierberri.parsers:parser_entry_point'
)

class WannierBerriParser(MatchingParser):
    """
    Parser for WannierBerri SHC output files.
    Populates archive.data with SHCResults for easier visualization.
    """

    def read_shc_component_names(self, mainfile: str) -> list[str]:
        with open(mainfile, 'r') as f:
            for line in f:
                if line.strip().startswith("# "):
                    header_line = line.strip()
                    break
            else:
                return []

        components = header_line.split()
        components = [comp for comp in components if not comp.startswith("#")]
        seen = set()
        components = [x for x in components if not (x in seen or seen.add(x))]
        return components[2:]  # skip 'energy' and 'omega'

    def read_shc_data(self, mainfile: str) -> pd.DataFrame:
        try:
            df = pd.read_csv(
                mainfile,
                sep=r'\s+',
                comment='#',
                skiprows=2,
                usecols=range(56),
                engine='python'
            )
        except Exception as e:
            raise ValueError(f"Failed to read SHC data from {mainfile}: {e}")

        energies = df.iloc[:, 0].values
        omega = df.iloc[:, 1].values
        real_parts = df.iloc[:, 2::2].to_numpy()
        imag_parts = df.iloc[:, 3::2].to_numpy()
        complex_tensor = real_parts + 1j * imag_parts

        components = self.read_shc_component_names(mainfile)

        df_shc = pd.DataFrame(complex_tensor, columns=components)
        df_shc.insert(0, "omega", omega)
        df_shc.insert(0, "energy", energies)

        return df_shc

    def parse(
        self,
        mainfile: str,
        archive: 'EntryArchive',
        logger: 'BoundLogger',
    ) -> None:
        logger.info("WannierBerriParser.parse started")

        # Minimal run section to satisfy NOMAD
        sec_run = Run()
        sec_run.program = Program(name='Wannier Berri', version='v0.17.0')
        archive.run.append(sec_run)

        # Read SHC data
        df_shc = self.read_shc_data(mainfile)

        # Create SHCResults instance and populate archive.data
        shc = SHCResults()
        archive.data = shc

        # shc.omega = df_shc['omega'].values if 'omega' in df_shc else None
        shc.Energies = df_shc['energy'].values if 'energy' in df_shc else None

        known_cols = [col for col in ['energy', 'omega', 'xyz'] if col in df_shc.columns]
        shc_only = df_shc.drop(columns=known_cols, errors='ignore')

        # shc.shc_components = np.round(shc_only.values.real, 6).astype(float)
        shc.SHC_Labels = shc_only.columns.values.tolist()

        if 'xyz' in df_shc:
            shc.SHC_XYZ_Real = df_shc['xyz'].values.real
            # shc.shc_xyz_imag = df_shc['xyz'].values.imag

        workflow = SinglePoint()
        archive.workflow2 = workflow