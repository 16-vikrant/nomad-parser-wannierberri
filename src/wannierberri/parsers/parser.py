from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive
    from structlog.stdlib import BoundLogger

import pandas as pd
import re
import numpy as np
from pathlib import Path

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
    Parser for WannierBerri SHC output text file.
    Plots the Spin Hall Conductivity (SHC) results.
    XYZ component is plotted against energy.
    """

    def read_shc_data(self, mainfile: str):
        numeric_lines = []
        component_candidates = []

        with open(mainfile, 'r') as f:
            for line in f:
                line_strip = line.strip()
                alpha_or_numeric = line_strip.split()
                def is_numeric(term):
                    try:
                        np.float64(term)
                        return True
                    except ValueError:
                        return False
                if not line_strip:
                    continue
                if not all(is_numeric(c) for c in alpha_or_numeric):
                    component_candidates.extend(re.findall(r'\b[a-z]{3}\b', line_strip.lower()))
                    continue
                numeric_lines.append(line_strip)

        if not numeric_lines:
            raise ValueError("No numeric data found in SHC file.")

        # Parse numeric data
        data = np.array([list(map(float, line.split())) for line in numeric_lines])

        energy = data[:, 0]
        omega = data[:, 1]
        shc_tensor_real = data[:, 2:56:2]  # real parts: cols 2,4,...,54
        shc_tensor_imag = data[:, 3:56:2]  # imag parts: cols 3,5,...,55

        # Extract and deduplicate labels
        exclude = {'energy', 'omega'}
        labels = []
        seen = set()
        for comp in component_candidates:
            if comp not in exclude and comp not in seen:
                seen.add(comp)
                labels.append(comp)

        df_real = pd.DataFrame(shc_tensor_real, columns=labels)
        df_imag = pd.DataFrame(shc_tensor_imag, columns=labels)

        return labels, energy, df_real, df_imag
    
    def extract_fermi_energy(self, mainfile: Path) -> float:
        regex = re.compile(r'fermi_energy\s*=\s*([\d\.\-]+)', re.IGNORECASE)
        search_dirs = [
            mainfile.parent,
            mainfile.parent.parent,
            *mainfile.parent.parent.glob('*/')
        ]

        for directory in search_dirs:
            wannier90_path = directory / 'wannier90.win'
            if wannier90_path.exists():
                content = wannier90_path.read_text()
                match = regex.search(content)
                if match:
                    return float(match.group(1))

        return 0.0
            
    def parse(
        self,
        mainfile: str,
        archive: 'EntryArchive',
        logger: 'BoundLogger',
    ) -> None:
        logger.info("WannierBerriParser.parse started")

        # Minimal run section to satisfy NOMAD
        sec_run = Run()
        sec_run.program = Program(name='WannierBerri', version='v0.17.0')
        archive.run.append(sec_run)

        # Read SHC data from file
        labels, energy, shc_tensor_real, shc_tensor_imag = self.read_shc_data(mainfile)

        # Create SHCResults instance
        shc = SHCResults()
        archive.data = shc

        # Assign data
        fermi_energy = self.extract_fermi_energy(Path(mainfile))
        energy_fermi_shift = energy - fermi_energy
        shc.energy = energy_fermi_shift
        shc.shc_labels = labels
        shc.shc_tensor_real = shc_tensor_real.values
        shc.shc_tensor_imag = shc_tensor_imag.values
        shc.fermi_energy = fermi_energy

        if 'xyz' in shc.shc_labels:
            idx = shc.shc_labels.index('xyz')
            shc.shc_xyz_real = shc_tensor_real.iloc[:, idx].values
        else:
            shc.shc_xyz_real = np.zeros(len(energy))

        # Now assign this section under archive.data (EntryData)
        # Create a subsection attribute, e.g., archive.data.shc_results
        archive.data.shc_results = shc

        # Add minimal workflow info
        workflow = SinglePoint()
        archive.workflow2 = workflow

        logger.info("WannierBerriParser.parse completed successfully")
