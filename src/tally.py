def get_labels(labels_file_name) -> dict:
    """
    Get the labels of the set 6 units.
    Args:
        labels_file_name: the filename to read from
    Returns:
        dictionary of set 6 units parsed
    """
    # read set 6 units in
    SET_6_UNITS = dict()
    with open(labels_file_name) as classes_file_handle:
        for line in classes_file_handle.readlines():
            unit_name, abbreviated_name = [x.strip() for x in line.split(",")]
            SET_6_UNITS[unit_name] = abbreviated_name
    return SET_6_UNITS
if __name__ == '__main__':
    import os
    import xml.etree.ElementTree as ET
    import argparse
    import glob
    import shutil
    import sys
    import re
    from pathlib import Path

    # construct the argument parser
    ap = argparse.ArgumentParser()
    ap.add_argument("-l", "--labels", required=False, help="path to the labels folder")
    ap.add_argument("-i", "--images", required=False, help="path to the images folder")
    # argument for verbosity
    ap.add_argument("-v", "--verbose", action="store_true", help="increase output verbosity")

    # parse the arguments
    args = vars(ap.parse_args())

    here = Path(__file__).parent
 
    # if the labels folder is not specified, use the default(clean_data\labels)
    if args["labels"]:
        labels_folder = args["labels"]
    else:
        labels_folder = here/'../clean_data/labels'
    # if the images folder is not specified, use the default(clean_data\screenshots)
    if args["images"]:
        images_folder = args["images"]
    else:
        images_folder = here/'../clean_data/images'
    # if the verbosity flag was set, print out the arguments
    if args["verbose"]:
        print("[INFO] labels folder: {}".format(labels_folder))
        print("[INFO] images folder: {}".format(images_folder))
    # open the csv of units to get the keys for the dict
    lp = here/'../clean_data/static/set6_classes.csv'
    units = get_labels(lp).values()
    # create a dict to store the counts of each unit type
    unit_counts = {}
    for unit in units:
        unit_counts[unit] = 0
    # get the list of label files
    label_files = glob.glob(str(labels_folder) + '/*.xml')
    # loop through the label files
    for label_file in label_files:
        # get the label file name without the extension
        label_name = Path(label_file).stem
        # get the image file name
        image_file = images_folder/f'{label_name}.png'
        # check that the image file exists
        if not image_file.exists():
            raise FileNotFoundError(f'{image_file} does not exist for label {label_name}.xml. There must be an image in the source images folder for each label in the source labels folder.')
        # open the label file
        tree = ET.parse(label_file)
        root = tree.getroot()
        # get the units that occur in the label file
        units = root.findall('object')
        # loop through the units
        for unit in units:
            # get the name of the unit
            unit_name = unit.find('name').text
            # increment the count of the unit type
            unit_counts[unit_name] += 1
    # print the counts of each unit type (only in verbose mode)
    if args["verbose"]:

        for unit in unit_counts:
            print(f'{unit}: {unit_counts[unit]}')
    # get the total number of units
    total_units = sum(unit_counts.values())
    # print the total number of units
    print(f'Total units: {total_units}')
    # get the total number of images
    total_images = len(label_files)
    # print the total number of images
    print(f'Total images: {total_images}')
    # get the average number of units per image
    avg_units = total_units/total_images
    # print the average number of units per image
    print(f'Average units per image: {avg_units}')
    # get the 10 units that occur the least
    least_units = sorted(unit_counts.items(), key=lambda x: x[1])[:10]
    # print the 10 units that occur the least using pretty formatting
    print('\n10 least occurring units:')
    for unit in least_units:
        print(f'{unit[0]}: {unit[1]}')
    # units that occur less than 100 times
    print('\nUnits that occur less than 100 times:')
    c = 0
    for unit in unit_counts:
        if unit_counts[unit] < 100:
            print(f'{unit}: {unit_counts[unit]}')
            c += 1
    # size of the units dict
    size = len(unit_counts)
    # percentage left to find
    left = 100 - (c/size)*100
    print(f'{left}% Of units occur less than 100 times')







