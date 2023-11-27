import sounddevice
import numpy as np
import math
import time
import yaml
from scipy import constants
import os
import argparse
 
sample_rate = 44100

# this function adapted from
# https://stackoverflow.com/questions/73494717/trying-to-play-multiple-frequencies-in-python-sounddevice-blow-horrific-speaker
def callback(outdata: np.ndarray, frames: int, time, status) -> None:
    """writes sound output to 'outdata' from sound_queue."""

    result = None

    for frequency, data in sonification_dictionary.items():

        t = (data["index"] + np.arange(frames)) / sample_rate
        t = t.reshape(-1, 1)

        wave = data["amplitude"]*np.sin(2 * np.pi * frequency * t)

        if result is None:
            result = wave
        else:
            result += wave

        if np.any(np.abs(result)>1):
            print("Halt: amplitude exceeding magnitude of 1")
            return
        # we need to be careful with amplitude...it can hurt your ears..
        # this stops amplitude being set too high. ONLY ADJUST IF YOU UNDERSTAND THE CONSEQUENCES!

        data["index"] += frames

    if result is None:
        result = np.arange(frames) / sample_rate
        result = result.reshape(-1, 1)

    outdata[:] = result

def get_athermal_amplitudes(dos_array=None, num_frequencies=None):
    """returns an (unnormalised) amplitude at which to play each frequency, not taking into account phonon occupation.
    If a dos array is supplied this will be applied to each frequency in turn.
    Elif num_frequencies supplied every frequency amplitude will be played at same amplitude."""

    if dos_array is not None:
        return dos_array / max(dos_array)

    elif num_frequencies:
        return np.ones(num_frequencies)

    else: 
        print("Error: no amplitude data supplied.")

def normalise_amplitudes(amplitudes):

    amplitudes = amplitudes / sum(amplitudes)

    return amplitudes

def phonon_to_audible(phonon_frequencies, min_phonon, max_phonon, min_audible, max_audible):
    """takes phonon frequencies (in Hz) and returns frequencies within the human hearing range (in Hz)"""

    if len(phonon_frequencies) == 1:
        audible_frequencies = [440]
        print("only one phonon frequency, so mapping to 440Hz")
    else:
        audible_frequencies = linear_map(phonon_frequencies, min_phonon, max_phonon, min_audible, max_audible)

    return audible_frequencies

def get_min_max_phonon_frequency(phonon_frequencies, min_phonon, max_phonon):

    if min_phonon is None:
        min_phonon = min(phonon_frequencies)

    elif min_phonon > min(phonon_frequencies):
        print("`min_phonon` parameter is more than the minimum phonon frequency in dataset; `min_phonon` will be overriden." )
        min_phonon = min(phonon_frequencies)

    if max_phonon is None:
        max_phonon = max(phonon_frequencies)

    elif max_phonon < max(phonon_frequencies):
        print("`max_phonon` parameter is less than than the maximum phonon frequency in dataset; `max_phonon` will be overriden." )
        max_phonon = max(phonon_frequencies)

    return min_phonon, max_phonon

def linear_map(phonon_frequencies, min_phonon, max_phonon, min_audible, max_audible):
    """linearly maps phonon frequencies (in Hz) to frequencies in the audible range (in Hz)"""

    scale_factor = (max_audible - min_audible) / (max_phonon - min_phonon)
    audible_frequencies = [ scale_factor*(frequency-min_phonon) + min_audible for frequency in phonon_frequencies]
    print("audible frequencies are (Hz):", audible_frequencies)

    return audible_frequencies

def gamma_frequencies_from_mesh(phonon_mesh_filepath):
    """return phonon frequencies at gamma point from a phonopy mesh.yaml. Assumes gamma point is zeroth
    element in data['phonon']."""

    # read yaml data 
    with open(phonon_mesh_filepath) as f:
        data = yaml.safe_load(f)

    # extract list of unique frequencies - these are in THz
    phonon_frequencies = list(set([dictionary['frequency'] for dictionary in data['phonon'][0]['band']]))
    phonon_frequencies = process_imaginary(phonon_frequencies)

    return phonon_frequencies

def process_imaginary(phonon_frequencies):
    # remove any imaginary modes
    phonon_cleaned_frequencies = [frequency for frequency in phonon_frequencies if frequency > 0]

    return phonon_cleaned_frequencies

def process_imaginary_dos(dos,phonon_frequencies) :
    # remove dos which correspond to imaginary modes
    dos_cleaned_frequencies = [dos[i] for i in range(len(phonon_frequencies)) if phonon_frequencies[i] > 0]

    return np.array(dos_cleaned_frequencies)

def gamma_frequencies_from_mp_id(mp_id):
    """return phonon frequencies (in Hz) at gamma point from for a material hosted on the Materials Project.
    Material is identified using unique ID number. Note that to use this feature you need a Materials
    Project API key (https://materialsproject.org/api)."""
    import mp_api
    from mp_api.client import MPRester

    with MPRester(os.environ.get('MP_API_Key')) as mpr:
        try:
            bs = mpr.phonon.get_data_by_id(mp_id).ph_bs
        except:
            print("this materials project entry does not appear to have phonon data")
            pass

    print("extracting frequencies for qpoint {}".format(bs.qpoints[0].cart_coords))

    phonon_frequencies = list(bs.bands[:,0]*1E12)   # convert from THz to Hz
    phonon_frequencies = process_imaginary(phonon_frequencies)
    print("phonon frequencies are (Hz):", phonon_frequencies)

    return phonon_frequencies

