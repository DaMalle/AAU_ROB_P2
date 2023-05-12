# Type help("robodk.robolink") or help("robodk.robomath") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/robodk.html
# Note: It is not required to keep a copy of this file, your Python script is saved with your RDK project
import time
# You can also use the new version of the API:
from robodk import robolink    # RoboDK API
from robodk import robomath    # Robot toolbox
RDK = robolink.Robolink()
robot = RDK.Item('UR5')

# Forward and backwards compatible use of the RoboDK API:
# Remove these 2 lines to follow python programming guidelines
from robodk import *      # RoboDK API
from robolink import *    # Robot toolbox
# Link to RoboDK
# RDK = Robolink()

#kører et program ved navnet "reset pos"
#RDK.Item("Reset Pos").RunProgram()

#gripper TBD
import wsg50
wsg50_instance = wsg50.wsg50()
#wsg50.grasp_part() #Will be used to grip the part
#wsg50.release_part() #will be used to release the part

#Modbus communication from fixture to main program
'''from pymodbus.client import ModbusTcpClient
HOST = "192.168.1.184"
PORT = 502
with ModbusTcpClient(host=HOST, port=PORT) as client:
    pass'''
#Inputs from the GUI
Top = 1
Bottom = 2
Fuse = 3
Holes = 3
Offset1 = 0
robotspeed = 1500
drillTime = 0.5
gripSpeed = 400
RDK.setSimulationSpeed(5)
### Fixture code
'''def Check_stock(Top, Bottom):
    client.connect()
    resultTop = client.read_holding_registers(address=Top, count=2, slave=255)
    print(resultTop.registers[0])
    resultBottom = client.read_holding_registers(address=Bottom, count=2, slave=255)
    print(resultBottom.registers[0])
    return [resultTop.registers[0], resultBottom.registers[0]]'''


def Robot_reset(): #Robot goes to "Home" position, and all the parts go back to the dipensers
    """Resets the position of the robot, and the parts"""
    RDK.Item("Reset Pos").RunProgram()


def Bottom_pickup(Bottom): #Route dependend on cover color
    """Picks up the bottom cover, depending on the Bottom number input, comming from the GUI"""
    match Bottom:
        case 1:#White
            robot.setPoseFrame(RDK.Item("Frame 5"))
            robot.MoveL(RDK.Item("Bottom Cover 1"))
            robot.MoveL(RDK.Item("Bottom Cover 2"))
            Grasp(68, gripSpeed)
            robot.MoveL(RDK.Item("Bottom Cover 1"))
        case 2:#Blue
            robot.setPoseFrame(RDK.Item("Frame 4"))
            robot.MoveL(RDK.Item("Bottom Cover 1"))
            robot.MoveL(RDK.Item("Bottom Cover 2"))
            Grasp(68, gripSpeed)
            robot.MoveL(RDK.Item("Bottom Cover 1"))
        case 3:#Black
            robot.setPoseFrame(RDK.Item("Frame 3"))
            robot.MoveL(RDK.Item("Bottom Cover 1"))
            robot.MoveL(RDK.Item("Bottom Cover 2"))
            Grasp(68, gripSpeed)
            robot.MoveL(RDK.Item("Bottom Cover 1"))
            


def PCB_pickup(): #PCB
    """Picks up the PCB, no input required"""
    robot.setPoseFrame(RDK.Item("FramePCB"))
    robot.MoveL(RDK.Item("PCB 1"))
    robot.MoveL(RDK.Item("PCB 2"))
    Grasp(52, gripSpeed)
    robot.MoveL(RDK.Item("PCB 1"))


