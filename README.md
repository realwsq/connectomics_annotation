# Connectomics Annotation Prototype

An interactive prototype to help correct the cell labels predicted by state-of-the-art image segmentation algorithm.

### NEW UPDATES

### TODO
- [ ] change the contrast of the image
- [ ] correct the segmentation by skeleton
- [ ] When saving, export to a file type readable by amria/vtk

### Functions
- [x] Three views.
- [x] The color image of predicted segmentation is overlayed on the origin cube data. Different colors encode different labels.
- [x] resize the image view with *ctrl + mouse wheel* and use *middle mouse* to drag the image
- [x] scrolling through z planes with *mouse wheel*
- [x] quick location with *middle mouse click + ctrl*
- [x] permit adjustment of opacity of segmentation overlay (*there is a trackbar where you can adjust the opacity of label opacity%*)
- [x] **Membrane Edition**
- [x] permit control over appearance of outlines. 1. For the selected ID, 1.1 permit the user to toggle whether the outline is visible (*press 'q' to toggle or toggle off*), 1.2 provide control over outline opacity or thickness.(*there is a trackbar where you can adjust the selected cell's outline opacity%*) 2. For the all segments, 2.1 permit the user to toggle whether the outline is visible (*there is also a trackbar where you can adjust the selected cell's outline opacity%*) (*press 'w' to toggle or toggle off*)
- [x] **Merge Cells** *left mouse click* selects which segmentation ID will receive additional segments (updated as foreground), *right click* specifies which region (segment  ID) should be added to the outlined, selected ID. 
- [x] Extend outline of selected segmentation ID to all z planes
- [x] **Permit operations on arbitrary “selections” (areas within a single Z-plane).**  (detailed description can be seen below)
- [ ] Split cells
- [x] **Clear small fragments** by *pressing 'ctrl + c'*
- [x] **multiple-step undo.**
- [x] save the current annotation: *press 'ctrl + s'* and it will saved in annotation_history/ (timestamp is used to distinguish between different versions.)

## INSTRUCTIONS

### Membrane Edition

0. Use the drop-down menu to go to "membrane edition" mode. 
1. **Hold on left mouse** as pencil to add membrane / **Ctrl + hold on left mose** as eraser to remove membrane.
2. **Ctrl + D** flood-fill 

### Merging Cells

0. Use the drop-down menu to go to "merge (global)" mode. 
1. **Left mouse click** to select host ID. After selection, pixels of the same label will be highlighted. And foreground label will be updated.
2. **Right mouse click** to select other ID to be fused with the host. 
3. Press 'ctrl + b' can toggle back the previous "adding" 

**Special note**: 

* You can click right mouse continuously to add the current cell to the "receive" cell. 
* You can also press 'b' continuously to restore the'added' segmentation to its original ID step by step. (MAXIMUM 8 steps will be stored, means you can only recover 8 steps.)

### Arbitrary Selections:

1. belong to a particular user-specified ID

    1.1. **Use the drop-down menu to go to "edit one ID (slice)" mode. ** 
    
    1.2. **press left mouse + ctrl** to select specified ID which will be relabeld(it will be highlighted and the ID color will show in background)
    
    1.3. **Hold on right mouse** to draw an arbitrary region
    
    1.4. after right mouse up, selected region with particular ID will be highlighted
    
    1.5. change label by
    
        * **Left Mouse click + ctrl** on other region
        
        
2. all region

    2.1. **Use the drop-down menu to go to "edit all IDs (slice)" mode. ** 
    
    2.2. **Hold on right mouse** to draw an arbitrary region
    
    2.3. after right mouse up, all selected region will be highlighted
    
    2.4. change label by
    
        * **Left Mouse click + ctrl** on other region
    


**special note**:

* labels won't be propagated through z-plane
* when you are drawing, keep the mouse pressed

### Splitting:

0. **Press 'v'** to go to splitting mode. (or use the drop-down menu) 
1. **hold on shift and move the mouse (keep it pressed)** to draw an cut (there is a slider that you can adjust the width of the line you draw)
2. the program will test whether the cell is splitted (across z index), if it's splitted, will assign the splitted part a new id/color.

### Undo:
1. press 'ctrl + b'

**Special note**:

* MAXIMUM 8 steps will be stored, means you can only recover 8 steps.

### Adjustment of Visualization
1. permit adjustment of opacity of segmentation overlay 
    * there is a trackbar where you can adjust the opacity of label opacity%
2. permit control over appearance of outlines. 
    
    2.1. For the selected ID, 
        
        2.1.1 permit the user to toggle whether the outline is visible      
            * press 'q' to toggle or toggle off 
        2.1.2 provide control over outline opacity.
            * there is a trackbar where you can adjust the opacity of selected cell
    2.2. For the all segments, 
        
        2.2.1 permit the user to toggle whether the outline is visible 
            *press 'w' to toggle or toggle off
        2.2.2 provide control over outline opacity.
            * there is a trackbar where you can adjust the opacity of all cells

### scrolling through z planes ###

1.**mouse wheel**

2.**middle mouse click + ctrl** to quick locate

### Saving Annotations

1. press 'ctrl + s'

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 

### Prerequisites

* python2.7
* opencv2 
* numpy
* [pyqt4](http://pyqt.sourceforge.net/Docs/PyQt4/installation.html) 


### Running

console -> open an ipython console

in ipython:

* import sys
* sys.path.append('path to the code folder')
* import annotate_gui_connectomics
* annotate_gui_connectomics.main()

in GUI:

* select sem_file, seg_file and output_folder in file dialog
* close file dialog



## Authors

* Shuqi Wang - *Initial work* 

