import os, sys
import subprocess 
import numpy as np
import gdspy as gp
import pysonnet19 as ps

class SonnetConfigData:
    """
    Class to hold static data fields for Sonnet .smc file creation.
    """

    def __init__(self, filename):
        self.filename = filename
        
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
        self.box_size_x = 200
        self.box_size_y = 50
        self.num_cells_x = 200
        self.num_cells_y = 50

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
             "Ls": 30.}
        ]
        self.tech_layers = [
            {"name": "Trace",
             "material": "NbTiN", #Must match one of the names in self.conductors
             "level": 1, 
             "model": "Thin Metal",
             "thickness": 0.010},
             {"name": "GND",
             "material": "Nb", #Must match one of the names in self.conductors
             "level": 0, 
             "model": "Thin Metal",
             "thickness": 0.200}
        ]
        
        # Polygon settings
        #self.polygon_tech_layer = ""  # Will be set to actual ID in CreateMacroCommandFile
        self.draw_polygons()
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
                       "loc": (0, self.box_size_y/2),
                       "layer": 1},
                      {"index": 2,
                       "loc": (self.box_size_x, self.box_size_y/2),
                       "layer": 1}]
        
        # Sweep settings
        self.freq_sweep_set = ""  # Will be set to actual ID in CreateMacroCommandFile
        self.freq_sweep_adaptive = "adaptive"
        self.freq_sweep_start = 0.1
        self.freq_sweep_stop = 2.0

        # Save path
        self.save_path = f"son_files/{self.filename}.sonx"
        self.output_filename = f"{self.filename}.s{len(self.ports)}p"

    def draw_polygons(self):
        "This function is where you create the entire circuit, and you must place it in self.cell"

        self.cell = gp.Cell("top")
        #This is user defined to go from GDSPY mapping to a tech-layer 
        self.gdspy_mapping = {1: "GND",
                              2: "Trace"}
        #Draw an inverted ground plane, with a microstrip line 
        lw = 4.5 
        gnd_plane = gp.Rectangle((0, 0),  (self.box_size_x, self.box_size_y), layer = 1)
        main_tl = gp.Rectangle((0, self.box_size_y/2 - lw/2), (self.box_size_x, self.box_size_y/2 + lw/2), layer = 2)

        self.cell.add(gnd_plane)
        self.cell.add(main_tl)




##############################################################
# Scripts to create the macro file based on the config class, and then run it
#
def main():
    # Create configuration data
    filename = "first_script_example"
    config = SonnetConfigData(filename = filename)

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
    main()

        