def Fuse_pickup(Fuse:int): #Route dependend on amount and placement of fuse
    """Picks up the Fuses, 0: zero fuses, 1: 1 top fuse, 2: bottom fuse, 3: both fuses"""
    robot.setPoseFrame(RDK.Item("Universal Frame"))
    robot.MoveL(RDK.Item("BetweenFuseAndAssembly"))
    match Fuse:
        case 1:#Top fuse
            robot.setPoseFrame(RDK.Item("FrameFuse"))
            robot.MoveL(RDK.Item("Top Fuse Approach & Exit"))
            robot.setSpeed(200)
            robot.MoveL(RDK.Item("Top Fuse"))
            #pickup <----
            robot.MoveL(RDK.Item("Top Fuse Approach & Exit"))
        case 2:#Bottom fuse
            robot.setPoseFrame(RDK.Item("FrameFuse"))
            robot.MoveL(RDK.Item("Bottom Fuse Approach & Exit"))
            robot.setSpeed(200)
            robot.MoveL(RDK.Item("Bottom Fuse"))
            #pickup <----
            robot.MoveL(RDK.Item("Bottom Fuse Approach & Exit"))
        case 3:#Both fuses
            robot.setPoseFrame(RDK.Item("FrameFuse"))
            robot.MoveL(RDK.Item("Top Fuse Approach & Exit"))
            robot.setSpeed(200)
            robot.MoveL(RDK.Item("Top Fuse"))
            #pickup <----
            robot.MoveL(RDK.Item("Top Fuse Approach & Exit"))
            robot.MoveL(RDK.Item("Bottom Fuse Approach & Exit"))
            robot.MoveL(RDK.Item("Bottom Fuse"))
            #pickup <----
            robot.MoveL(RDK.Item("Bottom Fuse Approach & Exit"))
        case 4:#No fuses
            pass
    robot.setSpeed(robotspeed)

def Top_pickup(Top:int): #Route dependend on cover color
    """Picks up the bottom cover, depending on the Bottom number input, comming from the GUI"""
    robot.setPoseFrame(RDK.Item("Universal frame"))
    robot.MoveJ(RDK.Item("BetweenTopCoverAndAssembly"))
    match Top:
        case 1:#White
            robot.setPoseFrame(RDK.Item("Frame 8"))
            robot.MoveL(RDK.Item("Bottom Cover 1"))
            robot.MoveL(RDK.Item("Bottom Cover 2"))
            Grasp(68, gripSpeed)
            robot.MoveL(RDK.Item("Bottom Cover 1"))
        case 2:#Blue
            robot.setPoseFrame(RDK.Item("Frame 7"))
            robot.MoveL(RDK.Item("Bottom Cover 1"))
            robot.MoveL(RDK.Item("Bottom Cover 2"))
            Grasp(68, gripSpeed)
            robot.MoveL(RDK.Item("Bottom Cover 1"))
        case 3:#Black
            robot.setPoseFrame(RDK.Item("Frame 6"))
            robot.MoveL(RDK.Item("Bottom Cover 1"))
            robot.MoveL(RDK.Item("Bottom Cover 2"))
            Grasp(68, gripSpeed)
            robot.MoveL(RDK.Item("Bottom Cover 1"))


def Hole_drill(Holes:int): #Route dependend on amount of holes
    """Drills holes for the bottom cover, 1: top holes, 2: bottom holes, 3: all four holes."""
    match Holes:
        case 1: #2 holes top
            robot.setPoseFrame(RDK.Item("FrameDrilling"))
            robot.MoveL(RDK.Item("Approach_Exit_Drilling"))
            robot.MoveL(RDK.Item("BeforeDrilling"))
            robot.MoveL(RDK.Item("Drilling"))
            time.sleep(drillTime)
            robot.MoveL(RDK.Item("BeforeDrilling"))
            robot.MoveL(RDK.Item("Approach_Exit_Drilling"))
            return 0
        case 2: #2 holes bottom
            robot.setPoseFrame(RDK.Item("FrameDrilling"))
            robot.MoveL(RDK.Item("Approach_Exit_Drilling"))
            robot.MoveJ(RDK.Item("DetachBottomCover180"))
            Release(80, gripSpeed)
            robot.MoveL(RDK.Item("DetachOffset"))
            Grasp(69, gripSpeed)
            robot.MoveJ(RDK.Item("AboveBottomCover180"))
            robot.MoveL(RDK.Item("BeforeDrilling180"))
            robot.MoveL(RDK.Item("Drilling180"))
            time.sleep(drillTime)
            robot.MoveL(RDK.Item("BeforeDrilling180"))
            robot.MoveJ(RDK.Item("Approach_Exit_Drilling"))
            return 1
            
        case 3: #4 holes
            robot.setPoseFrame(RDK.Item("FrameDrilling"))
            robot.MoveL(RDK.Item("Approach_Exit_Drilling"))
            robot.MoveL(RDK.Item("BeforeDrilling"))
            robot.MoveL(RDK.Item("Drilling"))
            time.sleep(drillTime)
            robot.MoveL(RDK.Item("BeforeDrilling"))
            robot.MoveJ(RDK.Item("AboveBottomCover180"))
            robot.MoveL(RDK.Item("DetachBottomCover180"))
            Release(80, gripSpeed)
            robot.MoveL(RDK.Item("DetachOffset"))
            Grasp(69, gripSpeed)
            robot.MoveJ(RDK.Item("AboveBottomCover180"))
            robot.MoveL(RDK.Item("Drilling180"))
            time.sleep(drillTime)
            robot.MoveL(RDK.Item("BeforeDrilling180"))
            robot.MoveJ(RDK.Item("Approach_Exit_Drilling"))
            return 1

