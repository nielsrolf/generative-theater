import { MenuItem, Select, Box, Typography } from '@mui/material';

const SettingsScreen = props => {

    const { 
        devices, 
        handleDeviceChange, 
        currentDevice,
        outputs, 
        midiOutput, 
        handleChangeMidiOutput } = props

    return <Box>
      <Typography id="modal-modal-title" variant="h6" component="h2">
        Select your soundcard.
      </Typography>
        
      <Select fullWidth 
        label="Device Output" 
        labelId="select-device-output"
        id="select-device-output" 
        defaultValue='default' 
        value={currentDevice}
        onChange={handleDeviceChange}>
          
        { !devices.length ||
          devices.map((output, index) => 
          <MenuItem value={output} key={index}>{output.label}</MenuItem>
          )
        }
        
      </Select>
  
      <div style={{width: '100%', height: 20}}/>
  
      <Typography id="modal-MIDI-title" variant="h6" component="h2">
        Select your MIDI output.
      </Typography>
        
      <Select fullWidth 
        label="Midi Output" 
        labelId="select-midi-output"
        id="select-midi-output" 
        defaultValue='default' 
        value={midiOutput}
        onChange={handleChangeMidiOutput}>
          
        { !outputs.length ||
          outputs.map((output, index) => 
          <MenuItem value={output} key={index}>{output.name}</MenuItem>
          )
        }
        
      </Select>
  
    <div style={{width: '100%', height: 20}}/>
    </Box>
  }

  export default SettingsScreen