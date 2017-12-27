import numpy as np
import cv2

# Identify pixels above the threshold
# Threshold of RGB > 160 does a nice job of identifying ground pixels only
def nav_color_thresh(img, value=150):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:,:,0]) #convert to hsv 
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    #modify the upper and lower bounds of the filter
    lower = np.array([0,0,value])
    upper = np.array([179,255,255])
    #create mask
    mask = cv2.inRange(hsv, lower, upper)
    #convert mask to binary
    truth = mask[:,:]>0
    color_select[truth] = 1
    # Return the binary image
    return color_select
def rock_color_thresh(img):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:,:,0])
    #convert to hsv
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    #modify the upper and lower bounds of the filter
    lower_yellow = np.array([20,128,128])
    upper_yellow = np.array([40,255,255])
    #create mask
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    #convert mask to binary
    truth = mask[:,:]>0
    color_select[truth] = 1
    # Return the binary image
    return color_select
    
def invert_thresh(img):
    inverse = ~img
    return inverse
    
# Define a function to convert from image coords to rover coords
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = -(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[1]/2 ).astype(np.float)
    return x_pixel, y_pixel


# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles

# Define a function to map rover space pixels to world space
def rotate_pix(xpix, ypix, yaw):
    # Convert yaw to radians
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = (xpix * np.cos(yaw_rad)) - (ypix * np.sin(yaw_rad))                            
    ypix_rotated = (xpix * np.sin(yaw_rad)) + (ypix * np.cos(yaw_rad))
    # Return the result  
    return xpix_rotated, ypix_rotated

def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale): 
    # Apply a scaling and a translation
    xpix_translated = (xpix_rot / scale) + xpos
    ypix_translated = (ypix_rot / scale) + ypos
    # Return the result  
    return xpix_translated, ypix_translated


# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world

# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):       
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    #create mask of transformed area
    mask = cv2.warpPerspective(np.ones_like(img[:,:,0]), M, (img.shape[1], img.shape[0]))# keep same size as input image
    #return the warped image and associated mask
    return warped, mask

#weighted gaussian filter centred on mu
def gaussian(x,mu=0,sig = 1):
    if x>180: #centre x about 0
        x = -1*(360 - x)
    return np.exp(-np.power(x-mu,2.)/(2*np.power(sig,2.)))

# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # Perform perception steps to update Rover()
    # TODO: 
    # NOTE: camera image is coming to you in Rover.img
    # 1) Define source and destination points for perspective transform
    # The destination box will be 2*dst_size on each side
    dst_size = 5 
    # Set a bottom offset to account for the fact that the bottom of the image 
    bottom_offset = 6
    source = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
    image = Rover.img
    destination = np.float32([[image.shape[1]/2 - dst_size, image.shape[0] - bottom_offset],
                  [image.shape[1]/2 + dst_size, image.shape[0] - bottom_offset],
                  [image.shape[1]/2 + dst_size, image.shape[0] - 2*dst_size - bottom_offset], 
                  [image.shape[1]/2 - dst_size, image.shape[0] - 2*dst_size - bottom_offset],
                  ])
    # 2) Apply perspective transform
    warped, mask = perspect_transform(Rover.img, source, destination)
    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    nav_threshed = nav_color_thresh(warped)
        #invert and apply mask to nav_threshed to get obs_threshed
    obs_threshed = np.absolute(np.float32(nav_threshed)-1)*mask
    rock_threshed = rock_color_thresh(warped)
    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
    Rover.vision_image[:,:,0] = obs_threshed*255
    Rover.vision_image[:,:,1] = rock_threshed*255
    Rover.vision_image[:,:,2] = nav_threshed*255
    # 5) Convert thresholded image pixel values to rover-centric coords
    nav_xpix, nav_ypix = rover_coords(nav_threshed)
    obs_xpix, obs_ypix = rover_coords(obs_threshed)
    rock_xpix, rock_ypix = rover_coords(rock_threshed)
    # 6) Convert rover-centric pixel values to world coords
    xpos = Rover.pos[0]
    ypos = Rover.pos[1]
    yaw = Rover.yaw
    world_size = Rover.worldmap.shape[0]
    scale = 2*dst_size
    nav_x_world, nav_y_world = pix_to_world(nav_xpix, nav_ypix, xpos, ypos, yaw, world_size, scale)
    obs_x_world, obs_y_world = pix_to_world(obs_xpix, obs_ypix, xpos, ypos, yaw, world_size, scale)
    rock_x_world, rock_y_world = pix_to_world(rock_xpix, rock_ypix, xpos, ypos, yaw, world_size, scale)
    #7 Update worldmap (to be displayed on right side of screen)
        #populate worldmap array with navigable and obstacle information - 
        #adding and subtracting in a weighted manner to cause a trend towards higher fidelity
    weight = gaussian(Rover.roll)*gaussian(Rover.pitch)#weighting of worldmap points significantly reduced by pitch roll being offcentre
    #weight = 1
    Rover.worldmap[nav_y_world, nav_x_world, 2] += 1*weight #add navigable pixels to blue worldmap
    Rover.worldmap[nav_y_world, nav_x_world, 0] -= 1*weight #subtract navigable pixels from red worldmap
    Rover.worldmap[obs_y_world, obs_x_world, 0] += 1*weight #add obstacle pixels to red worldmaps
    Rover.worldmap[obs_y_world, obs_x_world, 2] -= 1*weight #subtract obstacle pixels from blue worldmap
        #include rocks if found
    if rock_threshed.any():
        rock_dist, rock_ang = to_polar_coords(rock_xpix, rock_ypix)
            #set the rock position on the worldmap to be a single pixel closest to the rover
        rock_idx = np.argmin(rock_dist)#get the index of the closest rock pixels
        rock_xcen = rock_x_world[rock_idx]
        rock_ycen = rock_y_world[rock_idx]
            #update worldmap img
        Rover.worldmap[rock_ycen, rock_xcen, 1] = 255
    #clip the worldmap rgb values to be within 0-255
    Rover.worldmap = np.clip(Rover.worldmap[:,:,:],0,255)
    # 8) Convert rover-centric pixel positions to polar coordinates
    nav_dist, nav_ang = to_polar_coords(nav_xpix, nav_ypix)
    #Rover.nav_angles = np.average(nav_ang*180/pi, weights = 1/nav_dist)
    Rover.nav_angles = nav_ang
    Rover.nav_dists = nav_dist
    return Rover