def dos_data_from_mp_id(mp_id):
    """return frequencies (in Hz) at which density of states is evaluated, and the density of states itself. This is for a material hosted on the Materials Project.
    Material is identified using unique ID number. Note that to use this feature you need a Materials
    Project API key (https://materialsproject.org/api)."""
    import mp_api
    from mp_api.client import MPRester

    with MPRester(os.environ.get('MP_API_Key')) as mpr:

        try: 
            dos = mpr.phonon.get_data_by_id(mp_id).ph_dos
        except:
            print("this materials project entry does not appear to have phonon data")
            pass

        phonon_frequencies = list(np.array(dos.as_dict()['frequencies'])*1E12) # convert from THz to Hz 
        phonon_frequencies = process_imaginary(phonon_frequencies)    

        dos = dos.as_dict()['densities']
        dos = process_imaginary_dos(dos,phonon_frequencies) 
    
    return phonon_frequencies, dos


def bose_einstien_distribution(energy,temperature):
    return 1 / (math.exp(energy/(constants.Boltzmann*temperature)) - 1)

def frequency_to_energy(frequency):
    """convert frequency in Hz to energy in joules"""
    energy = constants.h*frequency
    return energy

def scale_by_occupation(amplitudes, phonon_frequencies, temperature):
    """Re-scale the amplitude by the Bose Einstein occupation factor for a state with energy h*frequency at specified temperature."""
    BE_occupations = np.array([bose_einstien_distribution(frequency_to_energy(frequency),temperature) 
                           for frequency in phonon_frequencies])

    # scale by occupation expressed as a fraction of the total occupation
    scaled_amplitudes = amplitudes*(BE_occupations/max(BE_occupations))

    return scaled_amplitudes

def play_chord(timelength):
    """DRONE POWER"""

    # create stream
    stream = sounddevice.OutputStream(channels=2, blocksize=sample_rate, 
                samplerate=sample_rate, callback=callback)

    # start stream and keep running for timelength
    stream.start()
    time.sleep(timelength)
    stream.stop()
    stream.close()

def check_arguments(args):

    # Check if min_phonon and max_phonon values are valid floats
    if args.min_phonon is not None:
        try:
            args.min_phonon = float(args.min_phonon)
        except ValueError:
            print("Error: min_phonon must be a valid float.")
            return

    if args.max_phonon is not None:
        try:
            args.max_phonon = float(args.max_phonon)
        except ValueError:
            print("Error: max_phonon must be a valid float.")
            return

    # Check if timelength is a valid float
    try:
        args.timelength = float(args.timelength)
    except ValueError:
        print("Error: timelength must be a valid float.")
        return

    if args.temperature:
        assert args.temperature >= 0, "Error: temperature is specified in kelvin and must not be negative."

    # Assert min_phonon and max_phonon values
    assert args.min_phonon is None or args.max_phonon is None or args.min_phonon < args.max_phonon, "min_phonon must be less than max_phonon"

    return args

def main(args):
    
    global sonification_dictionary  # global sonification_dictionary which holds data for callback
    
    args = check_arguments(args)

    for mp_id in args.mp_ids:

        if args.gamma_mode:
            # Get phonons (in THz) for the current MP ID
            phonon_frequencies = gamma_frequencies_from_mp_id(mp_id)
            amplitudes = get_athermal_amplitudes(num_frequencies=len(phonon_frequencies))

        else:
            phonon_frequencies, dos = dos_data_from_mp_id(mp_id)
            amplitudes = get_athermal_amplitudes(dos_array=dos,num_frequencies=len(phonon_frequencies))
        
        # Convert phonon frequencies to audible frequencies (return in Hz)
        min_phonon, max_phonon = get_min_max_phonon_frequency(phonon_frequencies, args.min_phonon, args.max_phonon)
        audible_frequencies = phonon_to_audible(phonon_frequencies, min_phonon, max_phonon, args.min_audible, args.max_audible)
        
        # Excite by heat and get updated amplitudes
        if args.temperature:
            amplitudes = scale_by_occupation(amplitudes, phonon_frequencies, args.temperature)
        
        # ensure that the sum of amplitudes at all times is < 1
        amplitudes = normalise_amplitudes(amplitudes)

        print("amplitudes are", amplitudes)

        assert len(audible_frequencies) == len(amplitudes), "length of frequency and amplitude arrays are not equal"

        # Create global dictionary containing frequencies as keys. This will be used in the output stream.
        # TODO: play around with index
        index=0
        index=np.random.randint(0,1E6)
        sonification_dictionary = {}
        for frequency, amplitude in zip(audible_frequencies,amplitudes):
            sonification_dictionary[frequency] = {'amplitude': amplitude, 'index': index}
            # I might be imagining it, but placing slightly out of phase with a random index seems to make sound less harsh.

        # Create and run the output stream for a set time
        play_chord(args.timelength)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Singing Materials Player")
    parser.add_argument("mp_ids", nargs='+', help="Materials Project IDs")
    parser.add_argument("--min_phonon", type=float, default=None, help="Minimum phonon frequency in Hz. If not set, this will be extracted from the phonon data.")
    parser.add_argument("--max_phonon", type=float, default=None, help="Maximum phonon frequency in Hz. If not set, this will be extracted from the phonon data.")
    parser.add_argument("--min_audible", type=float, default=20, help="Minimum sound frequency in Hz")             
    parser.add_argument("--max_audible", type=float, default=800, help="Maximum sound frequency in Hz") 
    parser.add_argument("--timelength", type=float, default=5, help="Length of the sample in seconds")
    parser.add_argument("--gamma_mode", type=bool, default=False, help="If True then gamma point frequencies are sonified only.")
    parser.add_argument("--temperature", type=float, default=None, help="Temperature in kelvin. If set the sonified amplitude is weighted by the bose-einstein distribution for phonon energy at specified temperature.")

    args = parser.parse_args()
    main(args)