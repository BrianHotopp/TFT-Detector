# this script automatically labels the images in the folder using an existing model
# the data will then be corrected by the user and can be used to train the model 

from re import L
import detecto
import detecto.core
import cv2
import torchvision.ops as ops
import numpy as np
import argparse
from pathlib import Path
def get_labels(labels_file_path) -> dict:
        """
        Get the labels of the units in the passed in file
        Args:
            labels_file_name: the filename to read from
        Returns:
            dictionary of units {unit_full_name: unit_abbreviation}
        """
        # read set 6 units in
        SET_6_UNITS = dict()
        with open(labels_file_path) as classes_file_handle:
            for line in classes_file_handle.readlines():
                unit_name, abbreviated_name = [x.strip() for x in line.split(",")]
                SET_6_UNITS[unit_name] = abbreviated_name
        return SET_6_UNITS
if __name__ == "__main__":
    # the program takes several command line arguments
    # the first is the folder to save the .xml label files to (defaults to ../labels)
    # the second is the folder where the images to label are located (defaults to ../screenshots)
    # the third is the path to the model to use (defaults to ../models/set6_best_model.pth)
    # the fourth is the path to the label file to use (defaults to ../labels/set6_labels.txt)
    parser = argparse.ArgumentParser(description='Label the League of Legends screenshots.')
    # optional argument to specify the folder to save the .xml label files to; defaults to ../labels if not specified
    parser.add_argument('-l', '--labels', help='Folder to save the .xml label files to.')
    # optional argument to specify the folder to save the images to; defaults to ../screenshots if not specified
    parser.add_argument('-i', '--images', help='Folder containing the images.')
    # optional argument to specify the path to the model to use; defaults to ../models/set6_best_model.pth if not specified
    parser.add_argument('-m', '--model', help='Path to the model to use.')
    # optional argument to specify the path to the label file to use; defaults to ../labels/set6_labels.txt if not specified
    parser.add_argument('-f', '--labels_file', help='Path to the label file to use.')

    args = parser.parse_args()
    here = Path(__file__).parent
    if args.labels:
        labels_folder = args.labels
    else:
        labels_folder = here/'../labels'
    if args.images:
        images_folder = args.images
    else:
        images_folder = here/'../screenshots'
    if args.model:
        model_path = args.model
    else:
        model_path = here/'../models/set6_best_model.pth'
    if args.labels_file:
        labels_file = args.labels_file
    else:
        labels_file = here/'../models/set6_labels.csv'
    # make sure the folders exist
    labels_folder.mkdir(parents=True, exist_ok=True)
    images_folder.mkdir(parents=True, exist_ok=True)
    # raise an error if the model file doesn't exist
    if not model_path.exists():
        raise Exception("Model file not found!" + str(model_path))
    # raise an error if the label file doesn't exist
    if not labels_file.exists():
        raise Exception("Label file not found!" + str(labels_file))
    # get the labels
    l_d = get_labels(labels_file)
    l = list(l_d.values())
    # load the model from disk
    model = detecto.core.Model.load(model_path, l)
    # get the list of images to label
    images = list(images_folder.glob('*.png'))
    # loop through the images
    for image_path in images:
        # if the image is already labeled, skip it
        if image_path.with_suffix('.xml').exists():
            continue
        # load the image
        image = cv2.imread(str(image_path))
        # get the labels, bounding boxes, and scores for the objects in the image
        labels, boxes, scores = model.predict(image)
        # perform non-maximum suppression on the bounding boxes
        kept_indices = ops.nms(boxes, scores, 0.5)
        # filter out the bounding boxes that were not kept
        labels = [labels[i] for i in kept_indices]
        boxes = boxes[kept_indices]
        scores = scores[kept_indices]
        # write an xml file for each image
        with open(str(labels_folder/image_path.stem) + '.xml', 'w') as f:
            f.write('<annotation>\n')
            f.write('\t<folder>{}</folder>\n'.format(image_path.parent.name))
            f.write('\t<filename>{}</filename>\n'.format(image_path.name))
            f.write('\t<path>{}</path>\n'.format(image_path))
            f.write('\t<source>\n')
            f.write('\t\t<database>Unknown</database>\n')
            f.write('\t</source>\n')
            f.write('\t<size>\n')
            f.write('\t\t<width>{}</width>\n'.format(image.shape[1]))
            f.write('\t\t<height>{}</height>\n'.format(image.shape[0]))
            f.write('\t\t<depth>{}</depth>\n'.format(image.shape[2]))
            f.write('\t</size>\n')
            f.write('\t<segmented>0</segmented>\n')
            for i in range(len(boxes)):
                # get the bounding box
                box = boxes[i]
                # get the label
                label = labels[i]
                # get the score
                score = scores[i]
                # write the bounding box to the xml file
                f.write('\t<object>\n')
                f.write('\t\t<name>{}</name>\n'.format(label))
                f.write('\t\t<pose>Unspecified</pose>\n')
                f.write('\t\t<truncated>0</truncated>\n')
                f.write('\t\t<difficult>0</difficult>\n')
                f.write('\t\t<bndbox>\n')
                f.write('\t\t\t<xmin>{}</xmin>\n'.format(int(box[0])))
                f.write('\t\t\t<ymin>{}</ymin>\n'.format(int(box[1])))
                f.write('\t\t\t<xmax>{}</xmax>\n'.format(int(box[2])))
                f.write('\t\t\t<ymax>{}</ymax>\n'.format(int(box[3])))
                f.write('\t\t</bndbox>\n')
                #f.write('\t\t<score>{}</score>\n'.format(score))
                f.write('\t</object>\n')
            f.write('</annotation>\n')

    