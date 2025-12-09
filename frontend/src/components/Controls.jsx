import { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  FormGroup,
  FormControlLabel,
  Checkbox,
  RadioGroup,
  Radio,
  Slider,
  Button,
  CircularProgress
} from '@mui/material';
import { AutoFixHigh as ProcessIcon } from '@mui/icons-material';

/**
 * Componente para controlar opciones de anonimizacion.
 */
function Controls({ onProcess, disabled, loading }) {
  const [detectFaces, setDetectFaces] = useState(true);
  const [detectPlates, setDetectPlates] = useState(true);
  const [method, setMethod] = useState('blur');
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.5);
  const [blurKernelSize, setBlurKernelSize] = useState(99);
  const [pixelateBlocks, setPixelateBlocks] = useState(10);

  const handleProcess = () => {
    onProcess({
      detectFaces,
      detectPlates,
      method,
      confidenceThreshold,
      blurKernelSize,
      pixelateBlocks
    });
  };

  return (
    <Paper elevation={3} sx={{ p: 3, mt: 3 }}>
      <Typography variant="h6" gutterBottom>
        Opciones de Anonimizacion
      </Typography>

      {/* Que detectar */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle2" gutterBottom>
          Elementos a Detectar
        </Typography>
        <FormGroup>
          <FormControlLabel
            control={
              <Checkbox
                checked={detectFaces}
                onChange={(e) => setDetectFaces(e.target.checked)}
              />
            }
            label="Rostros Humanos"
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={detectPlates}
                onChange={(e) => setDetectPlates(e.target.checked)}
              />
            }
            label="Matriculas de vehiculos"
          />
        </FormGroup>
      </Box>

      {/* Metodo de anonimizacion */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle2" gutterBottom>
          Tecnica de Anonimizacion
        </Typography>
        <RadioGroup value={method} onChange={(e) => setMethod(e.target.value)}>
          <FormControlLabel
            value="blur"
            control={<Radio />}
            label="Gaussian blur (Desenfoque)"
          />
          <FormControlLabel
            value="pixelate"
            control={<Radio />}
            label="Pixelacion"
          />
          <FormControlLabel
            value="mask"
            control={<Radio />}
            label="Cuadro negro (Masking)"
          />
        </RadioGroup>
      </Box>

      {/* Umbral de confianza */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle2" gutterBottom>
          Umbral de Confianza: {(confidenceThreshold * 100).toFixed(0)}%
        </Typography>
        <Slider
          value={confidenceThreshold}
          onChange={(e, value) => setConfidenceThreshold(value)}
          min={0.3}
          max={0.9}
          step={0.05}
          marks={[
            { value: 0.3, label: '30%' },
            { value: 0.5, label: '50%' },
            { value: 0.7, label: '70%' },
            { value: 0.9, label: '90%' }
          ]}
          valueLabelDisplay="auto"
          valueLabelFormat={(value) => `${(value * 100).toFixed(0)}%`}
        />
        <Typography variant="caption" color="text.secondary">
          Mayor umbral = mas precision, menos detecciones
        </Typography>
      </Box>

      {/* Parametros especificos del metodo */}
      {method === 'blur' && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            Intensidad de Blur: {blurKernelSize}
          </Typography>
          <Slider
            value={blurKernelSize}
            onChange={(e, value) => setBlurKernelSize(value)}
            min={11}
            max={199}
            step={2}
            marks={[
              { value: 11, label: 'Bajo' },
              { value: 99, label: 'Medio' },
              { value: 199, label: 'Alto' }
            ]}
            valueLabelDisplay="auto"
          />
        </Box>
      )}

      {method === 'pixelate' && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            Bloques de Pixelacion: {pixelateBlocks}
          </Typography>
          <Slider
            value={pixelateBlocks}
            onChange={(e, value) => setPixelateBlocks(value)}
            min={2}
            max={30}
            step={1}
            marks={[
              { value: 2, label: 'Bajo' },
              { value: 10, label: 'Medio' },
              { value: 30, label: 'Alto' }
            ]}
            valueLabelDisplay="auto"
          />
          <Typography variant="caption" color="text.secondary">
            Menos bloques = mayor pixelacion
          </Typography>
        </Box>
      )}

      {/* Boton procesar */}
      <Button
        variant="contained"
        color="primary"
        size="large"
        fullWidth
        startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <ProcessIcon />}
        onClick={handleProcess}
        disabled={disabled || loading || (!detectFaces && !detectPlates)}
      >
        {loading ? 'Procesando...' : 'Anonimizar Imagen'}
      </Button>

      {(!detectFaces && !detectPlates) && (
        <Typography variant="caption" color="error" display="block" sx={{ mt: 1, textAlign: 'center' }}>
          Selecciona al menos un elemento para detectar
        </Typography>
      )}
    </Paper>
  );
}

export default Controls;
