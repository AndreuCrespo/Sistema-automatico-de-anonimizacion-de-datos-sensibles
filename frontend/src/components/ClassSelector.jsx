import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Chip,
  Stack,
  Button,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckIcon,
  Stars as TrainedIcon
} from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function ClassSelector({ selectedClasses, onSelectionChange, disabled = false }) {
  const [categories, setCategories] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  const [defaults, setDefaults] = useState(null);

  useEffect(() => {
    fetchClasses();
  }, []);

  const fetchClasses = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/api/classes`);

      if (response.data.success) {
        setCategories(response.data.categories);
        setStats(response.data.stats);
        setDefaults(response.data.defaults);
      }
    } catch (err) {
      console.error('Error fetching classes:', err);
      setError('Error al cargar clases disponibles');
    } finally {
      setLoading(false);
    }
  };

  const handleClassToggle = (classId) => {
    const newSelection = selectedClasses.includes(classId)
      ? selectedClasses.filter(id => id !== classId)
      : [...selectedClasses, classId];

    onSelectionChange(newSelection);
  };

  const handleCategoryToggle = (category) => {
    const categoryClasses = categories[category].map(cls => cls.id);
    const allSelected = categoryClasses.every(id => selectedClasses.includes(id));

    if (allSelected) {
      // Deseleccionar todos
      const newSelection = selectedClasses.filter(id => !categoryClasses.includes(id));
      onSelectionChange(newSelection);
    } else {
      // Seleccionar todos
      const newSelection = [...new Set([...selectedClasses, ...categoryClasses])];
      onSelectionChange(newSelection);
    }
  };

  const handleSelectRecommended = () => {
    if (defaults && defaults.recommended) {
      onSelectionChange(defaults.recommended);
    }
  };

  const handleSelectAll = () => {
    const allClasses = Object.values(categories).flat().map(cls => cls.id);
    onSelectionChange(allClasses);
  };

  const handleClearAll = () => {
    onSelectionChange([]);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  const getCategoryProgress = (category) => {
    const categoryClasses = categories[category].map(cls => cls.id);
    const selectedCount = categoryClasses.filter(id => selectedClasses.includes(id)).length;
    return `${selectedCount}/${categoryClasses.length}`;
  };

  return (
    <Box>
      {/* Header con estadísticas */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="h6" gutterBottom>
          Select Classes to Detect
        </Typography>
        <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
          <Chip
            label={`${selectedClasses.length} / ${stats?.total_classes || 0} selected`}
            color="primary"
            size="small"
          />
          <Chip
            label={`${stats?.trained_classes || 0} trained`}
            icon={<TrainedIcon />}
            size="small"
            color="success"
            variant="outlined"
          />
          <Chip
            label={`${stats?.coco_classes || 0} COCO`}
            size="small"
            variant="outlined"
          />
        </Stack>

        {/* Botones de acción rápida */}
        <Stack direction="row" spacing={1}>
          <Button
            size="small"
            variant="outlined"
            onClick={handleSelectRecommended}
            disabled={disabled}
          >
            Recommended
          </Button>
          <Button
            size="small"
            variant="outlined"
            onClick={handleSelectAll}
            disabled={disabled}
          >
            Select All
          </Button>
          <Button
            size="small"
            variant="outlined"
            onClick={handleClearAll}
            disabled={disabled}
          >
            Clear All
          </Button>
        </Stack>
      </Box>

      {/* Acordeones por categoría */}
      {Object.entries(categories).map(([categoryName, classes]) => {
        const categoryClasses = classes.map(cls => cls.id);
        const allSelected = categoryClasses.every(id => selectedClasses.includes(id));
        const someSelected = categoryClasses.some(id => selectedClasses.includes(id));

        return (
          <Accordion key={categoryName} defaultExpanded={categoryName === "Personas"}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                <Checkbox
                  checked={allSelected}
                  indeterminate={someSelected && !allSelected}
                  onChange={() => handleCategoryToggle(categoryName)}
                  onClick={(e) => e.stopPropagation()}
                  disabled={disabled}
                  sx={{ mr: 1 }}
                />
                <Typography sx={{ flexGrow: 1 }}>
                  {categoryName}
                </Typography>
                <Chip
                  label={getCategoryProgress(categoryName)}
                  size="small"
                  color={allSelected ? "primary" : "default"}
                />
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <FormGroup>
                {classes.map((cls) => (
                  <FormControlLabel
                    key={cls.id}
                    control={
                      <Checkbox
                        checked={selectedClasses.includes(cls.id)}
                        onChange={() => handleClassToggle(cls.id)}
                        disabled={disabled}
                      />
                    }
                    label={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="body2">
                          {cls.name}
                        </Typography>
                        {cls.source === 'trained' && (
                          <Chip
                            icon={<TrainedIcon />}
                            label={`F1: ${cls.f1_score}%`}
                            size="small"
                            color="success"
                            variant="outlined"
                          />
                        )}
                        {cls.source === 'coco' && (
                          <Chip
                            label="COCO"
                            size="small"
                            variant="outlined"
                          />
                        )}
                        {cls.priority === 'high' && (
                          <Chip
                            label="High Priority"
                            size="small"
                            color="error"
                            variant="outlined"
                          />
                        )}
                      </Box>
                    }
                  />
                ))}
              </FormGroup>
            </AccordionDetails>
          </Accordion>
        );
      })}

      {/* Info RGPD */}
      {selectedClasses.length === 0 && (
        <Alert severity="warning" sx={{ mt: 2 }}>
          Please select at least one class to detect.
        </Alert>
      )}
    </Box>
  );
}
