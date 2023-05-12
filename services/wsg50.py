
#Copyright © 2023 Martin B. Jensen

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files
# (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

#################################### MODULES AND IMPORTED CLASSES ###########################################
import struct
import socket
import time
import sys

import numpy as np

#################################### CONSTANTS AND GLOBAL VARIABLES #########################################
# #inital message with header for later id and payload to be appended

# command ids
HOMING_ID = 32
PREPOSITION_ID = 33
GRASP_ID = 37
RELEASE_ID = 38

# payload sizes
HOMING_SIZE = 1
PREPOSITION_SIZE = 9
GRASP_SIZE = 8
RELEASE_SIZE = 8

# preambles for each message type
HOMING_PREAMBLE = [170, 170, 170, HOMING_ID, HOMING_SIZE, 0]
PREPOSITION_PREAMBLE = [170, 170, 170, PREPOSITION_ID, PREPOSITION_SIZE, 0, 0]
GRASP_PREAMBLE = [170, 170, 170, GRASP_ID, GRASP_SIZE, 0]
RELEASE_PREAMBLE = [170, 170, 170, RELEASE_ID, RELEASE_SIZE, 0]

# disconnect message
DISCONNECT_MSG = [170, 170, 170, 7, 0, 0, 53, 76]
REMOVE_ERROR_MSG = [170, 170, 170, 36, 3, 0, 97, 99, 107, 220, 185]

GRIPPER_STATUS_MSG = [170, 170, 170, 64, 3, 0, 1, 8, 62, 67, 76]

# error code messages and state flags
ERROR_CODES_WSG = {0: 'SUCCESS', 1: 'E_NOT_AVAILABLE', 2: 'E_NO_SENSOR',
                   3: 'E_NOT_INITIALIZED', 4: 'E_ALREADY_RUNNING', 5: 'E_FEATURE_NOT_SUPPORTED',
                   6: 'E_INCONSISTENT_DATA', 7: 'E_TIMEOUT', 8: 'E_READ_ERROR', 9: 'E_WRITE_ERROR',
                   10: 'E_INSUFFICIENT_RESOURCES', 11: 'E_CHECKSUM_ERROR', 12: 'E_NO_PARAM_EXPECTED',
                   13: 'E_NOT_ENOUGH_PARAMS', 14: 'E_CMD_UNKNOWN', 15: 'E_CMD_FORMAT_ERROR',
                   16: 'E_ACCESS_DENIED', 17: 'E_ALREADY_OPEN', 18: 'E_CMD_FAILED', 19: 'E_CMD_ABORTED',
                   20: 'E_INVALID_HANDLE', 21: 'E_NOT_FOUND', 22: 'E_NOT_OPEN', 23: 'E_IO_ERROR',
                   24: 'E_INVALID_PARAMETER', 25: 'E_INDEX_OUT_OF_BOUNDS', 26: 'E_CMD_PENDING',
                   27: 'E_OVERRUN', 28: 'E_RANGE_ERROR', 29: 'E_AXIS_BLOCKED', 30: 'E_FILE_EXISTS'}

SYSTEM_STATE_FLAGS = ['SF_REFERENCED', 'SF_MOVING', 'SF_BLOCKED_MINUS', 'SF_BLOCKED_PLUS',
                      'SF_SOFT_LIMIT_MINUS', 'SF_SOFT_LIMIT_PLUS', 'SF_AXIS_STOPPED',
                      'SF_TARGET_POS_REACHED', 'SF_OVERRIDE_MODE', 'SF_FORCECNTL_MODE',
                      'RESERVED', 'RESERVED', 'SF_FAST_STOP', 'SF_TEMP_WARNING',
                      'SF_TEMP_FAULT', 'SF_POWER_FAULT', 'SF_CURR_FAULT', 'SF_FINGER_FAULT',
                      'SF_CMD_FAILURE', 'SF_SCRIPT_RUNNING', 'SF_SCRIPT_FAILURE']


