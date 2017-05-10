import cognitive_sr.sound_recorder
import io
#import speech_recognition as sr


subscription_key = 'deb02ae701ff4d6fb34cbc85fcc4b935'
profile_id = '2d53504b-ff89-44c6-860c-d65493f999e8'
BING_KEY = "cf23b72dd9204d768a2014d3e106f5f4"



def create_profile():
    """ creates a user profile """
    speech_identification = cognitive_sr.SpeechIdentification(subscription_key)
    result = speech_identification.create_profile()
    print(result)


def delete_profile(profile_id):
    """ deletes a user profile """
    speech_identification = cognitive_sr.SpeechIdentification(subscription_key)
    result = speech_identification.delete_profile(profile_id)
    #print('Deleted:', result)


def enroll_profile(profile_id):
    """ enrolls a profile using a wav recording of them speaking """

    wav_path = cognitive_sr.sound_recorder.record_sound(profile_id)

    with io.open(wav_path, 'rb') as wav_file:
        wav_data = wav_file.read()

    speech_identification = cognitive_sr.SpeechIdentification(subscription_key)
    result = speech_identification.enroll_profile(profile_id, wav_data)
    #print(result)


def identify_profile(profile_ids):
    """ identifies a profile using a wav recording of them speaking """
    wav_path = cognitive_sr.sound_recorder.record_sound(profile_id)

    with io.open(wav_path, 'rb') as wav_file:
        wav_data = wav_file.read()

    speech_identification = cognitive_sr.SpeechIdentification(subscription_key)
    result = speech_identification.identify_profile(
        profile_ids, wav_data, short_audio=True)
    #print(result)


def list_profiles():
    """ lists all the currently registered profiles """
    speech_identification = cognitive_sr.SpeechIdentification(subscription_key)
    profiles = speech_identification.get_all_profiles()

    for profile in profiles:
        print(profile['identificationProfileId'])


# def speech2text():
#     r = sr.Recognizer()
#     with sr.Microphone() as source:
#         print("Say something!")
#         audio = r.listen(source)

#     try:
#         print("Microsoft Bing Voice Recognition thinks you said " + r.recognize_bing(audio, key=BING_KEY))
#     except sr.UnknownValueError:
#         print("Microsoft Bing Voice Recognition could not understand audio")
#     except sr.RequestError as e:
#         print("Could not request results from Microsoft Bing Voice Recognition service; {0}".format(e))


def initialize():
    ref = create_profile()

#identify_profile('f3f73008-b45d-46f0-949d-14ea93d0e077,ce1a3f07-decb-46af-aea3-aacff82fb0af')