def From_drill_to_assembly(Offset1): #Route dependend on offset
    """Desides the path from drill to assembly, in relation to offset, when drilling bottom holes, 1: No offset, 2: Offset"""
    # No path planning yet
    match Offset1:
        case 0: # path without offset
            robot.setPoseFrame(RDK.Item("Universal frame"))
            robot.MoveJ(RDK.Item("AboveAssemblyBottomCover"))
            robot.MoveL(RDK.Item("AssemblyBottomCover"))
            Release(80, gripSpeed)
            robot.MoveL(RDK.Item("AboveAssemblyBottomCover"))
        case 1: # path with offset
            robot.setPoseFrame(RDK.Item("Universal frame"))
            robot.MoveJ(RDK.Item("AboveAssemblyBottomCoverOffset"))
            robot.MoveL(RDK.Item("AssemblyBottomCoverOffset"))
            Release(80, gripSpeed)
            robot.MoveL(RDK.Item("AboveAssemblyBottomCoverOffset"))
    Offset1 = 0

def From_fuse_to_assembly():
    """Takes the path from fuse to assembly"""
    # No path planning yet
    robot.setPoseFrame(RDK.Item("Universal frame"))
    if Fuse!=4:
        robot.MoveL(RDK.Item("BetweenFuseAndAssembly"))
    robot.MoveJ(RDK.Item("AboveAssemblyPCB"))
    robot.MoveL(RDK.Item("AssemblyPCB"))
    Release(80, gripSpeed)
    robot.MoveL(RDK.Item("AboveAssemblyPCB"))

def From_top_cover_to_assembly():
    """Takes the path from top cover to assembly"""
    # No path planning yet
    robot.setPoseFrame(RDK.Item("Universal frame"))
    robot.MoveJ(RDK.Item("BetweenTopCoverAndAssembly"))
    robot.MoveJ(RDK.Item("TopCoverAboveAssembly"))
    robot.MoveL(RDK.Item("TopCoverAssembly"))
    robot.MoveL(RDK.Item("TopCoverAboveAssembly"))

def Layoff_assembled_phone():
    robot.setPoseFrame(RDK.Item("Universal frame"))
    robot.MoveJ(RDK.Item("AssembledPhoneLayoff"))
    Release(80, gripSpeed)
    robot.MoveJ(RDK.Item("AboveAssembledPhone"))

def Move_home():
    robot.MoveJ(RDK.Item("AboveAssemblyBottomCover"))

def Move_assembled_phone():
    robot.setPoseFrame(RDK.Item("Universal frame"))
    robot.MoveL(RDK.Item("AssembledPhone"))
    #Attach <------
    robot.MoveL(RDK.Item("AboveAssembledPhone"))
    robot.MoveL(RDK.Item("AssembledPhoneLayoff"))
    #Detach <------

def Grasp(width, speed):
    time.sleep(0.01)
    wsg50_instance.grasp_part(width, speed)
    time.sleep(0.01)

def Release(width, speed):
    time.sleep(0.01)
    wsg50_instance.release_part(width, speed)
    time.sleep(0.01)

def Initialize_robot():
    RDK.setRunMode(6)
    robot.setSpeed(robotspeed)
    robot.setSpeedJoints(190)

#print(Check_stock(4, 1))


Initialize_robot()
wsg50_instance.preposition_gripper(90, gripSpeed) 
Move_home()
Bottom_pickup(Bottom)
Offset1 = Hole_drill(Holes)
From_drill_to_assembly(Offset1)
PCB_pickup()
Fuse_pickup(Fuse)
From_fuse_to_assembly()
Top_pickup(Top)
From_top_cover_to_assembly()
Layoff_assembled_phone()
Move_home()