import soundfile as sf
import audiotranscode
import numpy as np
import emoji

import sys
sys.path.append("OpenVokaturi-2-2a/api")
import Vokaturi
Vokaturi.load("OpenVokaturi-2-2a/lib/Vokaturi_mac.so")


def get_sample(path_ogg):
    """
    :param path_ogg: path to .ogg file
    :return: samples of audio file and its sample rate
    """
    path_wav = path_ogg[:-3] + 'wav'

    at = audiotranscode.AudioTranscode()
    at.transcode(path_ogg, path_wav)

    (samples, sample_rate) = sf.read(path_wav)

    return samples, sample_rate


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
    voice.extract(quality, emotion_probabilities )
    voice.destroy()

    emo_dict = {"neutrality": emotion_probabilities .neutrality,
                "happiness": emotion_probabilities .happiness,
                "sadness": emotion_probabilities .sadness,
                "anger": emotion_probabilities .anger,
                "fear": emotion_probabilities .fear}

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

if __name__ == '__main__':
    raise RuntimeError