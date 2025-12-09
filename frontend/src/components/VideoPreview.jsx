import { useRef, useEffect } from 'react';
import { Box, Grid, Typography, Paper, Chip, LinearProgress, Stack } from '@mui/material';
import {
  Face as FaceIcon,
  DirectionsCar as PlateIcon,
  AccessTime as TimeIcon,
  Speed as FpsIcon,
  Visibility as FrameIcon
} from '@mui/icons-material';

export default function VideoPreview({
  originalVideo,
  processedVideo,
  metadata,
  processing = false,
  progress = null,
  currentFrame = null
}) {
  const canvasRef = useRef(null);

  // Actualizar canvas con el frame actual
  useEffect(() => {
    if (currentFrame && canvasRef.current) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');

      const img = new Image();
      img.onload = () => {
        // Ajustar tamaño del canvas manteniendo aspecto
        const maxWidth = canvas.parentElement.offsetWidth;
        const maxHeight = 300;
        const scale = Math.min(maxWidth / img.width, maxHeight / img.height);

        canvas.width = img.width * scale;
        canvas.height = img.height * scale;

        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      };
      img.src = currentFrame;
    }
  }, [currentFrame]);

  // Calcular FPS de procesamiento
  const fps = progress?.fps || 0;
  const estimatedTimeRemaining = progress?.total_frames && progress?.frame && fps > 0
    ? ((progress.total_frames - progress.frame) / fps).toFixed(1)
    : 0;

  return (
    <Box sx={{ mt: 3 }}>
      {/* Barra de progreso mejorada */}
      {processing && progress && (
        <Paper sx={{ p: 3, mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
          {/* Título y porcentaje */}
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" sx={{ flexGrow: 1, color: 'white', fontWeight: 'bold' }}>
              Processing Video...
            </Typography>
            <Chip
              label={`${Math.round(progress.progress_percent)}%`}
              color="success"
              size="medium"
              sx={{ fontWeight: 'bold', fontSize: '1rem' }}
            />
          </Box>

          {/* Barra de progreso principal */}
          <LinearProgress
            variant="determinate"
            value={progress.progress_percent}
            sx={{
              height: 12,
              borderRadius: 2,
              mb: 2,
              backgroundColor: 'rgba(255,255,255,0.3)',
              '& .MuiLinearProgress-bar': {
                borderRadius: 2,
                backgroundColor: '#4caf50'
              }
            }}
          />

          {/* Estadísticas en tiempo real */}
          <Grid container spacing={2}>
            <Grid item xs={6} sm={3}>
              <Stack spacing={0.5} alignItems="center">
                <FrameIcon sx={{ color: 'white', opacity: 0.9 }} />
                <Typography variant="caption" sx={{ color: 'white', opacity: 0.7 }}>
                  Frame
                </Typography>
                <Typography variant="h6" sx={{ color: 'white', fontWeight: 'bold' }}>
                  {progress.frame}/{progress.total_frames}
                </Typography>
              </Stack>
            </Grid>

            <Grid item xs={6} sm={3}>
              <Stack spacing={0.5} alignItems="center">
                <FaceIcon sx={{ color: 'white', opacity: 0.9 }} />
                <Typography variant="caption" sx={{ color: 'white', opacity: 0.7 }}>
                  Rostros
                </Typography>
                <Typography variant="h6" sx={{ color: 'white', fontWeight: 'bold' }}>
                  {progress.faces_in_frame || 0}
                </Typography>
              </Stack>
            </Grid>

            <Grid item xs={6} sm={3}>
              <Stack spacing={0.5} alignItems="center">
                <PlateIcon sx={{ color: 'white', opacity: 0.9 }} />
                <Typography variant="caption" sx={{ color: 'white', opacity: 0.7 }}>
                  Matrículas
                </Typography>
                <Typography variant="h6" sx={{ color: 'white', fontWeight: 'bold' }}>
                  {progress.plates_in_frame || 0}
                </Typography>
              </Stack>
            </Grid>

            <Grid item xs={6} sm={3}>
              <Stack spacing={0.5} alignItems="center">
                <FpsIcon sx={{ color: 'white', opacity: 0.9 }} />
                <Typography variant="caption" sx={{ color: 'white', opacity: 0.7 }}>
                  FPS
                </Typography>
                <Typography variant="h6" sx={{ color: 'white', fontWeight: 'bold' }}>
                  {fps.toFixed(1)}
                </Typography>
              </Stack>
            </Grid>
          </Grid>

          {/* Tiempo estimado */}
          {estimatedTimeRemaining > 0 && (
            <Typography
              variant="body2"
              align="center"
              sx={{ mt: 2, color: 'white', opacity: 0.8 }}
            >
              Tiempo estimado restante: {estimatedTimeRemaining}s
            </Typography>
          )}
        </Paper>
      )}

      {/* Videos */}
      <Grid container spacing={2}>
        {/* Video Original */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Video Original
            </Typography>
            {originalVideo ? (
              <Box
                component="video"
                src={originalVideo}
                controls
                sx={{
                  width: '100%',
                  height: 'auto',
                  borderRadius: 1,
                  backgroundColor: '#000'
                }}
              />
            ) : (
              <Box
                sx={{
                  width: '100%',
                  height: 300,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  backgroundColor: 'grey.100',
                  borderRadius: 1
                }}
              >
                <Typography variant="body2" color="text.secondary">
                  Selecciona un video para previsualizar
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Video Procesado / Preview en tiempo real */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              {processing && currentFrame ? 'Live Preview (Processing...)' : 'Video Anonimizado'}
            </Typography>

            {/* Preview en tiempo real durante procesamiento */}
            {processing && currentFrame ? (
              <Box
                sx={{
                  position: 'relative',
                  width: '100%',
                  borderRadius: 1,
                  overflow: 'hidden',
                  backgroundColor: '#000'
                }}
              >
                <canvas
                  ref={canvasRef}
                  style={{
                    width: '100%',
                    height: 'auto',
                    display: 'block'
                  }}
                />
                {/* Indicador de "En vivo" */}
                <Chip
                  label="LIVE"
                  color="error"
                  size="small"
                  sx={{
                    position: 'absolute',
                    top: 10,
                    right: 10,
                    fontWeight: 'bold',
                    animation: 'pulse 1.5s infinite'
                  }}
                />
              </Box>
            ) : processedVideo ? (
              /* Video finalizado */
              <>
                <Box
                  component="video"
                  src={processedVideo}
                  controls
                  sx={{
                    width: '100%',
                    height: 'auto',
                    borderRadius: 1,
                    backgroundColor: '#000'
                  }}
                />

                {/* Metadata */}
                {metadata && (
                  <Box sx={{ mt: 2 }}>
                    <Grid container spacing={1}>
                      <Grid item xs={6}>
                        <Chip
                          icon={<FaceIcon />}
                          label={`${metadata.totalFaces} rostros`}
                          color="primary"
                          size="small"
                          sx={{ width: '100%' }}
                        />
                      </Grid>
                      <Grid item xs={6}>
                        <Chip
                          icon={<PlateIcon />}
                          label={`${metadata.totalPlates} matrículas`}
                          color="secondary"
                          size="small"
                          sx={{ width: '100%' }}
                        />
                      </Grid>
                      <Grid item xs={12}>
                        <Chip
                          icon={<TimeIcon />}
                          label={`Tiempo: ${metadata.processingTime?.toFixed(2)}s`}
                          size="small"
                          sx={{ width: '100%' }}
                        />
                      </Grid>
                    </Grid>

                    <Typography variant="caption" display="block" sx={{ mt: 2 }} color="text.secondary">
                      Frames procesados: {metadata.framesProcessed}
                      {metadata.framesWithDetections &&
                        ` | Frames con detecciones: ${metadata.framesWithDetections}`
                      }
                    </Typography>
                  </Box>
                )}
              </>
            ) : (
              /* Estado inicial */
              <Box
                sx={{
                  width: '100%',
                  height: 300,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  backgroundColor: processing ? 'action.hover' : 'grey.100',
                  borderRadius: 1,
                  gap: 2
                }}
              >
                <Box
                  sx={{
                    width: 60,
                    height: 60,
                    borderRadius: '50%',
                    backgroundColor: 'primary.main',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    opacity: processing ? 1 : 0.5
                  }}
                >
                  <FaceIcon sx={{ fontSize: 30, color: 'white' }} />
                </Box>
                <Typography variant="body2" color="text.secondary">
                  {processing ? 'Starting processing...' : 'Processed video will appear here'}
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
