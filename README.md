# Singing Materials

### What is the Singing Materials project?

- Singing Materials explores the sonification of phonon data.
- The project team are [Prakriti Kayastha](https://prakayastha.github.io/), [Ify Nwabuokei](https://github.com/ifylala), [Adam Parkinson](https://peoplefinder.lsbu.ac.uk/researcher/825yv/dr-adam-parkinson), [Lucy Whalley](https://lucydot.github.io) and [Paul Vickers](https://paulvickers.github.io/).
- This project is at an early stage, with software development happening [here](https://github.com/nu-cem/singing-materials) and [here](https://github.com/nu-cem/singing-materials-app).
- Our starting point is the audification of phonon data  (mapping phonon frequencies to the audible range).
- In the medium term, we would like to explore the use of phonon data for science communication via electronic music performance: Phonon Rave, anyone?
- In the longer term, we would like to explore how phonon sonification may be used for real-time monitoring of molecular dynamics simulations.

### So what *is* a Phonon?

A phonon is a quantum mechanical particle of heat. 

When we imagine atoms in a material we may think of something perfectly static, unmoving.
However even at absolute zero the atoms are vibrating with energy.
Phonons are used to describe the vibrations of a crystalline material (a material formed with atoms in a periodically repeating geometric array).
These vibrations are important because they affect a whole host of material properties, like electrical conductivity.
They also

You can visualise phonons [here](https://henriquemiranda.github.io/phononwebsite/phonon.html).
There are also some articles for a more general audience [here](https://news.mit.edu/2010/explained-phonons-0706) and [here](https://www.reading.ac.uk/infrared/technical-library/absorption-theory/thermal-vibrations), for example.

Or, to quote chat GPT, after prompting with `explain what a phonon is for a general audience`:

> Sure! Imagine you're holding a string on a guitar or a rubber band. When you pluck that string or stretch the rubber band and then let it go, it starts to vibrate, right? As it vibrates, it produces sound waves that you can hear.
>
> Now, think about the tiny particles that make up everything around us, like atoms and molecules. Just like the guitar string or the rubber band, these particles can also vibrate, but in a different way. They don't make sound waves like the guitar string does, but they create something called "phonons."
>
> A phonon is like a tiny packet of energy associated with these vibrations of particles in a material. It's the way energy moves through a solid material by causing the particles to wiggle and jiggle. You can think of phonons as the "quanta" or individual units of these vibrations, similar to how light can be thought of as made up of particles called photons.
>
> So, when you heat up a metal rod or any solid object, you're actually giving energy to these phonons, making the particles inside it vibrate faster and spread that heat energy. Without phonons, heat wouldn't be able to move through materials, and things like cooking, heating your home, or even your computer's microchips wouldn't work as they do. In short, phonons are like the messengers that carry heat energy by making tiny particles dance and transfer that heat from one place to another.


### So what *is* sonification?

Sonification is the use of non-speech audio to convey information. A well-known scientific example is a geiger counter which produces an audible click when it detects an ionisation event. Sonification is being increasingly used within the physical sciences, in particular for [astrophysical research](https://www.scientificamerican.com/video/listen-to-the-astonishing-chirp-of-two-black-holes-merging). 

Sonification has also been used as a tool for music composition by a [number of contemporary classical composers](https://www.straebel.com/files/Straebel%202010_Sonification%20Metaphor.pdf). 

This continuum - from data representation to data abstraction - is discussed in the paper [`Making data sing`](https://www.researchgate.net/profile/Atau-Tanaka/publication/312740596_Making_Data_Sing_Embodied_Approaches_to_Sonification/links/5fc6b5f2299bf188d4e8d59e/Making-Data-Sing-Embodied-Approaches-to-Sonification.pdf), which inspired this project title.



### How can I run your code?

The code is currently in development, and is in a fragile (ie, easily broken) state.

To run through the code in the notebook follow these setup instructions: 

**Step 1: Clone the Git Repository**

Open a terminal or command prompt and navigate to the directory where you want to store the code from the Git repository. Then, use the following command to clone the repository. 

`git clone https://github.com/NU-CEM/singing-materials.git`

This will create a local copy of the code on your system.

**Step 2: Create a Conda Environment**

Navigate to the directory where you cloned the repository. Use the following commands to create a new Conda environment and activate it. 
In this case our environment_name is singing-materials. 

`conda info --envs`  
`conda create --name singing-materials`  

**Step 3: Activate the environment** 

To activate the environment, use the command;

`conda activate singing-materials`

**Step 4: Install Dependencies**

While in the activated environment, install the required Python packages. Use the following commands:
`conda install numpy scipy jupyter pip`   
`pip install sounddevice`   
`pip install mp-api`

This will install all the necessary packages.

**Step 5: Creating Materials Project API Key**

To interact with the Materials Project API, you will need an API key. Here's how you can obtain one:
* Visit the Materials Project website (https://materialsproject.org/).
* Sign up or log in to your account.
* Once logged in, navigate to your account settings.
* Under the API key section, generate a new API key.

**Step 6: Setting the API Key as an Environmental Variable**

To use the Materials Project API key with this code, you need to set it as an environmental variable in your system. Here's how you can do it:
For Linux or macOS,  add the command line below to your ~/.bashrc or ~/.bash_profile file, replacing [YOUR_MP_API_KEY_HERE] with your actual API key:

`export MP_API_KEY="YOUR_MP_API_KEY_HERE"`

For Windows, you can set the environmental variable using the Command Prompt:

`setx MP_API_KEY "YOUR_MP_API_KEY_HERE"`

This step is crucial to ensure that the code can authenticate and interact with the Materials Project API.

**Step 7: Running the Code**

Now that everything is set up, you can run the code from the Jupyter notebook. Navigate to the directory containing the notebook, start the server with `jupyter notebook`, open the notebook, and run each cell.
You should hear the sound output based on the phonon frequencies and other parameters defined.

### How can I get involved?

If you have a suggestion, please raise an issue on this repository and/or contact project lead Lucy: l.whalley@northumbria.ac.uk.
