#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append("..")
from rawdata import interpol, interpol2, read_csv_table
from utils import Container, resource_path

__all__ = ["stable", "saturation_table", "mixture_volume", "vapor_quality", "phase"]

__saturation_table__ = resource_path("saturated_water.csv")
#print "__saturation_table__ ", __saturation_table__
saturation_table = read_csv_table(__saturation_table__)
saturation_table = Container(**saturation_table)

tol = 1e-3

#psat = saturation_table['P']
#tsat = saturation_table['T']
#vfsat = saturation_table['Vf']
#vgsat = saturation_table['Vg']

def stable(value, _input, params):
    """
    Calculate the Saturated water thermodynamic properties 
    table from Steam table properties, given the temperature T.
    
    Source:          
        Apendix B, Page 775 - Table B1.1
        Fundamentals of Thermodynamics, 
        SI Units Thermodynamic Tables. 8th edition
        BORGNAKKE and SONNTAG

    :param T:       Temperature at ºC
    :param params:  List of properties to be calculated
    :param _input:   Type of input parameter. Possible values
    :return:        List of calculated properties
    
    Possible Values of input: ['T', 'P']
    
    Possible values of param:
    
    T, P, Vf, Vfg, Vg, Uf, Ufg, Ug, Hf, Hfg, Hg, Sf, Sfg, Sg
    
    T       Temperature                 ºC
    P       Pressure                    kPa
    Vf      Sat Liquid Specific Volume  m3/kg
    Vfg     Vg-Vf                       m3/kg
    Vg      Sat Vapor                   m3/kg
    Uf      Sat Liquid Internal Energy  kJ/kg
    Ufg     Ug-Uf                       kJ/kg
    Ug      Sat Vapor Internal Energy   kJ/kg
    Hg      Sat Liquid Entalphy         kJ/kg
    Hfg     Vf-Vg Entalphy              kJ/kg
    Hg      Sat Vapor Entalphy          kJ/kg
    Sf      Sat Liquid Entropy          kj/Kg-K
    Sfg     Vf-Vg Entropy               kj/Kg-K
    Sg      Sat Vapor Entropy           kj/Kg-K
        
    Example:
        >>> import thermo.steamtables
        >>> thermo.steamtables.sattable(232, 'T', ['P', 'Vf', 'Vg', 'Uf' ])
        [2900.98, 0.001213, 0.069092, 995.984]


        >>> s.stable(500, 'P', ['T', 'Vf', 'Vg', 'Uf' ])
        [151.79315476190476,
         0.0010921517857142857,
         0.3762758035714286,
         639.3956696428571]  
    """
    s = saturation_table
    result = []
    
    input_column= s[_input]
    
    for p in params:
        y = interpol(value, input_column, s[p])
        result.append(y)
    
    return result

def P_sat(T):
    """
    :param T: Saturation temperature in °C
    :return:  Water steam saturation pressure in kPa
    """
    return stable(T, 'T', ['P'])[0]

def Vf_sat(T):
    """
    :param T:  Saturation Temperature in °C
    :return:   Water saturation specific volume of water liquid phase.
    """
    return stable(T, 'T', ['Vf'])[0]

def Vg_sat(T):
    """
    :param T: Saturation Temperature in °C
    :return:  Water saturation specific volume of steam phase.
    """
    return stable(T, 'T', ['Vg'])[0]

def T_sat(P):
    """
    :param P: Saturation Pressure in kPa
    :return:  Saturation temperature in °C
    """
    return stable(P, 'P', ['T'])[0]



def mixture_volume(x, value, _input='T'):
    """
    Calculates the average specific volume 
    given the the vapor quality x (Mvap/M)
    and parameters value, _input:
    
    :param x: Vapor quality 0 < x < 1
    :param value: Value of Temperature or pressure
    :pram _input: Input type "P" for pressure, "T" for temperatur
    :return: Average Specific volume
    
    v = (1-x)*vf + x*vg 
    
    Example: 
    
    Calculate the specific volume m3/kg for 4 Mpa
    and quality x = 90% 
    
    >>> mixture_volume( 0.9, 4000, 'P')
    0.04495115454545455
           
    """
    
    vfsat, vgsat= stable(value, _input, ['Vf', 'Vg'])   
    v= (1-x)*vfsat + x*vgsat
    return v


def vapor_quality(v, value, _input='T'):
    """
    Calculates the vapor quality given
    v, vf and vg
    
    :return: (v-vf)/(vg-vf)
    """ 
    vfsat, vgsat= stable(value, _input, ['Vf', 'Vg'])       
    return (v-vfsat)/(vgsat-vfsat)
    
    

def phase(T, P=None, v=None, debug=False):
    """
    Determine the phase of saturated steam. 
    Given its temperature or Specific Volume
    """  
    
    # Only T and P is known
    if P is not None:
        
        Tsat, vfsat, vgsat = stable(P, 'P', ['T', 'Vf', 'Vg' ])
        
        if debug:
            print dict(Tsat=Tsat, vfsat=vfsat, vgsat=vgsat)
        
        if T < Tsat:
            return "Supercooled liquid"
        elif abs(T-Tsat) < tol:
            return "Two mixed phase mixture liquid and vapor"
        else:
            return "Vapor"
        
    if v is not None:
        
        Psat, vfsat, vgsat = stable(T, 'T', ['P', 'Vf', 'Vg' ])
        
        if debug:
            print dict(Psat=Psat, vfsat=vfsat, vgsat=vgsat)
        
        if v < vfsat:
            return "Liquid"
        elif vfsat < v < vgsat:
            return "Two mixed phase mixture liquid and vapor"
        elif v > vgsat:
            return "Super Heated Vapor"


