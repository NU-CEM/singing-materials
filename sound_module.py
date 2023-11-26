import sounddevice
import numpy as np
import math
import time
import yaml
from scipy import constants
import os
import argparse
 

phonon_mesh_filepath = './data/BaS_Fm3m/mesh.yaml'
sample_rate = 44100
min_audible = 20# minimum audible frequency in herz
max_audible = 8E3 # maximum audible frequency in herz


# this function adapted from
# https://stackoverflow.com/questions/73494717/trying-to-play-multiple-frequencies-in-python-sounddevice-blow-horrific-speaker
def callback(outdata: np.ndarray, frames: int, time, status) -> None:
    """writes sound output to 'outdata' from sound_queue."""
    result = None

    for frequency, start_index in audible_dictionary.items():
        t = (start_index + np.arange(frames)) / sample_rate
        t = t.reshape(-1, 1)

        wave = np.sin(2 * np.pi * frequency * t)

        if result is None:
            result = wave
        else:
            result += wave

        audible_dictionary[frequency] += frames

    if result is None:
        result = np.arange(frames) / sample_rate
        result = result.reshape(-1, 1)

    outdata[:] = result

def phonon_to_audible(phonon_frequencies):
    """takes phonon frequencies (in THz) and returns suitable phonon frequencies (in Hz)"""

    if len(phonon_frequencies) == 1:
        audible_frequencies = [440]
        print("only one phonon frequency, so mapping to 440Hz")
    else:
        audible_frequencies = linear_map(phonon_frequencies)

    return audible_frequencies

def linear_map(phonon_frequencies, min_phonon=None, max_phonon=None):
    """linearly maps phonon frequencies (in THz) to frequencies in the audible range (in Hz)"""

    if min_phonon is None:
        min_phonon_hz = min(phonon_frequencies)*1E12
    else:
        min_phonon_hz = min_phonon*1E12

    if max_phonon is None:
        max_phonon_hz = max(phonon_frequencies)*1E12
    else:
        max_phonon_hz = max_phonon*1E12        

    phonon_frequencies_hz = np.array(phonon_frequencies)*1E12
    scale_factor = (max_audible - min_audible) / (max_phonon_hz - min_phonon_hz)
    audible_frequencies = [ scale_factor*(frequency-min_phonon_hz) + min_audible for frequency in phonon_frequencies_hz]
    print("audible frequencies are (Hz):", audible_frequencies)

    return audible_frequencies

def frequencies_from_mesh(phonon_mesh_filepath):
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

def frequencies_from_mp_id(mp_id):
    """return phonon frequencies at gamma point from for a material hosted on the Materials Project ().
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

    phonon_frequencies = list(bs.bands[:,0])
    phonon_frequencies = process_imaginary(phonon_frequencies)
    print("phonon frequencies are (THz):", phonon_frequencies)

    return phonon_frequencies

def bose_einstien_distribution(energy,temperature):
    return 1 / (math.exp(energy/(constants.Boltzmann*temperature)) - 1)

def frequency_to_energy(frequency):
    """convert frequency in THz to energy in joules"""
    frequency_hz = frequency*1E12
    energy = constants.h*frequency_hz
    return energy

def excite_by_heat(phonon_frequencies, temperature):
    """return frequencies which have average occupation >= 1 at a given temperature. 
    Average occupation is calculated using Bose-Einstien statistics"""
    average_occupations = np.array([bose_einstien_distribution(frequency_to_energy(frequency),temperature) 
                           for frequency in phonon_frequencies])
    # need phonon_frequency as numpy array
    phonon_frequencies = np.array(phonon_frequencies)
    # can now use trendy indexing over a boolean array
    occupied_modes = phonon_frequencies[average_occupations >= 1]
    return occupied_modes

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


def main(args):
    
    global audible_dictionary  # global audio_dictionary for callback

    # Process command-line arguments
    mp_ids = args.mp_ids
    min_phonon = args.min_phonon
    max_phonon = args.max_phonon
    timelength = args.timelength

     # Check if min_phonon and max_phonon values are valid floats
    if min_phonon is not None:
        try:
            min_phonon = float(min_phonon)
        except ValueError:
            print("Error: min_phonon must be a valid float.")
            return

    if max_phonon is not None:
        try:
            max_phonon = float(max_phonon)
        except ValueError:
            print("Error: max_phonon must be a valid float.")
            return

    # Check if timelength is a valid float
    try:
        timelength = float(timelength)
    except ValueError:
        print("Error: timelength must be a valid float.")
        return

    # Assert min_phonon and max_phonon values
    assert min_phonon is None or max_phonon is None or min_phonon < max_phonon, "min_phonon must be less than max_phonon"

    result_data = {}

   # The mp_id variable can be used here to determine which material to process
    
    for mp_id in mp_ids:
        # Get phonons (in THz) for the current MP ID
        phonon_frequencies = frequencies_from_mp_id(mp_id)
        
        # Excite by heat and get frequencies
        phonon_frequencies = excite_by_heat(phonon_frequencies, 300)
        
        # Convert phonon frequencies to audible frequencies (return in Hz)
        audible_frequencies = phonon_to_audible(phonon_frequencies)
        
        # Store results for this MP ID
        result_data[mp_id] = {
            "phonon_frequencies": phonon_frequencies,
            "audible_frequencies": audible_frequencies
        }

        # Create global dictionary containing frequencies as keys. This will be used in the output stream.
        audible_dictionary = dict.fromkeys(audible_frequencies, 0)

        # Create and run the output stream for a set time
        play_chord(timelength)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phonon Audible Frequencies Player")
    parser.add_argument("mp_ids", nargs='+', help="Materials Project IDs")
    parser.add_argument("--min_phonon", type=float, default=None, help="Minimum phonon frequency in THz")
    parser.add_argument("--max_phonon", type=float, default=None, help="Maximum phonon frequency in THz")
    parser.add_argument("--timelength", type=float, default=5, help="Length of the sample in seconds")

    args = parser.parse_args()
    main(args)