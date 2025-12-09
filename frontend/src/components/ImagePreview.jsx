import { Box, Typography, Paper, Grid, Button } from '@mui/material';
import { Download as DownloadIcon } from '@mui/icons-material';

/**
 * Componente para mostrar imagen original y anonimizada.
 */
function ImagePreview({ originalImage, anonymizedImage, metadata }) {
  const handleDownload = () => {
    if (!anonymizedImage) return;

    const url = URL.createObjectURL(anonymizedImage);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'anonymized_image.jpg';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <Box sx={{ mt: 4 }}>
      <Grid container spacing={3}>
        {/* Imagen Original */}
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Imagen Original
            </Typography>
            <Box
              component="img"
              src={originalImage}
              alt="Original"
              sx={{
                width: '100%',
                height: 'auto',
                borderRadius: 1,
                border: '1px solid',
                borderColor: 'divider'
              }}
            />
          </Paper>
        </Grid>

        {/* Imagen Anonimizada */}
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Imagen Anonimizada
            </Typography>

            {anonymizedImage ? (
              <>
                <Box
                  component="img"
                  src={URL.createObjectURL(anonymizedImage)}
                  alt="Anonimizada"
                  sx={{
                    width: '100%',
                    height: 'auto',
                    borderRadius: 1,
                    border: '1px solid',
                    borderColor: 'divider',
                    mb: 2
                  }}
                />

                <Button
                  variant="contained"
                  color="success"
                  fullWidth
                  startIcon={<DownloadIcon />}
                  onClick={handleDownload}
                >
                  Descargar Imagen
                </Button>
              </>
            ) : (
              <Box
                sx={{
                  height: 300,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  bgcolor: 'action.hover',
                  borderRadius: 1,
                  border: '1px solid',
                  borderColor: 'divider'
                }}
              >
                <Typography color="text.secondary">
                  La imagen anonimizada aparecera aqui
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Metadata */}
      {metadata && (
        <Paper elevation={3} sx={{ p: 3, mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            Resultados de la Anonimizacion
          </Typography>

          <Grid container spacing={2}>
            <Grid item xs={6} sm={3}>
              <Typography variant="body2" color="text.secondary">
                Rostros Detectados
              </Typography>
              <Typography variant="h5" color="primary">
                {metadata.facesDetected || 0}
              </Typography>
            </Grid>

            <Grid item xs={6} sm={3}>
              <Typography variant="body2" color="text.secondary">
                Matriculas Detectadas
              </Typography>
              <Typography variant="h5" color="primary">
                {metadata.platesDetected || 0}
              </Typography>
            </Grid>

            <Grid item xs={6} sm={3}>
              <Typography variant="body2" color="text.secondary">
                Detecciones Totales
              </Typography>
              <Typography variant="h5" color="primary">
                {metadata.totalDetections || 0}
              </Typography>
            </Grid>

            <Grid item xs={6} sm={3}>
              <Typography variant="body2" color="text.secondary">
                Tiempo de Procesamiento
              </Typography>
              <Typography variant="h5" color="primary">
                {metadata.processingTime ? `${metadata.processingTime.toFixed(0)} ms` : 'N/A'}
              </Typography>
            </Grid>
          </Grid>
        </Paper>
      )}
    </Box>
  );
}

export default ImagePreview;
