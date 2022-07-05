import styled from '@emotion/styled'
import BasicModal from './components/Modal';
import useAudioDevice from './hooks/useAudioDevice';
import useMidiDevice from './hooks/useMidiDevice';
import AudioScreen from './screens/AudioScreen';
import SettingsScreen from './screens/SettingsScreen';


function App() {

  const files = [
    ...Array(10).fill({src:'', name: ''}).map(
    (file, index) => ({ src:`assets/L${index+1}.wav`, output: 102 }) ), 
    ...Array(1).fill({ src:'assets/C1.wav', output: 104 })
  ];

  const AudioDevice = useAudioDevice()
  const MidiDevice = useMidiDevice()

  return (<>

    <Container>
      {
        !MidiDevice.midiOutput.name || <AudioScreen files={files} midiOutput={MidiDevice.midiOutput}/>
      }
    </Container>

    <BasicModal title='Settings'>          
      <SettingsScreen {...AudioDevice} {...MidiDevice} />
    </BasicModal>
    </>
  );
}

export default App;

const Container = styled.div`
width: 100%;
min-height: 100vh;

display: flex;
justify-content: center;
align-items: center;
`
