from mp_api.client import MPRester
import os
import json

key = os.environ.get('MP_API_Key')

Cs3Sb = "mp-10378"

with MPRester(key) as mpr:
    try:
        dos = mpr.phonon.get_data_by_id(Cs3Sb).ph_dos
        print(dos)
    except:
        print("this materials project entry does not appear to have phonon data")
        pass


with open("dos.json", "w") as outfile:
    outfile.write(dos.to_json())