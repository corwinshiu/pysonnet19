import os, sys
import subprocess 
import numpy as np
import gdspy as gp
import pysonnet19 as ps

#from simulate_resonator_kitest_novia import simulate_resonator_kitest_novia as kitest
import simulate_resonator_kitest_novia as kitest
class SonnetConfigData:
    """
    Class to hold static data fields for Sonnet .smc file creation.
    """

    def __init__(self, filename, res_index, val):
        self.filename = filename
        self.res_index= res_index
        Lk = val
                
        # Project settings
        self.length_unit = "UM"
        self.roughness_unit = "micron"
        self.sheetres_unit = "OHSQ"
        self.resistance_unit = "OH"
        self.inductance_unit = "NH"
        self.capacitance_unit = "PF"
        self.frequency_unit = "GHZ"
        self.conductivity_unit = "SM"
        self.resistivity_unit = "OHCM"

        # Box size and cell settings
        self.box_size_x = 100
        self.box_size_y = 1400
        self.num_cells_x = 200
        self.num_cells_y = 1400

        # Dielectric material properties 
        # Must be a list where each layer is a dict( name, epsilon and loss tangent)
        self.dielectrics = [
        {
            "name": "SiSubstrate",
            "eps": 11.7,
            "tan": 0
        },
        {
            "name": "aSi",
            "eps": 9.1,
            "tan": 0.0001
        },
        ]

        # Dielectric layer settings
        """self.layers[0] = first dielectric layer where:
            - 0 is the level number
            - 100 is the layer thickness,
            - third value is the layer name
        """
        self.layers = [(0, 100.0, "air"), (1, 0.15, "aSi"), (2, 375, "SiSubstrate")] #must be lower case "air" not "Air" 

        # Conductor settings
        #self.conductor_name = "NbTiN"
        #self.conductivity = 5.8e7
        self.conductors = [
            {"name": "Nb",
             "Rdc": 0,
             "Rrf": 0,
             "Xdc": 0,
             "Ls": 0.08},
            {"name": "NbTiN",
             "Rdc": 0,
             "Rrf": 0,
             "Xdc": 0,
             "Ls": Lk}
        ]
        self.tech_layers = [
            {"name": "NbTiN",
             "material": "NbTiN", #Must match one of the names in self.conductors
             "level": 1, 
             "model": "Thin Metal",
             "thickness": 0.010},
             {"name": "Al",
             "material": "Al", #Must match one of the names in self.conductors
             "level": 1, 
             "model": "Thin Metal",
             "thickness": 0.200}
        ]
        
        # Polygon settings
        #self.polygon_tech_layer = ""  # Will be set to actual ID in CreateMacroCommandFile
        self.draw_polygons()
        #This code takes the gdspy cell and gets all the polygons 
        all_polys = self.cell.get_polygons(by_spec = True)
        self.polygons = [] #self.polygons must be a list, containing all the polygons we want to create.
        for k in all_polys:
            for poly in all_polys[k]:
                poly_in_sonnet_form = ";".join(f"{x},{y}" for x, y in poly)
                self.polygons.append({"tech_layer": self.gdspy_mapping[k[0]], #tech layer is the name (which is layer + material) 
                                      "points": poly_in_sonnet_form,
                                      "points_in_2d": poly}) #This is for convenience for our port finding algo.
        # Port settings
        #The different thing is we need to set which polygon contains the ports 
        self.ports = [{"index": 1, #Port numbering 1 
                       "loc": (0, 50),
                       "layer": 1,
                       "resistance": 49.9},
                      {"index": 2,
                       "loc": (self.box_size_x, 50),
                       "layer": 1,
                       "resistance":49.9},
                      {"index": 3,
                       "loc": (self.box_size_x/2, 312.3),
                       "layer": 1,
                       "resistance": 1E-6}]
                     
        
        # Sweep settings
        self.freq_sweep_dict = {"type": "linear",
                                "start": 2,
                                "stop": 4,
                                "step": 0.5} 
        
        # Save path
        self.save_path = f"son_files/{self.filename}.sonx"
        self.output_filename = f"{self.filename}.s{len(self.ports)}p"

    def draw_polygons(self):
        "This function is where you create the entire circuit, and you must place it in self.cell"
        self.cell = kitest.draw_resonator(self.res_index)
        
        #This is user defined to go from GDSPY mapping to a tech-layer
        #This MUST match the tech layers
        self.gdspy_mapping = {0: "Al",
                              1: "NbTiN"}
  




##############################################################
# Scripts to create the macro file based on the config class, and then run it
#
def main(KI):
    #Configured to sweep the kinetic inductance
    # Create configuration data
    res_index = 0 #Simulate the first resonator 
    filename = "ki_res{}_val{}pHsq".format(res_index, KI)
    config = SonnetConfigData(filename = filename, res_index = res_index, val = KI)

    # Make sure Macro Command folder and Project+Output folder exists respectively 
    macro_command_files_folder = "macro_files/"
    sonnet_project_folder = "son_files/"
    if not os.path.isdir(macro_command_files_folder):
        os.mkdir(macro_command_files_folder)
    if not os.path.isdir(sonnet_project_folder):
        os.mkdir(sonnet_project_folder)

    # Create and generate the macro command file
    macro_file = ps.CreateMacroCommandFile(f"macro_files/{filename}.smc", config)
    macro_file.generate_complete_file()

    #Run the macro file and create the Sonnet project ".sonx" file
    ps.run_macro_command_file(macro_file.output_path, config.save_path)

if __name__ == '__main__':
    for KI in np.arange(80, 121, 5): 
        main(KI)
        gp.current_library = gp.GdsLibrary() 

        
