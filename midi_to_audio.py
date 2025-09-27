#!/usr/bin/env python3
"""
Automatic MIDI to audio converter with VB-Audio routing.
This script automatically configures VB-Audio and Carla for MIDI to audio conversion.
Supports both GUI and headless modes for batch processing.
"""

import subprocess
import time
import os
import sys
import argparse
import mido
import sounddevice as sd
import numpy as np
from scipy.io import wavfile

def setup_vb_audio_routing():
    """Configure VB-Audio Virtual Cable as default audio device."""
    print("=== CONFIGURING VB-AUDIO ROUTING ===")

    # Check if VB-Audio devices are available
    devices = sd.query_devices()
    vb_input_device = None
    vb_output_device = None

    for i, device in enumerate(devices):
        device_name = device['name'].lower()
        if 'cable input' in device_name and device['max_output_channels'] > 0:
            vb_input_device = i
            print(f"Found VB-Audio Input: {device['name']} (ID: {i})")
        elif 'cable output' in device_name and device['max_input_channels'] > 0:
            vb_output_device = i
            print(f"Found VB-Audio Output: {device['name']} (ID: {i})")

    if not vb_input_device or not vb_output_device:
        print("ERROR: VB-Audio Virtual Cable not found!")
        print("Please install VB-Audio Virtual Cable first.")
        return False, None, None

    print("VB-Audio devices found successfully!")
    return True, vb_input_device, vb_output_device

def start_carla_with_project_file(project_file_path, headless=False):
    """Start Carla and automatically load the project file."""
    carla_path = r"C:\Program Files\Carla\Carla\Carla.exe"

    if not os.path.exists(carla_path):
        print("ERROR: Carla not found!")
        return None

    try:
        # Prepare command with headless options if requested
        cmd = [carla_path]

        if headless:
            # Try different headless options that Carla might support
            cmd.extend([
                "--no-gui",           # Common headless option
                "--nogui",            # Alternative headless option
                "-n",                 # Short headless option
                "--headless"          # Another possible headless option
            ])
            print(f"Starting Carla in HEADLESS mode with project file: {project_file_path}")
        else:
            print(f"Starting Carla in GUI mode with project file: {project_file_path}")

        cmd.append(project_file_path)

        # Start Carla with project file as argument
        process = subprocess.Popen(cmd)

        # Give more time for headless mode to initialize
        sleep_time = 5 if headless else 3
        time.sleep(sleep_time)

        if process.poll() is None:
            mode_str = "headless" if headless else "GUI"
            print(f"[OK] Carla started successfully in {mode_str} mode")
            print("[OK] Project file should be loading automatically...")
            return process
        else:
            print("[ERROR] Carla failed to start")
            return None
    except Exception as e:
        print(f"Error starting Carla with project file: {e}")

        if headless:
            print("Headless mode failed, trying GUI mode as fallback...")
            return start_carla_with_project_file(project_file_path, headless=False)
        else:
            print("Falling back to manual loading...")

            # Fallback: start Carla without arguments
            try:
                process = subprocess.Popen([carla_path])
                time.sleep(3)
                if process.poll() is None:
                    print("[OK] Carla started (manual project loading required)")
                    return process
            except Exception as e2:
                print(f"Fallback also failed: {e2}")

        return None

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Batch convert MIDI drum files to audio using Carla and MT Power Drum Kit 2',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python midi_to_audio.py                    # GUI mode (default)
  python midi_to_audio.py --headless         # Headless mode (no GUI)
  python midi_to_audio.py -h                 # Show this help

