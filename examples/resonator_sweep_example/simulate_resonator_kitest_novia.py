import numpy as np
import matplotlib.pyplot as plt
import pysonnet as ps
import gdspy as gp
import argparse


#Corresponding to design values
#[4.0ghz, 4.25, 4.50, 4.75, 5.0]
def draw_resonator(res_index): 

    inductor_length = [696.4, 615.2, 552.5, 499.5, 452.7]
    cpw_lw =10
    cpw_gap = 5.3


    ki_ph = 30
    dielectric_gap = 150
    induct_length = inductor_length[res_index]
  

    resonator_lw = 3
    cc_coupling = 13
    
    idc = 2 #Thickness of the IDC fingers
    cap_x = 60
    cap_y = 200
    num_fingers = cap_x//(idc*2*2*2)
    
    y0 = 50
    padding = 50 #Space from the feedline to the coupling capacitor 
    box_x = 100
    box_y = 1400
    extra_cap_space = 5 #Space from the coupling capacitor to the shunt capacitor #Note this space is also used for the via for the inductor 
    
    #CReate the resonator position
    y1 = y0 + cpw_gap + cpw_lw/2 + padding #+ cc_coupling
    y2 = y1 + extra_cap_space + cap_y
    cell = gp.Cell("resonator")

    extra = 1 #space for gnd plane to overcover the microstrip below
    cpw_line = gp.Rectangle((0, y0 - cpw_lw/2), (box_x, y0 + cpw_lw/2), layer = 0)
    #Make the coupling IDC
    cpw_cap_line = gp.Rectangle((box_x/2 - idc/2, y0), (box_x/2 + idc/2, y1 - idc), layer = 0)
    cpw_cap1 = gp.Rectangle((box_x/2 - 2.5*idc, y1), (box_x/2 - 1.5*idc, y1 - cc_coupling), layer = 0)
    cpw_cap2 = gp.Rectangle((box_x/2 + 2.5*idc, y1), (box_x/2 + 1.5*idc, y1 - cc_coupling), layer = 0)
    
    gnd_1 = gp.Rectangle((0, y1 + induct_length + cap_y - extra), (box_x, box_y), layer = 0) #Add extra space for extra edge

    gnd_1a = gp.Rectangle((0, y0 + cpw_lw/2 + cpw_gap), (box_x/2 - cap_x/2 - idc*0.5, y1 + induct_length + cap_y -  extra), layer = 0)
    gnd_1b = gp.Rectangle((box_x, y0 + cpw_lw/2 + cpw_gap), (box_x/2 + cap_x/2 + idc*0.5, y1 + induct_length + cap_y -  extra), layer = 0)

    gnd_2 = gp.Rectangle((0, y0 - cpw_lw/2 - cpw_gap), (box_x, 0), layer = 0)

    gnd_2a = gp.Rectangle((0, y0 + cpw_lw/2 + cpw_gap), (box_x/2 - 3, y1 - cc_coupling - 2*extra ), layer = 0)
    gnd_2b = gp.Rectangle((box_x, y0 + cpw_lw/2 + cpw_gap), (box_x/2 + 3, y1 - cc_coupling - 2*extra), layer = 0)

    cell.add(cpw_line)
    cell.add(cpw_cap1)
    cell.add(cpw_cap2)
    cell.add(cpw_cap_line)
    cell.add(gnd_1) 
    cell.add(gnd_2) 
    cell.add(gnd_1a)
    cell.add(gnd_1b)
    cell.add(gnd_2a)
    cell.add(gnd_2b) 
    #Resonator structure

    #gnd_cap = gp.Rectangle((box_x/2 - cap_x/2 - extra, y1 + extra_cap_space - extra ), (box_x/2 + cap_x/2 + extra, y1  + extra_cap_space + cap_y + extra), layer = 0)

    #Create the ground capacitor
    gnd_cap_edge = gp.Rectangle((box_x/2 - cap_x/2 + idc/2, y1 ), (box_x/2 + cap_x/2 - idc/2, y1 + idc), layer = 0)
    cell.add(gnd_cap_edge)
    #Create the IDC fingers
    for i in np.arange(-num_fingers, num_fingers + 1):
   
        gnd_finger = gp.Rectangle((box_x/2 - idc/2 + (4*i )*idc, y1 + idc),
                                  (box_x/2 + idc/2 + (4*i )*idc, y1 + idc + cap_y ), layer = 0)
        cell.add(gnd_finger)

    #Make a break for port 3
    idc_extend = 10
    gnd_finger = gp.Rectangle((box_x/2 - idc/2 , y1 + idc + cap_y),
                              (box_x/2 + idc/2 , y1 + idc + cap_y + idc_extend), layer = 0)
    cell.add(gnd_finger)

    #Create the gnd idc
    gnd_cap_edge1 = gp.Rectangle((box_x/2 - cap_x/2 - idc, y1 + cap_y + idc*2), (box_x/2  - idc*1.5, y1 + cap_y + idc*3), layer = 0)
    gnd_cap_edge2 = gp.Rectangle((box_x/2 + cap_x/2 + idc, y1 + cap_y + idc*2), (box_x/2  + idc*1.5, y1 + cap_y + idc*3), layer = 0)

    cell.add(gnd_cap_edge1)
    cell.add(gnd_cap_edge2)

    for i in np.arange(-num_fingers, num_fingers + 2): 
        gnd_finger = gp.Rectangle((box_x/2 - idc/2 + (4*i  - 2)*idc, y1 + idc + idc),
                                  (box_x/2 + idc/2 + (4*i  - 2)*idc, y1 + 2*idc + cap_y ), layer = 0)
        cell.add(gnd_finger)


    res_ind_path = np.array([[box_x/2, y1 +extra_cap_space +  cap_y], [box_x/2, y1 +extra_cap_space+ cap_y + induct_length]])
    res_ind = gp.FlexPath(res_ind_path, resonator_lw, layer = 1)





    cell.add(res_ind)
    return cell
#gp.LayoutViewer()

