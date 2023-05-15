#Library used to make the robot wait by using time.sleep()
import time

# Type help("robodk.robolink") for more information
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/robodk.html
# Note: It is not required to keep a copy of this file, your Python script is saved with your RDK project
from robodk import robolink    # RoboDK API
RDK = robolink.Robolink()
robot = RDK.Item('UR5')

# Forward and backwards compatible use of the RoboDK API:
# Remove these 2 lines to follow python programming guidelines
from robodk import *      # RoboDK API
from robolink import *    # Robot toolbox

#Gripper library and initialization
import wsg50
wsg50_instance = wsg50.wsg50()

#Modbus communication from fixture to main program
from pymodbus.client import ModbusTcpClient

#Libraries for GUI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

class Order(BaseModel):
    top_color: str
    bottom_color: str
    top_fuse: bool
    bottom_fuse: bool
    top_hole: bool
    bottom_hole: bool


app = FastAPI()
origins = [
    "http://localhost:5173/",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/")
def read_order(order: Order) -> str:
    '''Waits for an order to be made in the GUI and assembles order if possible.
    
    Parameters: (order: Class)'''
    Top = order.top_color
    Bottom = order.bottom_color
    top_fuse = order.top_fuse
    bottom_fuse = order.bottom_fuse
    top_holes = order.top_hole
    bottom_holes = order.bottom_hole
    
    #Main program
    Initialize_robot()
    wsg50_instance.preposition_gripper(90, gripSpeed) 
    Move_home()
    Bottom_pickup(Bottom)
    Offset1 = Hole_drill(top_holes, bottom_holes)
    From_drill_to_assembly(Offset1)
    PCB_pickup()
    Fuse_pickup(top_fuse, bottom_fuse)
    From_fuse_to_assembly(top_fuse, bottom_fuse)
    Top_pickup(Top)
    From_top_cover_to_assembly()
    Layoff_assembled_phone()
    Move_home()
    return {"Status": "success"}

# Variables to adjust different speeds
linear_speed = 1500
joint_speed = 190
drillTime = 0.5
gripSpeed = 400
RDK.setSimulationSpeed(5)

# Fixture code (Missing implementation)
def Check_stock(Top, Bottom) -> list[int]:
    HOST = "192.168.1.184"
    PORT = 502
    with ModbusTcpClient(host=HOST, port=PORT) as client:
        client.connect()
        resultTop = client.read_holding_registers(address=Top, count=2, slave=255)
        print(resultTop.registers[0])
        resultBottom = client.read_holding_registers(address=Bottom, count=2, slave=255)
        print(resultBottom.registers[0])
        return [resultTop.registers[0], resultBottom.registers[0]]

### -------- Functions for moving the UR5 -------- ###
def Initialize_robot(linear_speed: int, joint_speed: int) -> None:
    """Start the UR5 in mode: '6'. This will make it possible to move the real robot from the PC (PC is the client, the robot behaves like a server). \n 
    Then sets linear speed and joint speed of the UR5.\n
    Parameters: (linear_speed, joint_speed)"""
    RDK.setRunMode(6)
    robot.setSpeed(linear_speed)
    robot.setSpeedJoints(joint_speed)

def Move_home() -> None:
    """Moves to starting position above assembly station.\n
    Parameters: None"""
    robot.MoveJ(RDK.Item("AboveAssemblyBottomCover"))

def Grasp(width: int, speed: int) -> None:
    """Uses grasp function from wsg50 library.\n
    Parameters: (width: int, speed: int)"""
    time.sleep(0.01)
    wsg50_instance.grasp_part(width, speed)
    time.sleep(0.01)

def Release(width: int, speed: int):
    """Uses release function from wsg50 library.\n
    Parameters: (width: int, speed: int)"""
    time.sleep(0.01)
    wsg50_instance.release_part(width, speed)
    time.sleep(0.01)

def Bottom_pickup(Bottom: str) -> None:
    """Picks up the bottom cover, depending on the color input, cooming from the GUI.\n
    Parameters: (Bottom: str)"""
    match Bottom:
        case 'White':
            robot.setPoseFrame(RDK.Item("Frame 5"))
        case 'Blue':
            robot.setPoseFrame(RDK.Item("Frame 4"))
        case 'Black':
            robot.setPoseFrame(RDK.Item("Frame 3"))
    robot.MoveL(RDK.Item("Bottom Cover 1"))
    robot.MoveL(RDK.Item("Bottom Cover 2"))
    Grasp(68, gripSpeed)
    robot.MoveL(RDK.Item("Bottom Cover 1"))

def Hole_drill(top_holes: bool, bottom_holes: bool) -> int:
    """Drills the correct amount of holes in the bottom cover depended on values top_holes and bottom_holes\n
    Parameters: (top_holes: bool, bottom_holes: bool)"""
    if top_holes and bottom_holes: # Drills 4 holes
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
    if top_holes: # Drills 2 holes in the top of the bottom cover
        robot.setPoseFrame(RDK.Item("FrameDrilling"))
        robot.MoveL(RDK.Item("Approach_Exit_Drilling"))
        robot.MoveL(RDK.Item("BeforeDrilling"))
        robot.MoveL(RDK.Item("Drilling"))
        time.sleep(drillTime)
        robot.MoveL(RDK.Item("BeforeDrilling"))
        robot.MoveL(RDK.Item("Approach_Exit_Drilling"))
        return 0
    if bottom_holes: # Drills 2 holes in the bottom of the bottom cover
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

def From_drill_to_assembly(Offset1: int) -> None:
    """Desides the path from drill to assembly in relation to offset1, if the bottom cover was offset when drilling holes in the bottom.\n
    Parameters: (Offset1: int)"""
    match Offset1:
        case 0: # Path without offset
            robot.setPoseFrame(RDK.Item("Universal frame"))
            robot.MoveJ(RDK.Item("AboveAssemblyBottomCover"))
            robot.MoveL(RDK.Item("AssemblyBottomCover"))
            Release(80, gripSpeed)
            robot.MoveL(RDK.Item("AboveAssemblyBottomCover"))
        case 1: # Path with offset
            robot.setPoseFrame(RDK.Item("Universal frame"))
            robot.MoveJ(RDK.Item("AboveAssemblyBottomCoverOffset"))
            robot.MoveL(RDK.Item("AssemblyBottomCoverOffset"))
            Release(80, gripSpeed)
            robot.MoveL(RDK.Item("AboveAssemblyBottomCoverOffset"))
    Offset1 = 0

def PCB_pickup() -> None:
    """Picks up the PCB.\n
    Parameters: None"""
    robot.setPoseFrame(RDK.Item("FramePCB"))
    robot.MoveL(RDK.Item("PCB 1"))
    robot.MoveL(RDK.Item("PCB 2"))
    Grasp(52, gripSpeed)
    robot.MoveL(RDK.Item("PCB 1"))

def Fuse_pickup(top_fuse: bool, bottom_fuse: bool) -> None:
    """Picks up the the ordered amount of fuses depending on values top_fuse and bottom_fuse.\n
    Parameters: (top_fuse: bool, bottom_fuse: bool)"""
    robot.setPoseFrame(RDK.Item("Universal Frame"))
    robot.MoveL(RDK.Item("BetweenFuseAndAssembly"))
    if top_fuse and bottom_fuse: # Picks up both fuses
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
    elif top_fuse: # Picks up top fuse
        robot.setPoseFrame(RDK.Item("FrameFuse"))
        robot.MoveL(RDK.Item("Top Fuse Approach & Exit"))
        robot.setSpeed(200)
        robot.MoveL(RDK.Item("Top Fuse"))
        #pickup <----
        robot.MoveL(RDK.Item("Top Fuse Approach & Exit"))
    elif bottom_fuse: # Picks up bottom fuse
        robot.setPoseFrame(RDK.Item("FrameFuse"))
        robot.MoveL(RDK.Item("Bottom Fuse Approach & Exit"))
        robot.setSpeed(200)
        robot.MoveL(RDK.Item("Bottom Fuse"))
        #pickup <----
        robot.MoveL(RDK.Item("Bottom Fuse Approach & Exit"))
    robot.setSpeed(linear_speed)

def From_fuse_to_assembly(top_fuse: bool, bottom_fuse: bool) -> None:
    """Takes the path from fuse to assembly depended on the values top_fuse and bottom_fuse.\n
    Parameters: (top_fuse: bool, bottom_fuse: bool)"""
    robot.setPoseFrame(RDK.Item("Universal frame"))
    if top_fuse or bottom_fuse: # Goes to target always, unless no fuses were picked up
        robot.MoveL(RDK.Item("BetweenFuseAndAssembly"))
    robot.MoveJ(RDK.Item("AboveAssemblyPCB"))
    robot.MoveL(RDK.Item("AssemblyPCB"))
    Release(80, gripSpeed)
    robot.MoveL(RDK.Item("AboveAssemblyPCB"))

def Top_pickup(Top: str) -> None:
    """Picks up the top cover, depending on the ordered color input in the GUI.\n
    Parameters: (Top: str)"""
    robot.setPoseFrame(RDK.Item("Universal frame"))
    robot.MoveJ(RDK.Item("BetweenTopCoverAndAssembly"))
    match Top:
        case 'White':
            robot.setPoseFrame(RDK.Item("Frame 8"))
        case 'Blue':
            robot.setPoseFrame(RDK.Item("Frame 7"))
        case 'Black':
            robot.setPoseFrame(RDK.Item("Frame 6"))
    robot.MoveL(RDK.Item("Bottom Cover 1"))
    robot.MoveL(RDK.Item("Bottom Cover 2"))
    Grasp(68, gripSpeed)
    robot.MoveL(RDK.Item("Bottom Cover 1"))

def From_top_cover_to_assembly() -> None:
    """Takes the path from top cover to assembly.\n
    Parameters: None"""
    robot.setPoseFrame(RDK.Item("Universal frame"))
    robot.MoveJ(RDK.Item("BetweenTopCoverAndAssembly"))
    robot.MoveJ(RDK.Item("TopCoverAboveAssembly"))
    robot.MoveL(RDK.Item("TopCoverAssembly"))
    robot.MoveL(RDK.Item("TopCoverAboveAssembly"))

def Layoff_assembled_phone() -> None:
    """Takes the path to lay down the assembled phone in position to be removed.\n
    Parameters: None"""
    robot.setPoseFrame(RDK.Item("Universal frame"))
    robot.MoveJ(RDK.Item("AssembledPhoneLayoff"))
    Release(80, gripSpeed)
    robot.MoveJ(RDK.Item("AboveAssembledPhone"))