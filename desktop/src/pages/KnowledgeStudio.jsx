import React, { useState, useEffect } from 'react';
import {
    Box, Typography, Paper, Grid, List, ListItem, ListItemText,
    ListItemAvatar, Avatar, IconButton, Divider, Button,
    CircularProgress, Chip, Card, CardContent
} from '@mui/material';
import {
    Description as FileIcon,
    AccountTree as TreeIcon,
    RecordVoiceOver as PodcastIcon,
    Summarize as SummaryIcon,
    PlayArrow as PlayIcon,
    Pause as PauseIcon
} from '@mui/icons-material';
import { api } from '../services/api';

// Simple Tree Visualization Component (Recursive)
const TreeNode = ({ node, level = 0 }) => (
    <Box sx={{ ml: level * 2, mt: 1 }}>
        <Chip
            label={node.name || node.label}
            size="small"
            color={level === 0 ? "primary" : "default"}
            variant={level === 0 ? "filled" : "outlined"}
        />
        {node.children && node.children.map((child, i) => (
            <TreeNode key={i} node={child} level={level + 1} />
        ))}
    </Box>
);

const KnowledgeStudio = () => {
    const [files, setFiles] = useState([]);
    const [selectedFile, setSelectedFile] = useState(null);
    const [activeTab, setActiveTab] = useState('summary'); // summary, tree, podcast
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState({ summary: null, tree: null, podcast: null });

    useEffect(() => {
        fetchFiles();
    }, []);

    const fetchFiles = async () => {
        try {
            const res = await api.get('/knowledge/files');
            setFiles(res.files || []); // Expecting { files: [...] }
        } catch (err) {
            console.error("Failed to load files", err);
        }
    };

    const handleFileSelect = (file) => {
        setSelectedFile(file);
        setData({ summary: null, tree: null, podcast: null }); // Reset data
        // Auto-fetch summary if available in file metadata
        if (file.description) {
            setData(prev => ({ ...prev, summary: { final_summary: file.description } }));
        }
    };

    const generateFeature = async (feature) => {
        if (!selectedFile) return;
        setLoading(true);
        setActiveTab(feature);

        try {
            let result;
            const path = selectedFile.path || selectedFile.metadata?.path; // Handle structure diffs

            if (feature === 'summary') {
                // Force deep recursive summary
                result = await api.post('/knowledge/summary', { path });
                setData(prev => ({ ...prev, summary: result }));
            } else if (feature === 'tree') {
                result = await api.post('/knowledge/tree', { path });
                // Transform for simple visualization if needed, or stick to list
                setData(prev => ({ ...prev, tree: result }));
            } else if (feature === 'podcast') {
                result = await api.post('/knowledge/podcast', { path });
                setData(prev => ({ ...prev, podcast: result }));
            }
        } catch (err) {
            console.error(`Failed to generate ${feature}`, err);
        } finally {
            setLoading(false);
        }
    };

    // --- Renderers ---

    const renderSummary = () => (
        <Box>
            <Typography variant="h6" gutterBottom>Deep Summary</Typography>
            {data.summary ? (
                <Box>
                    <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
                        {data.summary.final_summary || data.summary}
                    </Typography>
                    {/* If recursive chunks exist */}
                    {data.summary.chunk_summaries && (
                        <Box mt={4}>
                            <Typography variant="subtitle2" color="text.secondary">Detailed Breakdown:</Typography>
                            {data.summary.chunk_summaries.map((chunk, i) => (
                                <Paper key={i} sx={{ p: 2, my: 1, bgcolor: 'background.default' }}>
                                    <Typography variant="body2">{chunk}</Typography>
                                </Paper>
                            ))}
                        </Box>
                    )}
                </Box>
            ) : (
                <Box textAlign="center" mt={4}>
                    <Typography color="text.secondary">No summary generated yet.</Typography>
                    <Button variant="contained" onClick={() => generateFeature('summary')} sx={{ mt: 2 }}>
                        Generate Deep Summary
                    </Button>
                </Box>
            )}
        </Box>
    );

    const renderTree = () => (
        <Box>
            <Typography variant="h6" gutterBottom>Knowledge Tree</Typography>
            {data.tree ? (
                <Box>
                    {/* Simple list of topics for now */}
                    <Typography variant="subtitle1">Root: {data.tree.root}</Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 2 }}>
                        {data.tree.topics && data.tree.topics.map((t, i) => (
                            <Chip
                                key={i}
                                label={t.properties?.name || "Topic"}
                                color="secondary"
                                variant="outlined"
                                icon={<TreeIcon />}
                            />
                        ))}
                    </Box>
                    {data.tree.topics?.length === 0 && <Typography>No topics extracted yet.</Typography>}
                </Box>
            ) : (
                <Box textAlign="center" mt={4}>
                    <Typography color="text.secondary">Knowledge graph not built.</Typography>
                    <Button variant="contained" onClick={() => generateFeature('tree')} sx={{ mt: 2 }}>
                        Build Knowledge Tree
                    </Button>
                </Box>
            )}
        </Box>
    );

    const renderPodcast = () => (
        <Box>
            <Typography variant="h6" gutterBottom>Deep Dive Podcast</Typography>
            {data.podcast ? (
                <Box>
                    <Typography variant="subtitle1" gutterBottom>{data.podcast.title}</Typography>
                    <Paper sx={{ maxHeight: '60vh', overflow: 'auto', p: 2 }}>
                        {data.podcast.script && data.podcast.script.map((line, i) => (
                            <Box key={i} sx={{ mb: 2, display: 'flex', gap: 2 }}>
                                <Avatar sx={{ bgcolor: line.speaker === 'Sarah' ? 'primary.main' : 'secondary.main' }}>
                                    {line.speaker[0]}
                                </Avatar>
                                <Box>
                                    <Typography variant="subtitle2" color="text.secondary">{line.speaker}</Typography>
                                    <Typography variant="body1">{line.text}</Typography>
                                </Box>
                            </Box>
                        ))}
                    </Paper>
                    <Box mt={2} textAlign="center">
                        <Button variant="outlined" startIcon={<PlayIcon />} disabled>
                            Play Audio (Coming Soon)
                        </Button>
                    </Box>
                </Box>
            ) : (
                <Box textAlign="center" mt={4}>
                    <Typography color="text.secondary">No podcast script generated.</Typography>
                    <Button variant="contained" onClick={() => generateFeature('podcast')} sx={{ mt: 2 }}>
                        Generate Podcast Script
                    </Button>
                </Box>
            )}
        </Box>
    );

    return (
        <Grid container spacing={0} sx={{ height: '100vh' }}>
            {/* Sidebar: File List */}
            <Grid item xs={3} sx={{ borderRight: 1, borderColor: 'divider', height: '100%', overflow: 'auto' }}>
                <Box p={2}>
                    <Typography variant="h6" gutterBottom>Knowledge Source</Typography>
                    <Divider sx={{ mb: 2 }} />
                    <List>
                        {files.map((file, i) => {
                            const path = file.path || file.metadata?.path;
                            const name = path ? path.split('/').pop() : 'Unknown File';
                            return (
                                <ListItem
                                    button
                                    key={i}
                                    selected={selectedFile === file}
                                    onClick={() => handleFileSelect(file)}
                                >
                                    <ListItemAvatar>
                                        <Avatar><FileIcon /></Avatar>
                                    </ListItemAvatar>
                                    <ListItemText primary={name} secondary={file.project || "No Project"} />
                                </ListItem>
                            );
                        })}
                    </List>
                </Box>
            </Grid>

            {/* Main Content */}
            <Grid item xs={9} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                {selectedFile ? (
                    <>
                        {/* Feature Tabs */}
                        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                            <Grid container>
                                <Grid item xs={4}>
                                    <Button
                                        fullWidth
                                        startIcon={<SummaryIcon />}
                                        variant={activeTab === 'summary' ? 'contained' : 'text'}
                                        onClick={() => setActiveTab('summary')}
                                        sx={{ borderRadius: 0, py: 2 }}
                                    >
                                        Smart Summary
                                    </Button>
                                </Grid>
                                <Grid item xs={4}>
                                    <Button
                                        fullWidth
                                        startIcon={<TreeIcon />}
                                        variant={activeTab === 'tree' ? 'contained' : 'text'}
                                        onClick={() => setActiveTab('tree')}
                                        sx={{ borderRadius: 0, py: 2 }}
                                    >
                                        Knowledge Tree
                                    </Button>
                                </Grid>
                                <Grid item xs={4}>
                                    <Button
                                        fullWidth
                                        startIcon={<PodcastIcon />}
                                        variant={activeTab === 'podcast' ? 'contained' : 'text'}
                                        onClick={() => setActiveTab('podcast')}
                                        sx={{ borderRadius: 0, py: 2 }}
                                    >
                                        Deep Dive Podcast
                                    </Button>
                                </Grid>
                            </Grid>
                        </Box>

                        {/* Content Area */}
                        <Box sx={{ p: 3, flex: 1, overflow: 'auto' }}>
                            {loading ? (
                                <Box display="flex" justifyContent="center" alignItems="center" height="50%">
                                    <CircularProgress />
                                    <Typography sx={{ ml: 2 }}>Analyzing Knowledge Base...</Typography>
                                </Box>
                            ) : (
                                <>
                                    {activeTab === 'summary' && renderSummary()}
                                    {activeTab === 'tree' && renderTree()}
                                    {activeTab === 'podcast' && renderPodcast()}
                                </>
                            )}
                        </Box>
                    </>
                ) : (
                    <Box display="flex" justifyContent="center" alignItems="center" height="100%">
                        <Typography variant="h5" color="text.secondary">
                            Select a file to begin Deep Analysis
                        </Typography>
                    </Box>
                )}
            </Grid>
        </Grid>
    );
};

export default KnowledgeStudio;
