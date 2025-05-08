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
from nomad.datamodel.metainfo.workflow import Workflow
from nomad.parsing.parser import MatchingParser
from wannierberri.schema_packages.schema_package import (
    SHCResults,
    NewSchemaPackage,
)
import pandas as pd
import numpy as np

configuration = config.get_plugin_entry_point(
    'wannierberri.parsers:parser_entry_point'
)



class WannierBerriParser(MatchingParser):

    def read_shc_component_names(self, file_path: str):
        """
        Reads the SHC component names from the second line of the file
        (after the comment line).
        Returns a list of component names.
        """
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip().startswith("# "):
                    header_line = line.strip()
                    break

        components = header_line.split()
        components = [comp for comp in components if not comp.startswith("#")]

        # Remove duplicate components
        seen = set()
        components = [x for x in components if not (x in seen or seen.add(x))]
        # Remove the first element which is the header
        return components[2:]

    def read_shc_data(self, file_path: str):
        """
        Reads the SHC data from the file and returns a DataFrame.
        The columns will have complex values with real part set to 0.
        """
        # Read the file, skipping the first two lines
        df = pd.read_csv(
            file_path, 
            sep=r"\s+", 
            comment='#', 
            usecols=range(56), 
            skiprows=2,
        )
        energies = df.iloc[:, 0].values
        omega = df.iloc[:, 1].values

        # Extract the real and imaginary parts (alternating columns)
        real_parts = df.iloc[:, 2::2].to_numpy()  # Columns 2, 4, 6, ...
        imag_parts = df.iloc[:, 3::2].to_numpy()  # Columns 3, 5, 7, ...
        
        # Create complex numbers with real part = 0 and imaginary part from `imag_parts`
        complex_tensor = real_parts + 1j * imag_parts 

        # Get component names
        components = self.read_shc_component_names(file_path)
        
        # Create a DataFrame with the energies, omega, and the complex tensor
        df_shc = pd.DataFrame(complex_tensor, columns=components)
        df_shc.insert(0, "omega", omega)
        df_shc.insert(0, "energy", energies)
        
        return df_shc
    
    def parse(
        self,
        mainfile: str,
        archive: 'EntryArchive',
        logger: 'BoundLogger',
        # child_archives: dict[str, 'EntryArchive'] = None,
    ) -> None:
        logger.info('WannierBerriParser.parse', parameter=configuration.parameter)

        # Parse the SHC data from the file
        df_shc = self.read_shc_data(mainfile)

        # Create an instance of SHCResults schema
        archive.data = SHCResults()

        # Fill the schema quantities with parsed data
        # archive.data.efermi = 0.0  
        archive.data.omega = df_shc['omega'].values    
        archive.data.energies = df_shc['energy'].values
        archive.data.shc_components = df_shc.drop(columns=['energy', 'omega']).values

        # Drop 'energy' and 'omega' columns
        shc_only = df_shc.drop(columns=['energy', 'omega'])
        shc_components_real = np.round(shc_only.values.real, 6)
        archive.data.shc_components = shc_components_real.astype(float)

        archive.data.shc_labels = df_shc.columns[2:].values
        archive.data.xyz_real = df_shc['xyz'].values.real
        archive.data.xyz_imag = df_shc['xyz'].values.imag

        # Add the parsed SHCResults schema to the archive
        archive.workflow2 = Workflow(name='Spin Hall Conductivity')
        archive.workflow2.shc_results = archive.data.xyz_real
        
        logger.info('SHC data parsed and stored in the archive.')
