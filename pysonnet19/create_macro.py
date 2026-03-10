import os
class GlobalFields:
    """
    Class to hold global string constants used in Sonnet macros.
    """
    PROJECT_STR = "project"
    DIELECTRIC_STR = "dielectric"
    DIEL_LAYER_STR = "diel_layer"
    CONDUCTOR_STR = "conductor"
    TECH_LAYER_PLANAR_STR = "tech_layer_planar"
    PLANAR_TL_STR = "planarTL"
    POLYGON_STR = "polygon"
    PORT_STR = "port"
    SWEEPSET_STR = "sweepset"
    FREQ_SWEEP_STR = "freq_sweep"

def generate_macro_id(character):
    """Generates a base 26 alpha character from a number greater than 0 Ex: 12 = L, 27 = AA"""
    result = ""
    while character > 0:
        remainder = (character - 1) % 26  # Adjust for 0-based indexing
        result = chr(ord('A') + remainder) + result
        character = (character - 1) // 26
    return result

class CreateMacroCommandFile:
    """
    Class to create a Sonnet macro command (.smc) file with methods for each command type.
    Works with SonnetConfigData to access configuration values.
    """

    def __init__(self, output_path, config=None):
        """
        Initialize the macro command file creator.

        Args:
            output_path: Path where the .smc file will be written
            config: Instance of SonnetConfigData containing configuration values
        """
        self.project_macro_id_string = None
        self.output_path = output_path
        self.config = config
        
        self.sonnet_macro_command_file = None

        # ID counters for generating macro IDs
        self.project_macro_id = 1
        self.dielectric_macro_id = 1
        self.diel_layer_macro_id = 1
        self.conductor_macro_id = 1
        self.tech_layer_macro_id = 1
        self.polygon_macro_id = 1
        self.port_macro_id = 1
        self.sweepset_macro_id = 1
        self.freq_sweep_macro_id = 1

        self.layers_macro_list = { }

    def open_file(self):
        """Opens the .smc file for writing."""
        self.sonnet_macro_command_file = open(self.output_path, 'w')

    def close_file(self):
        """Closes the .smc file."""
        if self.sonnet_macro_command_file:
            self.sonnet_macro_command_file.close()

    def add_project(self):
        """Writes the 'add project' line to the .smc file."""
        self.project_macro_id_string = GlobalFields.PROJECT_STR + generate_macro_id(self.project_macro_id)
        add_project_macro_string = ("add " + GlobalFields.PROJECT_STR +
                                    " id=" + self.project_macro_id_string + "\n\n")
        self.sonnet_macro_command_file.write(add_project_macro_string)
        self.project_macro_id += 1

    def modify_project_units(self):
        """Writes the 'modify project' units line to the .smc file."""
        modify_project_units_string = (
            f"modify {self.project_macro_id_string} "
            f"Length_unit={self.config.length_unit} "
            f"Roughness_unit={self.config.roughness_unit} "
            f"SheetRes_unit={self.config.sheetres_unit} "
            f"Resistance_unit={self.config.resistance_unit} "
            f"Inductance_unit={self.config.inductance_unit} "
            f"Capacitance_unit={self.config.capacitance_unit} "
            f"Frequency_unit={self.config.frequency_unit} "
            f"Conductivity_unit={self.config.conductivity_unit} "
            f"Resistivity_unit={self.config.resistivity_unit}\n\n"
        )
        self.sonnet_macro_command_file.write(modify_project_units_string)

    def modify_project_box(self):
        """Writes the 'modify project' box and cells line to the .smc file."""
        modify_project_box_string = (
            f"modify {self.project_macro_id_string} "
            f"box_size_x={self.config.box_size_x} "
            f"box_size_y={self.config.box_size_y} "
            f"num_cells_x={self.config.num_cells_x} "
            f"num_cells_y={self.config.num_cells_y}\n\n"
        )
        self.sonnet_macro_command_file.write(modify_project_box_string)

    def add_dielectric(self, dielectric_params):
        name = dielectric_params["name"]
        eps_value = dielectric_params["eps"]
        tan_value = dielectric_params["tan"]
        """Writes the 'add dielectric' line to the .smc file."""
        dielectric_macro_id_string = GlobalFields.DIELECTRIC_STR + generate_macro_id(self.dielectric_macro_id)
     
        add_dielectric_string = (
            f"add {GlobalFields.DIELECTRIC_STR} "
            f"id={dielectric_macro_id_string} "
            f"Name={name} "
            f"Eps:Value={eps_value} "
            f"Tan:Value={tan_value}\n\n"
        )
        self.sonnet_macro_command_file.write(add_dielectric_string)
        self.dielectric_macro_id += 1

    def add_diel_layers(self):
        """Writes the first 'add diel_layer' line to the .smc file."""
        for i in range(len(self.config.layers)):
            layer = self.config.layers[i]
            self.layers_macro_list[layer[0]] = GlobalFields.DIEL_LAYER_STR + generate_macro_id(self.diel_layer_macro_id)
            add_diel_layer_string = (
                f"add {GlobalFields.DIEL_LAYER_STR} "
                f"id={self.layers_macro_list[layer[0]]} "
                f"num={layer[0]} "
                f"Thickness={layer[1]}\n\n"
            )
            self.sonnet_macro_command_file.write(add_diel_layer_string)
            self.diel_layer_macro_id += 1

    def modify_diel_layers(self):
        """Writes the 'modify diel_layer' line to the .smc file."""
        for i in range(len(self.config.layers)):
            layer = self.config.layers[i]
            if layer[2] != "":
                diel_layer_id = self.layers_macro_list[layer[0]]
                modify_diel_layer_string = (
                    f"modify {diel_layer_id} "
                    f"MaterialName={layer[2]}\n\n"
                )
                self.sonnet_macro_command_file.write(modify_diel_layer_string)

    def add_conductor(self):
        """Writes the 'add conductor' line to the .smc file."""
        conductor_macro_id_string = GlobalFields.CONDUCTOR_STR + generate_macro_id(self.conductor_macro_id)
        add_conductor_string = (
            f"add {GlobalFields.CONDUCTOR_STR} "
            f"id={conductor_macro_id_string} "
            f"Name={self.config.conductor_name} "
            f"Conductivity={self.config.conductivity}\n\n"
        )
        self.sonnet_macro_command_file.write(add_conductor_string)
        self.conductor_macro_id += 1
    def add_conductor_general_metal(self, metal_params):
        name = metal_params["name"]
        Rdc = metal_params["Rdc"]
        Rrf = metal_params["Rrf"]
        Xdc = metal_params["Xdc"]
        Ls = metal_params["Ls"]
        """ Writes the general conductor line to the .smc file."""
        conductor_macro_id_string = GlobalFields.CONDUCTOR_STR + generate_macro_id(self.conductor_macro_id)
        add_conductor_string = (
            f"add {GlobalFields.CONDUCTOR_STR} "
            f"id={conductor_macro_id_string} LossType=SURFACE_IMPEDANCE "
            f"Name={name} "
            f"Rdc={Rdc} "
            f"Rrf={Rrf} "
            f"Xdc={Xdc} "
            f"Ls={Ls} \n\n")
        self.sonnet_macro_command_file.write(add_conductor_string)
        self.conductor_macro_id += 1

    def add_tech_layer_planar(self, tech_params):
        name = tech_params["name"]
        material = tech_params["material"]
        level = tech_params["level"]
        model = tech_params["model"]
        thickness = tech_params["thickness"] 
        """Writes the 'add tech_layer_planar' line to the .smc file."""
        tech_layer_macro_id_string = GlobalFields.PLANAR_TL_STR + generate_macro_id(self.tech_layer_macro_id)
        diel_layer_id = self.layers_macro_list[level] #Retrieve the correct dielectric layer id 

        # Set the tech layer ID in the config for later reference
        self.config.tech_layer_diel = diel_layer_id
                
        add_tech_layer_string = (
            f"add {GlobalFields.TECH_LAYER_PLANAR_STR} "
            f"id={tech_layer_macro_id_string} "
            f"diel_layer={diel_layer_id} "
            f"Thickness={thickness} "
            f'ModelType="{model}" '
            f"MaterialName={material} "
            f"Name={name}\n\n"
        )
        self.sonnet_macro_command_file.write(add_tech_layer_string)
        self.tech_layer_macro_id += 1

        # Save the generated ID
        self.config.polygon_tech_layer = tech_layer_macro_id_string

        if not hasattr(self.config, "tech_layer_mapping"):
            self.config.tech_layer_mapping = {}
        
        #We want the name or the level to retrieve the right ID 
        self.config.tech_layer_mapping[name] = {'id': tech_layer_macro_id_string,
                                                'level': level}
        
        
    def add_polygon(self, polygon_dict):
        tech_layer = polygon_dict["tech_layer"]
        
        polygon_points = polygon_dict["points"]
        tech_layer_macro_id_string = self.config.tech_layer_mapping[tech_layer]['id']
        
        """Writes the 'add polygon' line to the .smc file."""
        polygon_macro_id_string = GlobalFields.POLYGON_STR + generate_macro_id(self.polygon_macro_id)

        add_polygon_string = (
            f"add {GlobalFields.POLYGON_STR} "
            f"id={polygon_macro_id_string} "
            f"tech_layer={tech_layer_macro_id_string} "
            f"points={polygon_points}\n\n"
        )
        self.sonnet_macro_command_file.write(add_polygon_string)
        self.polygon_macro_id += 1
        #Save the generated ID
        polygon_dict["id"] = polygon_macro_id_string
        #Figure out which layer index it is,
        polygon_dict["layer"] = self.config.tech_layer_mapping[tech_layer]['level']

        # Save the generated ID
        #self.config.port1_poly, self.config.port2_poly = polygon_macro_id_string, polygon_macro_id_string
        #self.add_port(polygon_macro_id_string)


        
    def add_port(self, port_properties): #polygon_macro_id_string):
        """ Create a port """
        default_port_imped = {
            "resistance": 50,
            "reactance": 0,
            "inductance": 0,
            "capacitance": 0}
        port_properties = {**default_port_imped, **port_properties}
        
        #Unpack the port properties
        port_number = port_properties["index"]
        x,y = port_properties["loc"]
        layer = port_properties["layer"]
        resistance = port_properties["resistance"]
        #Note: The macro files don't have these as options that work
        # maybe this will be patched in a future software update
        reactance = port_properties["reactance"]
        inductance= port_properties["inductance"]
        capacitance = port_properties["capacitance"]
        
        #Find the ID of the polygon to place the port, and the edge number 
        pid, edge_number = self.find_polygon_at_point(x,y, layer)
        
        port_macro_id_string =  GlobalFields.PORT_STR + generate_macro_id(self.port_macro_id)
        add_port_string = (
            f"add {GlobalFields.PORT_STR} "
            f"id={port_macro_id_string} "
            f"port_number={port_number} "
            f"poly={pid} "
            f"edge={edge_number} \n\n"
            #f"Resistance={resistance} \n\n" #This doesn't always work??
            #f"Reactance={reactance} \n\n"
            #f"Inductance={inductance} "
            #f"Capacitance={capacitance} \n\n" 
        )
        self.sonnet_macro_command_file.write(add_port_string)
        self.port_macro_id += 1

    def find_polygon_at_point(self, x,y, layer):
        """Return the polygon ID that contains (x,y)"""
        for poly in self.config.polygons:
            
            pid = poly["id"]
            points = poly["points_in_2d"]
            
            polylayer = poly["layer"] #poly["layer"] is the index of the layer, not the name of the layer (the tech layer)
            #Check if we are in the correct layer 
            if layer != polylayer:
                continue
            #This is an algorithm to check if the point (x,y) is on the edge of the polygon defined by points
            check, edge_number = self.is_point_on_edge_of_poly(x,y, points)
            if check: 
                return pid, edge_number
        raise ValueError(f"WARNING: UNABLE to find polygon at point ({x}, {y}) on layer {layer}. No matching polygon edge was found.")
    def is_point_on_edge_of_poly(self, x,y,poly):
        num_vertices, _ = poly.shape
        for i in range(0, num_vertices):
            j = i + 1
            if j >= num_vertices:
                j = 0
            x1,y1 = poly[i]
            x2,y2 = poly[j]
            check = self.point_on_segment(x,y, x1,y1,x2,y2)
            if check:
                return True, i #i is the edge number
        return False, _ 

        
    def point_on_segment(self, x, y, x1, y1, x2, y2, eps=1e-4):
        # Check if (x,y) lies on the line segment [(x1,y1),(x2,y2)]
        dx = x2 - x1
        dy = y2 - y1
        if abs(dx) < eps and abs(dy) < eps:
            # segment is a single point
            return abs(x - x1) < eps and abs(y - y1) < eps
        # parametric position t of projection
        t = ((x - x1) * dx + (y - y1) * dy) / (dx*dx + dy*dy)
        if t < -eps or t > 1+eps:
            return False
        # distance from point to line
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        return ((x - closest_x)**2 + (y - closest_y)**2) < eps**2

    def add_sweepset(self, freq_sweep_dict):
        """Writes the 'add sweepset' line to the .smc file."""
        sweepset_macro_id_string = GlobalFields.SWEEPSET_STR + generate_macro_id(self.sweepset_macro_id)

        add_sweepset_string = (
            f"add {GlobalFields.SWEEPSET_STR} "
            f"id={sweepset_macro_id_string}\n\n"
        )
        self.sonnet_macro_command_file.write(add_sweepset_string)
        self.sweepset_macro_id += 1

        # Save the generated ID
        self.config.freq_sweep_set = sweepset_macro_id_string
        self.add_freq_sweep(sweepset_macro_id_string, freq_sweep_dict)

    def add_freq_sweep(self, sweepset_macro_id_string, freq_sweep_dict):
        """Writes the 'add freq_sweep' line to the .smc file."""
        freq_sweep_macro_id_string = GlobalFields.FREQ_SWEEP_STR + generate_macro_id(self.freq_sweep_macro_id)
        sweep_type = freq_sweep_dict["type"]
        sweep_start = freq_sweep_dict["start"]
        sweep_stop = freq_sweep_dict["stop"]
        sweep_step =freq_sweep_dict["step"]
        if sweep_type == "adaptive":
            add_freq_sweep_string = (
                f"add {GlobalFields.FREQ_SWEEP_STR} "
                f"id={freq_sweep_macro_id_string} "
                f"set={sweepset_macro_id_string} "
                f"{sweep_type} "
                f"start={sweep_start} "
                f"stop={sweep_stop}\n\n"
            )
        elif sweep_type == "linear":
                        add_freq_sweep_string = (
                f"add {GlobalFields.FREQ_SWEEP_STR} "
                f"id={freq_sweep_macro_id_string} "
                f"set={sweepset_macro_id_string} "
                f"{sweep_type} "
                f"start={sweep_start} "
                f"stop={sweep_stop} "
                f"step={sweep_step} \n\n"
            )
        self.sonnet_macro_command_file.write(add_freq_sweep_string)
        self.freq_sweep_macro_id += 1

    def save_project(self):
        """Writes the 'save' line to the .smc file."""
        save_string = f'save path="{self.config.save_path}"\n'
        self.sonnet_macro_command_file.write(save_string)

    def add_output_file(self, param = "S", data_format = "MA", file_format = "TOUCH"):
        """ Create an output file """
        output_string = (
            f"add output_file id=output_fileA "
            f'path="{self.config.output_filename}" '
            f"param={param} "
            f"file_format={file_format} "
            f"format={data_format}\n\n"
        )
        self.sonnet_macro_command_file.write(output_string)
        
            
    #TODO: Add an option for server hostname:port
    def analyze_project(self, clean_data = True, server = None):
        """Analyze the project with EM """
        if clean_data:
            clean_string = f'clean_data \n'
            self.sonnet_macro_command_file.write(clean_string)
        if server is None: 
            analyze_string = f'analyze monitor \n'
        self.sonnet_macro_command_file.write(analyze_string)
    def generate_complete_file(self):
        """
        Generates the complete .smc file by calling all methods in the correct order.
        """
        self.open_file()
        self.add_project()
        self.modify_project_units()
        self.modify_project_box()
        for d in self.config.dielectrics:
            self.add_dielectric(d)

        self.add_diel_layers()
        self.modify_diel_layers()


        for m in self.config.conductors:
            self.add_conductor_general_metal(m)

        for t in self.config.tech_layers: 
            self.add_tech_layer_planar(t)
        for poly in self.config.polygons:
            self.add_polygon(poly)

        for port in self.config.ports:
            self.add_port(port)
            
        self.add_sweepset(self.config.freq_sweep_dict)
        self.add_output_file()
        self.save_project()
        print('Commented out the analyze_project() due to bug')
        #self.analyze_project()
        self.close_file()
        print("\n************************      CREATED " + self.output_path +
              "      ************************")
