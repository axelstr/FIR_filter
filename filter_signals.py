# This program filters the samples with FIR filter signals.

# Main libraries
import numpy as np
from scipy.io import wavfile

# System libraries
import os
import sys
def exit():
    print(50*'-')
    sys.exit()


# Plotting libraries and settings
import matplotlib.pyplot as plt
import seaborn as sns
from pylab import cm
sns.set(style = 'darkgrid')
sns.set_style({'font.family':'serif', 'font.serif':'Times New Roman'})

class Filter_Sample():
    """This class filters an electric guitar sample with a FIR-filter.
    Input:
    - sample_path: relative path to electric guitar sample
    - filter_path: relative path to a .wav FIR-filter
    - output_path: relative path to where the filtered sample should be stored
                   as a .wav file3
    Output:
    - self.filtered_sample object is the filtered sample
    Written files:
    - the filtered sample is written to thegiven output_path filepath
    Specifications:
    - All arrays are numpy arrays with one row
    """

    def __init__(self,
                sample_path,
                filter_path,
                output_path
                ):
        """Initializes object according to class specifications."""

        # Read files
        print('\nReading sample file \t"%s"'%(sample_path))
        x_sample, fs_sample =  self.read_audio_file(sample_path)
        print('\nReading filter file \t"%s"'%(filter_path))
        x_filter, fs_filter =  self.read_audio_file(filter_path)
        # Normalize files
        x_sample = self.normalize_audio(x_sample)
        x_filter = self.normalize_audio(x_filter)

        assert fs_sample == fs_sample, "Sample and filter have uncompatible framerates (must be same)."

        # Filter sample with convolution
        print('Filtering sample through FIR-filter')
        x = self.fir_filter(x_sample, x_filter)
        fs = fs_sample
        x = self.normalize_audio(x)*.9

        # Store filtered sample
        print('Writing filtered sample to \t"%s"'%(output_path))
        self.write_audio_file(output_path, x, fs)
        self.filtered_sample = x
        self.fs = fs

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

    def fir_filter(self, x, h):
        """This function filters according to
            y_n = sum_{k=0}^{M-1} h_k * x(n-k)
        """
        # alt 1. Numpy convolve
        return np.convolve(x,h)

        # alt 2. Numpy dot produkt
        y = np.zeros(len(x))
        M = len(h)
        x = np.concatenate((np.zeros(M), x, np.zeros(M))) # Add zeroes before x for convolutions
        for n in range(M,len(x)-M):
            if n % 10000 == 0: print('Iterating over %s indexes, currently at n = %s'%(len(x),n))
            y[n-M] = np.dot(h, x[n+M:n:-1])
        return(y)


        # alt 3. Nestled for loops
        y = np.zeros(len(x))
        x = np.concatenate((np.zeros(len(h)), x)) # Add zeroes before x for convolutions
        for n in range(len(h),len(x)):
            if n % 1000 == 0: print('Iterating over %s indexes, currently at n = %s'%(len(x),n))
            for k in range(len(h)):
                y[n-len(h)] += h[k]*x[n-k]
        return(y)

def main():
    print(50*'-')
    # Get filepaths to .wav files of sample folder
    sample_folder = 'samples'
    sample_names = os.listdir(sample_folder)
    sample_names = [name for name in sample_names if name[-4:]=='.wav']
    sample_paths = [sample_folder+'/'+name for name in sample_names]

    # Print prompt samples
    print('The following .wav files was found in "/samples" directory:')
    [print('\t', x) for x in sample_names]
    filter_dur = input('Enter duration for FIR filter in ms (150 is recommended):\n\t ')
    try:    filter_dur = float(filter_dur)
    except: print('Error: Input must be float or integer, aborting program.'); sys.exit()

    # Check if filters exists
    filter_folder = 'FIR_filters/%s_ms'%(int(filter_dur))
    if not os.path.exists(filter_folder):
        print('No filters found in folder "%s". Please compute them with "create_fir_filter.py"'%(filter_folder))
        exit()

    # Get filepaths to .wav files of filter folder
    filter_names = os.listdir(filter_folder)
    filter_names = [name for name in filter_names if name[-4:]=='.wav']
    filter_paths = [filter_folder+'/'+name for name in filter_names]

    # Print prompt filters
    print('The following .wav files was found in "/%s":'%(filter_folder))
    [print('\t', x) for x in filter_names]


    for sample_name, sample_path in zip(sample_names, sample_paths):
        for filter_name, filter_path in zip(filter_names, filter_paths):
            output_path = 'filtered_samples/%s_ms/%s/%s'%(int(filter_dur), sample_name, filter_name)
            filtered_sample = Filter_Sample(sample_path,filter_path,output_path)
    exit()

if __name__ == '__main__':
    main()