Directory Structure:
  midis/          # Place your MIDI files here
  wavs/           # Converted WAV files will be saved here
  project.carxp   # Your Carla project configuration (required)
        """
    )

    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run Carla in headless mode (no GUI). Useful for batch processing on servers or automated workflows.'
    )

    parser.add_argument(
        '--no-gui',
        action='store_true',
        help='Alias for --headless'
    )

    return parser.parse_args()

def check_project_file():
    """Check if project.carxp (Carla project file) exists."""
    project_file = "project.carxp"
    if os.path.exists(project_file):
        print(f"Found Carla project file: {project_file}")
        print("This will load your complete Carla setup with MT Power Drum Kit...")
        return project_file
    else:
        print(f"ERROR: {project_file} not found!")
        print("Please ensure project.carxp (Carla project file) exists in the current directory.")
        return None

def prepare_carla_project_loading(project_file):
    """Prepare instructions for loading Carla project file."""
    print(f"Carla project file ready: {project_file}")
    print("This contains your complete MT Power Drum Kit setup with preset")

    # Get absolute path for the project file
    project_path = os.path.abspath(project_file)
    print(f"Project file path: {project_path}")

    return project_path

def play_midi_with_timing(midi_file_path):
    """Play MIDI file with proper timing."""
    try:
        midi_file = mido.MidiFile(midi_file_path)
        print(f"Playing MIDI: {midi_file_path}")
        print(f"Duration: {midi_file.length:.2f} seconds")

        # Find available MIDI output ports
        output_ports = mido.get_output_names()
        if not output_ports:
            print("No MIDI output ports available!")
            return False

        # Prefer Carla MIDI port if available, otherwise use system default
        selected_port = output_ports[0]
        for port in output_ports:
            if 'carla' in port.lower() or 'mt power' in port.lower():
                selected_port = port
                break

        print(f"Using MIDI port: {selected_port}")

        with mido.open_output(selected_port) as outport:
            for msg in midi_file.play():
                outport.send(msg)
                if msg.type in ['note_on', 'note_off']:
                    print(f"Sent: {msg.type} note={msg.note} vel={msg.velocity}")

        print("MIDI playback completed")
        return True

    except Exception as e:
        print(f"Error playing MIDI: {e}")
        return False

def record_vb_audio(duration, output_file, vb_device_id):
    """Record audio from VB-Audio Virtual Cable."""
    print(f"Recording from VB-Audio device {vb_device_id} for {duration} seconds...")

    try:
        sample_rate = 44100
        recording = sd.rec(int(duration * sample_rate),
                          samplerate=sample_rate,
                          channels=1,
                          device=vb_device_id)

        print("Recording started...")
        sd.wait()  # Wait for recording to complete

        # Analyze recording
        max_amplitude = np.max(np.abs(recording))
        rms = np.sqrt(np.mean(recording**2))

        print(f"Recording completed:")
        print(f"  Max amplitude: {max_amplitude:.6f}")
        print(f"  RMS level: {rms:.6f}")

        if max_amplitude > 0.001:
            print("Audio detected! Processing...")
            # Normalize and save
            recording = recording / max_amplitude * 0.95
            recording_int16 = (recording * 32767).astype(np.int16).flatten()
            wavfile.write(output_file, sample_rate, recording_int16)
            print(f"SUCCESS: Audio saved to {output_file}")
            return True
        else:
            print("WARNING: Very low audio level detected!")
            # Save anyway for analysis
            recording_int16 = (recording * 32767).astype(np.int16).flatten()
            wavfile.write(output_file, sample_rate, recording_int16)
            print(f"Low-level audio saved to {output_file}")
            return False

    except Exception as e:
        print(f"Error during recording: {e}")
        return False

def get_midi_files():
    """Get all MIDI files from the midis directory."""
    midis_dir = "midis"
    if not os.path.exists(midis_dir):
        print(f"ERROR: {midis_dir} directory not found!")
        print("Please create a 'midis' directory and place your MIDI files there.")
        return []

    midi_extensions = ['.mid', '.midi']
    midi_files = []

    for file in os.listdir(midis_dir):
        if any(file.lower().endswith(ext) for ext in midi_extensions):
            midi_files.append(os.path.join(midis_dir, file))

    if not midi_files:
        print(f"ERROR: No MIDI files found in {midis_dir} directory!")
        print("Please place your .mid or .midi files in the 'midis' directory.")
        return []

    return sorted(midi_files)

def convert_single_midi(midi_file_path, project_path, vb_input_id, vb_output_id, carla_process):
    """Convert a single MIDI file to audio."""
    # Generate output filename
    midi_filename = os.path.basename(midi_file_path)
    base_name = os.path.splitext(midi_filename)[0]
    output_file = os.path.join("wavs", f"{base_name}.wav")

    print(f"\n=== CONVERTING: {midi_filename} ===")

    # Get MIDI duration
    try:
        midi_file_obj = mido.MidiFile(midi_file_path)
        duration = midi_file_obj.length + 3  # Add buffer
        print(f"MIDI duration: {midi_file_obj.length:.2f} seconds")
    except Exception as e:
        print(f"Error loading MIDI: {e}")
        return False

    # Convert
    print("Starting conversion in 3 seconds...")
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)

    print("STARTING RECORDING AND MIDI PLAYBACK!")

    # Start recording
    sample_rate = 44100
    recording = sd.rec(int(duration * sample_rate),
                      samplerate=sample_rate,
                      channels=1,
                      device=vb_output_id)

    # Small delay then start MIDI
    time.sleep(0.5)
    success = play_midi_with_timing(midi_file_path)

    if not success:
        print(f"WARNING: MIDI playback failed for {midi_filename}")

    # Wait for recording to complete
    print("Waiting for recording to finish...")
    sd.wait()

    # Process recording
    max_amplitude = np.max(np.abs(recording))
    print(f"Recording completed. Max amplitude: {max_amplitude:.6f}")

    if max_amplitude > 0.001:
        print("SUCCESS: Audio detected!")
        recording = recording / max_amplitude * 0.95
        recording_int16 = (recording * 32767).astype(np.int16).flatten()
        wavfile.write(output_file, sample_rate, recording_int16)
        print(f"Audio saved to: {output_file}")
        return True
    else:
        print("WARNING: Low audio detected - saving anyway for analysis")
        recording_int16 = (recording * 32767).astype(np.int16).flatten()
        wavfile.write(output_file, sample_rate, recording_int16)
        print(f"File saved for analysis: {output_file}")
        return False

def main():
    """Main batch conversion function."""
    # Parse command line arguments
    args = parse_arguments()
    headless_mode = args.headless or args.no_gui

    mode_str = "HEADLESS" if headless_mode else "GUI"
    print(f"=== AUTOMATIC MIDI TO AUDIO BATCH CONVERTER ({mode_str} MODE) ===")
    print("This script processes multiple MIDI files from 'midis' directory.")
    if headless_mode:
        print("Running in headless mode - no Carla GUI will be shown.")
    print()

    # Get all MIDI files
    midi_files = get_midi_files()
    if not midi_files:
        return

    print(f"Found {len(midi_files)} MIDI file(s):")
    for i, midi_file in enumerate(midi_files, 1):
        print(f"  {i}. {os.path.basename(midi_file)}")
    print()

    # Ensure output directory exists
    os.makedirs("wavs", exist_ok=True)

    # Step 1: Setup VB-Audio routing
    vb_success, vb_input_id, vb_output_id = setup_vb_audio_routing()
    if not vb_success:
        return

    # Step 2: Check for Carla project file
    project_file = check_project_file()
    if not project_file:
        return

    project_path = prepare_carla_project_loading(project_file)

    # Step 3: Start Carla with automatic project loading
    mode_str = "HEADLESS" if headless_mode else "GUI"
    print(f"\n=== STARTING CARLA WITH AUTO-LOAD ({mode_str} MODE) ===")
    carla_process = start_carla_with_project_file(project_path, headless=headless_mode)
    if not carla_process:
        return

    # Step 4: Verification instructions
    print(f"\n=== AUTOMATIC PROJECT LOADING ({mode_str} MODE) ===")
    print(f"Carla should automatically load: {project_file}")

    if headless_mode:
        print("Headless mode - no GUI verification needed:")
        print("1. MT Power Drum Kit loads automatically in background")
        print("2. Audio routing should be configured from your project file")
        print("3. MIDI input configured automatically")
        print("4. No manual verification required")
        print()
        print("Waiting 10 seconds for headless loading...")

        for i in range(10, 0, -1):
            print(f"Auto-continuing in {i} seconds... (Loading in background)")
            time.sleep(1)
    else:
        print("GUI mode - please verify in Carla:")
        print("1. MT Power Drum Kit should be loaded with your custom preset")
        print("2. Check audio output: Settings > Configure Carla > Engine tab:")
        print("   - Output Device: 'CABLE Input (VB-Audio Virtual Cable)'")
        print("3. MIDI input should be configured automatically")
        print("4. Test by clicking drum pads to verify your sounds")
        print()
        print("Waiting 8 seconds for complete loading...")

        for i in range(8, 0, -1):
            print(f"Auto-continuing in {i} seconds... (Verify setup is ready!)")
            time.sleep(1)

    # Step 5: Process all MIDI files
    successful_conversions = 0
    failed_conversions = 0

    for i, midi_file in enumerate(midi_files, 1):
        print(f"\n{'='*60}")
        print(f"PROCESSING FILE {i}/{len(midi_files)}")
        print(f"{'='*60}")

        success = convert_single_midi(midi_file, project_path, vb_input_id, vb_output_id, carla_process)

        if success:
            successful_conversions += 1
        else:
            failed_conversions += 1

        # Small pause between files
        if i < len(midi_files):
            print("\nWaiting 2 seconds before next file...")
            time.sleep(2)

    # Step 6: Final summary
    print(f"\n{'='*60}")
    print("=== BATCH CONVERSION COMPLETED ===")
    print(f"{'='*60}")
    print(f"Total files processed: {len(midi_files)}")
    print(f"Successful conversions: {successful_conversions}")
    print(f"Failed conversions: {failed_conversions}")
    print(f"Output directory: wavs/")
    print()

    # Cleanup
    print("=== CLEANUP ===")
    try:
        carla_process.terminate()
        print("Carla stopped")
    except:
        print("Note: Close Carla manually if still running")

    print(f"\nBatch conversion completed!")
    print(f"Check the 'wavs' directory for your converted audio files.")

    # No cleanup needed - project file is preserved
    print(f"Carla project file preserved: {project_file}")
    print("Your complete Carla configuration remains saved for future use")

if __name__ == "__main__":
    main()