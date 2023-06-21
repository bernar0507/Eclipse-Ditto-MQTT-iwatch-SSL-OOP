import numpy as np
from scipy.signal import butter, lfilter
import time
from datetime import datetime
import yaml

class IWatchSimulator:
    def _init_(self, config_path):
        with open(config_path, 'r') as stream:
            self.config = yaml.safe_load(stream)
        self.dict_dt = {}

    def compute_filter_coefficients(self):
        nyquist_rate = self.config['sampling']['rate']/2  # Nyquist rate
        cutoff_freq_norm = self.config['filter']['cutoff_freq']/nyquist_rate
        b, a = butter(2, cutoff_freq_norm, btype='low')

    def generate_data(self):
        t_start = time.time()
        while True:
            t = np.arange(0, self.config['sampling']['duration'], 1/self.config['sampling']['rate'])

            # Generate random heart rate within a range
            heart_rate = np.random.randint(self.config['heart_rate']['min'], self.config['heart_rate']['max']+1)

            # Add variability based on breathing rate
            breathing_rate = np.random.normal(15, 5)  # breaths per minute
            breathing_scale = 1 + self.config['variability_factors']['breathing'] * np.sin(2*np.pi*breathing_rate/60*t)
            x = self.config['heart_rate']['amplitude'] * breathing_scale * np.sin(2*np.pi*heart_rate/60*t)

            # Add variability based on physical activity
            activity_level = np.random.normal(1, 0.2)  # arbitrary units
            activity_scale = 1 + self.config['variability_factors']['activity'] * np.random.rand() * activity_level
            x = x * activity_scale

            # Add variability based on stress and emotions
            stress_scale = 1 + self.config['variability_factors']['stress'] * np.random.rand()
            x = x * stress_scale

            # Add variability based on age and gender
            age_scale = 1 + self.config['variability_factors']['age'] * np.random.normal(0, 1)
            gender_scale = 1 + self.config['variability_factors']['age'] * np.random.rand()
            x = x * age_scale * gender_scale

            # Get timestamp
            timestamp = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))

            # Update location based on the change in latitude and longitude
            self.config['location']['latitude'] += self.config['location']['delta_lat'] * self.config['sampling']['duration']
            self.config['location']['longitude'] += self.config['location']['delta_long'] * self.config['sampling']['duration']

            self.dict_dt['timestamp'] = timestamp
            self.dict_dt['latitude'] = self.config['location']['latitude']
            self.dict_dt['longitude'] = self.config['location']['longitude']
            self.dict_dt['heart_rate'] = heart_rate

            # Wait until the end of the duration
            t_elapsed = time.time() - t_start
            time.sleep(self.config['sampling']['duration'] - t_elapsed % self.config['sampling']['duration'])

            yield self.dict_dt
