import torch
import torchaudio.functional as F
import numpy as np
from demucs.api import Separator

class DemucsProcessor:
    def __init__(self):
        self.separator = Separator("htdemucs", device="cpu", jobs=4)

    def process(self, input_filepath: str) -> np.ndarray:
        origin, separated = self.separator.separate_audio_file(input_filepath)
        vocals_tensor = separated["vocals"]
        
        vocals_mono = vocals_tensor.mean(dim=0, keepdim=True)
        
        target_sr = 16000
        if self.separator.samplerate != target_sr:
            vocals_16k = F.resample(
                vocals_mono, 
                orig_freq=self.separator.samplerate, 
                new_freq=target_sr
            )
        else:
            vocals_16k = vocals_mono
            
        audio_np = vocals_16k.squeeze(0).numpy()
        
        return audio_np