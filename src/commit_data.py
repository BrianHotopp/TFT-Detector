import argparse
from pathlib import Path
import xml.etree.ElementTree 
# this file moves verified images and labels to the data folder
# the data folder is then used to train the model
if __name__ == "__main__":
    # the program takes several command line arguments
    # the first is the folder containing the verified images
    # the second is the folder containing the verified labels
    # the third is the folder to move the verified .xml label files to (defaults to ../clean_data/labels)
    # the fourth is the folder to move the verified images to (defaults to ../clean_data/images)
    parser = argparse.ArgumentParser(description='Move verified images and labels to the data folder.')
    # optional argument to specify the folder containing the verified images; defaults to ../screenshots if not specified
    parser.add_argument('-i', '--images', help='Folder containing the verified images.')
    # optional argument to specify the folder containing the verified labels; defaults to ../labels if not specified
    parser.add_argument('-l', '--labels', help='Folder containing the verified labels.')
    # optional argument to specify the folder to move the verified images to; defaults to ../clean_data/images if not specified
    parser.add_argument('-di', '--commit-images-to', help='Folder to move the verified images to.')
    # optional argument to specify the folder to move the verified .xml label files to; defaults to ../clean_data/labels if not specified
    parser.add_argument('-dl', '--commit-labels-to', help='Folder to move the verified .xml label files to.')

    args = parser.parse_args()
    here = Path(__file__).parent
    if args.images:
        images_folder = args.images
    else:
        images_folder = here/'../screenshots'
    if args.labels:
        labels_folder = args.labels
    else:
        labels_folder = here/'../labels'
    if args.commit_labels_to:
        commit_labels_to = args.commit_labels_to
    else:
        commit_labels_to = here/'../clean_data/labels'
    if args.commit_images_to:
        commit_images_to = args.commit_images_to
    else:
        commit_images_to = here/'../clean_data/images'
    # err if the source folders don't exist
    if not images_folder.exists():
        raise FileNotFoundError(f'{images_folder} does not exist')
    if not labels_folder.exists():
        raise FileNotFoundError(f'{labels_folder} does not exist')
    # make sure the destination folders exist
    commit_labels_to.mkdir(parents=True, exist_ok=True)
    commit_images_to.mkdir(parents=True, exist_ok=True)
    # check that there is a corresponding label file for each image in the source folder
    for image_file in images_folder.glob('*.png'):
        # get the image file name without the extension
        image_name = image_file.stem
        # get the label file name
        label_file = labels_folder/f'{image_name}.xml'
        # check that the label file exists
        if not label_file.exists():
            raise FileNotFoundError(f'{label_file} does not exist for image {image_name}.png. There must be a label in the source labels folder for each image in the source images folder.')

    # gather all label files and image files
    label_files = list(labels_folder.glob('*.xml'))
    image_files = list(images_folder.glob('*.png')) 
    # collect the next len(label_files) available file names for the images and labels
    # get the next available file name for the images
    next_available_l= len(list(commit_labels_to.glob('*.xml')))
    next_available_i= len(list(commit_images_to.glob('*.png')))
    assert(next_available_i == next_available_l)
    new_l_stems = [f'{next_available_l+i}' for i in range(len(label_files))]
    new_i_stems = [f'{next_available_i+i}' for i in range(len(image_files))]
    # construct the new file names for the labels and images
    new_l_files = [commit_labels_to/f'{new_l_stem}.xml' for new_l_stem in new_l_stems]
    new_i_files = [commit_images_to/f'{new_i_stem}.png' for new_i_stem in new_i_stems]
    # report the changes to the user
    print('The following files will be moved:')
    for old_label_file, new_label_file in zip(label_files, new_l_files):
        print(f'{old_label_file} -> {new_label_file}')
    for old_image_file, new_image_file in zip(image_files, new_i_files):
        print(f'{old_image_file} -> {new_image_file}')
    # ask the user if they want to continue
    answer = input('Continue? (y/n) ')
    if answer.lower() == 'y':
        # move the files
        for label_file, new_label_file in zip(label_files, new_l_files):
            # change the folder file and path in the xml file to reflect the new location
            try:
                tree = xml.etree.ElementTree.parse(label_file)
            except xml.etree.ElementTree.ParseError:
                print(f'{label_file} is not a valid xml file. Skipping.')
                raise FileNotFoundError(f'{label_file} is not a valid xml file. Skipping.')
            root = tree.getroot()
            folder = root.find('folder')
            folder.text = commit_labels_to.name 
            for filename in root.findall('filename'):
                filename.text = str(new_label_file.name)
            # new path
            for path in root.findall('path'):
                path.text = str(new_label_file.resolve().parent)
            tree.write(label_file)
            label_file.rename(str(new_label_file))

        for image_file, new_image_file in zip(image_files, new_i_files):
            image_file.rename(new_image_file)
        print('Files moved successfully.')
        if len(list(commit_labels_to.glob('*.xml'))) != len(list(commit_images_to.glob('*.png'))):
            raise ValueError('The number of label files and image files in the destination folders must be the same. Label scheme might be corrputed.')
        n = len(list(commit_labels_to.glob('*.xml')))
        # check that the file names are in order
        for i in range(n):
            if not commit_labels_to.glob(f'{i}.xml') or not commit_images_to.glob(f'{i}.png'):
                raise ValueError('The file names in the destination folders are not in order. Label scheme might be corrputed.')
    else:
        print('Files not moved.')







