import numpy as np
import time

# This is where you can build a decision tree for determining throttle, brake and steer 
# commands based on the output of the perception_step() function
def angle_difference(initial, final):
    difference = final - initial
    if(difference < -180): 
        difference += 360
    if(difference > 180): 
        difference -= 360
    return difference
    
def decision_step(Rover):

    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!

    # Example:
    # Check if we have vision data to make decisions with
    if Rover.nav_angles is not None:
        # Check for Rover.mode status
        if Rover.mode == 'forward': 
            # Check the extent of navigable terrain
            # Rover.stall_timer +=1

            # if Rover.stall_timer > Rover.stall_timeout:#check to see if rover has stalled
                # Rover.stall_yaw = Rover.yaw#angle at which it is stalled
                # # Set mode to "stop" and hit the brakes!
                # Rover.throttle = 0
                # # Set brake to stored brake value
                # Rover.brake = Rover.brake_set
                # Rover.steer = 0
                # Rover.mode = 'stop'
                
            # elif Rover.vel>=0.2: #shut stall timer off once speed reached
                # Rover.stall_timer =0
            if Rover.vel > 0.2:
                Rover.stall_timer = time.time()#continually reset the stall clock so long as speed is greater than x
            if sum(Rover.nav_dists<50) >= Rover.stop_forward:  
                if (Rover.vel<0.2) & (time.time() - Rover.stall_timer > Rover.stall_timeout):
                    #then rover is probably stalled on rocks
                    if Rover.stalled == False:
                        Rover.stall_yaw = Rover.yaw #when initially stalled get yaw angle
                    Rover.stalled = True
                    Rover.throttle = 0
                    Rover.brake = 0
                    Rover.mode = 'stop'
                    
                # If mode is forward, navigable terrain looks good 
                # and velocity is below max, then throttle 
                elif Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                else: # Else coast
                    Rover.throttle = 0
                Rover.brake = 0
                # Set steering to average angle clipped to the range +/- 15
                Rover.steer = np.clip(np.average(Rover.nav_angles,weights = 1/Rover.nav_dists) * 180/np.pi, -15, 15)#+5 to favor steering left
            # If there's a lack of navigable terrain pixels then go to 'stop' mode
            elif sum(Rover.nav_dists<50) < Rover.stop_forward:
                    # Set mode to "stop" and hit the brakes!
                    Rover.throttle = 0
                    # Set brake to stored brake value
                    Rover.brake = Rover.brake_set
                    Rover.steer = 0
                    Rover.mode = 'stop'

        # If we're already in "stop" mode then make different decisions
        elif Rover.mode == 'stop':
            # If we're in stop mode but still moving keep braking
            # if Rover.stall_timer > Rover.stall_timeout: #is stalled
                # Rover.throttle = 0
                # # Release the brake to allow turning
                # Rover.brake = 0
                # # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                # Rover.steer = +15 # Could be more clever here about which way to turn
                # if(angle_difference(Rover.stall_yaw,Rover.yaw)>45):
                    # Rover.stall_timer=0
            if np.absolute(Rover.vel) > 0.2:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            # If we're not moving (vel < 0.2) then do something else
            elif np.absolute(Rover.vel) <= 0.2:
                # Now we're stopped and we have vision data to see if there's a path forward
                # Release the brake
                Rover.brake = 0
                if Rover.stalled == True:
                    if np.absolute(angle_difference(Rover.stall_yaw,Rover.yaw))<45:
                        #turn until the rover has rotated by x degrees
                        Rover.throttle = 0
                        Rover.steer = -15
                    else:
                        #once it has turned by x degrees set mode to 'stop' and stalled to false
                        Rover.stalled = False
                elif Rover.stalled ==False:
                    if sum(Rover.nav_dists<50) < Rover.go_forward:
                        Rover.throttle = 0
                        
                        # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                        Rover.steer = -15 # Could be more clever here about which way to turn
                    # If we're stopped but see sufficient navigable terrain in front then go!
                    if sum(Rover.nav_dists<50) >= Rover.go_forward:
                        # Set throttle back to stored value
                        Rover.throttle = Rover.throttle_set
                        
                        # Set steer to mean angle
                        Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                        Rover.mode = 'forward'
                        Rover.stall_timer = time.time()#whenever state changes to forward start stall timer
                    
    # Just to make the rover do something 
    # even if no modifications have been made to the code
    else:
        Rover.throttle = Rover.throttle_set
        Rover.steer = 0
        Rover.brake = 0
        
    # If in a state where want to pickup a rock send pickup command
    if Rover.near_sample and Rover.vel == 0 and not Rover.picking_up:
        Rover.send_pickup = True
    
    return Rover

