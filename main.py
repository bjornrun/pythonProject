# NOTE: this code is generated by Github's copilot code generator and Kite's code generator with very little interaction by me
import os
import sys
from zipfile import ZipFile
from argparse import ArgumentParser, SUPPRESS
import logging as log
import re
import random

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(BASE_DIR)

CURR_DIR = os.getcwd()
print(CURR_DIR)

num_classes = 0
train_file_path = ""
valid_file_path = ""
name_file_path = ""
data_file_path = ""
data_data_path = ""
train_data_list = []
valid_data_list = []
current_task = 0
name_list = []


def build_argparser():
    parser = ArgumentParser(add_help=False)
    args = parser.add_argument_group('Options')
    args.add_argument('-h', '--help', action='help', default=SUPPRESS,
                      help='Show this help message and exit.')
    args.add_argument('-i', '--input', required=True,
                      help='Required. An input directory to process. The input must be zipped tasks, '
                           'created by cvat.', type=str, metavar='"<path>"')
    args.add_argument('-o', '--output', required=True,
                      help='Required. Output directory where files are saved.', type=str, metavar='"<path>"')
    return parser


def do_train_txt(content):
    global train_data_list, valid_file_path
    for line in content.splitlines():
        fname = os.path.basename(line.decode('utf-8'))
        pathname = os.path.join(data_file_path, os.path.join(str(current_task), fname))
        if random.random() < 0.1:
            valid_data_list.append(pathname)
        else:
            train_data_list.append(pathname)


obj_data_dict = {
    'classes': re.compile(r'classes = (?P<classes>\d+)'),
    'train': re.compile(r'train = (?P<train>.*)'),
    'valid': re.compile(r'valid = (?P<valid>.*)'),
    'names': re.compile(r'names = (?P<names>.*)'),
    'backup': re.compile(r'backup = (?P<backup>.*)'),
}

def _parse_line(line, dict):
    for key, pattern in dict.items():
        match = pattern.search(line)
        if match:
            return key, match
    return None, None

def do_obj_data(content):
    global num_classes
    for line in content.splitlines():
        log.info("obj_data %s" % line.decode('utf-8'))
        key, match = _parse_line(line.decode('utf-8'), obj_data_dict)
        if key == 'classes':
            num_classes = int(match.group('classes'))
        elif key == 'train':
            pass
        elif key == 'valid':
            pass
        elif key == 'names':
            pass


def do_obj_names(content):
    global name_list
    for line in content.splitlines():
        log.info("obj_names %s" % line.decode('utf-8'))
        if line.decode('utf-8') not in name_list:
            name_list.append(line.decode('utf-8')) 


def do_task_file(f):
    global current_task
    fname = os.path.basename(f)
    if fname.startswith("task_") and fname.endswith(".zip"):
        print("found: ", f)
        task_dir = os.path.join(data_file_path, str(current_task))
        os.makedirs(task_dir, exist_ok=True)
        with ZipFile(f, 'r') as zipObj:
            listOfFileNames = zipObj.namelist()
            # Iterate over the file names
            for fileName in listOfFileNames:
                print(fileName)
                if fileName == 'train.txt':
                    do_train_txt(zipObj.read(fileName))
                elif fileName == 'obj.data':
                    do_obj_data(zipObj.read(fileName))
                elif fileName == 'obj.names':
                    do_obj_names(zipObj.read(fileName))
                elif fileName.endswith(".PNG") or fileName.endswith(".txt"):
                    with open(os.path.join(task_dir, os.path.basename(fileName)), 'wb') as f:
                        f.write(zipObj.read(fileName))  
        current_task += 1
                    


def find_labeled(directory):
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        # checking if it is a file
        if os.path.isfile(f):
            do_task_file(f)


def main():
    global train_file_path, valid_file_path, name_file_path, data_file_path, current_task, num_classes, data_data_path
    log.basicConfig(format='[ %(levelname)s ] %(message)s', level=log.INFO, stream=sys.stdout)
    args = build_argparser().parse_args()
    train_file_path = os.path.join(args.output, 'train.txt')
    valid_file_path = os.path.join(args.output, 'valid.txt')
    name_file_path = os.path.join(args.output, 'classes.name')
    data_file_path = os.path.join(args.output, 'data')
    data_data_path = os.path.join(args.output, 'data.data')
    os.makedirs(data_file_path, exist_ok=True)

    find_labeled(args.input)

    with open(train_file_path, 'w') as f:
        for t in train_data_list:
            f.write(t + '\n')
    with open(valid_file_path, 'w') as f:
        for t in valid_data_list:
            f.write(t + '\n')
    with open(name_file_path, 'w') as f:
        for t in name_list:
            f.write(t + '\n')
    with open(data_data_path, 'w') as f:
        f.write('classes = %d\n' % num_classes)
        f.write('train = %s\n' % train_file_path)
        f.write('valid = %s\n' % valid_file_path)
        f.write('names = %s\n' % name_file_path)
        f.write('backup = %s\n' % data_file_path)

    log.info("done")


if __name__ == '__main__':
    sys.exit(main() or 0)

