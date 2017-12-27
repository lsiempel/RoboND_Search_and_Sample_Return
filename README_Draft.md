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
[image3]: ./output/rock_input.jpg 
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
And another! 

![alt text][image2]
### Autonomous Navigation and Mapping

#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.


#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  

**Note: running the simulator with different choices of resolution and graphics quality may produce different results, particularly on different machines!  Make a note of your simulator settings (resolution and graphics quality set on launch) and frames per second (FPS output to terminal by `drive_rover.py`) in your writeup when you submit the project so your reviewer can reproduce your results.**

Here I'll talk about the approach I took, what techniques I used, what worked and why, where the pipeline might fail and how I might improve it if I were going to pursue this project further.  



![alt text][image3]


