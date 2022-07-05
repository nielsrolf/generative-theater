import { MIDIConstants } from '../utils/constants';

export const useMIDIOutput = (output) => {

  if (!output) return {};
  const noteOn = (note, velocity = 127, channel = 1) => {
    const noteOnAndChannel = MIDIConstants.noteOn | getChannel(channel);
    output.send([noteOnAndChannel, note, velocity]);
  };
  const noteOff = (note, velocity = 127, channel = 1) => {
    const noteOffAndChannel = MIDIConstants.noteOff | getChannel(channel);
    output.send([noteOffAndChannel, note, velocity]);
  };
  const cc = (value, control = 0x14, channel = 1) => {
    const ccAndChannel = MIDIConstants.cc | getChannel(channel);
    output.send([ccAndChannel, control, value]);
  };
  return { noteOn, noteOff, cc };
};

const getChannel = (channel) => {
  if (channel < 1 || channel > 16) return 0; //Channel 1
  return channel - 1;
};