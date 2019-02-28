# This program creates FIR filter signals from the the recordings in folder
# "recordings".

# Main libraries
import numpy as np
from scipy.io import wavfile

# System libraries
import os
import sys

# Plotting libraries and settings
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style = 'darkgrid')
sns.set_style({'font.family':'serif', 'font.serif':'Times New Roman'})


class Create_Filter():
    """This class implements a filter object that cuts a given recording
    to an filter length.
    Input:
    - filename: filepath to for a .wav recording in impulse_responses directory
    - dur_silent: silent time (ms) before impact from impulse
    - dur_filter: filter time (ms) of recording after impact
    - plot_result (optional): if True a plot will be generated and saved
        to the same folder as the resulting FIR
    Output:
    - self.generated_filter object is the generated_filter fitler
    Written files:
    - the filter is written to the filepath "{dur_filter}/{original_filename}"
    Specifications:
    - All arrays are numpy arrays with one row
    """

    def __init__(self,
                filename,
                dur_silent,
                dur_filter,
                plot_result = False):
        """Initializes object according to class specifications."""
        # Files
        recording_filepath = 'impulse_responses/'+filename
        filter_filepath = 'FIR_filters/%s_ms/%s'%(int(dur_filter), filename)

        # Convert to seconds
        dur_silent = dur_silent/1000.
        dur_filter = dur_filter/1000.

        # Calculate filters
        print('\nReading file \t\t"%s"'%(filename))
        x, fs =  self.read_audio_file(recording_filepath)
        # print('Normalizing audio')
        x = self.normalize_audio(x)*.9
        print('Computing FIR-filter')
        x = self.set_silent_duration(x, fs, dur_silent)
        x = self.set_filter_duration(x, fs, dur_filter)

        # Store filter
        print('Writing FIR-filter to \t"%s"'%(filter_filepath))
        self.write_audio_file(filter_filepath, x, fs)
        self.generated_filter = x
        self.fs = fs

        # Plot result
        if plot_result:
            plot_path = filter_filepath[:-4]+'.png'
            print('Plotting results to \t"%s"'%(plot_path))
            t = np.linspace(-dur_silent,-dur_silent+len(x)/fs,len(x))

            # fft
            n = len(x) # length of the signal
            k = np.arange(n)
            T = n/fs
            frq = k/T # two sides frequency range
            frq = frq[range(n//2)] # one side frequency range

            X = np.fft.fft(x)/n # fft computing and normalization
            X = X[range(n//2)]
            # X = np.log(X)
            X = X/np.max(np.abs(X))

            fig, ax = plt.subplots(2, 1)
            ax[0].plot(t,x,
                    color = 'k',
                    linewidth = .5)
            ax[0].set_xlabel('Time / [ms]')
            ax[0].set_ylabel('Amplitude')
            # ax.title('FIR-filter generated from %s with duration %s'%(filename,dur_filter))
            ax[1].semilogy(frq,abs(X),'r',linewidth=.5) # plotting the spectrum
            ax[1].set_xlabel('Freq (Hz)')
            ax[1].set_ylabel('|Y(freq)|')
            ax[1].set_xlim(0,5000)
            fig.suptitle('Filter generated from %s'%(filename))
            plt.tight_layout()
            plt.savefig(plot_path, dpi = 300)
            plt.cla()

    def normalize_audio(self,x):
        """This function takes an audio array x and then returns the array
        scaled so that abs(value) for values in the array are less or equal
        to 1."""
        return x/np.max(np.abs(x))

    def read_audio_file(self, filepath):
        """Reads an .wav file at the filepath and returns an array with the
        sample and its framerate."""
        fs, x = wavfile.read(filepath)
        if np.size(x[1]) == 2:  # merge stereo to mono
            x = np.array(x[:,0]+x[:,1])
        return x, fs

    def write_audio_file(self, filepath, x, fs):
        """Writes a x as a .wav file with framerate fs to file at filepath."""
        # # Assert folder available
        folderpath = filepath
        while folderpath[-1] != '/':
            folderpath = folderpath[:-1]
        folderpath = folderpath[:-1]
        if not os.path.exists(folderpath):
            os.makedirs(folderpath)
        x = np.array(x, dtype='float32')    # scipy.io.wavfile doesnt support 64 bit float
        wavfile.write(filepath, fs, x)

    def set_silent_duration(self, x, fs, dur_silent):
        """Takes an audio array x with framerate fs. It first prepends
        dur_silent*fs silent values to the array. It then calculates the
        initial impact index and only keeps dur_silent*fs values before
        the impact."""
        silent_indexes = int(fs*dur_silent)
        impact_index = self._get_impact_index(x)
        x = np.concatenate((np.zeros(silent_indexes),x))
        impact_index = self._get_impact_index(x)
        x = x[impact_index-silent_indexes:]
        return x

    def set_filter_duration(self, x, fs, dur_filter):
        """Takes an audio array x with framerate fs. It first appends
        dur_filter*fs silent values to the array. It then calculates the
        initial impact index and only keeps dur_filter*fs values after
        the impact."""
        filter_indexes = int(fs*dur_filter)
        impact_index = self._get_impact_index(x)
        x = np.concatenate((x, np.zeros(filter_indexes)))
        x = x[:impact_index+filter_indexes]
        return x

    def _get_impact_index(self, x, impact_value = .5):
        """This function takes an array and returns the first index where
        abs(x[index])>.5."""
        for index,value in enumerate(x):
            if np.abs(value) > impact_value:
                return index

def main():
    # Get filepaths to .wav in filenames
    filenames = os.listdir('impulse_responses')
    for name in filenames:  # Remove non .wav files
        if not name[-4:] == '.wav':
            filenames.remove(name)

    # Print prompt
    print('The following .wav files was found in "/impulse_responses" directory:')
    [print('\t', x) for x in filenames]
    filter_dur = input('Enter duration for FIR filter in ms (150 is recommended):\n\t ')
    try:    filter_dur = float(filter_dur)
    except: print('Error: Input must be float or integer, aborting program.'); sys.exit()
    silence_dur = 20

    # Generate filter
    for filepath in filenames:
        FIR_filter = Create_Filter(filepath, silence_dur, filter_dur, plot_result = True)

if __name__ == '__main__':
    main()
