import styled from "@emotion/styled";
import { Button } from "@mui/material";
import { useEffect, useState } from "react";
import { useMIDIOutput } from "../hooks/useMidiOutput";



const AudioScreen = props => {
    const { files, midiOutput } = props;
  
    const { cc } = useMIDIOutput(midiOutput);
    const [ selectedOutput, setSelectedOutput ] = useState({ name: 'default' });
  
    const [ currentFile, setCurrentFile ] = useState(0);
  
    
    useEffect(()=>{
      
      const AudioElement = document.getElementById('track01');
      
      function handleOutputChange(channel){
        if (!channel) return;
      
        if (selectedOutput) {
          cc(0, selectedOutput, 9);
          setSelectedOutput(channel);
          cc(127, channel, 9);
        };
        
        setSelectedOutput(channel);
        cc(127, channel, 9);
      }
  
      handleOutputChange(files[currentFile].output)
      document.getElementById(files[currentFile].src).scrollIntoView({behavior: "smooth", block: "center"});
      AudioElement.play();
  
    },[currentFile])
    
    
  
    function handleNext(){
      setCurrentFile(state => ((state + 1)%files.length) )
    }
    function handlePrevious(){
      setCurrentFile(state => !state ? state : (state - 1)%files.length )
    }
  
    return <Container>
        <div>
      <audio controls style={{width: '100%'}}
        onEnded={handleNext}
        src={files[currentFile]?.src}  
        id='track01'>  
      </audio>
      <div>
        <Button children='Previous Track' variant='outlined' onClick={handlePrevious} disabled={!currentFile} />
        <Button children='Next Track' variant='outlined' onClick={handleNext} />
      </div>
        <p children={`Track source: ${files[currentFile].src}`}/>
        <p children={`Track index: ${currentFile}`}/>
        </div>

      <FileListContainer>
        {
          files.map((file, idx) =>
            <FileListItem id={file.src} isActive={idx === currentFile} key={idx} 
            children={file.src} onClick={()=>setCurrentFile(idx)}/>
          )
        }
      </FileListContainer>
    </Container>
  }

  export default AudioScreen

  const Container = styled.div`
    width: 100%;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1em;
    padding: 2em;
  `
  const FileListContainer = styled.div`
    width: 100%;
    max-height: 40vh;
    overflow-y: scroll;
    overflow-x: hidden;
 `
  const FileListItem = styled.p`
    cursor: pointer;
    width: 100%;
    padding: 0.5em;
    background-color: ${props => props.isActive ? '#202020' : '#353535'};
  `