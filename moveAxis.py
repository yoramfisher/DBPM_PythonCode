import sys
import os
from pprint import pprint

if 0:
    from msl.equipment import EquipmentRecord, ConnectionRecord, Backend
    from msl.equipment.resources.thorlabs import MotionControl


"""
moveAxis.py
Description This example shows how to communicate with Thorlabs KST101, KCube Stepper Motor.
Usage ~ [X|Y|Z] abs_pos_in_mm [-verbose]
      ~ status  - display three motors positions
"""

# As seen by CCD
# X is Left/Right,  0 on the Left
# Y is Up/Down,  0 is on bottom
# Z is toward X-ray source, 0 is furthest.
#
#  Important that these serial numbers match the axes.
# 
motorX = '80861709'
motorY = '80861770'
motorZ = '80861765'


# globals
verbose = 0

def ShowHelp():
   print("Usage:")
   print("  moveAxis [X | Y | Z] abs_pos_in_mm [-verbose] ")
   print("  moveAxis status -- show all 3 motors positions ")
   

def showMotorStatus():

    labels = ["X", "Y", "Z"]
    for  i,x in enumerate([motorX, motorY, motorZ]):
        motor = setup(x)
        position = motor.get_position()
        real = motor.get_real_value_from_device_unit(position, 'DISTANCE')
        print('  {} at position {} [steps] {:.3f} [mm]'.\
            format( labels[i], position, real))
        close( motor )



def pollMotorStatus(doPrint = 1):

    labels = ["X", "Y"]
    
    motor1 = None
    motor2 = None
    
    
    try:
        motor1 = setup(motorX)
        motor2 = setup(motorY)

        position1 = motor1.get_position()
        position2 = motor2.get_position()

        real1 = motor1.get_real_value_from_device_unit(position1, 'DISTANCE')
        real2 = motor2.get_real_value_from_device_unit(position2, 'DISTANCE')
 
        if doPrint:
            print('  {}: {:.3f} {}: {:.3f}'.\
                format( labels[0], real1, labels[1], real2))

        return (real1, real2)
   

    except Exception as e:        
        print("oops exception")



   
 
    if (motor1):
         close( motor1 )   
    if (motor2):
        close( motor2 )  



def move(motor,  pos):
    """ 
    pos is in mm
    """

 
    steps = motor.get_device_unit_from_real_value(pos, 'DISTANCE') 
    # move to position 100000
    ##print('Moving to {} ({:.3f}mm)...'.format(steps, pos))
    ##motor.move_to_position(100000)
    motor.move_to_position( steps )
    wait( motor )
    ##print('Moving done. At position {} [device units]'.format(motor.get_position()))


def setup( sn ):
    """ Returns motor
    """
    # ensure that the Kinesis folder is available on PATH
    os.environ['PATH'] += os.pathsep + 'C:/Program Files/Thorlabs/Kinesis'

    # rather than reading the EquipmentRecord from a database we can create it manually
    record = EquipmentRecord(
        manufacturer='Thorlabs',
        model='KST101',
        serial= sn,  # update the serial number for your KST101
        connection=ConnectionRecord(
            backend=Backend.MSL,
            address='SDK::Thorlabs.MotionControl.KCube.StepperMotor.dll',
        ),
    )
     # avoid the FT_DeviceNotFound error
    MotionControl.build_device_list()

       # connect to the KCube Stepper Motor
    motor = record.connect()
    #print('Connected to {}'.format(motor))

    # load the configuration settings (so that we can use the get_real_value_from_device_unit() method)
    motor.load_settings()

    # start polling at 200 ms
    motor.start_polling(200)

    return motor


def wait( motor ):
    motor.clear_message_queue()
    while True:
        status = motor.convert_message(*motor.wait_for_message())['id']
        if status == 'Homed' or status == 'Moved':
            break

        if verbose:
            position = motor.get_position()
            real = motor.get_real_value_from_device_unit(position, 'DISTANCE')
            print('  at position {} [device units] {:.3f} [real-world units]'.format(position, real))

def close( motor ):
    motor.stop_polling()
    motor.disconnect()


# this "if" statement is used so that Sphinx does not execute this script when the docs are being built
if __name__ == '__main__':

    if len(sys.argv) >= 2 and sys.argv[1].upper() == "STATUS":
        showMotorStatus()
        sys.exit()
    
    if len(sys.argv) < 2:
        ShowHelp()
        sys.exit()

    theAxisToMoveSN = None
   
    if sys.argv[1].upper() == 'X':
        theAxisToMoveSN = motorX

    elif sys.argv[1].upper() == 'Y':
        theAxisToMoveSN = motorY


    elif sys.argv[1].upper() == 'Z':
        theAxisToMoveSN = motorZ
    else:
        ShowHelp()
        sys.exit()
        

    
    if len(sys.argv) == 4 and sys.argv[3].upper() == "-VERBOSE":
        verbose = 1

    pos = float(sys.argv[2])
   
    motor = setup(theAxisToMoveSN)
    
    move(motor,pos)

    ## home the device
    #print('Homing...')
    #motor.home()
   # wait(motor)
    #print('Homing done. At position {} [device units]'.format(motor.get_position()))

    

    # move by a relative amount of -5000
    #print('Moving by -5000...')
    #motor.move_relative(-5000)
    #wait()
    #print('Moving done. At position {} [device units]'.format(motor.get_position()))

    # jog forwards
    #print('Jogging forwards by {} [device units]'.format(motor.get_jog_step_size()))
    #motor.move_jog('Forwards')
    #wait()
    #print('Jogging done. At position {} [device units]'.format(motor.get_position()))

    # stop polling and close the connection
    close( motor )
    
    # you can access the default settings for the motor to pass to the set_*() methods
    #print('\nThe default motor settings are:')
    #pprint(motor.settings)
