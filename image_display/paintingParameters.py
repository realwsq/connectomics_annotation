# image_display.paintingParameters.py

class Painting_Parameters(object):
    label_transparency = 0.4
    special_cell_boundary_visible = True
    common_cell_boundary_visible = True
    special_cell_boundary_opacity = 1.0
    common_cell_boundary_opacity = 0.5
    draw_stroke = 3
    membrane_erase_stroke_width = 1


# singleton
painting_parameters = Painting_Parameters()