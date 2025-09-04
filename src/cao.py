from cadquery import exporters ,importers

def convert_step_to_stl(step_file):
    shape = importers.importStep(step_file)
    stl_file = step_file.rsplit('.', 1)[0] + '.stl'
    exporters.export(shape, stl_file)
    print(f"Converted {step_file} to {stl_file}")
    return stl_file


def get_bounding_box_dimensions(step_file):
    shape = importers.importStep(step_file)
    bbox = shape.val().BoundingBox()
    length = bbox.xlen
    width = bbox.ylen
    height = bbox.zlen
    return length, width, height
