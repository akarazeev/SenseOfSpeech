import soundfile as sf
import numpy as np
import subprocess
import emoji
import sys
import os

import logging
import audiotranscode

from open_vok.api import Vokaturi
from accessories import emoji_mapping


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
Vokaturi.load("open_vok/lib/Vokaturi_mac.so")
logger = logging.getLogger(__name__)


def get_sample(path_ogg):
    """
    :param path_ogg: path to .ogg file
    :return: samples of audio file and its sample rate
    """
    path_wav = path_ogg[:-3] + 'wav'

    # Convert .ogg to .wav format
    at = audiotranscode.AudioTranscode()
    at.transcode(path_ogg, path_wav)

    # ogg_to_wav(path_ogg, path_wav)

    (samples, sample_rate) = sf.read(path_wav)

    return samples, sample_rate


def emodict_from_wav(path_wav):
    """
    :param path_wav: .wav file
    :return:
    """
    (samples, sample_rate) = sf.read(path_wav)

    return emodict_from_samples(samples, sample_rate)


def emodict_from_ogg(path_ogg):
    """
    :param path_ogg: path to .ogg file
    :return: indicator of validity and dictionary with detected
             emotions and its probabilities
    """
    (samples, sample_rate) = get_sample(path_ogg)

    return emodict_from_samples(samples, sample_rate)


def emodict_from_samples(samples, sample_rate):
    buffer_length = len(samples)

    c_buffer = Vokaturi.SampleArrayC(buffer_length)

    if samples.ndim == 1:
        c_buffer[:] = samples[:]  # mono
    else:
        c_buffer[:] = 0.5 * (samples[:,0] + 0.0 + samples[:,1])  # stereo

    voice = Vokaturi.Voice(sample_rate, buffer_length)

    # filling Voice with `samples`
    voice.fill(buffer_length, c_buffer)
    quality = Vokaturi.Quality()
    emotion_probabilities = Vokaturi.EmotionProbabilities()
    voice.extract(quality, emotion_probabilities)
    voice.destroy()

    emo_dict = {"neutrality": emotion_probabilities.neutrality,
                "happiness": emotion_probabilities.happiness,
                "sadness": emotion_probabilities.sadness,
                "anger": emotion_probabilities.anger,
                "fear": emotion_probabilities.fear}

    return quality.valid, emo_dict


def with_emoji(emo_dict, mapping):
    """
    :param emo_dict:
    :param mapping:
    :return:
    """
    text = list()

    for emo, prob in emo_dict.items():
        text.append(emoji.emojize('{emo_str}: {prob_str:.3f}'.format(emo_str=mapping[emo],
                                                                     prob_str=prob),
                                  use_aliases=True))
    return text


def get_dict_of_emotions():
    """
    :return: dict of emotions and paths to audio examples
    """
    list_res = list(filter(lambda x: x[0] != '.', os.listdir(os.path.join('res', 'audio_emotions'))))
    splitted = list(map(lambda x: x.split('_'), list_res))
    tuples3 = list(map(lambda x: (x[1], '_'.join(x)), filter(lambda x: x[0] == '3', splitted)))

    return dict(tuples3)


def emotion_file_path(emotion, abs_path=''):
    """
    :param emotion:
    :param abs_path: absolute path to this file
    """
    path = get_dict_of_emotions()[emotion]

    return os.path.join(abs_path, 'res', 'audio_emotions', path)


def ogg_to_wav(path_ogg, path_wav):
    """
    Convert .ogg to .wav format.
    """
    bash_command = "ffmpeg -i {ogg} {wav}".format(ogg=path_ogg, wav=path_wav)
    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    process.communicate()


def emo_distribution(file_name):
    """
    :param file_name:
    :return: (valid, emo_dict)
    """
    valid = None
    emo_dict = None

    try:
        if file_name[-4:] == ".wav":
            valid, emo_dict = emodict_from_wav(file_name)
        elif file_name[-4:] == ".ogg":
            valid, emo_dict = emodict_from_ogg(file_name)
        else:
            raise RuntimeError
    except:
        logger.warning("Wrong file format")

    return valid, emo_dict


def to_text(valid, emo_dict):
    if valid:
        return with_emoji(emo_dict, emoji_mapping)
    else:
        return ["\_(^_^)_/"]


def emo_distance(emo_dict1, emo_dict2):
    def get_array(emo_dict):
        return np.array(list(map(lambda x: x[1], sorted(emo_dict.items(), key=lambda x: x[0]))))

    emotions1 = get_array(emo_dict1)
    emotions2 = get_array(emo_dict2)

    tmp_sum = sum((emotions1 - emotions2) ** 2)

    return np.sqrt(tmp_sum)


if __name__ == '__main__':
    raise RuntimeError
