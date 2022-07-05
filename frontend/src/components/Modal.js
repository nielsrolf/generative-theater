import * as React from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Modal from '@mui/material/Modal';

const style = {
  position: 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: 400,
  bgcolor: '#202020',
  boxShadow: 1,
  p: 4,
};

export default function BasicModal(props) {
  const { title } = props
  const [open, setOpen] = React.useState(true);
  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  return (
    <div style={{position: 'fixed', top: 0, right: 0}}>
      <Button onClick={handleOpen}> {title} </Button>
      <Modal
        open={open}
        onClose={handleClose}
        aria-labelledby="modal-modal-title"
        aria-describedby="modal-modal-description"
      >
        <Box sx={style}>

            {props.children}

            <Button variant='outlined' onClick={handleClose}>
                Continue
            </Button>

        </Box>
      </Modal>
    </div>
  );
}