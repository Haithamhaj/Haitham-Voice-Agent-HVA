import React, { useState, useEffect } from 'react';
import { Folder, File, ChevronRight, ChevronDown, HardDrive } from 'lucide-react';
import { api } from '../../services/api';

const TreeNode = ({ node, level = 0 }) => {
    const [isOpen, setIsOpen] = useState(false);
    const hasChildren = node.children && node.children.length > 0;

    const getIcon = () => {
        if (node.type === 'directory') return <Folder size={16} className="text-blue-400" />;
        // Add more specific file icons here if needed
        return <File size={16} className="text-hva-muted" />;
    };

    return (
        <div className="select-none">
            <div
                className={`flex items-center gap-2 py-1 px-2 hover:bg-white/5 rounded cursor-pointer transition-colors ${level === 0 ? 'font-bold text-hva-cream' : 'text-hva-muted text-sm'}`}
                style={{ paddingRight: `${level * 12}px` }} // RTL indentation
                onClick={() => hasChildren && setIsOpen(!isOpen)}
            >
                {hasChildren && (
                    <span className="text-hva-muted">
                        {isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} className="rtl:rotate-180" />}
                    </span>
                )}
                {!hasChildren && <span className="w-[14px]" />} {/* Spacer */}

                {getIcon()}
                <span className="truncate">{node.name}</span>
            </div>

            {isOpen && hasChildren && (
                <div className="mr-2 border-r border-white/10 pr-2">
                    {node.children.map((child, index) => (
                        <TreeNode key={index} node={child} level={level + 1} />
                    ))}
                </div>
            )}
        </div>
    );
};

const FileSystemTree = () => {
    const [treeData, setTreeData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchTree = async () => {
            try {
                // Fetch Home directory with depth 3
                const result = await api.getFileTree("~", 3);
                if (result.success) {
                    setTreeData(result.tree);
                } else {
                    setError(result.message);
                }
            } catch (err) {
                setError("Failed to load file system.");
            } finally {
                setLoading(false);
            }
        };

        fetchTree();
    }, []);

    if (loading) return <div className="animate-pulse h-40 bg-white/5 rounded-xl"></div>;
    if (error) return <div className="text-red-400 text-sm p-4">Error: {error}</div>;

    return (
        <div className="bg-hva-card rounded-2xl border border-hva-border-subtle p-4 h-[400px] flex flex-col">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold text-hva-cream flex items-center gap-2">
                    <HardDrive size={20} className="text-hva-accent" />
                    شجرة المعرفة (الملفات)
                </h2>
                <div className="text-xs text-hva-muted bg-white/5 px-2 py-1 rounded">Live</div>
            </div>

            <div className="flex-1 overflow-y-auto custom-scrollbar pr-1" dir="rtl">
                {treeData ? (
                    <TreeNode node={treeData} />
                ) : (
                    <p className="text-hva-muted text-center mt-10">No files found.</p>
                )}
            </div>
        </div>
    );
};

export default FileSystemTree;
