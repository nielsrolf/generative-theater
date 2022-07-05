import * as React from 'react';
import FormGroup from '@mui/material/FormGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import Switch from '@mui/material/Switch';

export default function SwitchLabels({ label, callback, value }) {
  return (
    <FormGroup>
      <FormControlLabel control={<Switch onChange={callback} value={value} />} label={label} />
    </FormGroup>
  );
}
