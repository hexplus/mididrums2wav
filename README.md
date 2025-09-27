# MIDI to Audio Converter (Drums)

Batch convert multiple MIDI drum files to high-quality audio WAV files using Carla and MT Power Drum Kit 2 with your custom drum sounds. Process entire folders of MIDI files automatically with one command.

## Requirements

### Software Dependencies
- **Carla**: Audio plugin host - Install to `C:\Program Files\Carla\Carla\Carla.exe`
  - Download: https://kx.studio/Applications:Carla
- **MT Power Drum Kit 2**: VST3 drum plugin - Install to `C:\Program Files\Common Files\VST3\`
  - Download: https://www.powerdrumkit.com/download76187.php
- **VB-Audio Virtual Cable**: Virtual audio routing
  - Download: https://vb-audio.com/Cable/index.htm

### Python Dependencies
```bash
pip install -r requirements.txt
```

Required packages: `mido`, `sounddevice`, `numpy`, `scipy`

## Setup

### 1. Create Your Drum Configuration
1. Open Carla
2. Add MT Power Drum Kit 2 plugin
3. Configure your custom drum sounds and settings
4. Set audio output to VB-Audio Virtual Cable
5. Save project: **File > Save Project As > project.carxp**

### 2. Prepare MIDI Files
- Create a `midis` directory in the project folder
- Place all your MIDI drum files (`.mid` or `.midi`) in the `midis` directory
- The script will process all MIDI files in this directory automatically

## Usage

### Run the Batch Converter

**GUI Mode (Default):**
```bash
python midi_to_audio.py
```

**Headless Mode (No GUI):**
```bash
python midi_to_audio.py --headless
# or
python midi_to_audio.py --no-gui
```

**Help:**
```bash
python midi_to_audio.py --help
```

### Automatic Batch Process
1. **File Detection**: Scans `midis` directory for all MIDI files
2. **VB-Audio Detection**: Script automatically configures virtual audio routing
3. **Carla Launch**: Opens Carla with your `project.carxp` configuration
4. **Auto-Load**: Your custom MT Power Drum Kit setup loads automatically
5. **Verification**: 8-second wait to verify everything loaded correctly
6. **Batch Conversion**: Processes each MIDI file one by one:
   - Sends MIDI events to the drum kit with precise timing
   - Records output through VB-Audio Virtual Cable
   - Normalizes audio and saves as WAV file
   - 2-second pause between files
7. **Summary Report**: Shows successful and failed conversions

### Output
- **Directory**: `wavs/` (automatically created)
- **Files**: One WAV file per MIDI file (e.g., `song1.mid` → `wavs/song1.wav`)
- **Format**: 16-bit WAV, 44.1 kHz, mono
- **Quality**: High-quality drum sounds with your custom configuration

## Files

- `midi_to_audio.py` - Main batch conversion script
- `midis/` - **Input directory**: Place your MIDI files here
- `wavs/` - **Output directory**: Converted WAV files (automatically created)
- `project.carxp` - **Required**: Your Carla project with custom drum setup
- `requirements.txt` - Python dependencies

## Success Indicators

### ✅ Conversion Successful
- **Max amplitude > 0.1**: Real drum audio detected
- **File size > 100KB**: Contains actual audio data
- **Duration matches MIDI**: Correct timing
- **No errors**: Script completes successfully

### ⚠️ Troubleshooting
- **Low amplitude < 0.001**: Check VB-Audio configuration in Carla
- **Silent output**: Verify MT Power Drum Kit is loaded and audible
- **Wrong duration**: Check MIDI file format and timing

## Technical Details

- **Audio Routing**: VB-Audio Virtual Cable for clean signal path
- **MIDI Timing**: Precise playback using `mido` library
- **Normalization**: Audio normalized to 95% to prevent clipping
- **Buffer**: 3-second buffer added for reverb tails
- **No Cleanup**: Your `project.carxp` configuration is preserved

## Batch Processing Features

- **Multiple Files**: Process entire folders of MIDI files automatically
- **Progress Tracking**: Shows current file progress (e.g., "3/10 files")
- **Error Handling**: Continues processing even if some files fail
- **Summary Report**: Final statistics of successful vs failed conversions
- **Organized Output**: Each MIDI file gets its own corresponding WAV file
- **Single Setup**: Configure Carla once, process unlimited files
- **GUI & Headless Modes**: Run with or without Carla GUI interface

## Headless Mode

**Perfect for:**
- **Server environments** without display
- **Automated workflows** and CI/CD pipelines
- **Batch processing** large numbers of files
- **Background processing** without user interaction

**Benefits:**
- **Lower resource usage** (no GUI rendering)
- **Faster startup** times
- **Server-friendly** operation
- **Automated deployment** compatible

## Command Line Options

```bash
python midi_to_audio.py [OPTIONS]

Options:
  --headless    Run Carla in headless mode (no GUI)
  --no-gui      Alias for --headless
  -h, --help    Show help message and exit

Examples:
  python midi_to_audio.py                    # GUI mode (default)
  python midi_to_audio.py --headless         # Headless mode
  python midi_to_audio.py --no-gui          # Same as --headless
```

## Notes

- The script requires your pre-configured `project.carxp` file
- Supports both `.mid` and `.midi` file extensions
- All MIDI events are sent with proper timing to the drum kit
- VB-Audio provides isolated audio capture without system sounds
- Process is fully automated after initial Carla project setup
- Carla remains open during batch processing for efficiency
- Headless mode falls back to GUI mode if unsupported

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.