class wsg50():
    def __init__(self, server_ip='192.168.1.22', server_port=1000):

        self.server_ip = server_ip # set the local class ip 
        self.server_port = server_port # set the local class port

        self.sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # construct the class for the socket connection
        self.sckt.connect((self.server_ip, self.server_port)) # connect with TCP/IP to the gripper

        errorRemove = bytearray()
        for m in REMOVE_ERROR_MSG: # compile the byte array for the error remove message(this message is static on only needs to be created once)
            errorRemove.append(m)
        self.errorRemove = errorRemove

        disconnect = bytearray()
        for m in DISCONNECT_MSG: # compile the byte array for the disconnect message(this message is static on only needs to be created once)
            disconnect.append(m)
        self.disconnect = disconnect

        state = bytearray()
        for m in GRIPPER_STATUS_MSG: # compile the byte array for the disconnect message(this message is static on only needs to be created once)
            state.append(m)
        self.gripper_status = state

        self.homing() # Home the gripper once connected to it
        time.sleep(0.5)

    ################ PRIVATE METHODS #####################
    def _remove_err(self):
        """Remove checksum errors from the gripper status. 
        """

        self.sckt.sendall(self.errorRemove)
        self.sckt.setblocking(0)
        
    def _float_to_payload(self, payload):
        """Decomposes a float to IEEE 754 32-bit float representation(4 bytes).

        Args:
            payload (float): Input float that needs to be converted.

        Returns:
            list: List consisting of 4 bytes that describes the float in IEEE 754.
        """
        
        hex_list = hex(struct.unpack('>I', struct.pack('>f', payload))[0])

        payload_list = []
        for i in range(0, len(hex_list[2:]), 2):
            payload_list.append(int(hex_list[i + 2 : i + 4], 16))

        return payload_list[::-1] #return as little endian

    ################ PUBLIC METHODS #####################
    def homing(self):
        """Homing gripper to 110mm and recalibrates finger pose.
        """

        homing_payload = [0]
        combined_payload = HOMING_PREAMBLE + homing_payload # create the specific payload for the homing procedure # checksum , 143, 131
        
        byte_msg = bytearray()
        for byte in combined_payload:
            byte_msg.append(byte)

        self.sckt.sendall(byte_msg)
        self._remove_err()
        self.sckt.setblocking(1)

        err_code = None
        while err_code != 0:
            data = self.sckt.recv(256) 
            err_code = struct.unpack('<h', data[6:8])[0]# byte 6-8 are error codes: 0: SUCCESS, 26: PENDING, 4: RUNNING, 10: DENIED
            print("Homing response: ", err_code, ERROR_CODES_WSG[err_code])


    def preposition_gripper(self, width, speed):
        """Preposition the gripper to a set width at a certain speed. \n
        (DO NOT USE THIS FUNCTION TO GRASP PARTS. IT WILL RETURN AN ERROR FROM THE GRIPPER)

        Args:
            width (float): Set the width of the gripper fingers in mm.
            speed (float): Set the speed of the gripper fingers in mm/s.
        """
 
        width_payload = self._float_to_payload(width) # decompose float to 4 bytes that can be attached to message
        speed_payload = self._float_to_payload(speed)
        combined_payload = PREPOSITION_PREAMBLE + width_payload + speed_payload
        
        byte_msg = bytearray()
        for byte in combined_payload:
            byte_msg.append(byte)

        self.sckt.sendall(byte_msg)
        self._remove_err()
        self.sckt.setblocking(1)

        err_code = None
        while err_code != 0:
            data = self.sckt.recv(256) # byte 5-6 are error codes: 10 denied and 1a success
            err_code = struct.unpack('<h', data[6:8])[0]
            print("Preposition reponse from {0}:".format([width, speed]), err_code, ERROR_CODES_WSG[err_code])


    def grasp_part(self, width, speed):
        """This function is used to grasp a part. \n
        (USING THIS FUNCTION WITHOUT HAVING A PART TO GRASP WILL RETURN AN ERROR)

        Args:
            width (float): Set the width of the part that has to be grasped in mm.
            speed (float): Set the speed of the gripper fingers in mm/s.
        """

        width_payload = self._float_to_payload(width)
        speed_payload = self._float_to_payload(speed)
        combined_payload = GRASP_PREAMBLE + width_payload + speed_payload

        byte_msg = bytearray()
        for byte in combined_payload:
            byte_msg.append(byte)

        self.sckt.sendall(byte_msg)
        self._remove_err()
        self.sckt.setblocking(1)

        err_code = None
        while err_code != 0:
            data = self.sckt.recv(256) # byte 5-6 are error codes: 10 denied and 1a success
            err_code = struct.unpack('<h', data[6:8])[0]
            print("Grasp reponse from {0}:".format([width, speed]), err_code, ERROR_CODES_WSG[err_code])
            print(type(err_code))
            if err_code == 18:
                break


    def release_part(self, width, speed):
        """Release a previously grasped part.

        Args:
            width (float): Set the width of the gripper fingers in mm.
            speed (float): Set the speed of the gripper fingers in mm/s.
        """

        width_payload = self._float_to_payload(width)
        speed_payload = self._float_to_payload(speed)
        combined_payload = RELEASE_PREAMBLE + width_payload + speed_payload

        byte_msg = bytearray()
        for byte in combined_payload:
            byte_msg.append(byte)

        self.sckt.sendall(byte_msg)
        self._remove_err()
        self.sckt.setblocking(1)

        err_code = None
        while err_code != 0:
            data = self.sckt.recv(256) # byte 5-6 are error codes: 10 denied and 1a success
            err_code = struct.unpack('<h', data[6:8])[0]

            print("Release reponse from {0}:".format([width, speed]), err_code, ERROR_CODES_WSG[err_code])

    def gripper_state(self):
        """Gets all the present state flags from the gripper.\n
        This can be used for debugging and checking the overall state of the robot.

        Returns:
            list[str]: Returns a list of all the present states on the gripper
        """

        self.sckt.sendall(self.gripper_status)
        self.sckt.setblocking(1)
        data = self.sckt.recv(16)
        binarized = bin(int(data.hex()[4:10], 16))[2:23] # Take the 21 bits that are allocated to state flags. For more information see: WSG50 Command Set Reference Maunal, Appendix B

        state_mask =  [] # Added mask for the error_states
        for bit in binarized:
            state_mask.append(bool(int(bit)))
        
        present_state_flags = [SYSTEM_STATE_FLAGS[i] for i in range(len(SYSTEM_STATE_FLAGS)) if state_mask[i]]
        print(present_state_flags)

        return present_state_flags
        

    def start_connection(self, server_ip='192.168.1.22', server_port=1000):
        """Start a TCP/IP socket connection with a desired IP and port.

        Args:
            server_ip (str, optional): IP address of the desired server. Defaults to '192.168.1.21'.
            server_port (int, optional): Port of the desired server. Defaults to 1000.
        """

        self.sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # construct the class for the socket connection
        self.sckt.connect((server_ip, server_port)) # connect with TCP/IP to the 

    def end_connection(self):
        """End TCP/IP socket connection.
        """

        self.sckt.sendall(self.disconnect)
        #self._remove_err()
        self.sckt.setblocking(1)

        err_code = None
        while err_code != 0: # While the command hasn't returned 0 for SUCCESS continue listening
            data = self.sckt.recv(256) # byte 5-6 are error codes: 10 denied and 1a success
            err_code = struct.unpack('<h', data[6:8])[0]
            print("Close connection reponse:", err_code, ERROR_CODES_WSG[err_code])

        self.sckt.close()

def test(wsg_instance):

    """Testing all 3 types of movement: preposition, grasp and release

    Args:
        wsg_instance (class_instance): declare the wsg50 class and pass the object to this function.
    """

    wsg_instance.preposition_gripper(20, 100)

    #wsg_instance.grasp_part(55, 100)

    #time.sleep(5)

    #wsg_instance.release_part(70, 100)

    wsg_instance.end_connection()

def main():
    
    print("This script is running in the class file!")


    wsg_instance = wsg50()

    try:
        test(wsg_instance)
        #wsg_instance.grasp_part(58, 100)
        #time.sleep(2)
        #wsg_instance.gripper_state()
        
        #wsg_instance.end_connection()
    
    except KeyboardInterrupt:
        print('interrupted!')
        wsg_instance.end_connection()
        sys.exit(0)    

if __name__ == "__main__":
    main()


