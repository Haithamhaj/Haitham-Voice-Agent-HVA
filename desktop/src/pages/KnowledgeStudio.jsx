import React, { useState, useEffect } from 'react';
import {
    FileText,
    Network,
    Mic,
    FileOutput,
    Play,
    Pause,
    Clock,
    UploadCloud
} from 'lucide-react';
import { api } from '../services/api';

// Simple Tree Visualization Component (Recursive)
const TreeNode = ({ node, level = 0 }) => (
    <div style={{ marginLeft: `${level * 16}px`, marginTop: '8px' }}>
        <span className={`inline-flex items-center px-2 py-1 rounded text-sm ${level === 0 ? 'bg-hva-accent text-hva-primary font-bold' : 'border border-hva-card-hover text-hva-cream'}`}>
            {node.name || node.label}
        </span>
        {node.children && node.children.map((child, i) => (
            <TreeNode key={i} node={child} level={level + 1} />
        ))}
    </div>
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
            setFiles(res.files || []);
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
            const path = selectedFile.path || selectedFile.metadata?.path;

            if (feature === 'summary') {
                result = await api.post('/knowledge/summary', { path });
                setData(prev => ({ ...prev, summary: result }));
            } else if (feature === 'tree') {
                result = await api.post('/knowledge/tree', { path });
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

    const handleUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        setLoading(true);
        const formData = new FormData();
        formData.append('file', file);
        formData.append('project_id', 'general');

        try {
            await api.post('/knowledge/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            // Refresh list
            await fetchFiles();
        } catch (err) {
            console.error("Upload failed", err);
        } finally {
            setLoading(false);
        }
    };

    // --- Renderers ---

    const renderSummary = () => (
        <div className="space-y-4">
            <h2 className="text-xl font-bold text-hva-cream mb-4">Deep Summary</h2>
            {data.summary ? (
                <div className="space-y-4">
                    <div className="p-4 bg-hva-card rounded-lg border border-hva-card-hover text-hva-cream whitespace-pre-line leading-relaxed">
                        {data.summary.final_summary || data.summary}
                    </div>
                    {/* If recursive chunks exist */}
                    {data.summary.chunk_summaries && (
                        <div className="mt-6">
                            <h3 className="text-sm font-semibold text-hva-muted mb-2">Detailed Breakdown:</h3>
                            {data.summary.chunk_summaries.map((chunk, i) => (
                                <div key={i} className="p-3 mb-2 bg-hva-primary/50 rounded border border-hva-card-hover text-sm text-hva-dim">
                                    {chunk}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            ) : (
                <div className="text-center mt-12">
                    <p className="text-hva-muted mb-4">No summary generated yet.</p>
                    <button
                        onClick={() => generateFeature('summary')}
                        className="px-6 py-2 bg-hva-accent text-hva-primary font-bold rounded-lg hover:bg-hva-accent/90 transition-colors"
                    >
                        Generate Deep Summary
                    </button>
                </div>
            )}
        </div>
    );

    const renderTree = () => (
        <div>
            <h2 className="text-xl font-bold text-hva-cream mb-4">Knowledge Tree</h2>
            {data.tree ? (
                <div>
                    <div className="mb-4">
                        <span className="text-hva-muted">Root: </span>
                        <span className="text-hva-accent font-mono">{data.tree.root}</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                        {data.tree.topics && data.tree.topics.map((t, i) => (
                            <div key={i} className="flex items-center gap-2 px-3 py-2 bg-hva-card border border-hva-card-hover rounded-lg">
                                <Network size={16} className="text-hva-accent" />
                                <span className="text-hva-cream">{t.properties?.name || "Topic"}</span>
                            </div>
                        ))}
                    </div>
                    {data.tree.topics?.length === 0 && <p className="text-hva-muted">No topics extracted yet.</p>}
                </div>
            ) : (
                <div className="text-center mt-12">
                    <p className="text-hva-muted mb-4">Knowledge graph not built.</p>
                    <button
                        onClick={() => generateFeature('tree')}
                        className="px-6 py-2 bg-hva-accent text-hva-primary font-bold rounded-lg hover:bg-hva-accent/90 transition-colors"
                    >
                        Build Knowledge Tree
                    </button>
                </div>
            )}
        </div>
    );

    const renderPodcast = () => (
        <div>
            <h2 className="text-xl font-bold text-hva-cream mb-4">Deep Dive Podcast</h2>
            {data.podcast ? (
                <div>
                    <h3 className="text-lg font-medium text-hva-accent mb-4">{data.podcast.title}</h3>
                    <div className="max-h-[60vh] overflow-y-auto space-y-4 p-4 bg-hva-card rounded-xl border border-hva-card-hover custom-scrollbar">
                        {data.podcast.script && data.podcast.script.map((line, i) => (
                            <div key={i} className={`flex gap-4 ${line.speaker === 'Sarah' ? 'flex-row' : 'flex-row-reverse'}`}>
                                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${line.speaker === 'Sarah' ? 'bg-purple-500/20 text-purple-400' : 'bg-blue-500/20 text-blue-400'
                                    }`}>
                                    {line.speaker[0]}
                                </div>
                                <div className={`flex-1 p-3 rounded-lg ${line.speaker === 'Sarah' ? 'bg-purple-500/10 rounded-tl-none' : 'bg-blue-500/10 rounded-tr-none'
                                    }`}>
                                    <div className="text-xs font-bold mb-1 opacity-70 {line.speaker === 'Sarah' ? 'text-purple-400' : 'text-blue-400'}">
                                        {line.speaker}
                                    </div>
                                    <p className="text-hva-cream leading-relaxed">{line.text}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                    <div className="mt-6 text-center">
                        <button disabled className="px-6 py-2 border border-hva-muted text-hva-muted rounded-lg flex items-center gap-2 mx-auto cursor-not-allowed opacity-50">
                            <Play size={18} /> Play Audio (Coming Soon)
                        </button>
                    </div>
                </div>
            ) : (
                <div className="text-center mt-12">
                    <p className="text-hva-muted mb-4">No podcast script generated.</p>
                    <button
                        onClick={() => generateFeature('podcast')}
                        className="px-6 py-2 bg-hva-accent text-hva-primary font-bold rounded-lg hover:bg-hva-accent/90 transition-colors"
                    >
                        Generate Podcast Script
                    </button>
                </div>
            )}
        </div>
    );

    return (
        <div className="flex h-full">
            {/* Sidebar: File List */}
            <div className="w-1/4 border-l border-hva-card-hover h-full flex flex-col bg-hva-card/30">
                <div className="p-4 border-b border-hva-card-hover">
                    <h2 className="text-lg font-bold text-hva-cream flex items-center gap-2">
                        <FileText size={20} className="text-hva-accent" />
                        Knowledge Source
                    </h2>
                </div>

                {/* Upload Button */}
                <div className="px-4 pb-4 border-b border-hva-card-hover">
                    <label className="flex items-center justify-center gap-2 w-full py-2 bg-hva-accent/10 border border-hva-accent/30 rounded-lg text-hva-accent hover:bg-hva-accent/20 cursor-pointer transition-colors">
                        <UploadCloud size={18} />
                        <span className="font-medium text-sm">Upload New File</span>
                        <input type="file" className="hidden" onChange={handleUpload} />
                    </label>
                </div>

                <div className="flex-1 overflow-y-auto custom-scrollbar p-2">
                    {files.map((file, i) => {
                        const path = file.path || file.metadata?.path;
                        const name = path ? path.split('/').pop() : 'Unknown File';
                        const isSelected = selectedFile === file;
                        return (
                            <button
                                key={i}
                                onClick={() => handleFileSelect(file)}
                                className={`w-full text-right p-3 rounded-lg mb-2 transition-all duration-200 flex items-start gap-3 ${isSelected
                                    ? 'bg-hva-accent/20 border border-hva-accent/50'
                                    : 'hover:bg-hva-card-hover border border-transparent'
                                    }`}
                            >
                                <div className={`mt-1 ${isSelected ? 'text-hva-accent' : 'text-hva-muted'}`}>
                                    <FileText size={18} />
                                </div>
                                <div className="flex-1 overflow-hidden">
                                    <div className={`font-medium truncate ${isSelected ? 'text-hva-cream' : 'text-hva-dim'}`}>
                                        {name}
                                    </div>
                                    <div className="text-xs text-hva-muted truncate mt-0.5">
                                        {file.project || "No Project"}
                                    </div>
                                </div>
                            </button>
                        );
                    })}
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 flex flex-col h-full overflow-hidden">
                {selectedFile ? (
                    <>
                        {/* Feature Tabs */}
                        <div className="border-b border-hva-card-hover bg-hva-card/50">
                            <div className="flex">
                                {[
                                    { id: 'summary', icon: FileOutput, label: 'Smart Summary' },
                                    { id: 'tree', icon: Network, label: 'Knowledge Tree' },
                                    { id: 'podcast', icon: Mic, label: 'Deep Podcast' }
                                ].map(tab => (
                                    <button
                                        key={tab.id}
                                        onClick={() => setActiveTab(tab.id)}
                                        className={`flex-1 py-4 flex items-center justify-center gap-2 transition-all duration-200 border-b-2 ${activeTab === tab.id
                                            ? 'border-hva-accent text-hva-accent bg-hva-accent/5'
                                            : 'border-transparent text-hva-muted hover:text-hva-cream hover:bg-hva-card-hover'
                                            }`}
                                    >
                                        <tab.icon size={18} />
                                        <span className="font-medium">{tab.label}</span>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Content Area */}
                        <div className="flex-1 p-6 overflow-y-auto custom-scrollbar">
                            {loading ? (
                                <div className="h-full flex flex-col items-center justify-center text-hva-accent/80">
                                    <Clock size={48} className="animate-spin mb-4" />
                                    <p className="text-lg animate-pulse">Analyzing Knowledge Base...</p>
                                </div>
                            ) : (
                                <div className="max-w-4xl mx-auto">
                                    {activeTab === 'summary' && renderSummary()}
                                    {activeTab === 'tree' && renderTree()}
                                    {activeTab === 'podcast' && renderPodcast()}
                                </div>
                            )}
                        </div>
                    </>
                ) : (
                    <div className="h-full flex flex-col items-center justify-center text-hva-muted">
                        <div className="w-20 h-20 bg-hva-card rounded-full flex items-center justify-center mb-6">
                            <FileText size={40} className="text-hva-dim" />
                        </div>
                        <h3 className="text-xl font-medium mb-2">Select a file to begin</h3>
                        <p className="text-sm opacity-60">Choose a document from the sidebar to analyze</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default KnowledgeStudio;
