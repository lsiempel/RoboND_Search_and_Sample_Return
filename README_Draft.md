## Project: Search and Sample Return
*Deliverables completed by Lewis Siempelkamp*

---


**The goals / steps of this project were the following:**  

**Training / Calibration**  

* The simulator was downloaded and sample data was recorded in "Training Mode"
* Test out the functions in the Jupyter Notebook provided
* Add functions to detect obstacles and samples of interest (golden rocks)
* Fill in the `process_image()` function with the appropriate image processing steps (perspective transform, color threshold etc.) to get from raw images to a map.  The `output_image` created in this step demonstrates the performance of my mapping pipeline.
* Use `moviepy` to process the images in your saved dataset with the `process_image()` function.  Include the video you produce as part of your submission.

**Autonomous Navigation / Mapping**

* Fill in the `perception_step()` function within the `perception.py` script with the appropriate image processing functions to create a map and update `Rover()` data (similar to what you did with `process_image()` in the notebook). 
* Fill in the `decision_step()` function within the `decision.py` script with conditional statements that take into consideration the outputs of the `perception_step()` in deciding how to issue throttle, brake and steering commands. 
* Iterate on your perception and decision function until your rover does a reasonable (need to define metric) job of navigating and mapping.  

[//]: # (Image References)

[image1]: ./output/input_raw.jpg
[image2]: ./output/output_nav_thresh.jpg
[image3]: ./calibration_images/example_rock1.jpg
[image4]: ./output/rock_threshed.jpg 

## [Rubric](https://review.udacity.com/#!/rubrics/916/view) Points
### Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---
### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  

You're reading it!

### Notebook Analysis

The Jupyter Notebook used for working out the "Perception Steps" of the Rover can be seen in the [Code Folder](code/)

Note that although the Jupyter Notebook was used to outline the perception.py script function content, variable names, and color thresholding values may differ slightly between the script in the notebook and the perception.py script. 

#### 1. Run the functions provided in the notebook on test images (first with the test data provided, next on data you have recorded). Add/modify functions to allow for color selection of obstacles and rock samples.

Functions to perform color-selection of the navigable terrain, obstacles, and golden rock samples can be seen under the **Color Threshholding** Heading in the [Jupyter Notebook](code/Rover_Project_Test_Notebook.ipynb).

The functions are called nav_color_thresh2, obs_color_thresh2, and rock_color_thresh respectively. The '2' in the function name reflects the fact that I played with multiple approaches at performing high fidelity color thresholding: RGB thresholding and HSV thresholding

In my Perception.py script I opted to use the HSV method for all threshhgolding functions because it allowed for cleaner color selection particularily for the golden rock samples.

The inputs/outputs to the color thresholding functions might look something like this:

Navigable Terrain:

![alt_text][image1]
![alt_text][image2]

Golden Rock Sample:

![alt text][image3]
![alt_text][image4]

#### 1. Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result. 

Under the Heading **Write a function to process images** in the Jupyter Notebook a cell block contains a script with a series of steps that take an input image, perform some processing steps, and from it extract usable data abpout the nearby terrain which is then overlaid into a 3-channel array representing the worldmap.

The steps taken are roughly as follows:
* Apply a perspective transform on the image to warp it from the First-Person-View to a Top-Down-View
* Threshhold the warped image to create three masks: 1 isolating the navigable terrain, 1 isolating the obstacles, and 1 isolating the golden rock samples.
* Convert the top down masks into 'Rover-Centric' arrays that assign each 'pixel' of terrain info to an x-y coord relative to the Rover
* Translate/Rotate the terrain info from Relative 'Rover-Centric' coords to Absolute 'Worldmap' coords.
* Add/subtract the terrain pixels to the in-progress worldmap array: navigable terrain pixels are added to the blue channel, obstacles are added to the red channel, and rock sample pixels are cleaned up and added as a signle point to the green channel. 
* overlay the newly generated worldmap onto 'known' total worldmap for comparison

A video showing a collage of pre and post processed images can be seen in the [test output video](output/test_mapping.mp4).


### Autonomous Navigation and Mapping

#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.

The modified perception.py and decision.py files can be seen in the [Code Folder](code/).

**perception_step(Rover)**
The addtions/modifications to my perception_step are as follows:
* My perspective_transform() returns a binary mask of the transformed area in addition to the tranformed image to aid with the subsequent thresholding steps
* Rather then creating a separate function to threshhold for obstacles I have taken the inverse of the navigable_threshold multiplied by the perspective transform mask
* A 'weight' is generated for each frame from the Rover based on a normal (gaussian) distribution centred about Roll,Yaw = 0. A weight of 1 is generated for Roll,Pitch = 0 but sharply drops to 0 for Roll,Pitch that deviate from 0. This weight is then applied to the terrain pixels causing frames captured in which the Rover is not flat to be largely discounted in an attempt to improve terrain fidelity.
* I foudn it convenient to add/subtract/clip terrain pixels from the worldmap within the perception_step causing the generated worldmap to hopefully converge to a higher fidelity with subsequent frames of the same region. 
* The rock pixels are cleaned up by only selecting the nearest rock pixel in each frame to represent a sample.
* In addition to updating the worldmap, an array of the angle and distance to each navigable pixel in each frame is returned for subsequent use.

**decision_step(Rover)**
My decision step is only slightly modified from the provided template as I found I achieved passable results with the original once my perception step was tuned well.

In fact the only change I made was to add the smarts to deal with becoming stuck on the 'boulder' obstacles scattered in various open areas. This was done by adding a stall timer that kept track of how long the throttle was activated without the velocity increasing beyong some low threshold. If the velocity did not increase beyond the threshold in a certain time span then the Rover decided it was stalled and executes a 45 degree turn.

Other from the stall condition smarts and actions the decision tree was left alone with very good results. I played with biasing the turning in favor of one direction more than the other to cause the Rover to crawl along one edge of the terrain but felt it was unneccesary as I am able to consistently map out the majority of the terrain without issue with the stall timer implementation alone.


#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  

I ran my Rover Simulator with the following settings:

Windowed

Screen Resolution: 1024x768

Graphics Quality: Good

FPS: ~ 24

In Autonomous mode with my drive_rover.py and associated scripts running in the background, my Rover consistently maps a significant portion of the map at ~85% total terrain fidelity.

My rover identifies all samples, though, does not collect them.

If I were to continue tackling this project I would improve the decision_step() function to give the Rover more smarts for more efficiently traversing the generated worldmap and implementing the collection of samples. To ensure a higher percentage of the worldmap is traversed more quickly with less repetition the Rover could be made to note intersections in some fashion by weigthing its turning towards less counted terrain pixels.

A video output of the simulation running autonmously can be seen in the generated [simulation video](output/Rover Simulator 2017-12-27 1_30_19 AM)

