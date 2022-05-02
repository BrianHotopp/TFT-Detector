import argparse
from pathlib import Path
import xml.etree.ElementTree 
# this file ensures that the data folder is in a consistent state
if __name__ == "__main__":
    # this program takes several command line arguments
    # the first is the folder containing the verified images
    # the second is the folder containing the verified labels
    # it walks through the verified images and labels and ensures that the file names are ordered 1-n
    # it also ensures that the corresponding label file exists for each image

    parser = argparse.ArgumentParser(description='Move verified images and labels to the data folder.')
    # optional argument to specify the folder containing the verified images; defaults to ../clean_data/images if not specified
    parser.add_argument('-i', '--images', help='Folder containing the verified images.')
    # optional argument to specify the folder containing the verified labels; defaults to ../clean_data/labels if not specified
    parser.add_argument('-l', '--labels', help='Folder containing the verified labels.')

    args = parser.parse_args()
    here = Path(__file__).parent
    if args.images:
        images_folder = args.images
    else:
        images_folder = here/'../clean_data/images'
    if args.labels:
        labels_folder = args.labels
    else:
        labels_folder = here/'../clean_data/labels'

    # err if the source folders don't exist
    if not images_folder.exists():
        raise FileNotFoundError(f'{images_folder} does not exist')
    if not labels_folder.exists():
        raise FileNotFoundError(f'{labels_folder} does not exist')

    # get count of images and labels
    image_count = len(list(images_folder.glob('*.png')))
    label_count = len(list(labels_folder.glob('*.xml')))
    # check that there is a corresponding label file for each image in the source folder
    for image_file in images_folder.glob('*.png'):
        # get the image file name without the extension
        image_name = image_file.stem
        # get the label file name
        label_file = labels_folder/f'{image_name}.xml'
        # check that the label file exists
        if not label_file.exists():
            raise FileNotFoundError(f'{label_file} does not exist for image {image_name}.png. There must be a label in the source labels folder for each image in the source images folder.')
    # check that the image and label counts are equal
    if image_count != label_count:
        raise Exception(f'{image_count} images found in {images_folder} but {label_count} labels found in {labels_folder}. The number of images must equal the number of labels.')
    # rename the images and labels to 0-(n-1)
    image_names = list(images_folder.glob('*.png'))
    label_names = list(labels_folder.glob('*.xml'))
    # sort the image and label names
    image_names.sort(key=lambda x: int(x.stem))
    label_names.sort(key=lambda x: int(x.stem))
    for i in range(image_count):
        image_names[i].rename(images_folder/f'{i}.png')
        label_names[i].rename(labels_folder/f'{i}.xml')

    # repair the xml files      
    # fix the folder file and path in the xml file
    for label_file in labels_folder.glob('*.xml'):
        # get the image file
        image_file = images_folder/f'{label_file.stem}.png'
        # get the xml tree
        tree = xml.etree.ElementTree.parse(label_file)
        # get the root element
        root = tree.getroot()
        # get the folder element
        folder = root.find('folder')
        # set the folder to the folder containing the image 
        folder.text = image_file.parent.name
        # get the filename element
        filename = root.find('filename')
        # set the filename to the image file name
        filename.text = image_file.name
        # get the path element
        path = root.find('path')
        # set the path to the image file name
        path.text = image_file.resolve().as_posix()
        # write the xml file
        tree.write(label_file)

        
        



