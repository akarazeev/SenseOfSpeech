import soundfile as sf
# import audiotranscode
import numpy as np
import subprocess
import emoji
import os

import sys
sys.path.append("OpenVokaturi-2-2a/api")
import Vokaturi

OS = 'LINUX'

if OS == 'MAC':
    pass
elif OS == 'LINUX':
    Vokaturi.load("OpenVokaturi-2-2a/lib/Vokaturi_linux32.so")


def get_sample(path_ogg):
    """
    :param path_ogg: path to .ogg file
    :return: samples of audio file and its sample rate
    """
    path_wav = path_ogg[:-3] + 'wav'

    # FIX:
    # at = audiotranscode.AudioTranscode()
    # at.transcode(path_ogg, path_wav)

    ogg_to_wav(path_ogg, path_wav)

    (samples, sample_rate) = sf.read(path_wav)

    return samples, sample_rate


def emodict_from_path(path):
    """
    :param path: .wav file
    :return:
    """
    (samples, sample_rate) = sf.read(path)
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
    voice.extract(quality, emotion_probabilities )
    voice.destroy()

    emo_dict = {"neutrality": emotion_probabilities.neutrality,
                "happiness": emotion_probabilities.happiness,
                "sadness": emotion_probabilities.sadness,
                "anger": emotion_probabilities.anger,
                "fear": emotion_probabilities.fear}

    return quality.valid, emo_dict


def emotion_wrapper(path_ogg):
    """
    :param path_ogg: path to .ogg file
    :return: indicator of validity and dictionary with detected
             emotions and its probabilities
    """
    (samples, sample_rate) = get_sample(path_ogg)
    buffer_length = len(samples)

    c_buffer = Vokaturi.SampleArrayC(buffer_length)
    c_buffer[:] = samples[:]

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
    text = []

    for emo, prob in emo_dict.items():
        text.append(emoji.emojize('{emo_str}: {prob_str:.3f}'.format(emo_str=mapping[emo],
                                                                     prob_str=prob), use_aliases=True))

    return text


def get_dict_of_emotions():
    """
    :return: dict of emotions and paths to audio examples
    """
    list_res = list(filter(lambda x: x[0] != '.', os.listdir('res/')))
    splitted = list(map(lambda x: x.split('_'), list_res))
    tuples3 = list(map(lambda x: (x[1], '_'.join(x)), filter(lambda x: x[0] == '3', splitted)))

    return dict(tuples3)


def send_emo(emotion, abs_path=''):
    """
    :param emotion:
    :param abs_path: absolute path to this file
    """
    path = get_dict_of_emotions()[emotion]

    return os.path.join(abs_path, 'res', path)


def ogg_to_wav(path_ogg, path_wav):
    """
    Convert .ogg to .wav format.
    """
    bashCommand = "ffmpeg -i {ogg} {wav}".format(ogg=path_ogg, wav=path_wav)
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()


if __name__ == '__main__':
    raise RuntimeError
