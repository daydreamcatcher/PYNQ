#   Copyright (c) 2016, Xilinx, Inc.
#   All rights reserved.
# 
#   Redistribution and use in source and binary forms, with or without 
#   modification, are permitted provided that the following conditions are met:
#
#   1.  Redistributions of source code must retain the above copyright notice, 
#       this list of conditions and the following disclaimer.
#
#   2.  Redistributions in binary form must reproduce the above copyright 
#       notice, this list of conditions and the following disclaimer in the 
#       documentation and/or other materials provided with the distribution.
#
#   3.  Neither the name of the copyright holder nor the names of its 
#       contributors may be used to endorse or promote products derived from 
#       this software without specific prior written permission.
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
#   THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
#   PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
#   EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
#   PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#   OR BUSINESS INTERRUPTION). HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
#   WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
#   OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
#   ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

__author__      = "Yun Rock Qu"
__copyright__   = "Copyright 2016, Xilinx"
__email__       = "xpp_support@xilinx.com"


from . import pmod_const
from .devmode import DevMode

class PMOD_IO(object):
    """This class controls the PMOD IO pins as inputs or outputs.
    
    Note
    ----
    The parameter 'direction' determines whether the instance is input/output:
    'in'  : receiving input from offchip to onchip. 
    'out' : sending output from onchip to offchip.
    The index of the PMOD pins:
    upper row, from left to right: {vdd,gnd,3,2,1,0}.
    lower row, from left to right: {vdd,gnd,7,6,5,4}.
    
    Attributes
    ----------
    iop : _IOP
        The _IOP object returned from the DevMode.
    index : int
        The index of the PMOD pin, from 0 to 7.
    direction : str
        Input 'in' or output 'out'.
    
    """
    def __init__(self, pmod_id, index, direction): 
        """Return a new instance of a PMOD IO object.
    
        Note
        ----
        The pmod_id 0 is reserved for XADC (JA).
        
        Parameters
        ----------
        pmod_id : int
            The PMOD ID (1, 2, 3, 4) corresponding to (JB, JC, JD, JE).
        index: int
            The index of the PMOD pin, from 0 to 7.
        direction : str
            Input 'in' or output 'out'.
            
        """
        if (index not in range(8)):
            raise ValueError("Valid pin indexes are 0 - 7.")
        if (direction not in ['in', 'out']):
            raise ValueError("Direction can only be 'in', or 'out'.")
            
        self.iop = DevMode(pmod_id, pmod_const.IOP_SWCFG_PMODIOALL)
        self.index = index
        self.direction = direction
        
        self.iop.start()
        if (self.direction == 'in'):
            self.iop.write_cmd(pmod_const.IOPMM_PMODIO_BASEADDR+
                                pmod_const.IOPMM_PMODIO_TRI_OFFSET,
                                pmod_const.IOCFG_PMODIO_ALLINPUT)
        else:
            self.iop.write_cmd(pmod_const.IOPMM_PMODIO_BASEADDR+
                                pmod_const.IOPMM_PMODIO_TRI_OFFSET,
                                pmod_const.IOCFG_PMODIO_ALLOUTPUT)
                                
        self.iop.load_switch_config()
    
    def write(self, value): 
        """Send the value to the offboard PMOD IO device.

        Note
        ----
        Only use this function when direction = 'out'.
        
        Parameters
        ----------
        value : int
            The value to be written to the PMOD IO device.
            
        Returns
        -------
        None
            
        """
        if not value in (0,1):
            raise ValueError("PMOD IO can only write 0 or 1.")
        if not self.direction is 'out':
            raise ValueError('PMOD IO used as output, but declared as input.')

        if value:
            #: Set 1 to a PMOD IO pin.
            currVal = self.iop.read_cmd(pmod_const.IOPMM_PMODIO_BASEADDR+
                                        pmod_const.IOPMM_PMODIO_DATA_OFFSET)
            newVal = currVal | (0x1<<self.index)
            self.iop.write_cmd(pmod_const.IOPMM_PMODIO_BASEADDR + 
                                pmod_const.IOPMM_PMODIO_DATA_OFFSET, newVal)
        else:
            #: Set 0 to a PMOD IO pin.
            currVal = self.iop.read_cmd(pmod_const.IOPMM_PMODIO_BASEADDR+
                                        pmod_const.IOPMM_PMODIO_DATA_OFFSET)
            newVal = currVal & (0xff ^ (0x1<<self.index))
            self.iop.write_cmd(pmod_const.IOPMM_PMODIO_BASEADDR + 
                                pmod_const.IOPMM_PMODIO_DATA_OFFSET, newVal)

    def read(self):
        """Receive the value from the offboard PMOD IO device.

        Note
        ----
        Only use this function when direction = 'in'.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        int
            The data (0 or 1) on the specified PMOD IO pin.
        
        """  
        if not self.direction is 'in':
            raise ValueError('PMOD IO used as input, but declared as output.')
        
        raw_value = self.iop.read_cmd(pmod_const.IOPMM_PMODIO_BASEADDR + 
                                        pmod_const.IOPMM_PMODIO_DATA_OFFSET)
        return (raw_value >> (self.index)) & 0x1
        
    def _state(self):
        """Retrieve the current state of the PMOD IO.
        
        This function is usually used for debug purpose. Users should still
        rely on read() or write() to get/put a value.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        int
            The data (0 or 1) on the specified PMOD IO pin.
        
        """
        raw_value = self.iop.read_cmd(pmod_const.IOPMM_PMODIO_BASEADDR + 
                                        pmod_const.IOPMM_PMODIO_DATA_OFFSET)
        return (raw_value >> (self.index)) & 0x1
        