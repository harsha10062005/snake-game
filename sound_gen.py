import math
import struct
import wave
import os

def write_wav(filename, samples, sample_rate=22050):
    """Writes float samples (-1.0 to 1.0) as 16-bit mono PCM WAV file."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with wave.open(filename, 'w') as w:
        w.setnchannels(1)      # Mono
        w.setsampwidth(2)       # 16-bit
        w.setframerate(sample_rate)
        
        for sample in samples:
            # Clamp sample to [-1.0, 1.0]
            sample = max(-1.0, min(1.0, sample))
            # Convert to 16-bit signed integer
            val = int(sample * 32767)
            w.writeframesraw(struct.pack('<h', val))

def generate_food_sound(filename, sample_rate=22050):
    """Generates a pleasant retro chirp sound for eating food."""
    duration = 0.12  # seconds
    num_samples = int(duration * sample_rate)
    samples = []
    
    for i in range(num_samples):
        t = i / sample_rate
        # Frequency sweep from 500 Hz to 1200 Hz
        f = 500 + (1200 - 500) * (t / duration)
        # Phase is 2 * pi * integral of f(t) dt
        # integral of f(t) is 500*t + 350*t^2/duration
        phase = 2 * math.pi * (500 * t + 350 * (t ** 2) / duration)
        
        # Exponential volume decay
        envelope = (1.0 - t / duration) * math.exp(-2.0 * t / duration)
        
        # Combined wave (sine + subtle triangle for character)
        sine = math.sin(phase)
        tri = abs((phase / math.pi) % 2 - 1) * 2 - 1
        wave_val = 0.8 * sine + 0.2 * tri
        
        samples.append(wave_val * envelope * 0.4)  # moderate volume
        
    write_wav(filename, samples, sample_rate)

def generate_gameover_sound(filename, sample_rate=22050):
    """Generates a retro descending chiptune sound for Game Over."""
    duration = 0.5  # seconds
    num_samples = int(duration * sample_rate)
    samples = []
    
    for i in range(num_samples):
        t = i / sample_rate
        # Descending frequency from 350 Hz down to 80 Hz
        f = 350 - (350 - 80) * (t / duration)
        phase = 2 * math.pi * (350 * t - 135 * (t ** 2) / duration)
        
        # Decay volume envelope
        envelope = 1.0 - t / duration
        
        # Square wave for a buzzier, dramatic chiptune effect
        # sign of sin
        square = 1.0 if math.sin(phase) >= 0 else -1.0
        
        samples.append(square * envelope * 0.25)
        
    write_wav(filename, samples, sample_rate)

def generate_music_loop(filename, sample_rate=22050):
    """Generates a pleasant, repeating 8-bit chiptune loop."""
    # Settings
    bpm = 115
    beat_duration = 60.0 / bpm  # seconds per beat (~0.52s)
    total_beats = 16
    total_duration = beat_duration * total_beats  # ~8.35s
    num_samples = int(total_duration * sample_rate)
    
    # Initialize audio buffer
    buffer = [0.0] * num_samples
    
    # Simple retro synth ADSR-like envelope
    def add_note(freq, start_beat, duration_beats, volume, waveform='sine'):
        start_time = start_beat * beat_duration
        note_duration = duration_beats * beat_duration
        
        start_idx = int(start_time * sample_rate)
        end_idx = min(num_samples, int((start_time + note_duration) * sample_rate))
        
        for idx in range(start_idx, end_idx):
            t_note = (idx - start_idx) / sample_rate
            phase = 2 * math.pi * freq * t_note
            
            # Simple envelope: rapid rise, slow decay
            if t_note < 0.02:
                envelope = t_note / 0.02
            else:
                envelope = max(0.0, 1.0 - (t_note - 0.02) / (note_duration - 0.02))
            
            # Add exponential decay filter behavior
            envelope *= math.exp(-1.5 * t_note / note_duration)
            
            if waveform == 'sine':
                val = math.sin(phase)
            elif waveform == 'triangle':
                val = abs((phase / math.pi) % 2 - 1) * 2 - 1
            elif waveform == 'square':
                val = 1.0 if math.sin(phase) >= 0 else -1.0
            else:
                val = math.sin(phase)
                
            buffer[idx] += val * envelope * volume

    # Define frequencies
    # A minor chord progression: Am, F, C, G
    freqs = {
        'A2': 110.00, 'B2': 123.47, 'C3': 130.81, 'D3': 146.83, 'E3': 164.81, 'F3': 174.61, 'G3': 196.00,
        'A3': 220.00, 'B3': 246.94, 'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23, 'G4': 392.00,
        'A4': 440.00, 'B4': 493.88, 'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'F5': 698.46, 'G5': 783.99,
        'A5': 880.00
    }
    
    # 1. Bassline (simple walking bass, triangle wave)
    bass_notes = [
        # Am (beats 0-3)
        ('A2', 0.0, 0.75), ('E3', 1.0, 0.75), ('A2', 2.0, 0.75), ('C3', 3.0, 0.75),
        # F (beats 4-7)
        ('F2', 4.0, 0.75), ('C3', 5.0, 0.75), ('F2', 6.0, 0.75), ('A2', 7.0, 0.75),
        # C (beats 8-11)
        ('C3', 8.0, 0.75), ('G3', 9.0, 0.75), ('C3', 10.0, 0.75), ('E3', 11.0, 0.75),
        # G (beats 12-15)
        ('G2', 12.0, 0.75), ('D3', 13.0, 0.75), ('G2', 14.0, 0.75), ('B2', 15.0, 0.75),
    ]
    # Standardize octave values for missing low octaves
    freqs['F2'] = 87.31
    freqs['G2'] = 98.00
    
    for note, start, dur in bass_notes:
        add_note(freqs[note], start, dur, volume=0.22, waveform='triangle')
        
    # 2. Arpeggio / Harmony (soft square wave, repeating patterns)
    arp_notes = [
        # Am
        ('A3', 0.0, 0.5), ('C4', 0.5, 0.5), ('E4', 1.0, 0.5), ('A4', 1.5, 0.5),
        ('C4', 2.0, 0.5), ('E4', 2.5, 0.5), ('A4', 3.0, 0.5), ('E4', 3.5, 0.5),
        # F
        ('F3', 4.0, 0.5), ('A3', 4.5, 0.5), ('C4', 5.0, 0.5), ('F4', 5.5, 0.5),
        ('A3', 6.0, 0.5), ('C4', 6.5, 0.5), ('F4', 7.0, 0.5), ('C4', 7.5, 0.5),
        # C
        ('C3', 8.0, 0.5), ('E3', 8.5, 0.5), ('G3', 9.0, 0.5), ('C4', 9.5, 0.5),
        ('E3', 10.0, 0.5), ('G3', 10.5, 0.5), ('C4', 11.0, 0.5), ('G3', 11.5, 0.5),
        # G
        ('G3', 12.0, 0.5), ('B3', 12.5, 0.5), ('D4', 13.0, 0.5), ('G4', 13.5, 0.5),
        ('B3', 14.0, 0.5), ('D4', 14.5, 0.5), ('G4', 15.0, 0.5), ('D4', 15.5, 0.5),
    ]
    for note, start, dur in arp_notes:
        add_note(freqs[note], start, dur, volume=0.08, waveform='square')
        
    # 3. Lead Melody (soft sine wave, catchy melody)
    melody = [
        # Am
        ('E5', 0.0, 1.5), ('D5', 1.5, 0.5), ('C5', 2.0, 1.0), ('B4', 3.0, 1.0),
        # F
        ('A4', 4.0, 2.0), ('C5', 6.0, 1.0), ('E5', 7.0, 1.0),
        # C
        ('G5', 8.0, 1.5), ('F5', 9.5, 0.5), ('E5', 10.0, 1.0), ('D5', 11.0, 1.0),
        # G
        ('B4', 12.0, 2.0), ('D5', 14.0, 1.0), ('G5', 15.0, 1.0),
    ]
    for note, start, dur in melody:
        add_note(freqs[note], start, dur, volume=0.15, waveform='sine')
        
    write_wav(filename, buffer, sample_rate)

def main():
    import sys
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sounds_dir = os.path.join(base_dir, "sounds")
    
    print("Generating game sounds...")
    generate_food_sound(os.path.join(sounds_dir, "food.wav"))
    print("Generated food.wav")
    generate_gameover_sound(os.path.join(sounds_dir, "gameover.wav"))
    print("Generated gameover.wav")
    generate_music_loop(os.path.join(sounds_dir, "music.wav"))
    print("Generated music.wav")
    print("Sound generation complete!")

if __name__ == "__main__":
    main()
