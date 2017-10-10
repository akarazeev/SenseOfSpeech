import sys

emoji_mapping = {
    'anger':      ':astonished:',
    'fear':       ':scream:',
    'happiness':  ':smile:',
    'neutrality': ':neutral_face:',
    'sadness':    ':pensive:'
}

actions = {
    'DETECT':  '1',
    'TRAIN':   '2',
    'Neutral': '3',
    'Happy':   '4',
    'Sad':     '5',
    'Excited': '6',
    'Fear':    '7'
}

rev_actions = dict(zip(actions.values(), actions.keys()))

mapping = {
    'anger':      'Excited',
    'fear':       'Fear',
    'happiness':  'Happy',
    'neutrality': 'Neutral',
    'sadness':    'Sad'
}

rev_mapping = dict(zip(mapping.values(), mapping.keys()))

OS_MAPPING = {
    'darwin': 'mac',
    'linux2': 'linux',
    'linux':  'linux'
}

OS = OS_MAPPING[sys.platform]

if __name__ == '__main__':
    raise RuntimeError
