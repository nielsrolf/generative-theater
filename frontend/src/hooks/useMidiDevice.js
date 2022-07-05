import { useState } from "react"
import { useMIDI } from "./useMidi"

function useMidiDevice(){
    const { outputs } = useMIDI()
    const [ midiOutput, setMidiOutput ] = useState(outputs[0] || {})

    const handleChangeMidiOutput = event => {
    setMidiOutput(event.target.value)
  }

  return ({
    outputs,
    midiOutput,
    handleChangeMidiOutput,
  })
}

export default useMidiDevice