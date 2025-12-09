import { useState, useRef } from 'react';
import {
  Box,
  Typography,
  Alert,
  AlertTitle,
  Paper,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Button,
  ButtonGroup,
  Chip,
  Stack,
  Switch
} from '@mui/material';
import {
  PlayArrow as ProcessIcon,
  Refresh as ResetIcon,
  Download as DownloadIcon,
  VideoSettings as VideoIcon
} from '@mui/icons-material';

import VideoUpload from '../components/VideoUpload';
import VideoPreview from '../components/VideoPreview';
import ClassSelector from '../components/ClassSelector';
import { processVideo, getVideoInfo, processVideoWithWebSocket } from '../services/api';

export default function VideoProcessing() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [originalVideoUrl, setOriginalVideoUrl] = useState(null);
  const [processedVideo, setProcessedVideo] = useState(null);
  const [videoInfo, setVideoInfo] = useState(null);
  const [metadata, setMetadata] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingInfo, setLoadingInfo] = useState(false);
  const [progress, setProgress] = useState(null);
  const [currentFrame, setCurrentFrame] = useState(null);
  const [error, setError] = useState(null);

  const startTimeRef = useRef(null);
  const frameCountRef = useRef(0);

  // Opciones de detección
  const [selectedClasses, setSelectedClasses] = useState(['face', 'plate']);
  const [method, setMethod] = useState('blur');
  const [enableLivePreview, setEnableLivePreview] = useState(true);

  const handleVideoSelect = async (file) => {
    setSelectedFile(file);
    setOriginalVideoUrl(URL.createObjectURL(file));
    setProcessedVideo(null);
    setMetadata(null);
    setProgress(null);
    setError(null);

    // Obtener info del video
    setLoadingInfo(true);
    try {
      const info = await getVideoInfo(file);
      setVideoInfo(info.info);
    } catch (err) {
      console.error('Error obteniendo info del video:', err);
    } finally {
      setLoadingInfo(false);
    }
  };

  const handleProcess = async () => {
    if (!selectedFile) {
      setError('No hay video seleccionado');
      return;
    }

    if (selectedClasses.length === 0) {
      setError('Selecciona al menos una clase para detectar');
      return;
    }

    setLoading(true);
    setError(null);
    setCurrentFrame(null);
    setProcessedVideo(null);
    setProgress({
      frame: 0,
      total_frames: videoInfo?.frame_count || 100,
      progress_percent: 0,
      fps: 0,
      faces_in_frame: 0,
      plates_in_frame: 0
    });

    // Inicializar contador de FPS
    startTimeRef.current = Date.now();
    frameCountRef.current = 0;

    try {
      // Usar WebSocket para recibir frames en tiempo real
      processVideoWithWebSocket(
        selectedFile,
        {
          detect_faces: selectedClasses.includes('face'),
          detect_plates: selectedClasses.includes('plate'),
          anonymization_method: method,
          blur_kernel_size: 51,
          pixelate_blocks: 10,
          enablePreview: enableLivePreview
        },
        // Callback de progreso (cada frame)
        (progressData) => {
          frameCountRef.current += 1;
          const elapsed = (Date.now() - startTimeRef.current) / 1000; // segundos
          const fps = elapsed > 0 ? frameCountRef.current / elapsed : 0;

          setProgress({
            frame: progressData.frame,
            total_frames: progressData.total_frames,
            progress_percent: progressData.progress_percent,
            fps: fps,
            faces_in_frame: progressData.faces_in_frame || 0,
            plates_in_frame: progressData.plates_in_frame || 0
          });

          // Actualizar frame actual si está disponible
          if (progressData.current_frame) {
            setCurrentFrame(`data:image/jpeg;base64,${progressData.current_frame}`);
          }
        },
        // Callback de completado
        (result) => {
          console.log('Video procesado:', result);
          console.log('Blob:', result.blob);
          console.log('Blob type:', result.blob?.constructor?.name);

          // Validar que el blob existe
          if (!result.blob || !(result.blob instanceof Blob)) {
            console.error('Error: result.blob no es un Blob válido', result);
            setError('Error al recibir el video procesado');
            setLoading(false);
            return;
          }

          // Crear URL para el video procesado
          const videoUrl = URL.createObjectURL(result.blob);
          setProcessedVideo(videoUrl);

          setMetadata({
            totalFaces: result.stats.total_faces,
            totalPlates: result.stats.total_plates,
            framesProcessed: result.stats.frames_processed,
            framesWithDetections: result.stats.frames_with_detections,
            processingTime: (Date.now() - startTimeRef.current) / 1000
          });

          setProgress(null);
          setCurrentFrame(null);
          setLoading(false);
        },
        // Callback de error
        (error) => {
          console.error('Error al procesar video:', error);
          setError(
            error?.message ||
            'Error al procesar el video. Por favor intenta de nuevo.'
          );
          setProgress(null);
          setCurrentFrame(null);
          setLoading(false);
        }
      );

    } catch (err) {
      console.error('Error iniciando procesamiento:', err);
      setError(
        'Error al iniciar el procesamiento. Por favor intenta de nuevo.'
      );
      setProgress(null);
      setCurrentFrame(null);
      setLoading(false);
    }
  };

  const handleReset = () => {
    if (originalVideoUrl) {
      URL.revokeObjectURL(originalVideoUrl);
    }
    if (processedVideo) {
      URL.revokeObjectURL(processedVideo);
    }

    setSelectedFile(null);
    setOriginalVideoUrl(null);
    setProcessedVideo(null);
    setVideoInfo(null);
    setMetadata(null);
    setProgress(null);
    setError(null);
  };

  const handleDownload = () => {
    if (!processedVideo) return;

    const link = document.createElement('a');
    link.href = processedVideo;
    link.download = `anonymized_${selectedFile.name}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
        Video Processing
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Process videos frame-by-frame with real-time detection and anonymization
      </Typography>

      {/* Información del sistema */}
      <Alert severity="info" sx={{ mb: 3, borderRadius: 3 }}>
        <AlertTitle>Processing Information</AlertTitle>
        Los videos se procesan frame por frame en el servidor. Videos largos pueden tardar varios minutos.
        El progreso se actualiza en tiempo real.
      </Alert>

      {/* Mensaje de error */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          <AlertTitle>Error</AlertTitle>
          {error}
        </Alert>
      )}

      {/* Upload de video */}
      {!selectedFile ? (
        <VideoUpload onVideoSelect={handleVideoSelect} disabled={loading} />
      ) : (
        <Box>
          {/* Info del video */}
          {videoInfo && (
            <Paper sx={{ p: 3, mb: 3, borderRadius: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <VideoIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Video Information
                </Typography>
              </Box>
              <Stack direction="row" spacing={1} flexWrap="wrap" gap={1}>
                <Chip label={`${videoInfo.fps} FPS`} size="small" sx={{ fontWeight: 500 }} />
                <Chip label={`${videoInfo.frame_count} frames`} size="small" sx={{ fontWeight: 500 }} />
                <Chip label={`${videoInfo.width}x${videoInfo.height}`} size="small" sx={{ fontWeight: 500 }} />
                <Chip label={`Duración: ${videoInfo.duration_formatted}`} size="small" sx={{ fontWeight: 500 }} />
              </Stack>
            </Paper>
          )}

          {/* Selector de clases */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <ClassSelector
              selectedClasses={selectedClasses}
              onSelectionChange={setSelectedClasses}
              disabled={loading}
            />
            <Alert severity="info" sx={{ mt: 2 }}>
              <AlertTitle>Note</AlertTitle>
              Currently, only <strong>Face</strong> and <strong>License Plate</strong> detection are available.
              Other COCO classes will be enabled in future updates.
            </Alert>
          </Paper>

          {/* Controles */}
          <Paper sx={{ p: 3, mb: 3, borderRadius: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
              Processing Options
            </Typography>

            {/* Método de anonimización */}
            <Typography variant="subtitle2" gutterBottom>
              Anonymization Method:
            </Typography>
            <ButtonGroup size="small" sx={{ mb: 3 }}>
              <Button
                variant={method === 'blur' ? 'contained' : 'outlined'}
                onClick={() => setMethod('blur')}
                disabled={loading}
              >
                Blur
              </Button>
              <Button
                variant={method === 'pixelate' ? 'contained' : 'outlined'}
                onClick={() => setMethod('pixelate')}
                disabled={loading}
              >
                Pixelate
              </Button>
              <Button
                variant={method === 'mask' ? 'contained' : 'outlined'}
                onClick={() => setMethod('mask')}
                disabled={loading}
              >
                Mask
              </Button>
            </ButtonGroup>

            {/* Toggle para Live Preview */}
            <FormControlLabel
              control={
                <Switch
                  checked={enableLivePreview}
                  onChange={(e) => setEnableLivePreview(e.target.checked)}
                  disabled={loading}
                  color="primary"
                />
              }
              label="Show Live Preview (may slow down processing)"
              sx={{ mb: 2 }}
            />

            {/* Botones de acción */}
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                color="primary"
                startIcon={<ProcessIcon />}
                onClick={handleProcess}
                disabled={loading || !selectedFile || selectedClasses.length === 0}
                fullWidth
              >
                {loading ? 'Processing...' : 'Process Video'}
              </Button>

              {processedVideo && (
                <Button
                  variant="contained"
                  color="success"
                  startIcon={<DownloadIcon />}
                  onClick={handleDownload}
                  disabled={loading}
                >
                  Download
                </Button>
              )}

              <Button
                variant="outlined"
                startIcon={<ResetIcon />}
                onClick={handleReset}
                disabled={loading}
              >
                Reset
              </Button>
            </Box>
          </Paper>

          {/* Preview de videos */}
          <VideoPreview
            originalVideo={originalVideoUrl}
            processedVideo={processedVideo}
            metadata={metadata}
            processing={loading}
            progress={progress}
            currentFrame={currentFrame}
          />
        </Box>
      )}
    </Box>
  );
}
