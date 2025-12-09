import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  ButtonGroup,
  Grid,
  Chip,
  Stack,
  Alert,
  AlertTitle,
  Divider,
  List,
  ListItem,
  ListItemText,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  CircularProgress,
  RadioGroup,
  Radio,
  FormControl,
  FormLabel
} from '@mui/material';
import {
  PlayArrow as AnalyzeIcon,
  Refresh as ResetIcon,
  ExpandMore as ExpandMoreIcon,
  Security as SecurityIcon,
  Psychology as LLMIcon,
  Code as RegexIcon
} from '@mui/icons-material';
import { getTextCategories, analyzeText } from '../services/api';

export default function TextAnalysis() {
  const [text, setText] = useState('');
  const [anonymizedText, setAnonymizedText] = useState('');
  const [detections, setDetections] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(false);
  const [loadingCategories, setLoadingCategories] = useState(true);
  const [error, setError] = useState(null);
  const [method, setMethod] = useState('replace');
  const [detectionMode, setDetectionMode] = useState('regex');
  const [categories, setCategories] = useState({});
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [availableModes, setAvailableModes] = useState(['regex']);
  const [ollamaAvailable, setOllamaAvailable] = useState(false);

  useEffect(() => {
    fetchCategories(detectionMode);
  }, [detectionMode]);

  const fetchCategories = async (mode) => {
    try {
      setLoadingCategories(true);
      const data = await getTextCategories(mode);

      setCategories(data.categories);
      setAvailableModes(data.available_modes || ['regex']);
      setOllamaAvailable(data.ollama_available || false);

      // Seleccionar todas las categorías por defecto
      const allCategories = Object.values(data.categories).flatMap(cat => Object.keys(cat));
      setSelectedCategories(allCategories);
    } catch (err) {
      console.error('Error fetching categories:', err);
      setError('Error al cargar categorías');
    } finally {
      setLoadingCategories(false);
    }
  };

  const handleModeChange = (event) => {
    const newMode = event.target.value;
    setDetectionMode(newMode);
  };

  const handleCategoryToggle = (categoryId) => {
    setSelectedCategories(prev =>
      prev.includes(categoryId)
        ? prev.filter(id => id !== categoryId)
        : [...prev, categoryId]
    );
  };

  const handleGroupToggle = (groupName) => {
    const groupCategories = Object.keys(categories[groupName] || {});
    const allSelected = groupCategories.every(cat => selectedCategories.includes(cat));

    if (allSelected) {
      setSelectedCategories(prev => prev.filter(cat => !groupCategories.includes(cat)));
    } else {
      setSelectedCategories(prev => [...new Set([...prev, ...groupCategories])]);
    }
  };

  const handleAnalyze = async () => {
    if (!text.trim()) {
      setError('Por favor ingresa un texto');
      return;
    }

    if (selectedCategories.length === 0) {
      setError('Selecciona al menos una categoría');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await analyzeText(text, selectedCategories, method, detectionMode);

      setAnonymizedText(result.anonymized_text);
      setDetections(result.detections);
      setStats(result.stats);
    } catch (err) {
      console.error('Error analyzing text:', err);
      setError(err.response?.data?.detail || 'Error al analizar el texto');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setText('');
    setAnonymizedText('');
    setDetections([]);
    setStats({});
    setError(null);
  };

  const exampleText = `Hola, soy Juan Pérez. Mi email es juan.perez@example.com y mi teléfono es 654123456.
Mi DNI es 12345678Z y mi IBAN es ES12 1234 5678 9012 3456 7890.
Vivo en Calle Mayor 123, 28013 Madrid.
Mi tarjeta de crédito es 4532-1234-5678-9010.
Trabajo en Microsoft España y viajo frecuentemente a Valencia.`;

  const getTypeColor = (type) => {
    const colors = {
      phone: 'primary',
      email: 'secondary',
      dni_nie: 'error',
      credit_card: 'warning',
      iban: 'success',
      person_name: 'info',
      location: 'default',
      organization: 'primary',
      default: 'default'
    };
    return colors[type] || colors.default;
  };

  const getModeIcon = (mode) => {
    if (mode === 'regex') return <RegexIcon />;
    if (mode === 'llm') return <LLMIcon />;
    return <SecurityIcon />;
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 2 }}>
        Text Analysis
        <Chip label="Privacy First" size="small" sx={{ fontWeight: 500, background: 'rgba(16, 185, 129, 0.2)', color: '#10b981' }} />
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Detect and anonymize sensitive data using pattern recognition (Regex) or AI (LLM)
      </Typography>

      {/* Alert info */}
      <Alert severity="info" icon={<SecurityIcon />} sx={{ mb: 3 }}>
        <AlertTitle>100% Local Processing</AlertTitle>
        All text analysis happens locally on your machine. No data is sent to external servers.
      </Alert>

      {/* Ollama warning */}
      {!ollamaAvailable && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <AlertTitle>LLM Mode Not Available</AlertTitle>
          Ollama is not detected. Only regex mode is available. To enable LLM detection (names, locations, organizations), install Ollama from <a href="https://ollama.ai/download" target="_blank" rel="noopener noreferrer">ollama.ai</a> and run: <code>ollama pull llama3.2</code>
        </Alert>
      )}

      {/* Error */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Detection Mode Selector */}
      <Paper sx={{ p: 3, mb: 3, borderRadius: 3 }}>
        <FormControl component="fieldset">
          <FormLabel component="legend">
            <Typography variant="h6" gutterBottom>
              Detection Mode
            </Typography>
          </FormLabel>
          <RadioGroup
            row
            value={detectionMode}
            onChange={handleModeChange}
          >
            <FormControlLabel
              value="regex"
              control={<Radio />}
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <RegexIcon fontSize="small" />
                  <Box>
                    <Typography variant="body2" fontWeight="bold">Regex</Typography>
                    <Typography variant="caption" color="text.secondary">
                      Pattern-based (fast, precise)
                    </Typography>
                  </Box>
                </Box>
              }
            />
            <FormControlLabel
              value="llm"
              control={<Radio />}
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <LLMIcon fontSize="small" />
                  <Box>
                    <Typography variant="body2" fontWeight="bold">LLM</Typography>
                    <Typography variant="caption" color="text.secondary">
                      AI-powered (contextual)
                    </Typography>
                  </Box>
                </Box>
              }
              disabled={!ollamaAvailable}
            />
            <FormControlLabel
              value="both"
              control={<Radio />}
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <SecurityIcon fontSize="small" />
                  <Box>
                    <Typography variant="body2" fontWeight="bold">Both</Typography>
                    <Typography variant="caption" color="text.secondary">
                      Maximum detection
                    </Typography>
                  </Box>
                </Box>
              }
              disabled={!ollamaAvailable}
            />
          </RadioGroup>
        </FormControl>
      </Paper>

      <Grid container spacing={3}>
        {/* Input y opciones */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%', borderRadius: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
              Input Text
            </Typography>

            <TextField
              fullWidth
              multiline
              rows={12}
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Enter or paste text here..."
              variant="outlined"
              disabled={loading}
              sx={{ mb: 2 }}
            />

            <Button
              size="small"
              variant="outlined"
              onClick={() => setText(exampleText)}
              disabled={loading}
              sx={{ mb: 2 }}
            >
              Load Example
            </Button>

            <Divider sx={{ my: 2 }} />

            <Typography variant="subtitle2" gutterBottom>
              Anonymization Method:
            </Typography>
            <ButtonGroup size="small" sx={{ mb: 2 }}>
              <Button
                variant={method === 'replace' ? 'contained' : 'outlined'}
                onClick={() => setMethod('replace')}
                disabled={loading}
              >
                Replace
              </Button>
              <Button
                variant={method === 'mask' ? 'contained' : 'outlined'}
                onClick={() => setMethod('mask')}
                disabled={loading}
              >
                Mask
              </Button>
              <Button
                variant={method === 'remove' ? 'contained' : 'outlined'}
                onClick={() => setMethod('remove')}
                disabled={loading}
              >
                Remove
              </Button>
            </ButtonGroup>

            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                fullWidth
                variant="contained"
                color="primary"
                startIcon={loading ? <CircularProgress size={20} /> : <AnalyzeIcon />}
                onClick={handleAnalyze}
                disabled={loading || !text.trim() || selectedCategories.length === 0}
              >
                {loading ? 'Analyzing...' : 'Analyze Text'}
              </Button>
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
        </Grid>

        {/* Output */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%', borderRadius: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
              Anonymized Text
            </Typography>

            <TextField
              fullWidth
              multiline
              rows={12}
              value={anonymizedText}
              InputProps={{
                readOnly: true,
              }}
              placeholder="Anonymized text will appear here..."
              variant="outlined"
              sx={{ mb: 2 }}
            />

            {/* Estadísticas */}
            {Object.keys(stats).length > 0 && (
              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Detections:
                </Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ gap: 1 }}>
                  {Object.entries(stats).map(([type, count]) => (
                    <Chip
                      key={type}
                      label={`${type}: ${count}`}
                      color={getTypeColor(type)}
                      size="small"
                    />
                  ))}
                  <Chip
                    label={`Total: ${detections.length}`}
                    color="primary"
                    size="small"
                  />
                </Stack>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Selector de categorías */}
      <Paper sx={{ p: 3, mt: 3, borderRadius: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
          Select Categories to Detect
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Choose which types of sensitive data to detect and anonymize.
          {detectionMode === 'both' && ' Combining Regex + LLM for maximum coverage.'}
          {detectionMode === 'llm' && ' Using AI for contextual detection.'}
          {detectionMode === 'regex' && ' Using pattern-based detection.'}
        </Typography>

        {loadingCategories ? (
          <CircularProgress />
        ) : (
          Object.entries(categories).map(([groupName, groupCategories]) => (
            <Accordion key={groupName} defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                  <Checkbox
                    checked={Object.keys(groupCategories).every(cat => selectedCategories.includes(cat))}
                    indeterminate={
                      Object.keys(groupCategories).some(cat => selectedCategories.includes(cat)) &&
                      !Object.keys(groupCategories).every(cat => selectedCategories.includes(cat))
                    }
                    onChange={() => handleGroupToggle(groupName)}
                    onClick={(e) => e.stopPropagation()}
                  />
                  <Typography>
                    {groupName}
                    {groupName.includes('LLM') && (
                      <Chip label="AI" size="small" color="info" sx={{ ml: 1 }} />
                    )}
                  </Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <FormGroup>
                  {Object.entries(groupCategories).map(([catId, catName]) => (
                    <FormControlLabel
                      key={catId}
                      control={
                        <Checkbox
                          checked={selectedCategories.includes(catId)}
                          onChange={() => handleCategoryToggle(catId)}
                        />
                      }
                      label={catName}
                    />
                  ))}
                </FormGroup>
              </AccordionDetails>
            </Accordion>
          ))
        )}
      </Paper>

      {/* Lista de detecciones con tokens numerados */}
      {detections.length > 0 && (
        <Paper sx={{ p: 3, mt: 3, borderRadius: 3 }}>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
            Detection Details ({detections.length} found)
          </Typography>
          <List>
            {detections.map((detection, index) => (
              <ListItem key={index}>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                      <Chip
                        label={detection.type_name}
                        color={getTypeColor(detection.type)}
                        size="small"
                      />
                      {detection.source && (
                        <Chip
                          label={detection.source}
                          size="small"
                          variant="outlined"
                          icon={detection.source === 'llm' ? <LLMIcon fontSize="small" /> : <RegexIcon fontSize="small" />}
                        />
                      )}
                      <Typography variant="body2" component="span">
                        <strong>{detection.text}</strong> → <code>{detection.replacement}</code>
                      </Typography>
                    </Box>
                  }
                  secondary={`Position: ${detection.start}-${detection.end} | Confidence: ${(detection.confidence * 100).toFixed(0)}%`}
                />
              </ListItem>
            ))}
          </List>
        </Paper>
      )}
    </Box>
  );
}
