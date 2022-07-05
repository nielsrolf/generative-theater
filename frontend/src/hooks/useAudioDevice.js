import { useEffect, useState } from 'react'

function useAudioDevice(){
    const [ devices, setDevices ] = useState([])
    const [ currentDevice, setCurrentDevice ] = useState('default')
  
    useEffect(()=>{
        async function GetAudioDevices() {
        await navigator.mediaDevices.getUserMedia({
            audio: { deviceId: undefined },
            video: false
        });
        const devices = await navigator.mediaDevices.enumerateDevices();
        const audioDevices = devices.filter((device) => device.kind === "audiooutput");
        setDevices(audioDevices)
        setCurrentDevice(audioDevices[0])
        }
        GetAudioDevices()
    },[])

  
    const audioElement = document.getElementById('track01');
    
    async function handleDeviceChange(e){
        await audioElement.setSinkId(e.target.value.deviceId);
        setCurrentDevice(e.target.value)
    }


    return ({
        devices,
        setDevices,
        handleDeviceChange,
        currentDevice
    })
}

export default useAudioDevice