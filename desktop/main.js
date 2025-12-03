import { app, BrowserWindow, ipcMain, globalShortcut } from 'electron';
import path from 'path';
import { fileURLToPath } from 'url';
import { spawn } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let mainWindow;
let apiProcess;

async function startApi() {
    if (process.env.NODE_ENV === 'development') {
        console.log('Development mode: API should be running separately.');
        return;
    }

    const apiPath = path.join(process.resourcesPath, 'hva_backend');
    console.log('Starting API from:', apiPath);

    const logFile = path.join('/tmp', 'hva_backend.log');
    const fs = await import('fs');
    const out = fs.openSync(logFile, 'a');
    const err = fs.openSync(logFile, 'a');

    apiProcess = spawn(apiPath, [], {
        stdio: ['ignore', out, err]
    });

    apiProcess.on('error', (err) => {
        console.error('Failed to start API:', err);
    });
}

function createWindow() {
    startApi();

    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1000,
        minHeight: 700,
        frame: false,
        transparent: true,
        vibrancy: 'under-window',
        visualEffectState: 'active',
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false,
            webSecurity: false
        }
    });

    // Load React app
    if (process.env.NODE_ENV === 'development') {
        mainWindow.loadURL('http://localhost:5173');
        mainWindow.webContents.openDevTools();
    } else {
        mainWindow.loadFile(path.join(__dirname, 'dist_renderer/index.html'));
    }

    // Register global shortcut
    globalShortcut.register('CommandOrControl+Shift+H', () => {
        mainWindow.webContents.send('trigger-voice');
    });
}

app.whenReady().then(() => {
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (apiProcess) {
        apiProcess.kill();
    }
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('before-quit', () => {
    if (apiProcess) {
        apiProcess.kill();
    }
});

// IPC Handlers
ipcMain.handle('minimize', () => mainWindow.minimize());
ipcMain.handle('maximize', () => {
    if (mainWindow.isMaximized()) {
        mainWindow.unmaximize();
    } else {
        mainWindow.maximize();
    }
});
ipcMain.handle('close', () => mainWindow.close());
